"""Проверки параметров и стартовых скриптов."""

import contextlib
import io
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from src.config import parse_arguments
from src.shell import CommandStatus, Shell
from src.startup import run_startup


def run_script(content):
    """Запускает временный UTF-8 скрипт и возвращает вывод."""
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "script with spaces.txt"
        path.write_text(content, encoding="utf-8")
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            status = run_startup(path, Shell())
        return status, output.getvalue()


class TestStartup(unittest.TestCase):
    """Проверяет штатные и ошибочные пути startup."""

    def test_parameters(self):
        """Пути с пробелами и значения по умолчанию сохраняются."""
        config = parse_arguments(["--vfs", "my dir", "--script", "my file"])
        self.assertEqual(config.vfs, "my dir")
        self.assertEqual(config.script, "my file")
        self.assertIsNone(parse_arguments([]).vfs)

    def test_success(self):
        """Скрипт показывает команды и заканчивается успешно."""
        status, output = run_script("\nls\ncd .\n")
        self.assertEqual(status, CommandStatus.success)
        self.assertIn("default:~$ ls", output)
        self.assertIn("default:~$ cd .", output)

    def test_stop_on_error(self):
        """После первой ошибки ничего больше не исполняется."""
        status, output = run_script("\n\nbad\nnever_run\n")
        self.assertEqual(status, CommandStatus.error)
        self.assertIn("line 3", output)
        self.assertNotIn("never_run", output)

    def test_invalid_arguments(self):
        """Неверные аргументы тоже прерывают startup."""
        status, output = run_script("cd a b\nnever_run\n")
        self.assertEqual(status, CommandStatus.error)
        self.assertNotIn("never_run", output)

    def test_bom_and_exit(self):
        """BOM поддерживается; exit прекращает чтение скрипта."""
        status, output = run_script("\ufeffexit\nnever_run\n")
        self.assertEqual(status, CommandStatus.exit)
        self.assertNotIn("never_run", output)

    def test_read_error(self):
        """Отсутствие файла и неверный UTF-8 дают контролируемую ошибку."""
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "missing.txt"
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(run_startup(path, Shell()),
                                 CommandStatus.error)
                path.write_bytes(b"\xff")
                self.assertEqual(run_startup(path, Shell()),
                                 CommandStatus.error)

    def test_cli_error(self):
        """Ошибка startup даёт код 1 и не запускает REPL."""
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bad.txt"
            path.write_text("bad\n", encoding="utf-8")
            result = subprocess.run(
                [sys.executable, "-m", "src.main", "--script", str(path)],
                input="never_run\n", text=True, capture_output=True, timeout=10,
            )
        self.assertEqual(result.returncode, 1)
        self.assertNotIn("never_run", result.stdout)
        self.assertIn("Script:", result.stdout)

    def test_invalid_options(self):
        """Argparse отвергает неизвестные опции и отсутствующие значения."""
        for args in (["--unknown"], ["--script"], ["--vfs"]):
            result = subprocess.run(
                [sys.executable, "-m", "src.main", *args], input="",
                text=True, capture_output=True, timeout=10,
            )
            self.assertEqual(result.returncode, 2)
