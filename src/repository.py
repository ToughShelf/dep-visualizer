"""Получение прямых зависимостей пакетов Python (pip)."""

import json
import re
import ssl
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

USER_AGENT = "dep-visualizer/0.2"
HTTP_TIMEOUT = 20
SIMPLE_SUFFIX = "/simple"
PYPI_SUFFIX = "/pypi"
HTTP_NOT_FOUND = 404
NAME_PATTERN = re.compile(r"[-_.]+")
CERT_CANDIDATES = (
    "/etc/ssl/cert.pem",
    "/opt/homebrew/etc/openssl@3/cert.pem",
    "/usr/local/etc/openssl@3/cert.pem",
)


class RepoError(ValueError):
    """Ошибка чтения зависимостей из репозитория."""


def normalize_name(name: str) -> str:
    """Приводит имя пакета к каноническому виду PEP 503."""
    return NAME_PATTERN.sub("-", name).lower()


def pypi_json_url(repo: str, package: str, version: str) -> str:
    """Строит URL JSON-API репозитория pip/PyPI."""
    base = repo.rstrip("/")
    lowered = base.lower()
    if lowered.endswith(SIMPLE_SUFFIX):
        base = base[: -len(SIMPLE_SUFFIX)]
        lowered = base.lower()
    if lowered.endswith(PYPI_SUFFIX):
        return f"{base}/{package}/{version}/json"
    return f"{base}/pypi/{package}/{version}/json"


def requirement_line(raw: str) -> str | None:
    """Оставляет прямую зависимость, отбрасывая extra."""
    text = raw.strip()
    if not text:
        return None
    body, _, marker = text.partition(";")
    if "extra" in marker:
        return None
    body = body.strip()
    if not body:
        return None
    return body


def deps_from_pypi_json(payload: dict[str, Any]) -> list[str]:
    """Читает Requires-Dist из ответа JSON-API."""
    info = payload.get("info")
    if not isinstance(info, dict):
        raise RepoError("некорректный ответ репозитория")
    requires = info.get("requires_dist")
    if not requires:
        return []
    result: list[str] = []
    for item in requires:
        if not isinstance(item, str):
            continue
        line = requirement_line(item)
        if line is not None:
            result.append(line)
    return result


def deps_from_test_data(
    data: dict[str, Any],
    package: str,
    version: str,
) -> list[str]:
    """Читает прямые зависимости из файла тестового репозитория."""
    versions = _find_package(data, package)
    if versions is None:
        raise RepoError(f"пакет не найден: {package}")
    if not isinstance(versions, dict):
        raise RepoError("некорректный тестовый репозиторий")
    info = versions.get(version)
    if info is None:
        raise RepoError(f"версия не найдена: {package} {version}")
    if not isinstance(info, dict):
        raise RepoError("некорректный тестовый репозиторий")
    dependencies = info.get("dependencies", {})
    if not isinstance(dependencies, dict):
        raise RepoError("некорректный список зависимостей")
    result: list[str] = []
    for name, dep_version in dependencies.items():
        if dep_version:
            result.append(f"{name}=={dep_version}")
        else:
            result.append(str(name))
    return result


def _find_package(
    data: dict[str, Any],
    package: str,
) -> Any | None:
    """Ищет пакет в тестовом репозитории без учёта регистра."""
    wanted = normalize_name(package)
    for name, versions in data.items():
        if normalize_name(str(name)) == wanted:
            return versions
    return None


def load_test_repo(path: str) -> dict[str, Any]:
    """Загружает JSON тестового репозитория с диска."""
    try:
        raw = Path(path).read_text(encoding="utf-8")
    except OSError as error:
        raise RepoError(
            f"не удалось прочитать тестовый репозиторий: {error}",
        ) from error
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as error:
        raise RepoError(
            "некорректный JSON тестового репозитория",
        ) from error
    if not isinstance(data, dict):
        raise RepoError("некорректный тестовый репозиторий")
    return data


def ssl_context() -> ssl.SSLContext:
    """Собирает SSL-контекст со системными сертификатами."""
    context = ssl.create_default_context()
    paths = ssl.get_default_verify_paths()
    if paths.cafile and Path(paths.cafile).is_file():
        return context
    if paths.capath and Path(paths.capath).exists():
        return context
    for path in CERT_CANDIDATES:
        if Path(path).is_file():
            context.load_verify_locations(cafile=path)
            return context
    return context


def fetch_pypi_json(url: str) -> dict[str, Any]:
    """Скачивает JSON метаданных пакета по HTTP."""
    request = urllib.request.Request(
        url,
        headers={"User-Agent": USER_AGENT},
    )
    try:
        with urllib.request.urlopen(
            request,
            timeout=HTTP_TIMEOUT,
            context=ssl_context(),
        ) as response:
            raw = response.read()
    except urllib.error.HTTPError as error:
        if error.code == HTTP_NOT_FOUND:
            raise RepoError(
                "пакет или версия не найдены",
            ) from error
        raise RepoError(f"ошибка HTTP {error.code}") from error
    except urllib.error.URLError as error:
        reason = getattr(error, "reason", error)
        raise RepoError(
            f"не удалось обратиться к репозиторию: {reason}",
        ) from error
    try:
        payload = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise RepoError("некорректный ответ репозитория") from error
    if not isinstance(payload, dict):
        raise RepoError("некорректный ответ репозитория")
    return payload


def get_direct_dependencies(
    package: str,
    version: str,
    repo: str,
    test_mode: bool,
) -> list[str]:
    """Возвращает прямые зависимости указанной версии пакета."""
    if test_mode:
        data = load_test_repo(repo)
        return deps_from_test_data(data, package, version)
    url = pypi_json_url(repo, package, version)
    payload = fetch_pypi_json(url)
    return deps_from_pypi_json(payload)
