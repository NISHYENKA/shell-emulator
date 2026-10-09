"""Выполнение стартового скрипта с остановкой на первой ошибке."""

from src.parser import parse_command
from src.shell import CommandStatus


def run_startup(path, shell):
    """Печатает ввод и вывод, возвращает статус последней команды."""
    try:
        with open(path, encoding="utf-8-sig") as script:
            for number, line in enumerate(script, start=1):
                command = line.strip()
                if not command:
                    continue
                print(f"{shell.prompt()}{command}")
                status = shell.execute(parse_command(command))
                if status == CommandStatus.error:
                    print(f"error: startup line {number}")
                if status != CommandStatus.success:
                    return status
    except (OSError, UnicodeError) as error:
        print(f"error: cannot read startup: {error}")
        return CommandStatus.error
    return CommandStatus.success
