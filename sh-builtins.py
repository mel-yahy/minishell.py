import os
import sys


env = os.environ # Should be removed here


def echoBuiltIn(text: str) -> None:
    print(text)


def exitBuiltIn(status: int) -> None:
    sys.exit(status)


def cdBuiltIn(path: str) -> None:
    os.chdir(path)


def pwdBuiltIn() -> None:
    cwd = os.getcwd()
    print(cwd)


def envBuiltIn() -> None:
    for key, value in env.items():
        print(f"{key}={value}")


def exportBuiltIn(statement: str) -> None:
    equalSign = statement.index("=")
    key = statement[:equalSign]
    value = statement[equalSign + 1 :]
    env[key] = value


def unsetBuiltIn(key: str) -> None:
    _ = env.pop(key)
