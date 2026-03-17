import click

@click.command()
@click.argument("suite")
@click.option("-m","--input_method",default="defaults")
@click.option("-p","--platform",default="nccs_discover_sles15")
@click.option("-o","--override",default=None)
@click.option("-a","--advanced",is_flag=True)
@click.option("-s","--slurm",default=None)

def cli(
        suite,
        input_method,
        platform,
        override,
        advanced,
        slurm):

    from swell.deployment.create_experiment import create_experiment_directory

    create_experiment_directory(
        suite,
        input_method,
        platform,
        override,
        advanced,
        slurm
    )


def main(args):
    cli.main(args=args)
