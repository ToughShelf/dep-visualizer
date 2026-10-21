"""Разбор параметров командной строки визуализатора."""

import argparse
import re
from argparse import Namespace
from pathlib import Path
from urllib.parse import urlparse

UNSET = "(не задан)"
TRUE_LABEL = "вкл"
FALSE_LABEL = "выкл"
TRUE_VALUES = frozenset({"on", "true", "yes", "1", "да", "вкл"})
FALSE_VALUES = frozenset({"off", "false", "no", "0", "нет", "выкл"})
URL_SCHEMES = frozenset({"http", "https"})
PACKAGE_PATTERN = re.compile(
    r"^[@A-Za-z0-9][A-Za-z0-9._+\-]*(/[A-Za-z0-9._+\-]+)?$",
)
VERSION_PATTERN = re.compile(
    r"^\d+(?:\.\d+)*(?:[._\-]?[A-Za-z0-9]+)*$",
)


class ConfigError(ValueError):
    """Ошибка значения параметра запуска."""


def parse_test_mode(value: str) -> bool:
    """Преобразует строку режима тестового репозитория в bool."""
    normalized = value.strip().lower()
    if normalized in TRUE_VALUES:
        return True
    if normalized in FALSE_VALUES:
        return False
    message = f"неверное значение режима: {value}"
    raise argparse.ArgumentTypeError(message)


def parse_args(argv: list[str] | None = None) -> Namespace:
    """Читает имя пакета, репозиторий, режим теста и версию."""
    parser = argparse.ArgumentParser(
        description="Визуализатор графа зависимостей пакетов",
    )
    parser.add_argument(
        "--package",
        dest="package",
        default=None,
        help="Имя анализируемого пакета",
    )
    parser.add_argument(
        "--repo",
        dest="repo",
        default=None,
        help="URL репозитория или путь к файлу тестового репозитория",
    )
    parser.add_argument(
        "--test-mode",
        dest="test_mode",
        default=None,
        type=parse_test_mode,
        help="Режим работы с тестовым репозиторием (on/off)",
    )
    parser.add_argument(
        "--package-version",
        dest="package_version",
        default=None,
        help="Версия пакета",
    )
    return parser.parse_args(argv)


def format_param(value: str | None) -> str:
    """Возвращает значение параметра или пометку, что он не задан."""
    if value is None:
        return UNSET
    return value


def format_test_mode(value: bool | None) -> str:
    """Возвращает текстовое представление режима тестового репозитория."""
    if value is None:
        return UNSET
    if value:
        return TRUE_LABEL
    return FALSE_LABEL


def print_config(args: Namespace) -> None:
    """Печатает отладочный вывод всех параметров запуска."""
    test_mode = format_test_mode(args.test_mode)
    print("Параметры запуска:")
    print(f"  Имя пакета: {format_param(args.package)}")
    print(f"  Репозиторий: {format_param(args.repo)}")
    print(f"  Режим тестового репозитория: {test_mode}")
    print(f"  Версия пакета: {format_param(args.package_version)}")


def validate_package(name: str | None) -> None:
    """Проверяет, что имя пакета задано и корректно."""
    if name is None:
        raise ConfigError("имя пакета не задано")
    stripped = name.strip()
    if not stripped:
        raise ConfigError("имя пакета не задано")
    if PACKAGE_PATTERN.fullmatch(stripped) is None:
        raise ConfigError(f"неверное имя пакета: {name}")


def validate_version(version: str | None) -> None:
    """Проверяет версию пакета, если она задана."""
    if version is None:
        return
    stripped = version.strip()
    if not stripped:
        raise ConfigError("версия пакета не задана")
    if VERSION_PATTERN.fullmatch(stripped) is None:
        raise ConfigError(f"неверный формат версии: {version}")


def is_repo_url(value: str) -> bool:
    """Проверяет, что строка выглядит как http(s) URL."""
    parsed = urlparse(value)
    if parsed.scheme not in URL_SCHEMES:
        return False
    return bool(parsed.netloc)


def validate_repo(repo: str | None, test_mode: bool | None) -> None:
    """Проверяет URL репозитория или путь к тестовому файлу."""
    if repo is None or not repo.strip():
        raise ConfigError("репозиторий не задан")
    stripped = repo.strip()
    if test_mode:
        path = Path(stripped)
        if not path.is_file():
            raise ConfigError(
                f"файл тестового репозитория не найден: {repo}",
            )
        return
    if not is_repo_url(stripped):
        raise ConfigError(
            f"ожидается URL репозитория, получен путь: {repo}",
        )


def validate_config(args: Namespace) -> None:
    """Проверяет все настраиваемые параметры запуска."""
    validate_package(args.package)
    validate_version(args.package_version)
    validate_repo(args.repo, args.test_mode)
