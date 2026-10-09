"""Точка входа консольного эмулятора."""

from src.parser import parse_command
from src.shell import CommandStatus, Shell


def run_interactive(shell):
    """Выполняет REPL до exit, EOF или Ctrl+C."""
    while True:
        try:
            line = input(shell.prompt())
        except (EOFError, KeyboardInterrupt):
            print()
            return
        if shell.execute(parse_command(line)) == CommandStatus.exit:
            return


def main():
    """Запускает эмулятор и возвращает код завершения процесса."""
    run_interactive(Shell())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
