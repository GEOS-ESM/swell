# (C) Copyright 2021-2022 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.

# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


import glob
import netCDF4 as nc
import numpy as np
import os
import xarray as xr
import yaml

from swell.tasks.base.task_base import taskBase
from swell.utilities.observations import find_instrument_from_string


# --------------------------------------------------------------------------------------------------


class MergeIodaFiles(taskBase):

    """
    Task to combine IODA output files written by each processor of a JEDI run.
    """

    def execute(self):

        # Parse config
        cycle_dir = self.config.get('cycle_dir')
        save_geovals = self.config.get("save_geovals", False)

        # Config file used with jedi executable
        jedi_config_file = os.path.join(cycle_dir, 'jedi_config.yaml')

        # Read into dictionary
        with open(jedi_config_file, 'r') as jedi_config_string:
            config = yaml.safe_load(jedi_config_string)

        # Dictionary with observation config
        observers = config['observations']['observers']

        # Loop over observations
        for observer in observers:

            # Dataset to hold the concatenated files for both observations and geovals
            ds_all = xr.Dataset()

            # Arrays to hold metadata for each variable
            units = []
            coordinates = []
            fillvalues = []

            # Keep track of whether there is something to write
            data_to_write = False

            # Split the full obs output path into path and filename
            cycle_dir, obs_file = os.path.split(observer['obs space']['obsdataout']['obsfile'])

            # Read in the observation output files if the pool is larger than 1
            # -----------------------------------------------------------------

            # Check IO pool and skip merge if ioda output a single file
            try:
                max_pool_size = observer['obs space']['io pool']['max pool size']
            except Exception:
                max_pool_size = None

            if max_pool_size == 1:
                self.logger.info('Max pool size for IO is 1 for this intrument, skipping merge.')
            else:

                # Write info
                instrument = find_instrument_from_string(obs_file, self.logger)
                self.logger.info('Combining IODA output files for '+instrument+'.')

                # Split base and extension part of filename
                obs_file_bse = os.path.splitext(obs_file)[0]
                obs_file_ext = os.path.splitext(obs_file)[1]

                # Append with underscore and proc number
                filename_search = os.path.join(cycle_dir, obs_file_bse + '_*' + obs_file_ext)

                # Get a list of files for this instrument
                filenames = glob.glob(filename_search)
                filenames.sort()

                # Read all variables from the filenames
                # -------------------------------------
                nlocs_start = 1
                for ifile, filename in enumerate(filenames):

                    # Open the data with NetCDF to get info
                    nds = nc.Dataset(filename)
                    coord_names = list(nds.dimensions)

                    # Create a dictionary of coordinate data
                    coord_data_dict = {}
                    for coord_name in coord_names:
                        coord_data_dict[coord_name] = nds[coord_name][:].data

                        # For nlocs put in actual range
                        if 'nlocs' in coord_name:
                            nlocs_final = nlocs_start + len(nds[coord_name][:].data)
                            coord_data_dict[coord_name] = range(nlocs_start, nlocs_final)
                            nlocs_start = nlocs_final

                        # Set nvars to integer
                        if 'nvars' in coord_name:
                            coord_data_dict[coord_name] = range(1, len(nds[coord_name][:].data) + 1)

                    # Create dataset with coordinates
                    ds_obs = xr.Dataset(coords=coord_data_dict)

                    # Read group variables into Dataset
                    for group in list(nds.groups):

                        # Open group
                        with xr.open_dataset(filename, group=group, mask_and_scale=False) as ds_grp:

                            # Read all the variables in the group
                            for variable in list(ds_grp.variables):

                                # Put variables into dataset named group/variable
                                ds_obs[group+'/'+variable] = ds_grp[variable]

                                # Save units, fillvalue and coordinates
                                if ifile == 0:
                                    nds_var = nds.groups[group].variables[variable]
                                    try:
                                        fillvalues.append(nds_var._FillValue)
                                    except Exception:
                                        fillvalues.append('')
                                    try:
                                        coordinates.append(nds_var.coordinates)
                                    except Exception:
                                        coordinates.append('')
                                    try:
                                        units.append(nds_var.units)
                                    except Exception:
                                        units.append('')

                    if ifile == 0:
                        ds_obs_all = ds_obs
                    else:
                        ds_obs_all = xr.concat([ds_obs_all, ds_obs], dim='nlocs')

                    # Close netcdf file
                    nds.close()

                # Merge with main dataset
                # -----------------------
                ds_all = ds_all.merge(ds_obs_all)
                data_to_write = True

            # Add the GeoVaLs variables if needed
            # -----------------------------------
            if save_geovals:

                # Loop over filters, find geoval saver and extract filename
                for obs_filter in observer['obs filters']:
                    if obs_filter['filter'] == 'GOMsaver':
                        cycle_dir, geovals_file = os.path.split(obs_filter['filename'])
                        break

                # Write info
                instrument = find_instrument_from_string(geovals_file, self.logger)
                self.logger.info('Adding GeoVaLs for '+instrument+'.')

                # Split base and extension part of filename
                gvals_file_bse = os.path.splitext(geovals_file)[0]
                gvals_file_ext = os.path.splitext(geovals_file)[1]

                # Append with underscore and proc number
                filename_search = os.path.join(cycle_dir, gvals_file_bse + '_*' + gvals_file_ext)

                # Get a list of files for this instrument
                filenames = glob.glob(filename_search)
                filenames.sort()

                # Loop over geovals files
                nlocs_start = 1
                for ifile, filename in enumerate(filenames):

                    # Open the file as a Dataset
                    with xr.open_dataset(filename) as ds_geovals:

                        # Create a dictionary of coordinate data
                        coord_data_dict = {}
                        for dim in list(ds_geovals.dims):
                            coord_data_dict[dim] = range(1, ds_geovals.dims[dim]+1)

                            # For nlocs put in actual range
                            if 'nlocs' in dim:
                                nlocs_final = nlocs_start + ds_geovals.dims[dim]
                                coord_data_dict[dim] = range(nlocs_start, nlocs_final)
                                nlocs_start = nlocs_final

                        ds_geovals = ds_geovals.assign_coords(coords=coord_data_dict)

                        # Rename variables to GeoVaLs/variable
                        rename_dict = {}
                        for data_var in list(ds_geovals.data_vars):
                            rename_dict[data_var] = 'GeoVaLs/' + data_var
                        ds_geovals = ds_geovals.rename(rename_dict)

                        # Concatenate the files
                        if ifile == 0:
                            ds_geovals_all = ds_geovals
                        else:
                            ds_geovals_all = xr.concat([ds_geovals_all, ds_geovals], dim='nlocs')

                    # No metadata for geovals
                    if ifile == 0:
                        for data_var in list(ds_geovals.data_vars):
                            units.append('')
                            coordinates.append('')
                            fillvalues.append('')

                # Merge with main dataset
                # -----------------------
                ds_all = ds_all.merge(ds_geovals_all)
                data_to_write = True

            # Write file
            # ----------
            if data_to_write:
                write_mode = 'w'
                if max_pool_size:
                    # There are GeoVals to write but IODA already merged so need to append GeoVaLs
                    write_mode = 'a'

                # Set output filename and create/open
                output_file = os.path.join(cycle_dir, obs_file)
                ncfile = nc.Dataset(output_file, mode=write_mode)

                # Write dimensions and coordinates
                # --------------------------------
                for dim in list(ds_all.dims):
                    dim_val = ncfile.createDimension(dim, ds_all.dims[dim])
                    cor_val = ncfile.createVariable(dim, int, (dim,))
                    if dim != 'nlocs':
                        cor_val[:] = ds_all.coords[dim].data
                    else:
                        cor_val[:] = range(1, len(dim_val)+1)

                # Map between xarray types and nc4 types
                # --------------------------------------
                # TODO: this seems hacky. Is there a better way?
                type_dict = {}
                type_dict['datetime64[ns]'] = 'int64'
                type_dict['int32'] = 'int32'
                type_dict['float32'] = 'float32'
                type_dict['float64'] = 'float64'
                type_dict['object'] = str

                # Loop over datavars
                # ------------------
                for n, data_var in enumerate(list(ds_all.data_vars)):
                    nctype = type_dict[str(ds_all[data_var].dtype)]
                    coord_array = list(ds_all[data_var].sizes)
                    if fillvalues[n] != '':
                        cor_val = ncfile.createVariable(data_var, nctype, (coord_array),
                                                        fill_value=fillvalues[n])
                    else:
                        cor_val = ncfile.createVariable(data_var, nctype, (coord_array))

                    # Write metadata
                    if coordinates[n] != '':
                        cor_val.coordinates = coordinates[n]
                    if units[n] != '':
                        cor_val.units = units[n]

                    # Write data
                    if len(coord_array) == 1:
                        cor_val[:] = ds_all[data_var].values
                    elif len(coord_array) == 2:
                        cor_val[:, :] = ds_all[data_var].values
                    else:
                        self.logger.abort('In merge_ioda_files the dimension of the variable ' +
                                          'is not supported')

                # Close file
                ncfile.close()
