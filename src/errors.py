"""Ошибки эмулятора, предназначенные для вывода пользователю."""


class ShellError(Exception):
    """Ошибка аргументов, команды или виртуальной файловой системы."""


def validate_count(arguments, allowed):
    """Проверяет число аргументов по множеству разрешённых значений."""
    if len(arguments) not in allowed:
        raise ShellError("invalid number of arguments")
