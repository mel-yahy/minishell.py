import os
import sys
import re
import config


def echo_builtin(args: list[str]) -> None:
    with_option = len(args) > 1 and args[1] == "-n"
    i = 2 if with_option else 1
    while i < len(args):
        end_char = " " if i != len(args) - 1 else ""
        print(args[i], end=end_char)
        i += 1
    if not with_option:
        print()
    sys.exit(0)


def exit_builtin(args: list[str]) -> None:
    if len(args) == 1:
        sys.exit(config.LAST_EXIT)
    elif len(args) > 1:
        try:
            exit_code = int(args[1])
        except ValueError:
            print(f"exit: {args[1]}: numeric argument required", file=sys.stderr)
            sys.exit(2)
        if len(args) == 2:
            sys.exit(exit_code)
        else:
            print("exit: too many arguments", file=sys.stderr)
            config.LAST_EXIT = 1


def cd_builtin(args: list[str]) -> None:
    if len(args) > 2:
        print("cd: too many arguments", file=sys.stderr)
        config.LAST_EXIT = 1
        return
    try:
        os.chdir(args[1])
        config.LAST_EXIT = 0
    except OSError as error:
        print(f"cd: {args[1]}: {error.strerror}")
        config.LAST_EXIT = 1


def pwd_builtin() -> None:
    cwd = os.getcwd()
    print(cwd)
    sys.exit(0)


def env_builtin() -> None:
    for key, value in config.ENV.items():
        print(f"{key}={value}")
    sys.exit(0)


def export_builtin(args: list[str]) -> None:
    config.LAST_EXIT = 0
    for arg in args[1:]:
        if "=" in arg:
            key, value = arg.split("=", 1)
        else:
            key, value = arg, None
        if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", key):
            print(f"export: '{key}': not a valid identifier", file=sys.stderr)
            config.LAST_EXIT = 1
            continue
        if value is not None:
            config.ENV[key] = value


def unset_builtin(args: list[str]) -> None:
    for arg in args[1:]:
        _ = config.ENV.pop(arg, None)
    config.LAST_EXIT = 0
