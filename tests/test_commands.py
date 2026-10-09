"""Проверки ls, cd, date, pwd и cal."""

import calendar
from datetime import datetime, timezone
import unittest
from unittest.mock import patch

from src.shell import CommandStatus, Shell
from tests.test_shell import execute
from tests.test_vfs import loaded_vfs


class TestCommands(unittest.TestCase):
    """Проверяет реальные команды и все поддерживаемые режимы."""

    def test_unknown_option_matching_directory(self):
        """Неизвестная опция не становится именем каталога."""
        shell = Shell(vfs=loaded_vfs())
        shell.vfs.nodes["/--bad"] = None
        for command in ("ls --bad", "cd --bad"):
            self.assertEqual(execute(shell, command)[0], CommandStatus.error)
        self.assertEqual(execute(shell, "cd ./--bad")[0],
                         CommandStatus.success)

    def test_navigation(self):
        """ls/cd/pwd работают внутри VFS и поддерживают пути."""
        shell = Shell(vfs=loaded_vfs())
        self.assertEqual(execute(shell, "ls")[1], "home\ntmp\n")
        self.assertEqual(execute(shell, "cd home")[0], CommandStatus.success)
        self.assertEqual(execute(shell, "pwd")[1], "/home\n")
        self.assertEqual(execute(shell, "ls hello.txt")[1], "hello.txt\n")
        execute(shell, "cd ..")
        self.assertEqual(execute(shell, "pwd")[1], "/\n")
        execute(shell, "cd /home")
        execute(shell, "cd")
        self.assertEqual(execute(shell, "pwd")[1], "/\n")

    def test_path_errors_preserve_cwd(self):
        """Ошибки перехода не меняют текущий каталог."""
        shell = Shell(vfs=loaded_vfs())
        for command in ("cd missing", "cd /home/hello.txt", "ls missing"):
            self.assertEqual(execute(shell, command)[0], CommandStatus.error)
            self.assertEqual(shell.vfs.cwd, "/")

    def test_date(self):
        """date использует локальное время, date -u — UTC."""
        local = datetime(2026, 10, 9, 12, 30)
        utc = datetime(2026, 10, 9, 9, 30, tzinfo=timezone.utc)
        with patch("src.commands.datetime") as clock:
            clock.now.return_value = local
            self.assertEqual(execute(Shell(), "date")[1],
                             local.strftime("%a %b %d %H:%M:%S %Y") + "\n")
            clock.now.assert_called_with()
            clock.now.return_value = utc
            self.assertIn("09:30:00", execute(Shell(), "date -u")[1])
            clock.now.assert_called_with(timezone.utc)

    def test_cal(self):
        """Календарь месяца и года соответствует стандартному модулю."""
        formatter = calendar.TextCalendar(firstweekday=calendar.MONDAY)
        self.assertEqual(execute(Shell(), "cal 2 2024")[1],
                         formatter.formatmonth(2024, 2))
        self.assertEqual(execute(Shell(), "cal 2026")[1],
                         formatter.formatyear(2026))
        with patch("src.commands.datetime") as clock:
            clock.now.return_value = datetime(2026, 10, 9)
            self.assertEqual(execute(Shell(), "cal")[1],
                             formatter.formatmonth(2026, 10))

    def test_bad_arguments(self):
        """Ошибки формата и диапазона не приводят к traceback."""
        commands = ("date bad", "date -u extra", "pwd extra", "cal 0",
                    "cal 10000", "cal 13 2026", "cal 0 2026", "cal x",
                    "cal 1 2 3", "vfs-info extra")
        for command in commands:
            with self.subTest(command=command):
                self.assertEqual(execute(Shell(), command)[0],
                                 CommandStatus.error)
