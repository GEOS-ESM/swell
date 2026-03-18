import click
from swell.commands.help_strings import no_detach_help, log_path_help


@click.command()
@click.argument('suite_path')
@click.option('-b', '--no-detach', 'no_detach', is_flag=True, default=False, help=no_detach_help)
@click.option('-l', '--log_path', 'log_path', default=None, help=log_path_help())
def launch(
    suite_path: str,
    no_detach: bool,
    log_path: str
) -> None:
    """
    Launch an experiment with the cylc workflow manager

    This command launches an experiment using the provided suite path and options.

    Arguments: \n
        suite_path (str): Path to where the flow.cylc and associated suite files are located. \n

    """
    from swell.deployment.launch_experiment import launch_experiment
    launch_experiment(suite_path, no_detach, log_path)
