import click

@click.command()
@click.argument('utility', type=click.Choice(get_utilities()))

def cli(utility):
    from swell.utilities.scripts.utility_driver import utility_wrapper

    utility_wrapper(utility)


def main(args):
    cli.main(args=args)
