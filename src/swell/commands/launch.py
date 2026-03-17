import click

@click.command()
@click.argument('suite_path')
@click.option('-b', '--no-detach', 'no_detach', is_flag=True, default=False)
@click.option('-l', '--log_path', 'log_path', default=None)

def cli(
    suite_path,
    no_detach,
    log_path
):
    from swell.deployment.launch_experiment import launch_experiment

    launch_experiment(suite_path, no_detach, log_path)


def main(args):
    cli.main(args=args)
