import click

@click.command()
@click.argument('configuration')
@click.argument('experiment_id')
@click.option('-m', '--input_method', default='defaults',
              type=click.Choice(['defaults', 'cli']))
@click.option('-p', '--platform', default=None)
@click.option('-a', '--advanced', is_flag=True, default=False)

def cli(
    configuration,
    experiment_id,
    input_method,
    platform,
    advanced
):
    from swell.deployment.create_experiment import clone_config, create_experiment_directory

    experiment_dict_str = clone_config(configuration, experiment_id, input_method, platform, advanced)
    create_experiment_directory(experiment_dict_str)


def main(args):
    cli.main(args=args)
