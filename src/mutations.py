"""Создание каталогов и копирование только в памяти VFS."""

from src.errors import ShellError, validate_count


def target_path(vfs, path):
    """Разрешает родителя нового пути, не создавая объекты."""
    if not path:
        raise ShellError("empty path")
    stripped = path.rstrip("/")
    parent, separator, name = stripped.rpartition("/")
    if name in ("", ".", ".."):
        return vfs.resolve(path)
    base = parent or ("/" if separator else ".")
    directory = vfs.resolve(base)
    vfs.require_directory(directory)
    return directory.rstrip("/") + "/" + name


def create_parents(vfs, path):
    """Создаёт отсутствующие компоненты пути mkdir -p."""
    current = "/" if path.startswith("/") else vfs.cwd
    for part in path.split("/"):
        if not part:
            continue
        vfs.require_directory(current)
        if part == ".":
            continue
        if part == "..":
            current = current.rpartition("/")[0] or "/"
        else:
            current = current.rstrip("/") + "/" + part
            if current not in vfs.nodes:
                vfs.nodes[current] = None
            vfs.require_directory(current)


def mkdir_command(arguments, vfs):
    """Создаёт один каталог или родителей при -p."""
    parents = bool(arguments and arguments[0] == "-p")
    paths = arguments[1:] if parents else arguments
    validate_count(paths, (1,))
    path = paths[0]
    if path.startswith("-"):
        raise ShellError("usage: mkdir [-p] path")
    if parents:
        create_parents(vfs, path)
        return
    target = target_path(vfs, path)
    if target in vfs.nodes:
        raise ShellError(f"path already exists: {path}")
    vfs.nodes[target] = None


def copy_target(vfs, source, destination):
    """Определяет целевое имя с учётом каталога назначения."""
    target = target_path(vfs, destination)
    if target in vfs.nodes and vfs.nodes[target] is None:
        target = target.rstrip("/") + "/" + source.rpartition("/")[2]
    elif destination.endswith("/"):
        raise ShellError("destination directory does not exist")
    if target == source or target.startswith(source.rstrip("/") + "/"):
        raise ShellError("cannot copy onto itself or into its descendant")
    return target


def copy_nodes(vfs, source, target, recursive):
    """Проверяет типы и атомарно вставляет независимую копию поддерева."""
    data = vfs.nodes[source]
    if data is None:
        if not recursive:
            raise ShellError("copying a directory requires -r")
        if target in vfs.nodes:
            raise ShellError("directory copy destination already exists")
        prefix = source.rstrip("/") + "/"
        updates = {target + path[len(source):]: value
                   for path, value in vfs.nodes.items()
                   if path == source or path.startswith(prefix)}
    else:
        if target in vfs.nodes and vfs.nodes[target] is None:
            raise ShellError("cannot overwrite a directory with a file")
        updates = {target: data}
    vfs.nodes.update(updates)


def copy_command(arguments, vfs):
    """Копирует файл или дерево (-r), не обращаясь к диску."""
    recursive = bool(arguments and arguments[0] == "-r")
    paths = arguments[1:] if recursive else arguments
    validate_count(paths, (2,))
    if any(path.startswith("-") for path in paths):
        raise ShellError("usage: cp [-r] source destination")
    source = vfs.resolve(paths[0])
    target = copy_target(vfs, source, paths[1])
    copy_nodes(vfs, source, target, recursive)
