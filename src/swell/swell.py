import click
import importlib
import sys

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
        return sorted(COMMANDS.keys())

    def get_command(self, ctx, name):
        if name not in COMMANDS:
            return None
        # Move imports inside the getter so they only trigger when the command is called
        module = importlib.import_module(COMMANDS[name])
        cmd_func_name = name.replace("-", "_")
        return getattr(module, cmd_func_name, None)


@click.group(cls=SwellCLI)
# Fetch version lazily to avoid importing the whole package on every call
@click.version_option(package_name='swell')
def swell_driver():
    """
    Welcome to swell!

    The normal process for creating and running an experiment is to issue:

      swell create <suite_name>

    followed by

      swell launch <suite_path>
    """
    pass


def main() -> None:
    if len(sys.argv) > 1 and sys.argv[1] not in ("--help", "-h", "--version", "-V"):
        from swell.utilities.welcome_message import write_welcome_message
        write_welcome_message()

    swell_driver()


if __name__ == "__main__":
    main()
