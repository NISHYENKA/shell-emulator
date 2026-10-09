"""Проверки cp/mkdir и неизменности файловой системы хоста."""

from pathlib import Path
import unittest

from src.shell import CommandStatus, Shell
from tests.test_shell import execute
from tests.test_vfs import loaded_vfs


def host_snapshot():
    """Сохраняет имена и байты исходных файлов для проверки изоляции."""
    root = Path("vfs/several")
    return {str(path.relative_to(root)): path.read_bytes()
            for path in root.rglob("*") if path.is_file()}


class TestMutations(unittest.TestCase):
    """Проверяет все поддерживаемые режимы изменяющих команд."""

    def test_mkdir(self):
        """mkdir создаёт один каталог; -p — недостающие родители."""
        shell = Shell(vfs=loaded_vfs())
        for command in ("mkdir new", "mkdir -p new/a/b", "mkdir -p new/a/b"):
            self.assertEqual(execute(shell, command)[0], CommandStatus.success)
        self.assertIsNone(shell.vfs.nodes["/new/a/b"])
        execute(shell, "cd new")
        self.assertEqual(execute(shell, "mkdir relative")[0],
                         CommandStatus.success)
        self.assertIn("/new/relative", shell.vfs.nodes)

    def test_copy_file_and_overwrite(self):
        """cp создаёт файл, копирует в каталог и перезаписывает файл."""
        shell = Shell(vfs=loaded_vfs())
        for command in ("cp home/hello.txt copy.txt", "cp home/hello.txt tmp",
                        "cp home/note.txt copy.txt"):
            self.assertEqual(execute(shell, command)[0], CommandStatus.success)
        self.assertEqual(shell.vfs.nodes["/copy.txt"],
                         shell.vfs.nodes["/home/note.txt"])
        self.assertEqual(shell.vfs.nodes["/tmp/hello.txt"],
                         shell.vfs.nodes["/home/hello.txt"])

    def test_recursive_copy(self):
        """Рекурсивная копия содержит отдельное полное поддерево."""
        shell = Shell(vfs=loaded_vfs())
        execute(shell, "mkdir -p home/a/b")
        self.assertEqual(execute(shell, "cp -r home copy")[0],
                         CommandStatus.success)
        self.assertIn("/copy/a/b", shell.vfs.nodes)
        self.assertEqual(shell.vfs.nodes["/copy/hello.txt"],
                         shell.vfs.nodes["/home/hello.txt"])
        shell.vfs.nodes["/copy/hello.txt"] = b"different"
        self.assertNotEqual(shell.vfs.nodes["/copy/hello.txt"],
                            shell.vfs.nodes["/home/hello.txt"])

    def test_copy_into_directory(self):
        """cp -r помещает источник в существующий каталог."""
        shell = Shell(vfs=loaded_vfs())
        self.assertEqual(execute(shell, "cp -r home tmp")[0],
                         CommandStatus.success)
        self.assertIn("/tmp/home/hello.txt", shell.vfs.nodes)

    def test_errors_do_not_change_tree(self):
        """Конфликты cp/mkdir не повреждают существующее дерево."""
        commands = ("cp", "cp missing copy", "cp home copy",
                    "cp -r home home/inside",
                    "cp home/hello.txt home/hello.txt",
                    "cp -r home home/hello.txt", "cp home/hello.txt missing/",
                    "cp --bad a b", "mkdir", "mkdir --bad x", "mkdir home",
                    "mkdir missing/a", "mkdir home/hello.txt/a",
                    "mkdir -p home/hello.txt", "cp home/hello.txt home")
        for command in commands:
            shell = Shell(vfs=loaded_vfs())
            before = dict(shell.vfs.nodes)
            with self.subTest(command=command):
                self.assertEqual(execute(shell, command)[0],
                                 CommandStatus.error)
                self.assertEqual(shell.vfs.nodes, before)

    def test_host_unchanged_and_hash_updates(self):
        """Исходный каталог не меняется, хеш памяти отражает изменения."""
        before = host_snapshot()
        shell = Shell(vfs=loaded_vfs())
        original_hash = shell.vfs.fingerprint()
        execute(shell, "mkdir created")
        execute(shell, "cp home/hello.txt created/copy")
        self.assertEqual(host_snapshot(), before)
        self.assertFalse(Path("vfs/several/created").exists())
        self.assertNotEqual(shell.vfs.fingerprint(), original_hash)
        self.assertEqual(loaded_vfs().fingerprint(), original_hash)
