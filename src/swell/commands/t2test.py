import click
from swell.deployment.platforms.platforms import get_platforms
from swell.commands.help_strings import platform_help
from typing import Optional, Literal


@click.command()
@click.option('-p', '--platform', 'platform', type=click.Choice(get_platforms()),
              default="nccs_discover_sles15", help=platform_help())
@click.argument('suite', type=click.Choice(("hofx", "3dvar_marine", "ufo_testing",
                                            "convert_ncdiags", "3dfgat_atmos", "build_jedi")))
def t2test(
    suite: Literal["hofx", "3dvar_marine", "ufo_testing",
                   "convert_ncdiags", "3dfgat_atmos", "build_jedi"],
        platform: Optional[str] = "nccs_discover_sles15"
) -> None:
    """
    Run a particular swell suite from the tier 2 tests.

    Arguments:
        suite (str): Name of the suite to run (e.g., hofx, 3dvar_marine, ufo_testing)
    """
    from swell.test.suite_tests.suite_tests import run_suite, TestSuite
    run_suite(suite, platform, TestSuite.TIER2)

    
