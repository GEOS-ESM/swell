import click

@click.command()
@click.argument('test', type=click.Choice(valid_tests))

def cli(test):
    from swell.test.test_driver import test_wrapper

    test_wrapper(test)


def main(args):
    cli.main(args=args)
