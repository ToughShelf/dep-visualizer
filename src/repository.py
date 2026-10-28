"""Получение прямых зависимостей пакетов Python (pip)."""

import json
import re
import ssl
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from src.graph import NeighborFn

USER_AGENT = "dep-visualizer/0.2"
HTTP_TIMEOUT = 20
SIMPLE_SUFFIX = "/simple"
PYPI_SUFFIX = "/pypi"
HTTP_NOT_FOUND = 404
NAME_PATTERN = re.compile(r"[-_.]+")
REQ_NAME_PATTERN = re.compile(
    r"^([A-Za-z0-9][A-Za-z0-9._+\-]*)",
)
EQ_VERSION_PATTERN = re.compile(r"==\s*([A-Za-z0-9._+\-]+)")
GRAPH_WILDCARD = "*"
COMMENT_PREFIX = "#"
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


def parse_graph_text(raw: str) -> dict[str, list[str]]:
    """Читает граф пакетов A-Z из текстового описания."""
    adjacency: dict[str, list[str]] = {}
    for line_no, line in enumerate(raw.splitlines(), 1):
        stripped = line.strip()
        if not stripped or stripped.startswith(COMMENT_PREFIX):
            continue
        if ":" not in stripped:
            raise RepoError(f"некорректная строка графа: {line_no}")
        name, _, rest = stripped.partition(":")
        name = name.strip()
        _check_letter_name(name)
        deps = rest.split()
        for dep in deps:
            _check_letter_name(dep)
        adjacency[name] = deps
        for dep in deps:
            adjacency.setdefault(dep, [])
    if not adjacency:
        raise RepoError("пустой граф тестового репозитория")
    return adjacency


def _check_letter_name(name: str) -> None:
    """Имя пакета в тестовом графе — заглавные латинские буквы."""
    if not name or not name.isalpha() or name != name.upper():
        raise RepoError(
            f"пакет должен быть заглавными буквами: {name}",
        )


def graph_to_json(adjacency: dict[str, list[str]]) -> dict[str, Any]:
    """Превращает текстовый граф в формат тестового JSON."""
    data: dict[str, Any] = {}
    for pkg, deps in adjacency.items():
        data[pkg] = {
            GRAPH_WILDCARD: {
                "dependencies": {dep: "" for dep in deps},
            },
        }
    return data


def split_requirement(spec: str) -> tuple[str, str | None]:
    """Выделяет имя пакета и точную версию из строки зависимости."""
    text = spec.strip()
    match = REQ_NAME_PATTERN.match(text)
    if match is None:
        raise RepoError(f"некорректная зависимость: {spec}")
    name = match.group(1)
    exact = EQ_VERSION_PATTERN.search(text)
    if exact is not None:
        return name, exact.group(1)
    return name, None


def pypi_project_url(repo: str, package: str) -> str:
    """Строит URL JSON-API проекта без номера версии."""
    base = repo.rstrip("/")
    lowered = base.lower()
    if lowered.endswith(SIMPLE_SUFFIX):
        base = base[: -len(SIMPLE_SUFFIX)]
        lowered = base.lower()
    if lowered.endswith(PYPI_SUFFIX):
        return f"{base}/{package}/json"
    return f"{base}/pypi/{package}/json"


def fetch_latest_version(repo: str, package: str) -> str:
    """Берёт актуальную версию пакета из JSON-API."""
    payload = fetch_pypi_json(pypi_project_url(repo, package))
    info = payload.get("info")
    if not isinstance(info, dict):
        raise RepoError("некорректный ответ репозитория")
    version = info.get("version")
    if not isinstance(version, str) or not version:
        raise RepoError(f"версия не найдена: {package}")
    return version


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
        info = versions.get(GRAPH_WILDCARD)
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
    except json.JSONDecodeError:
        return graph_to_json(parse_graph_text(raw))
    if not isinstance(data, dict):
        raise RepoError("некорректный тестовый репозиторий")
    if _is_simple_adjacency(data):
        return graph_to_json(_simple_json_to_graph(data))
    return data


def _is_simple_adjacency(data: dict[str, Any]) -> bool:
    """Проверяет JSON вида {"A": ["B", "C"]}."""
    if not data:
        return False
    return all(isinstance(value, list) for value in data.values())


def _simple_json_to_graph(data: dict[str, Any]) -> dict[str, list[str]]:
    """Читает простой JSON-граф с именами A-Z."""
    adjacency: dict[str, list[str]] = {}
    for pkg, deps in data.items():
        name = str(pkg)
        _check_letter_name(name)
        names = [str(dep) for dep in deps]
        for dep in names:
            _check_letter_name(dep)
        adjacency[name] = names
        for dep in names:
            adjacency.setdefault(dep, [])
    return adjacency


def load_full_adjacency(path: str) -> dict[str, list[str]]:
    """Загружает полный граф тестового репозитория."""
    data = load_test_repo(path)
    adjacency: dict[str, list[str]] = {}
    for pkg, versions in data.items():
        if not isinstance(versions, dict) or not versions:
            continue
        info = versions.get(GRAPH_WILDCARD)
        if info is None:
            info = next(iter(versions.values()))
        if not isinstance(info, dict):
            continue
        deps = info.get("dependencies", {})
        if not isinstance(deps, dict):
            continue
        names = [str(name) for name in deps]
        adjacency[str(pkg)] = names
        for name in names:
            adjacency.setdefault(name, [])
    return adjacency


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


def get_direct_pairs(
    package: str,
    version: str,
    repo: str,
    test_mode: bool,
) -> list[tuple[str, str]]:
    """Возвращает пары имя-версия прямых зависимостей."""
    specs = get_direct_dependencies(
        package,
        version,
        repo,
        test_mode,
    )
    pairs: list[tuple[str, str]] = []
    for spec in specs:
        name, dep_version = split_requirement(spec)
        if dep_version is None and not test_mode:
            dep_version = fetch_latest_version(repo, name)
        if dep_version is None:
            dep_version = version
        pairs.append((name, dep_version))
    return pairs


def make_neighbors(
    repo: str,
    test_mode: bool,
    start_version: str,
) -> NeighborFn:
    """Создаёт функцию прямых соседей для обхода BFS."""
    versions: dict[str, str] = {}

    def neighbors(name: str) -> list[str]:
        version = versions.get(name, start_version)
        pairs = get_direct_pairs(name, version, repo, test_mode)
        names: list[str] = []
        for dep_name, dep_version in pairs:
            versions[dep_name] = dep_version
            names.append(dep_name)
        return names

    return neighbors
