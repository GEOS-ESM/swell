# Help strings for optional arguments

input_method_help = 'Method by which to create the YAML configuration file. If choosing ' + \
                    'defaults the setting for the default suite test will be used. If using ' + \
                    'CLI you will be led through the questions to configure the experiment.'

def platform_help():
    from swell.deployment.platforms.platforms import get_platforms
    return (
        "If using defaults for input_method, this option is used to determine which "
        "platform to use for platform specific defaults. Options are "
        + str(get_platforms())
    )
#
#platform_help = 'If using defaults for input_method, this option is used to determine which ' + \
#                'platform to use for platform specific defaults. Options are ' + \
#                str(get_platforms())

override_help = 'After generating the config file, parameters inside can be overridden ' + \
                'using values from the override config file.'

advanced_help = 'Show configuration questions which are otherwise not shown to the user.'

no_detach_help = 'Tells the workflow manager not to detach. That is to say run the entire ' + \
                 'run the entire workflow in the foreground and pass back a return code.'

def log_path_help():
    return (
        'Directory to receive workflow manager logging output (instead of '
        '$HOME/cylc-run/<suite_name>'
        )
#log_path_help = 'Directory to receive workflow manager logging output (instead of ' + \
#                '$HOME/cylc-run/<suite_name>)'

datetime_help = 'Datetime to use for task execution. Format is yyyy-mm-ddThh:mm:ss. Note that ' + \
                'non-numeric characters will be stripped from the string. Minutes and seconds ' + \
                'are optional.'

model_help = 'Data assimilation system. I.e. the model being initialized by data assimilation.'

ensemble_help = 'When handling ensemble workflows using a parallel strategy, ' + \
                'specify which packet of ensemble members to consider.'

slurm_help = """
Customize SLURM directives, globally (e.g., account name), for specific tasks,
or for task-model combinations.
"""

skip_r2d2_help = """Skip registering this experiment and storing products in R2D2."""
