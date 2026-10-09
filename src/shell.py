"""Приглашение и выполнение команд текущего этапа."""

from enum import Enum

from src.errors import ShellError, validate_count


class CommandStatus(Enum):
    """Результат команды для REPL и стартового скрипта."""

    success = "success"
    error = "error"
    exit = "exit"


class Shell:
    """Состояние сеанса и диспетчер команд."""

    def __init__(self, vfs_name="default"):
        """Создаёт сеанс с именем виртуальной файловой системы."""
        self.vfs_name = vfs_name

    def prompt(self):
        """Возвращает приглашение с именем VFS."""
        return f"{self.vfs_name}:~$ "

    def execute(self, tokens):
        """Выполняет команду, преобразуя ожидаемые ошибки в статус."""
        if not tokens:
            return CommandStatus.success
        command, arguments = tokens[0], tokens[1:]
        try:
            if command == "exit":
                validate_count(arguments, (0,))
                return CommandStatus.exit
            self._dispatch(command, arguments)
            return CommandStatus.success
        except ShellError as error:
            print(f"error: {error}")
            return CommandStatus.error

    def _dispatch(self, command, arguments):
        """Вызывает доступную команду или сообщает о неизвестной."""
        if command not in ("ls", "cd"):
            raise ShellError(f"unknown command: {command}")
        validate_count(arguments, (0, 1))
        if arguments and arguments[0].startswith("-"):
            raise ShellError("unsupported option")
        print(command, *arguments)
