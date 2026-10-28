"""Визуализатор графа зависимостей пакетов.

Этап 3: транзитивный граф, BFS с рекурсией, циклы.
"""

from src.config import ConfigError, parse_args, validate_config
from src.graph import recursive_bfs
from src.repository import RepoError, make_neighbors


def print_graph(
    package: str,
    adjacency: dict[str, list[str]],
    cycles: list[tuple[str, str]],
) -> None:
    """Печатает транзитивный граф и найденные циклы."""
    print(f"Граф зависимостей {package}:")
    edges = [
        (src, dst)
        for src, dests in adjacency.items()
        for dst in dests
    ]
    if not edges:
        print("  (нет)")
    else:
        for src, dst in edges:
            print(f"  {src} -> {dst}")
    print("Циклические зависимости:")
    if not cycles:
        print("  (нет)")
        return
    for src, dst in cycles:
        print(f"  {src} -> {dst}")


def main() -> None:
    """Точка входа: строит граф BFS и печатает его."""
    args = parse_args()
    try:
        validate_config(args)
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


if __name__ == "__main__":
    main()
