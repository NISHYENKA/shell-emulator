"""Чтение каталога хоста в независимый снимок памяти."""

from pathlib import Path

from src.errors import ShellError


def is_link(path):
    """Обнаруживает символические ссылки и Windows junction."""
    return path.is_symlink() or path.is_junction()


def read_directory(path, virtual, nodes):
    """Рекурсивно считывает обычные файлы и каталоги без записи на диск."""
    for child in sorted(path.iterdir()):
        target = virtual.rstrip("/") + "/" + child.name
        if is_link(child):
            raise ShellError(f"links are not supported: {child}")
        if child.is_dir():
            nodes[target] = None
            read_directory(child, target, nodes)
        elif child.is_file():
            nodes[target] = child.read_bytes()
        else:
            raise ShellError(f"unsupported file type: {child}")


def load_snapshot(source):
    """Возвращает имя и дерево источника, сообщая об ошибках чтения."""
    path = Path(source)
    try:
        if is_link(path) or not path.is_dir():
            raise ShellError("VFS source must be an existing directory")
        nodes = {"/": None}
        read_directory(path, "/", nodes)
        return path.resolve().name or "root", nodes
    except (OSError, RecursionError) as error:
        raise ShellError(f"cannot load VFS: {error}") from error
