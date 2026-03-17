import click

@click.command()
@click.argument('source')
@click.argument('destination')

def cli(source, destination):
    from swell.utilities.scripts.utility_driver import extract_files

    extract_files(source, destination)


def main(args):
    cli.main(args=args)
