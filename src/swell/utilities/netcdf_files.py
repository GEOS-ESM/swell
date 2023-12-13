# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


import os
import xarray as xr


# --------------------------------------------------------------------------------------------------


def combine_files_without_groups(logger, list_of_input_files, output_file, concat_dim,
                                 delete_input=False):

    # Write some information
    logger.info('Combining the following netCDF files (using no-group combine): ')
    for f in list_of_input_files:
        logger.info(f' - {f}', False)
    logger.info(f'Writing to file {output_file}')

    # Load the files as Xarray datasets
    datasets = [xr.open_dataset(f) for f in list_of_input_files]

    # Concatenate the datasets along the 'nlocs' dimension
    concatenated_ds = xr.concat(datasets, dim=concat_dim)

    # Write the concatenated dataset to a new file
    concatenated_ds.to_netcdf(output_file)

    # Delete the input files if requested
    if delete_input:
        for f in list_of_input_files:
            os.remove(f)


# --------------------------------------------------------------------------------------------------
