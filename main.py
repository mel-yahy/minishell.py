from parse import parsePipeline
from execute import execute
import readline
import re


def shell_loop() -> None:
    while True:
        try:
            line = input("sh.py> ")
        except EOFError:
            exit(0)
        except KeyboardInterrupt:
            print()
            continue
        tokens = re.findall(r'[^"\s]\S*|".+?"', line)
        pipeline = parsePipeline(tokens)
        if pipeline:
            execute(pipeline)


def main():
    shell_loop()


if __name__ == "__main__":
    main()
