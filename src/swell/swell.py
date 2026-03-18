import click
import importlib
import sys

# Import the package to access __version__
import swell
__version__ = swell.__version__

from swell.utilities.welcome_message import write_welcome_message

COMMANDS = {
    "clone":   "swell.commands.clone",
    "create":  "swell.commands.create",
    "launch":  "swell.commands.launch",
    "t1test":  "swell.commands.t1test",
    "t2test":  "swell.commands.t2test",
    "task":    "swell.commands.task",
    "test":    "swell.commands.test",
    "utility": "swell.commands.utility",
}


class SwellCLI(click.MultiCommand):
    def list_commands(self, ctx):
        """Returns sorted list of command names for the Commands: section"""
        return sorted(COMMANDS.keys())

    def get_command(self, ctx, name):
        """Lazy-load the requested command module and return its Click command object"""
        if name not in COMMANDS:
            raise click.UsageError(f"Unknown command: {name}")

        module = importlib.import_module(COMMANDS[name])

        # The command function is usually named the same as the subcommand
        cmd_func_name = name.replace("-", "_")  # handles possible future hyphenated names
        if hasattr(module, cmd_func_name):
            return getattr(module, cmd_func_name)

        # Fallback: look for any click.Command in the module
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if isinstance(attr, click.Command):
                return attr

        raise click.UsageError(
            f"Command '{name}' not found in {COMMANDS[name]}. "
            f"Expected a Click command named '{cmd_func_name}' or similar."
        )


@click.group(cls=SwellCLI)
@click.version_option(
    version=__version__,
    prog_name="swell",
    message="%(prog)s version %(version)s",
)
def swell_driver():
    """
    Welcome to swell!

    This is the top level driver for swell. It serves as a container for various commands
    related to experiment creation, launching, tasks, and utilities.

    The normal process for creating and running an experiment is to issue:

      swell create <suite_name>

    followed by

      swell launch <suite_path>
    """
    pass


def main() -> None:
    """
    Entry point (used by pyproject.toml: swell = "swell.swell:main")
    """

    if len(sys.argv) > 1:
        first_arg = sys.argv[1]
        if first_arg not in ("--help", "-h", "--version", "-V") and "--help" not in sys.argv:
            write_welcome_message()

    swell_driver()


if __name__ == "__main__":
    main()
