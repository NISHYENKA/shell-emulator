"""Проверки REPL и команд варианта 12."""

import contextlib
import io
import subprocess
import sys
import unittest

from src.parser import parse_command
from src.shell import CommandStatus, Shell


def execute(shell, command):
    """Возвращает статус и перехваченный вывод команды."""
    output = io.StringIO()
    with contextlib.redirect_stdout(output):
        status = shell.execute(parse_command(command))
    return status, output.getvalue()


class TestShell(unittest.TestCase):
    """Проверяет интерфейс и сообщения об ошибках."""

    def test_parser(self):
        """Парсер делит по пробельным символам без обработки кавычек."""
        self.assertEqual(parse_command("  cd\t home  "), ["cd", "home"])
        self.assertEqual(parse_command(" \t"), [])
        self.assertEqual(parse_command('cd "two words"'),
                         ["cd", '"two', 'words"'])

    def test_prompt(self):
        """Имя VFS находится в приглашении."""
        self.assertEqual(Shell().prompt(), "default:~$ ")
        self.assertEqual(Shell("my-vfs").prompt(), "my-vfs:~$ ")

    def test_empty_and_exit(self):
        """Пустой ввод успешен, exit завершает сеанс."""
        self.assertEqual(execute(Shell(), "")[0], CommandStatus.success)
        self.assertEqual(execute(Shell(), "exit")[0], CommandStatus.exit)

    def test_unknown_command(self):
        """Неизвестная команда сообщает об ошибке."""
        status, output = execute(Shell(), "unknown")
        self.assertEqual(status, CommandStatus.error)
        self.assertIn("error:", output)

    def test_invalid_arguments(self):
        """Неверное число аргументов и опции не игнорируются."""
        for command in ("exit extra", "cd a b", "ls a b", "ls --bad"):
            with self.subTest(command=command):
                status, output = execute(Shell(), command)
                self.assertEqual(status, CommandStatus.error)
                self.assertIn("error:", output)

    def test_stubs(self):
        """Заглушки печатают команду и аргументы."""
        self.assertEqual(execute(Shell(), "ls docs"),
                         (CommandStatus.success, "ls docs\n"))
        self.assertEqual(execute(Shell(), "cd docs"),
                         (CommandStatus.success, "cd docs\n"))

    def test_repl(self):
        """REPL продолжает работу после ошибки и завершает по exit."""
        result = subprocess.run(
            [sys.executable, "-m", "src.main"], input="bad\nls\nexit\n",
            capture_output=True, text=True, timeout=10,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("default:~$", result.stdout)
        self.assertIn("error:", result.stdout)

    def test_eof(self):
        """Закрытый ввод не вызывает traceback."""
        result = subprocess.run(
            [sys.executable, "-m", "src.main"], input="",
            capture_output=True, text=True, timeout=10,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
