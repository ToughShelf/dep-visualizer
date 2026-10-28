"""Визуализатор графа зависимостей пакетов.

Этап 2: сбор прямых зависимостей.
"""

from src.config import ConfigError, parse_args, validate_config
from src.repository import RepoError, get_direct_dependencies


def print_dependencies(
    package: str,
    version: str,
    deps: list[str],
) -> None:
    """Печатает прямые зависимости пакета."""
    print(f"Прямые зависимости {package}=={version}:")
    if not deps:
        print("  (нет)")
        return
    for dep in deps:
        print(f"  {dep}")


def main() -> None:
    """Точка входа: читает зависимости и печатает их."""
    args = parse_args()
    try:
        validate_config(args)
        deps = get_direct_dependencies(
            package=args.package,
            version=args.package_version,
            repo=args.repo,
            test_mode=bool(args.test_mode),
        )
    except (ConfigError, RepoError) as error:
        print(f"Ошибка: {error}")
        raise SystemExit(1) from error
    print_dependencies(args.package, args.package_version, deps)


if __name__ == "__main__":
    main()
