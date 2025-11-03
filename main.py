from parse import parsePipeline
from execute import execute
import config
import readline
import re
import sys
import signal


def shell_loop() -> None:
    _ = signal.signal(signal.SIGQUIT, signal.SIG_IGN)
    while True:
        try:
            line = input("sh.py> ")
            if not line or line.isspace():
                continue
        except EOFError:
            sys.exit(config.LAST_EXIT)
        except KeyboardInterrupt:
            print()
            continue
        tokens = re.findall(r'[^"\s\']\S*|"[^"]*"|\'[^\']*\'', line)
        pipeline = parsePipeline(tokens)
        if pipeline:
            execute(pipeline)


def main():
    shell_loop()


if __name__ == "__main__":
    main()
