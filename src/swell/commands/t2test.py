import click

@click.command()
@click.option('-p', '--platform', 'platform', default="nccs_discover_sles15")
@click.argument('suite', type=click.Choice(("hofx", "3dvar_marine", "ufo_testing",
                                            "convert_ncdiags", "3dfgat_atmos", "build_jedi")))

def cli(
    suite,
    platform
):
    from swell.test.suite_tests.suite_tests import run_suite

    run_suite(suite, platform, 'TIER2')


def main(args):
    cli.main(args=args)
