"""Визуализатор графа зависимостей пакетов.

Этап 5: описание графа на языке Mermaid.
"""

from src.config import ConfigError, parse_args, validate_config
from src.graph import invert_adjacency, recursive_bfs
from src.mermaid import to_mermaid
from src.repository import (
    RepoError,
    load_full_adjacency,
    make_neighbors,
)


def print_graph(
    package: str,
    adjacency: dict[str, list[str]],
    cycles: list[tuple[str, str]],
) -> None:
    """Печатает граф зависимостей на языке Mermaid."""
    del cycles
    print(f"Граф зависимостей {package}:")
    print(to_mermaid(adjacency))


def print_reverse(package: str, names: list[str]) -> None:
    """Печатает пакеты, которые зависят от заданного."""
    print(f"Обратные зависимости {package}:")
    if not names:
        print("  (нет)")
        return
    for name in names:
        print(f"  {name}")


def main() -> None:
    """Точка входа: прямой или обратный граф BFS."""
    args = parse_args()
    try:
        validate_config(args)
        if args.reverse:
            _run_reverse(args.package, args.repo, args.test_mode)
            return
        neighbors = make_neighbors(
            args.repo,
            bool(args.test_mode),
            args.package_version,
        )
        adjacency, cycles, _order = recursive_bfs(
            args.package,
            neighbors,
        )
    except (ConfigError, RepoError) as error:
        print(f"Ошибка: {error}")
        raise SystemExit(1) from error
    print_graph(args.package, adjacency, cycles)


def _run_reverse(package: str, repo: str, test_mode: bool | None) -> None:
    """Строит обратные зависимости BFS по тестовому графу."""
    if not test_mode:
        raise ConfigError(
            "обратные зависимости доступны в тестовом режиме",
        )
    full = load_full_adjacency(repo)
    if package not in full:
        raise RepoError(f"пакет не найден: {package}")
    inverted = invert_adjacency(full)
    _adjacency, _cycles, order = recursive_bfs(
        package,
        lambda name: inverted.get(name, []),
    )
    print_reverse(package, order[1:])


if __name__ == "__main__":
    main()
