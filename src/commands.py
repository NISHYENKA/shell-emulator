"""Основные команды варианта 12."""

import calendar
from datetime import datetime, timezone

from src.errors import ShellError, validate_count


min_year = 1
max_year = 9999
min_month = 1
max_month = 12


def list_command(arguments, vfs):
    """Выводит имена каталога либо имя указанного файла."""
    validate_count(arguments, (0, 1))
    reject_options(arguments)
    path = vfs.resolve(arguments[0] if arguments else ".")
    if vfs.nodes[path] is not None:
        print(path.rpartition("/")[2])
        return
    prefix = path.rstrip("/") + "/"
    for name in sorted(vfs.nodes):
        if name.startswith(prefix) and name != path:
            relative = name[len(prefix):]
            if "/" not in relative:
                print(relative)


def change_directory(arguments, vfs):
    """Меняет рабочий каталог; отсутствие аргумента означает корень."""
    validate_count(arguments, (0, 1))
    reject_options(arguments)
    target = vfs.resolve(arguments[0] if arguments else "/")
    vfs.require_directory(target)
    vfs.cwd = target


def reject_options(arguments):
    """Отвергает опции; имена с дефисом доступны через ./имя."""
    if arguments and arguments[0].startswith("-"):
        raise ShellError("unsupported option")


def print_directory(arguments, vfs):
    """Печатает текущий абсолютный путь внутри VFS."""
    validate_count(arguments, (0,))
    print(vfs.cwd)


def date_command(arguments, vfs):
    """Печатает локальную дату/время или UTC для флага -u."""
    if arguments not in ([], ["-u"]):
        raise ShellError("usage: date [-u]")
    now = datetime.now(timezone.utc) if arguments else datetime.now()
    print(now.strftime("%a %b %d %H:%M:%S %Y"))


def calendar_command(arguments, vfs):
    """Печатает текущий месяц, заданный год или заданный месяц года."""
    validate_count(arguments, (0, 1, 2))
    try:
        values = [int(value) for value in arguments]
    except ValueError as error:
        raise ShellError("calendar arguments must be integers") from error
    now = datetime.now()
    year = values[-1] if values else now.year
    if not min_year <= year <= max_year:
        raise ShellError("year must be between 1 and 9999")
    formatter = calendar.TextCalendar(firstweekday=calendar.MONDAY)
    if len(values) in (1,):
        print(formatter.formatyear(year), end="")
        return
    month = values[0] if values else now.month
    if not min_month <= month <= max_month:
        raise ShellError("month must be between 1 and 12")
    print(formatter.formatmonth(year, month), end="")


def run_command(command, arguments, vfs):
    """Выбирает основную команду по имени."""
    handlers = {"ls": list_command, "cd": change_directory,
                "pwd": print_directory, "date": date_command,
                "cal": calendar_command}
    if command not in handlers:
        raise ShellError(f"unknown command: {command}")
    handlers[command](arguments, vfs)
