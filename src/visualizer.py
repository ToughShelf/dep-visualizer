"""Визуализатор графа зависимостей пакетов.

Этап 1: прототип с конфигурацией.
"""

from src.config import (
    ConfigError,
    parse_args,
    print_config,
    validate_config,
)


def main() -> None:
    """Точка входа: проверяет параметры и печатает их значения."""
    args = parse_args()
    try:
        validate_config(args)
    except ConfigError as error:
        print(f"Ошибка: {error}")
        raise SystemExit(1) from error
    print_config(args)


if __name__ == "__main__":
    main()
