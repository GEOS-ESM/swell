import click

@click.command()
@click.argument("task")
@click.argument("config")

def cli(task, config):

    from swell.tasks.base.task_base import task_wrapper

    task_wrapper(task, config)


def main(args):
    cli.main(args=args)
