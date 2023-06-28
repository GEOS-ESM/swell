# (C) Copyright 2021-2022 United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------


from datetime import datetime as dt
import isodate
import os
import tarfile
import glob
from swell.tasks.base.task_base import taskBase
from r2d2 import R2D2Data

# --------------------------------------------------------------------------------------------------


class ObsProcessSetup(taskBase):

    def execute(self):

        """Acquires background files from a GEOS experiment. Expects traj files stored in a tarfile

           Parameters
           ----------
             All inputs are extracted from the JEDI experiment file configuration.
             See the taskBase constructor for more information.
        """

        # Path to ioda-converters install
        # -------------------------------
        # define iodabin in experiment file
        iodabin = self.config.get('iodabin')

        # Current cycle time (middle of the window)
        # -----------------------------------------
        current_cycle = self.config.get('current_cycle')
        current_cycle_dt = dt.strptime(current_cycle, self.config.dt_format)

        # Set time windows for R2D2
        # ------------------------
        obs_offset = isodate.parse_duration(self.config.get('geos_obs_offset'))
        obs_r2d2_dt = current_cycle_dt - obs_offset

        satbias_offset = isodate.parse_duration(self.config.get('geos_satbias_offset'))
        satbias_r2d2_dt = current_cycle_dt - satbias_offset

        # Create cycle directory if needed
        # --------------------------------
        cycle_dir = self.config.get('cycle_dir')
        print(cycle_dir)
        if not os.path.exists(cycle_dir):
            os.makedirs(cycle_dir, 0o755, exist_ok=True)
        out_dir = cycle_dir + '/out/'
        os.makedirs(out_dir, 0o755, exist_ok=True)

        # Geos experiment settings
        # ------------------------
        geos_experiment = self.config.get('geos_experiment')
        obs_dir_template = self.config.get('geos_obs_dir_template')
        combined_obs_template = self.config.get('combined_obs_template')
        sondes_obs_template = self.config.get('sondes_obs_template')
        sondes_obs_template_rename = self.config.get('sondes_obs_template_rename')
        sfcship_obs_template = self.config.get('sfcship_obs_template')
        sfcship_obs_template_rename = self.config.get('sfcship_obs_template_rename')
        r2d2_obs_standard_template = self.config.get('r2d2_obs_standard_template')
        satbias_org_template = self.config.get('satbias_org_template')
        satbias_template = self.config.get('satbias_template')
        satbiaspc_template = self.config.get('satbiaspc_template')
        satbias_dir_template = self.config.get('satbias_dir_template')
        tlapse_template = self.config.get('tlapse_template')
        r2d2_satbias_template = self.config.get('r2d2_satbias_template')

        obs_dir = current_cycle_dt.strftime(obs_dir_template)
        satbias_dir = obs_r2d2_dt.strftime(satbias_dir_template)
        combined_obs = current_cycle_dt.strftime(combined_obs_template)
        sondes_obs = current_cycle_dt.strftime(sondes_obs_template)
        sondes_obs_rename = current_cycle_dt.strftime(sondes_obs_template_rename)
        sfcship_obs = current_cycle_dt.strftime(sfcship_obs_template)
        sfcship_obs_rename = current_cycle_dt.strftime(sfcship_obs_template_rename)
        r2d2_obs_standard = obs_r2d2_dt.strftime(r2d2_obs_standard_template)
        satbias_org = obs_r2d2_dt.strftime(satbias_org_template)
        satbias = obs_r2d2_dt.strftime(satbias_template)
        satbiaspc = obs_r2d2_dt.strftime(satbiaspc_template)
        tlapse_name = satbias_r2d2_dt.strftime(tlapse_template)
        r2d2_satbias = satbias_r2d2_dt.strftime(r2d2_satbias_template)

        # Copy obs files to cycle directory
        # ---------------------------------
        for filepath in list(glob.glob(obs_dir + '/*ges*nc4')):
            filename = os.path.basename(filepath)
            os.system('ln -sf ' + filepath + ' ' + cycle_dir + '/' + filename)

        # Run proc_gsi_ncdiag
        # ---------------------------------
        # try these without the python calls
        os.system('python ' + iodabin + '/proc_gsi_ncdiag.py -o ' + out_dir + ' ' + cycle_dir)

        # Combine conventional types
        # --------------------------
        conv_types = ['aircraft_', 'rass_', 'sfc_', 'sfcship_', 'sondes_']
        for conv_type in conv_types:
            file_list_str = ''
            for file_name in glob.glob(out_dir + conv_type + '*'):
                file_list_str = file_list_str + file_name + ' '
            os.system('python ' + iodabin + '/combine_obsspace.py -i '
                      + file_list_str + ' -o ' + out_dir + '/' + conv_type + combined_obs)
            # remove files
            os.system('rm ' + file_list_str)

        # Rename some files
        # -----------------
        os.system('mv ' + out_dir + '/' + sondes_obs + ' ' + out_dir + '/' + sondes_obs_rename)
        os.system('mv ' + out_dir + '/' + sfcship_obs + ' ' + out_dir + '/' + sfcship_obs_rename)

        # Rename the files with R2D2 standard
        # -----------------------------------
        os.system('rename _' + combined_obs + ' ' + r2d2_obs_standard + ' ' + out_dir + '/*')

        # Handle satbias
        # --------------
        satbias_out_dir = out_dir + '/satbias/'
        os.system('mkdir -p ' + satbias_out_dir)

        os.system('tar -xvf ' + satbias_dir + satbias_org + ' -C '
                  + satbias_out_dir + ' ' + satbias + ' ' + satbiaspc)
        os.system('ln -sf ' + satbias_out_dir + satbias + ' '
                  + satbias_out_dir + 'ana_satbias_rst.txt')
        os.system('ln -sf ' + satbias_out_dir + satbiaspc + ' '
                  + satbias_out_dir + 'ana_satbiaspc_rst.txt')

        sensors = ['airs_aqua', 'amsua_aqua', 'amsua_metop-a', 'amsua_metop-b', 'amsua_metop-c',
                   'amsua_n15', 'amsua_n18', 'amsua_n19', 'atms_n20', 'atms_npp', 'avhrr3_metop-a',
                   'avhrr3_metop-b', 'avhrr3_n18', 'avhrr3_n19', 'cris-fsr_npp', 'cris-fsr_n20',
                   'gmi_gpm', 'hirs4_metop-a', 'hirs4_n18', 'hirs4_n19', 'iasi_metop-a',
                   'iasi_metop-b', 'mhs_metop-a', 'mhs_metop-b', 'mhs_metop-c', 'mhs_n19',
                   'seviri_m08', 'ssmis_f17', 'ssmis_f18']
        for sensor in sensors:
            os.system('grep -i ' + sensor + ' ' + satbias_out_dir
                      + """ana_satbias_rst.txt | awk '{print $2" "$3" "$4}' > """
                      + satbias_out_dir + 'gsi.' + geos_experiment + '.bc.' + sensor + tlapse_name)

        os.system('module unload core/anaconda/3.8')
        # Make satbias converter part of swell
        os.system('cp ' + '/discover/nobackup/asewnath/jedi_scripts/satbias_converter.yaml '
                  + satbias_out_dir)
        os.chdir(satbias_out_dir)
        print(iodabin + '/satbias2ioda.x satbias_converter.yaml')
        os.system(iodabin + '/satbias2ioda.x satbias_converter.yaml')

        os.system('rename satbias_ gsi.' + geos_experiment + '.bc. *nc4')
        os.system('rename .nc4 ' + r2d2_satbias + ' *nc4')

        os.system('mv ' + satbias_out_dir + '*satbias ' + out_dir)
        os.system('mv ' + satbias_out_dir + '*tlapse ' + out_dir)
        os.chdir(out_dir)
        os.system('rm -rf ' + satbias_out_dir)

        # Call R2D2 to store files
        # ------------------------

        os.environ['R2D2_HOST'] = 'localhost'

        # Perform store of observations
        for filepath in list(glob.glob(out_dir + '/*nc4')):

            source_file = os.path.basename(filepath)
            filename_parts = source_file.split('.')
            name = filename_parts[0]

            file_extension = os.path.splitext(source_file)[1].replace(".", "")

            R2D2Data.store(item             = 'observation'
                          ,source_file      = source_file
                          ,data_store       = 'swell-r2d2'
                          ,provider         = 'x0044'
                          ,observation_type = name
                          ,file_extension   = file_extension
                          ,window_start     = obs_r2d2_dt
                          ,window_length    = 'PT6H')
                          # ,create_date =
                          # ,mod_date =

#            store(date=obs_r2d2_dt,
#                  source_file=source_file,
#                  provider='ncdiag',
#                  obs_type=name,
#                  type='ob',
#                  experiment=geos_experiment)

        # Perform store of satbias
        for filepath in list(glob.glob(out_dir + '/*satbias')):

            source_file = os.path.basename(filepath)
            filename_parts = source_file.split('.')
            name = filename_parts[3]

            file_extension = os.path.splitext(source_file)[1].replace(".", "")

            R2D2Data.store(item             = 'bias_correction'
                          ,source_file      = source_file
                          ,data_store       = 'swell-r2d2'
                          ,model            = 'geos_atmosphere'
                          ,experiment       = geos_experiment
                          ,provider         = 'gsi'
                          ,observation_type = name
                          ,file_extension   = file_extension
                          ,file_type        = 'satbias'
                          ,date             = satbias_r2d2_dt)
                          # ,create_date =
                          # ,mod_date = )

#            store(date=satbias_r2d2_dt,
#                  source_file=source_file,
#                  provider='gsi',
#                  obs_type=name,
#                  type='bc',
#                  experiment=geos_experiment,
#                  file_type='satbias')

        # Perform store of tlapse
        for filepath in list(glob.glob(out_dir + '/*tlapse')):

            source_file = os.path.basename(filepath)
            filename_parts = source_file.split('.')
            name = filename_parts[3]

            file_extension = os.path.splitext(source_file)[1].replace(".", "")

            R2D2Data.store(item             = 'bias_correction'
                          ,source_file      = source_file
                          ,data_store       = 'swell-r2d2'
                          ,model            = 'geos_atmosphere'
                          ,experiment       = geos_experiment
                          ,provider         = 'gsi'
                          ,observation_type = name
                          ,file_extension   = file_extension
                          ,file_type        = 'tlapse'
                          ,date             = satbias_r2d2_dt)
                          # ,create_date =
                          # ,mod_date = )

#            store(date=satbias_r2d2_dt,
#                  source_file=source_file,
#                  provider='gsi',
#                  obs_type=name,
#                  type='bc',
#                  experiment=geos_experiment,
#                  file_type='tlapse')
# --------------------------------------------------------------------------------------------------
