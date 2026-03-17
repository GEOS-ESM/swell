#import pkgutil
import importlib
import sys
#import swell.commands

#COMMANDS = {
#    name: f"swell.commands.{name}"
#    for _, name, _ in pkgutil.iter_modules(swell.commands.__path__)
#}

COMMANDS = {
   "clone":   "swell.commands.clone",
   "create":  "swell.commands.create",
   "extract": "swell.commands.extract",
   "launch":  "swell.commands.launch",
   "t1test":  "swell.commands.t1test",
   "t2test":  "swell.commands.t2test",
   "task":    "swell.commands.task",
   "test": "swell.commands.test",
   "utility": "swell.commands.utility",
}
   

#COMMANDS = {
#    "create": "swell.commands.create",
#    "task": "swell.commands.task",
#    "t2test": "swell.commands.t2test",
#    "launch": "swell.commands.launch",
#    # Add other commands here as needed
#}


def main():
    if len(sys.argv) < 2:
        print("Usage: swell <command>")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd not in COMMANDS:
        print(f"Unknown command: {cmd}")
        sys.exit(1)

    module = importlib.import_module(COMMANDS[cmd])

    module.main(sys.argv[2:])


if __name__ == "__main__":
    main()
