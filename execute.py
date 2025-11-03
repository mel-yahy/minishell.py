import sys
from defs import AstNode, AstType, CmdNode, RedirNode, RedirType
from utils import expand_env_vars, is_non_state_changing_builtin, is_state_changing_builtin
from sh_builtins import *
import config
import os
import signal


def handle_here_doc(redir: RedirNode) -> int:
    read_end, write_end = os.pipe()
    while True:
        try:
            line = input()
        except EOFError:
            print(
                f"\nwarning: here-document delimited by end-of-file (wanted '{redir.target}')",
                file=sys.stderr,
            )
            break
        if line == redir.target:
            break
        line += "\n"
        _ = os.write(write_end, line.encode())
    os.close(write_end)
    return read_end


def setup_redirs(redir: RedirNode) -> None:
    if redir.type is RedirType.HEREDOC:
        fd = handle_here_doc(redir)
    elif redir.type is RedirType.INPUT:
        fd = os.open(redir.target, os.O_RDONLY)
    elif redir.type is RedirType.OUTPUT:
        fd = os.open(redir.target, os.O_CREAT | os.O_WRONLY | os.O_TRUNC, 0o644)
    elif redir.type is RedirType.APPEND:
        fd = os.open(redir.target, os.O_CREAT | os.O_WRONLY | os.O_APPEND, 0o644)
    else:
        raise ValueError("It will never reach here... Maybe")
    _ = os.dup2(fd, redir.src_fd)
    os.close(fd)


def execute_builtins(cmd_name: str, cmd_args: list[str]) -> None:
    match cmd_name:
        case "echo":
            echo_builtin(cmd_args)
        case "cd":
            cd_builtin(cmd_args)
        case "pwd":
            pwd_builtin()
        case "export":
            export_builtin(cmd_args)
        case "unset":
            unset_builtin(cmd_args)
        case "env":
            env_builtin()
        case "exit":
            exit_builtin(cmd_args)
        case _:
            pass


def execute_cmd(cmd: CmdNode) -> None:
    if cmd.redir:
        setup_redirs(cmd.redir)
    if not cmd.path:
        print(f"{cmd.name}: command was not found", file=sys.stderr)
        sys.exit(127)
    expand_env_vars(cmd.args)
    if is_non_state_changing_builtin(cmd.name):
        execute_builtins(cmd.name, cmd.args)
    else:
        os.execve(cmd.path, cmd.args, config.ENV)


def execute_pipeline(ast: AstNode) -> int:
    read_end, write_end = os.pipe()
    id_1 = os.fork()
    if id_1 == 0:
        _ = signal.signal(signal.SIGQUIT, signal.SIG_DFL)
        _ = signal.signal(signal.SIGINT, signal.SIG_DFL)
        os.close(read_end)
        if ast.left and ast.left.cmd:
            _ = os.dup2(write_end, 1)
            os.close(write_end)
            execute_cmd(ast.left.cmd)
            sys.exit(0)
    id_2 = os.fork()
    if id_2 == 0:
        _ = signal.signal(signal.SIGQUIT, signal.SIG_DFL)
        _ = signal.signal(signal.SIGINT, signal.SIG_DFL)
        os.close(write_end)
        if ast.right:
            _ = os.dup2(read_end, 0)
            os.close(read_end)
            execute(ast.right)
            sys.exit(config.LAST_EXIT)
    os.close(read_end)
    os.close(write_end)
    _ = os.waitpid(id_1, 0)
    _, status = os.waitpid(id_2, 0)
    if os.WIFEXITED(status):
        return os.WEXITSTATUS(status)
    elif os.WIFSIGNALED(status):
        sig_num = os.WTERMSIG(status)
        return 128 + sig_num
    else:
        return 1


def execute(ast: AstNode) -> None:
    original_action = signal.getsignal(signal.SIGINT)
    _ = signal.signal(signal.SIGQUIT, signal.SIG_IGN)
    _ = signal.signal(signal.SIGINT, signal.SIG_IGN)
    if ast.type is AstType.PIPELINE:
        config.LAST_EXIT = execute_pipeline(ast)
    elif ast.type is AstType.CMD and ast.cmd:
        if is_state_changing_builtin(ast.cmd.name):
            execute_builtins(ast.cmd.name, ast.cmd.args)
        else:
            id = os.fork()
            if id == 0:
                _ = signal.signal(signal.SIGQUIT, signal.SIG_DFL)
                _ = signal.signal(signal.SIGINT, signal.SIG_DFL)
                execute_cmd(ast.cmd)
            _, status = os.waitpid(id, 0)
            if os.WIFEXITED(status):
                config.LAST_EXIT = os.WEXITSTATUS(status)
            elif os.WIFSIGNALED(status):
                sig_num = os.WTERMSIG(status)
                config.LAST_EXIT = 128 + sig_num
            else:
                config.LAST_EXIT = 1
    _ = signal.signal(signal.SIGINT, original_action)
