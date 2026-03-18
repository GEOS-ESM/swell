import click
from swell.commands.help_strings import input_method_help, platform_help, advanced_help

@click.command()
@click.argument('configuration')
@click.argument('experiment_id')
@click.option('-m', '--input_method', 'input_method', default='defaults',
              type=click.Choice(['defaults', 'cli']), help=input_method_help)
@click.option('-p', '--platform', 'platform', default=None, help=platform_help())
@click.option('-a', '--advanced', 'advanced', default=False, help=advanced_help)
def clone(
    configuration: str,
    experiment_id: str,
    input_method: str,
    platform: str,
    advanced: bool
) -> None:
    """
    Clone an existing experiment

    This command creates an experiment directory based on the provided experiment configuration.

    Arguments: \n
        configuration (str): Path to a YAML containing the experiment configuration you wish to
        clone from. \n

    """

    from swell.deployment.create_experiment import clone_config, create_experiment_directory
    # Create experiment configuration by cloning from existing experiment
    experiment_dict_str = clone_config(configuration, experiment_id, input_method, platform,
                                       advanced)

    # Create the experiment directory
    create_experiment_directory(experiment_dict_str)
