import click
from swell.utilities.scripts.utility_driver import get_utilities

@click.command()
@click.argument('utility', type=click.Choice(get_utilities()))
def utility(utility: str) -> None:
    """
    Run a utility script

    This command performs a utility operation specified by the utility argument.

    Arguments:\n
        utility (str): Name of the utility operation to perform.\n

    """
    from swell.utilities.scripts.utility_driver import utility_wrapper
    utility_wrapper(utility)

def main(args):
    utility.main(args=args)
