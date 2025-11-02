from defs import RedirType
import os


def isRedirToken(redirToken: str) -> bool:
    if redirToken in ("<", ">", "<<", ">>"):
        return True
    return False


def getRedirType(redirToken: str) -> RedirType:
    match redirToken:
        case "<":
            return RedirType.INPUT
        case ">":
            return RedirType.OUTPUT
        case "<<":
            return RedirType.HEREDOC
        case ">>":
            return RedirType.APPEND
        case _:
            return RedirType.DEFAULT


def findCmdPath(cmdName: str) -> str | None:
    pathEnv = os.getenv("PATH", None)
    if not pathEnv:
        return None
    for dirPath in pathEnv.split(":"):
        fullPath = os.path.join(dirPath, cmdName)
        if os.path.isfile(fullPath) and os.access(fullPath, os.X_OK):
            return fullPath
    return None


def expandEnvVars(args: list[str]) -> None:
    for i, token in enumerate(args):
        if token.startswith("'") and token.endswith("'"):
            args[i] = token[1:-1]
            continue
        elif token.startswith('"') and token.endswith('"'):
            args[i] = token[1:-1]
        if "$" in token:
            args[i] = os.path.expandvars(token)  # You should implement this yourself
