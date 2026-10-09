"""Точка входа консольного эмулятора."""

from src.config import parse_arguments
from src.errors import ShellError
from src.parser import parse_command
from src.shell import CommandStatus, Shell
from src.startup import run_startup
from src.vfs import VirtualFileSystem


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
    config = parse_arguments()
    print(f"VFS: {config.vfs}")
    print(f"Script: {config.script}")
    vfs = VirtualFileSystem()
    try:
        if config.vfs:
            vfs.load(config.vfs)
    except ShellError as error:
        print(f"error: {error}")
        return 1
    shell = Shell(vfs=vfs)
    if config.script:
        status = run_startup(config.script, shell)
        if status == CommandStatus.error:
            return 1
        if status == CommandStatus.exit:
            return 0
    run_interactive(shell)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
