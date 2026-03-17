import click

@click.command()
@click.option('-p', '--platform', 'platform', default="nccs_discover_sles15")
@click.argument('suite', type=click.Choice(("hofx", "3dvar_marine", "3dvar_atmos",
                                            "localensembleda", "3dvar_cycle")))

def cli(
    suite,
    platform
):
    from swell.test.suite_tests.suite_tests import run_suite

    run_suite(suite, platform, 'TIER1')


def main(args):
    cli.main(args=args)
