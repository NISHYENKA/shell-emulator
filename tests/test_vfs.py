"""Проверки снимка каталога, путей и SHA-256."""

import contextlib
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from src.errors import ShellError
from src.shell import CommandStatus, Shell
from src.vfs import VirtualFileSystem


def loaded_vfs():
    """Загружает независимую тестовую файловую систему."""
    vfs = VirtualFileSystem()
    vfs.load("vfs/several")
    return vfs


class TestVfs(unittest.TestCase):
    """Проверяет успешную загрузку и отказ без изменения состояния."""

    def test_default(self):
        """Без источника существует пустой корень с именем default."""
        vfs = VirtualFileSystem()
        self.assertEqual(vfs.name, "default")
        self.assertEqual(vfs.nodes, {"/": None})
        self.assertEqual(len(vfs.fingerprint()), 64)

    def test_fixtures(self):
        """Все три требуемых варианта структуры доступны."""
        for name in ("minimal", "several", "nested"):
            vfs = VirtualFileSystem()
            vfs.load(f"vfs/{name}")
            self.assertEqual(vfs.name, name)
        self.assertIn("/a/b/c/report.txt", vfs.nodes)

    def test_binary_memory(self):
        """Файлы остаются в памяти после удаления источника."""
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)
            (path / "binary").write_bytes(bytes(range(256)))
            (path / "empty").mkdir()
            vfs = VirtualFileSystem()
            vfs.load(path)
        self.assertEqual(vfs.nodes["/binary"], bytes(range(256)))
        self.assertIsNone(vfs.nodes["/empty"])
        self.assertEqual(len(vfs.fingerprint()), 64)

    def test_invalid_sources(self):
        """Несуществующий путь и обычный файл вместо каталога запрещены."""
        for path in ("vfs/missing", "README.md"):
            with self.subTest(path=path), self.assertRaises(ShellError):
                VirtualFileSystem().load(path)

    def test_failed_reload(self):
        """Ошибка загрузки не изменяет прежнее дерево и имя."""
        vfs = loaded_vfs()
        before = (vfs.name, vfs.fingerprint())
        with self.assertRaises(ShellError):
            vfs.load("vfs/missing")
        self.assertEqual((vfs.name, vfs.fingerprint()), before)

    def test_unreadable_file(self):
        """Ошибка чтения преобразуется в понятную ошибку загрузки."""
        with patch.object(Path, "read_bytes", side_effect=PermissionError):
            with self.assertRaises(ShellError):
                loaded_vfs()

    def test_links_rejected(self):
        """Обнаруженная ссылка не обходится загрузчиком."""
        with patch("src.vfs_loader.is_link", return_value=True):
            with self.assertRaises(ShellError):
                loaded_vfs()

    def test_hash_order_and_location(self):
        """Имя исходного каталога и порядок создания не влияют на хеш."""
        with tempfile.TemporaryDirectory() as directory:
            first = Path(directory) / "one"
            second = Path(directory) / "two"
            first.mkdir()
            second.mkdir()
            for root, names in ((first, ("a", "b")), (second, ("b", "a"))):
                for name in names:
                    (root / name).write_bytes(name.encode())
            left, right = VirtualFileSystem(), VirtualFileSystem()
            left.load(first)
            right.load(second)
            self.assertEqual(left.fingerprint(), right.fingerprint())
            right.nodes["/a"] = b"changed"
            self.assertNotEqual(left.fingerprint(), right.fingerprint())

    def test_hash_includes_empty_directories_and_names(self):
        """Даже пустые каталоги и переименование меняют хеш."""
        vfs = VirtualFileSystem()
        original = vfs.fingerprint()
        vfs.nodes["/empty"] = None
        self.assertNotEqual(vfs.fingerprint(), original)
        before = vfs.fingerprint()
        vfs.nodes["/other"] = vfs.nodes.pop("/empty")
        self.assertNotEqual(vfs.fingerprint(), before)

    def test_paths(self):
        """Разрешение путей не пропускает файлы в середине пути."""
        vfs = loaded_vfs()
        self.assertEqual(vfs.resolve("/home/../home/./hello.txt"),
                         "/home/hello.txt")
        self.assertEqual(vfs.resolve("../../../"), "/")
        for path in ("/missing/..", "/home/hello.txt/..", "/home/hello.txt/"):
            with self.subTest(path=path), self.assertRaises(ShellError):
                vfs.resolve(path)

    def test_vfs_info(self):
        """Служебная команда выводит имя VFS и её хеш."""
        vfs = loaded_vfs()
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            status = Shell(vfs=vfs).execute(["vfs-info"])
        self.assertEqual(status, CommandStatus.success)
        self.assertIn(vfs.name, output.getvalue())
        self.assertIn(vfs.fingerprint(), output.getvalue())
        self.assertEqual(Shell(vfs=vfs).prompt(), "several:~$ ")
