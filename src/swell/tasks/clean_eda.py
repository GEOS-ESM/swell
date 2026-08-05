# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.


# --------------------------------------------------------------------------------------------------

import os
import glob
import shutil
from pathlib import Path
from swell.tasks.base.task_base import taskBase


# --------------------------------------------------------------------------------------------------


class CleanEda(taskBase):

    # ----------------------------------------------------------------------------------------------
    # this file handles both eda and eda_controlpert cases
    #

    def execute(self) -> None:

        # Jedi application name
        # ---------------------
        jedi_application = 'eda'

        # Parse configuration
        # -------------------
        window_type = self.config.window_type()
        window_length = self.config.window_length()
        forecast_length = self.config.forecast_length(window_length)
        background_time_offset = self.config.background_time_offset()
        number_of_iterations = self.config.number_of_iterations()
        jedi_forecast_model = self.config.jedi_forecast_model(None)

        # Set the observing system records path
        self.jedi_rendering.set_obs_records_path(self.config.observing_system_records_path(None))

        gsibec_nlats = self.config.gsibec_nlats(None)
        gsibec_nlons = self.config.gsibec_nlons(None)
        gsibec_configuration = self.config.gsibec_configuration(None)
        npx_proc = self.config.npx_proc(None)
        npy_proc = self.config.npy_proc(None)
        npx = self.config.npx(None)
        npy = self.config.npy(None)

        # Compute data assimilation window parameters
        # --------------------------------------------
        background_time = self.da_window_params.background_time(background_time_offset)
        local_background_time = self.da_window_params.local_background_time(window_length,
                                                                            window_type)
        local_background_time_iso = self.da_window_params.local_background_time_iso(window_length,
                                                                                    window_type)
        window_begin = self.da_window_params.window_begin(window_length)
        window_begin_iso = self.da_window_params.window_begin_iso(window_length)
        window_end_iso = self.da_window_params.window_end_iso(window_length)
        nmember = self.config.ensemble_num_members()
        # imember = self.get_ensemble_imember()

        # Populate jedi interface templates dictionary
        # --------------------------------------------
        self.jedi_rendering.add_key('window_begin_iso', window_begin_iso)
        self.jedi_rendering.add_key('window_end_iso', window_end_iso)
        self.jedi_rendering.add_key('window_length', window_length)
        self.jedi_rendering.add_key('forecast_length', forecast_length)
        self.jedi_rendering.add_key('minimizer', self.config.minimizer())
        self.jedi_rendering.add_key('number_of_iterations', number_of_iterations[0])
        self.jedi_rendering.add_key('analysis_variables', self.config.analysis_variables())
        self.jedi_rendering.add_key('saber_central_block', self.config.saber_central_block(None))
        self.jedi_rendering.add_key('saber_outer_block', self.config.saber_outer_block(None))
        self.jedi_rendering.add_key('gradient_norm_reduction',
                                    self.config.gradient_norm_reduction())
        self.jedi_rendering.add_key('marine_models', self.config.marine_models(None))

        # Background
        # ----------
        self.jedi_rendering.add_key('horizontal_resolution', self.config.horizontal_resolution())
        self.jedi_rendering.add_key('local_background_time', local_background_time)
        self.jedi_rendering.add_key('local_background_time_iso', local_background_time_iso)
        self.jedi_rendering.add_key('ensemble_num_members', self.config.ensemble_num_members())
        self.jedi_rendering.add_key('ensemble_imember', 1)   # pass an integer to jinja2

        # Geometry
        # --------
        self.jedi_rendering.add_key('vertical_resolution', self.config.vertical_resolution())
        self.jedi_rendering.add_key('gsibec_nlats', gsibec_nlats)
        self.jedi_rendering.add_key('gsibec_nlons', gsibec_nlons)
        self.jedi_rendering.add_key('npx_proc', npx_proc)
        self.jedi_rendering.add_key('npy_proc', npy_proc)
        self.jedi_rendering.add_key('npx', npx)
        self.jedi_rendering.add_key('npy', npy)
        self.jedi_rendering.add_key('total_processors', self.config.total_processors(None))

        # Observations
        # ------------
        self.jedi_rendering.add_key('background_time', background_time)
        self.jedi_rendering.add_key('crtm_coeff_dir', self.config.crtm_coeff_dir(None))
        self.jedi_rendering.add_key('window_begin', window_begin)

        # Atmosphere background error model
        # ---------------------------------
        if gsibec_configuration is not None:
            self.jedi_rendering.add_key('gsibec_configuration', gsibec_configuration)
            self.jedi_rendering.add_key('gsibec_nlats', gsibec_nlats)
            self.jedi_rendering.add_key('gsibec_nlons', gsibec_nlons)
            self.jedi_rendering.add_key('gsibec_npx_proc', npx_proc)
            self.jedi_rendering.add_key('gsibec_npy_proc', 6*npy_proc)

        # Model
        # -----
        if window_type == '4D':
            self.jedi_rendering.add_key('background_frequency', self.config.background_frequency())

        # Open the JEDI config file and fill initial templates
        # ----------------------------------------------------
        jedi_config_dict = self.jedi_rendering.render_oops_file(f'{jedi_application}{window_type}',
                                                                window_type,
                                                                jedi_forecast_model)

        # This special design works with either eda or eda_control_pert
        # handle eda case:      analysis/mem00x
        # eda controlpert case: analysis_chunk/chunk00x/mem00y
        # This avoids blindly search for mem0xx dir, as some of them
        # only contains linked analysis files and donot require clean up
        # --------------------------------------------------------------
        d1 = os.path.join(self.cycle_dir(), 'analysis_chunk')        # control pert case
        if not os.path.exists(d1):
            d1 = os.path.join(self.cycle_dir(), 'analysis')          # eda case
        target_dirs = [str(p) for p in Path(d1).rglob('mem*') if p.is_dir()]
        self.logger.info(f'target_dirs = {target_dirs}')

        for mem_dir in target_dirs:
            d2 = os.path.join(mem_dir, 'fv3-jedi')
            if os.path.exists(d2):
                if os.path.islink(d2):
                    # Only remove the symlink itself, never follow it
                    os.unlink(d2)
                    self.logger.info(f"Deleted symlink dir: {d2}")
                else:
                    shutil.rmtree(d2, ignore_errors=True)
                    self.logger.info(f"Deleted directory: {d2}")
            for observer in jedi_config_dict['cost function']['observations']['observers']:
                # Get observation name
                observation = observer['observation_name']
                # Delete input obsfile (.nc4 .tlapse.txt acftbias acftbias_cov)
                for file_path in glob.glob(os.path.join(mem_dir, f'{observation}.*')):
                    if os.path.islink(file_path):
                        os.unlink(file_path)               # safe: removes only the link
                        self.logger.info(f"Deleted symlink file: {file_path}")
                    else:
                        try:
                            os.remove(file_path)
                            self.logger.info(f"Deleted file: {file_path}")
                        except FileNotFoundError:
                            pass   # file disappeared between glob and remove


# --------------------------------------------------------------------------------------------------
