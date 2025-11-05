import config
from defs import RedirType
import os
import re


def is_redir_token(redir_token: str) -> bool:
    redir_tokens = {"<", ">", "<<", ">>"}
    return redir_token in redir_tokens


def get_redir_type(redir_token: str) -> RedirType:
    match redir_token:
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


def find_cmd_path(cmd_name: str) -> str | None:
    path_env = os.getenv("PATH", None)
    if not path_env:
        return None
    for dir_path in path_env.split(":"):
        full_path = os.path.join(dir_path, cmd_name)
        if os.path.isfile(full_path) and os.access(full_path, os.X_OK):
            return full_path
    return None


def expand_dollar_vars(text: str):
    pattern = re.compile(r"\$([A-Za-z0-9_]+)")
    result = text
    for match in pattern.finditer(text):
        var_name = match.group(1)
        var_value = config.ENV.get(var_name, "")
        result = result.replace(match.group(0), var_value)
    return result


def expand_env_vars(args: list[str]) -> None:
    for i, token in enumerate(args):
        if token.startswith("'") and token.endswith("'"):
            args[i] = token[1:-1]
            continue
        elif token.startswith('"') and token.endswith('"'):
            args[i] = token[1:-1]
        if "$?" in args[i]:
            args[i] = args[i].replace("$?", str(config.LAST_EXIT))
        if "$" in args[i]:
            args[i] = expand_dollar_vars(args[i])


def is_state_changing_builtin(cmd_name: str) -> bool:
    builtins = {"cd", "export", "unset", "exit"}
    return cmd_name in builtins


def is_non_state_changing_builtin(cmd_name: str) -> bool:
    builtins = {"echo", "pwd", "env"}
    return cmd_name in builtins
