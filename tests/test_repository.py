"""Юнит-тесты получения прямых зависимостей."""

import json
import unittest
import urllib.error
from pathlib import Path
from unittest.mock import patch

from src.repository import (
    RepoError,
    deps_from_pypi_json,
    deps_from_test_data,
    get_direct_dependencies,
    pypi_json_url,
    requirement_line,
)

REPO_FILE = Path(__file__).resolve().parent.parent / "repo" / "test_repo.json"


class FakeResponse:
    """Поддельный HTTP-ответ для тестов."""

    def __init__(self, payload: str) -> None:
        """Сохраняет тело ответа."""
        self.payload = payload.encode("utf-8")

    def read(self) -> bytes:
        """Возвращает тело ответа."""
        return self.payload

    def __enter__(self) -> "FakeResponse":
        """Открывает контекстный менеджер."""
        return self

    def __exit__(self, *_args: object) -> bool:
        """Закрывает контекстный менеджер."""
        return False


class TestRequirementLine(unittest.TestCase):
    """Проверяет разбор строк Requires-Dist."""

    def test_plain_requirement(self) -> None:
        """Обычная зависимость сохраняется."""
        self.assertEqual(requirement_line("blinker>=1.6.2"), "blinker>=1.6.2")

    def test_extra_requirement_skipped(self) -> None:
        """Зависимости extra отбрасываются."""
        raw = "asgiref>=3.2; extra == 'async'"
        self.assertIsNone(requirement_line(raw))

    def test_marker_without_extra_kept(self) -> None:
        """Маркер окружения без extra не отбрасывает зависимость."""
        raw = "importlib-metadata>=3.6.0; python_version < '3.10'"
        self.assertEqual(
            requirement_line(raw),
            "importlib-metadata>=3.6.0",
        )


class TestPypiJson(unittest.TestCase):
    """Проверяет разбор JSON-API репозитория pip."""

    def test_json_url_from_simple(self) -> None:
        """URL /simple превращается в JSON-API."""
        url = pypi_json_url("https://pypi.org/simple", "flask", "3.0.3")
        self.assertEqual(url, "https://pypi.org/pypi/flask/3.0.3/json")

    def test_deps_from_payload(self) -> None:
        """Из requires_dist берутся только прямые зависимости."""
        payload = {
            "info": {
                "requires_dist": [
                    "blinker>=1.6.2",
                    "click>=8.1.3",
                    "asgiref>=3.2; extra == 'async'",
                ],
            },
        }
        deps = deps_from_pypi_json(payload)
        self.assertEqual(deps, ["blinker>=1.6.2", "click>=8.1.3"])

    def test_empty_requires_dist(self) -> None:
        """Пустой список зависимостей допустим."""
        self.assertEqual(deps_from_pypi_json({"info": {}}), [])

    def test_invalid_payload(self) -> None:
        """Без поля info ответ отклоняется."""
        with self.assertRaises(RepoError):
            deps_from_pypi_json({})


class TestTestRepo(unittest.TestCase):
    """Проверяет чтение тестового репозитория."""

    def test_flask_direct_deps(self) -> None:
        """Для flask 3.0.3 читаются прямые зависимости."""
        data = json.loads(REPO_FILE.read_text(encoding="utf-8"))
        deps = deps_from_test_data(data, "flask", "3.0.3")
        self.assertIn("blinker==1.8.2", deps)
        self.assertIn("jinja2==3.1.4", deps)
        self.assertNotIn("markupsafe==2.1.5", deps)

    def test_missing_package(self) -> None:
        """Неизвестный пакет вызывает ошибку."""
        with self.assertRaises(RepoError) as ctx:
            deps_from_test_data({}, "flask", "3.0.3")
        self.assertIn("пакет не найден", str(ctx.exception))

    def test_missing_version(self) -> None:
        """Неизвестная версия вызывает ошибку."""
        data = {"flask": {"1.0.0": {"dependencies": {}}}}
        with self.assertRaises(RepoError) as ctx:
            deps_from_test_data(data, "flask", "3.0.3")
        self.assertIn("версия не найдена", str(ctx.exception))

    def test_get_direct_dependencies_test_mode(self) -> None:
        """Публичная функция читает тестовый файл."""
        deps = get_direct_dependencies(
            "Flask",
            "3.0.3",
            str(REPO_FILE),
            True,
        )
        self.assertTrue(deps)

class TestFetchPypi(unittest.TestCase):
    """Проверяет HTTP-запрос к репозиторию без pip."""

    def test_fetch_success(self) -> None:
        """JSON-ответ репозитория разбирается в зависимости."""
        payload = json.dumps({
            "info": {"requires_dist": ["click>=8.1.3"]},
        })
        fake = FakeResponse(payload)
        with patch("urllib.request.urlopen", return_value=fake):
            deps = get_direct_dependencies(
                "flask",
                "3.0.3",
                "https://pypi.org/simple",
                False,
            )
        self.assertEqual(deps, ["click>=8.1.3"])

    def test_fetch_not_found(self) -> None:
        """HTTP 404 превращается в ошибку репозитория."""
        error = urllib.error.HTTPError(
            url="https://pypi.org/pypi/missing/1.0.0/json",
            code=404,
            msg="Not Found",
            hdrs=None,
            fp=None,
        )
        with patch("urllib.request.urlopen", side_effect=error):
            with self.assertRaises(RepoError) as ctx:
                get_direct_dependencies(
                    "missing",
                    "1.0.0",
                    "https://pypi.org/simple",
                    False,
                )
        self.assertIn("не найдены", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
