"""Юнит-тесты разбора и проверки параметров запуска."""

import io
import unittest
from argparse import Namespace
from contextlib import redirect_stdout
from pathlib import Path

from src.config import (
    UNSET,
    ConfigError,
    format_param,
    format_test_mode,
    parse_args,
    parse_test_mode,
    print_config,
    validate_config,
    validate_package,
    validate_repo,
    validate_version,
)

REPO_FILE = Path(__file__).resolve().parent.parent / "repo" / "test_repo.json"


def make_args(
    package: str | None = None,
    repo: str | None = None,
    test_mode: bool | None = None,
    package_version: str | None = None,
) -> Namespace:
    """Собирает Namespace с параметрами запуска."""
    return Namespace(
        package=package,
        repo=repo,
        test_mode=test_mode,
        package_version=package_version,
    )


class TestParseArgs(unittest.TestCase):
    """Проверяет чтение опций командной строки."""

    def test_all_parameters(self) -> None:
        """Все четыре параметра читаются из CLI."""
        args = parse_args(
            [
                "--package",
                "flask",
                "--repo",
                "https://pypi.org/simple",
                "--test-mode",
                "off",
                "--package-version",
                "3.0.3",
            ],
        )
        self.assertEqual(args.package, "flask")
        self.assertEqual(args.repo, "https://pypi.org/simple")
        self.assertFalse(args.test_mode)
        self.assertEqual(args.package_version, "3.0.3")

    def test_defaults_are_unset(self) -> None:
        """Без опций параметры остаются незаданными."""
        args = parse_args([])
        self.assertIsNone(args.package)
        self.assertIsNone(args.repo)
        self.assertIsNone(args.test_mode)
        self.assertIsNone(args.package_version)

    def test_test_mode_on(self) -> None:
        """Значение on включает режим тестового репозитория."""
        self.assertTrue(parse_test_mode("on"))
        self.assertTrue(parse_test_mode("ДА"))

    def test_test_mode_off(self) -> None:
        """Значение off выключает режим тестового репозитория."""
        self.assertFalse(parse_test_mode("off"))
        self.assertFalse(parse_test_mode("нет"))

    def test_test_mode_invalid(self) -> None:
        """Неизвестное значение режима вызывает ошибку разбора."""
        with self.assertRaises(Exception) as ctx:
            parse_test_mode("maybe")
        self.assertIn("неверное значение режима", str(ctx.exception))


class TestValidateParameters(unittest.TestCase):
    """Проверяет обработку ошибок для каждого параметра."""

    def test_empty_package(self) -> None:
        """Пустое имя пакета отклоняется."""
        with self.assertRaises(ConfigError) as ctx:
            validate_package("   ")
        self.assertEqual(str(ctx.exception), "имя пакета не задано")

    def test_invalid_package(self) -> None:
        """Имя пакета с пробелом отклоняется."""
        with self.assertRaises(ConfigError) as ctx:
            validate_package("bad name")
        self.assertIn("неверное имя пакета", str(ctx.exception))

    def test_valid_package(self) -> None:
        """Обычное имя пакета принимается."""
        validate_package("flask")
        validate_package("@scope/name")

    def test_empty_version(self) -> None:
        """Пустая версия отклоняется."""
        with self.assertRaises(ConfigError) as ctx:
            validate_version("")
        self.assertEqual(str(ctx.exception), "версия пакета не задана")

    def test_invalid_version(self) -> None:
        """Версия без цифр отклоняется."""
        with self.assertRaises(ConfigError) as ctx:
            validate_version("latest")
        self.assertIn("неверный формат версии", str(ctx.exception))

    def test_valid_version(self) -> None:
        """Семантическая версия принимается."""
        validate_version("3.0.3")
        validate_version("1.0.0-alpha")

    def test_repo_url_required_without_test_mode(self) -> None:
        """Без тестового режима нужен URL, а не путь."""
        with self.assertRaises(ConfigError) as ctx:
            validate_repo("repo/test_repo.json", False)
        self.assertIn("ожидается URL репозитория", str(ctx.exception))

    def test_repo_file_missing_in_test_mode(self) -> None:
        """В тестовом режиме отсутствующий файл вызывает ошибку."""
        with self.assertRaises(ConfigError) as ctx:
            validate_repo("repo/missing.json", True)
        self.assertIn("файл тестового репозитория не найден", str(ctx.exception))

    def test_repo_required_in_test_mode(self) -> None:
        """Тестовый режим без пути к файлу недопустим."""
        with self.assertRaises(ConfigError) as ctx:
            validate_repo(None, True)
        self.assertIn("нужен путь к файлу репозитория", str(ctx.exception))

    def test_valid_url_repo(self) -> None:
        """Корректный URL принимается вне тестового режима."""
        validate_repo("https://pypi.org/simple", False)

    def test_valid_file_repo(self) -> None:
        """Существующий файл принимается в тестовом режиме."""
        validate_repo(str(REPO_FILE), True)

    def test_empty_repo(self) -> None:
        """Пустой репозиторий отклоняется."""
        with self.assertRaises(ConfigError) as ctx:
            validate_repo("  ", False)
        self.assertEqual(str(ctx.exception), "репозиторий не задан")


class TestPrintConfig(unittest.TestCase):
    """Проверяет вывод параметров в формате ключ-значение."""

    def test_print_all_parameters(self) -> None:
        """Печатаются все четыре настраиваемых параметра."""
        args = make_args(
            package="flask",
            repo="https://pypi.org/simple",
            test_mode=False,
            package_version="3.0.3",
        )
        buf = io.StringIO()
        with redirect_stdout(buf):
            print_config(args)
        text = buf.getvalue()
        self.assertIn("Имя пакета: flask", text)
        self.assertIn("Репозиторий: https://pypi.org/simple", text)
        self.assertIn("Режим тестового репозитория: выкл", text)
        self.assertIn("Версия пакета: 3.0.3", text)

    def test_print_unset_parameters(self) -> None:
        """Незаданные параметры помечаются явно."""
        self.assertEqual(format_param(None), UNSET)
        self.assertEqual(format_test_mode(None), UNSET)
        self.assertEqual(format_test_mode(True), "вкл")

    def test_validate_config_ok(self) -> None:
        """Полный корректный набор параметров проходит проверку."""
        args = make_args(
            package="flask",
            repo="https://pypi.org/simple",
            test_mode=False,
            package_version="3.0.3",
        )
        validate_config(args)


if __name__ == "__main__":
    unittest.main()
