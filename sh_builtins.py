import os
import sys
import re
import config


def echoBuiltIn(args: list[str]) -> None:
    withOption = len(args) > 1 and args[1] == "-n"
    i = 2 if withOption else 1
    while i < len(args):
        endChar = " " if i != len(args) - 1 else ""
        print(args[i], end=endChar)
    if not withOption:
        print()


def exitBuiltIn() -> None:
    sys.exit(config.LAST_EXIT)


def cdBuiltIn(path: str) -> None:
    try:
        os.chdir(path)
    except OSError:
        print(f"cd: {OSError}")


def pwdBuiltIn() -> None:
    cwd = os.getcwd()
    print(cwd)


def envBuiltIn() -> None:
    for key, value in config.ENV.items():
        print(f"{key}={value}")


def exportBuiltIn(args: list[str]) -> None:
    for arg in args[1:]:
        if "=" in arg:
            key, value = arg.split("=", 1)
        else:
            key, value = arg, None
        if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", key):
            print(f"export: '{key}': not a valid identifier", file=sys.stderr)
            config.LAST_EXIT = 1
            continue
        if value is None:
            config.ENV[key] = ""
        else:
            config.ENV[key] = value


def unsetBuiltIn(args: list[str]) -> None:
    for arg in args[1:]:
        _ = config.ENV.pop(arg, None)
