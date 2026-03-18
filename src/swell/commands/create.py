import os
import click
from typing import Union
from swell.swell_path import get_swell_path
from swell.deployment.platforms.platforms import get_platforms
from swell.commands.help_strings import (input_method_help, platform_help,
                                         override_help, advanced_help, slurm_help, skip_r2d2_help)

class LazySuiteChoice(click.ParamType):
    name = "suite"
    def convert(self, value, param, ctx):
        suites_dir = os.path.join(get_swell_path(), 'suites')
        suite_names = [
            name for name in os.listdir(suites_dir)
            if os.path.isdir(os.path.join(suites_dir, name))
            and not name.startswith('__')
        ]
        if value not in suite_names:
            self.fail(f"{value} is not a valid suite", param, ctx)
        return value


@click.command()
@click.argument('suite', type=LazySuiteChoice())
@click.option('-m', '--input_method', 'input_method', default='defaults',
              type=click.Choice(['defaults', 'cli']), help=input_method_help)
@click.option('-p', '--platform', 'platform', default='nccs_discover_sles15',
              type=click.Choice(get_platforms()), help=platform_help())
@click.option('-o', '--override', 'override', default=None, help=override_help)
@click.option('-a', '--advanced', 'advanced', default=False, help=advanced_help)
@click.option('-s', '--slurm', 'slurm', default=None, help=slurm_help)
@click.option('-k', '--skip-r2d2', 'skip_r2d2', is_flag=True, default=False, help=skip_r2d2_help)

def create(
    suite: str,
    input_method: str,
    platform: str,
    override: Union[dict, str, None],
    advanced: bool,
    slurm: str,
    skip_r2d2: bool
) -> None:
    """
    Create a new experiment

    This command creates an experiment directory based on the provided suite name and options.

    Arguments: \n
        suite (str): Name of the suite you wish to run. \n

    """
    from swell.deployment.create_experiment import create_experiment_directory
    create_experiment_directory(suite, input_method, platform, override, advanced, slurm, skip_r2d2)

def main(args):
    create.main(args=args)

