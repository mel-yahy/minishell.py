from parse import parse_pipeline
from execute import execute
import config
import readline
import re
import sys


def shell_loop() -> None:
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
        pipeline = parse_pipeline(tokens)
        if pipeline:
            execute(pipeline)


def main():
    shell_loop()


if __name__ == "__main__":
    main()
