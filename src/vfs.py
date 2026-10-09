"""Виртуальное дерево и пути, полностью независимые от диска."""

import hashlib

from src.errors import ShellError
from src.vfs_loader import load_snapshot


class VirtualFileSystem:
    """Плоское отображение абсолютных путей в каталоги или байты файлов."""

    def __init__(self):
        """Создаёт пустую файловую систему по умолчанию."""
        self.name = "default"
        self.nodes = {"/": None}
        self.cwd = "/"

    def load(self, source):
        """Заменяет состояние только после успешной полной загрузки."""
        name, nodes = load_snapshot(source)
        self.name, self.nodes, self.cwd = name, nodes, "/"

    def resolve(self, path):
        """Находит существующий путь, проверяя каждый компонент."""
        current = "/" if path.startswith("/") else self.cwd
        for part in path.split("/"):
            if not part:
                continue
            self.require_directory(current)
            if part == ".":
                continue
            if part == "..":
                current = current.rpartition("/")[0] or "/"
            else:
                current = current.rstrip("/") + "/" + part
                if current not in self.nodes:
                    raise ShellError(f"path not found: {path}")
        if path.endswith("/"):
            self.require_directory(current)
        return current

    def require_directory(self, path):
        """Отвергает путь к файлу вместо каталога."""
        if path not in self.nodes or self.nodes[path] is not None:
            raise ShellError(f"not a directory: {path}")

    def fingerprint(self):
        """Хеширует сортированные пути, типы и точные байты с длинами."""
        digest = hashlib.sha256()
        for path, data in sorted(self.nodes.items()):
            kind = b"directory" if data is None else b"file"
            for field in (kind, path.encode("utf-8"), data or b""):
                digest.update(len(field).to_bytes(8, "big"))
                digest.update(field)
        return digest.hexdigest()
