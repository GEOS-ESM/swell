# (C) Copyright 2021- United States Government as represented by the Administrator of the
# National Aeronautics and Space Administration. All Rights Reserved.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.

# --------------------------------------------------------------------------------------------------

# Aerosol extinction coefficient field IO names mapping JEDI variable names to GEOS file names

field_io_names = {
    'air_pressure_thickness': 'DELP',
    'moist_air_density': 'AIRDENS',
    'volume_extinction_in_air_due_to_aerosol_particles_lambda1' : 'TOTEXTCOEF470',
    'volume_extinction_in_air_due_to_aerosol_particles_lambda2' : 'TOTEXTCOEF550',
    'volume_extinction_in_air_due_to_aerosol_particles_lambda3' : 'TOTEXTCOEF870'
}

# --------------------------------------------------------------------------------------------------

state_variables = list(field_io_names.keys())

# --------------------------------------------------------------------------------------------------
