from parse import parsePipeline
from execute import execute
import readline


def shell_loop() -> None:
    while True:
        try:
            command = input("sh.py> ")
        except EOFError:
            exit(0)
        except KeyboardInterrupt:
            print()
            continue
        tokens = command.split()
        pipeline = parsePipeline(tokens)
        if pipeline:
            execute(pipeline)


def main():
    shell_loop()


if __name__ == "__main__":
    main()
