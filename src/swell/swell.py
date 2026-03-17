import importlib
import sys
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

def main():
    if len(sys.argv) < 2:
        print("Usage: swell <command>")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd not in COMMANDS:
        print(f"Unknown command: {cmd}")
        sys.exit(1)

    module = importlib.import_module(COMMANDS[cmd])

    write_welcome_message()
    module.main(sys.argv[2:])


if __name__ == "__main__":
    main()
