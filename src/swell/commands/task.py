import os
import glob
import click
from typing import Optional
from swell.swell_path import get_swell_path
from swell.commands.help_strings import datetime_help, model_help, ensemble_help


def snake_case_to_camel_case(name: str) -> str:
    return ''.join(word.capitalize() for word in name.split('_'))


class TaskChoice(click.ParamType):
    """Click parameter type for dynamically listing tasks."""

    name = "task"

    def convert(self, value, param, ctx):
        tasks = self.get_tasks()  # lazy evaluation
        if value not in tasks:
            self.fail(f"{value} is not a valid task", param, ctx)
        return value

    @staticmethod
    def get_tasks() -> list[str]:
        """Return list of task names in CamelCase."""
        tasks_dir = os.path.join(get_swell_path(), "tasks", "*.py")
        return sorted(
            snake_case_to_camel_case(os.path.splitext(os.path.basename(f))[0])
            for f in glob.glob(tasks_dir)
            if "__" not in os.path.basename(f)
        )


TASK = TaskChoice()


@click.command()
@click.argument('task', type=TASK)
@click.argument('config')
@click.option('-d', '--datetime', 'datetime', default=None, help=datetime_help)
@click.option('-m', '--model', 'model', default=None, help=model_help)
@click.option('-p', '--ensemblePacket', 'ensemblePacket', default=None, help=ensemble_help)
def task(
        task: str,
        config: str,
        datetime: Optional[str],
        model: Optional[str],
        ensemblePacket: Optional[str]
) -> None:
    """
    Run a workflow task

    This command executes a task using the provided task name, configuration file and options.

    Arguments:\n
        task (str): Name of the task to execute.\n
        config (str): Path to the configuration file for the task.\n

    """
    from swell.tasks.base.task_base import task_wrapper
    task_wrapper(task, config, datetime, model, ensemblePacket)
