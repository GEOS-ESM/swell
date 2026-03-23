import click
from swell.test.test_driver import valid_tests


@click.command()
@click.argument('test', type=click.Choice(valid_tests))
def test(test: str) -> None:
    """
    Run one of the test suites

    This command performs the test specified by the test argument.

    Arguments:\n
        test (str): Name of the test to execute.

    """
    from swell.test.test_driver import test_wrapper
    test_wrapper(test)
