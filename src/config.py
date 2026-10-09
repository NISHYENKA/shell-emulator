"""Параметры запуска эмулятора."""

import argparse


def parse_arguments(argv=None):
    """Разбирает необязательные --vfs и --script."""
    parser = argparse.ArgumentParser(description="Shell emulator, variant 12")
    parser.add_argument("--vfs", help="source directory for the VFS")
    parser.add_argument("--script", help="UTF-8 startup script")
    return parser.parse_args(argv)
