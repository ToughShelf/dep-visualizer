"""Визуализатор графа зависимостей пакетов. Этап 1: прототип с конфигурацией."""

from src.config import parse_args, print_config, validate_config, ConfigError


def main() -> None:
    """Точка входа: печатает параметры и проверяет их значения."""
    args = parse_args()
    print_config(args)
    try:
        validate_config(args)
    except ConfigError as error:
        print(f"Ошибка: {error}")
        raise SystemExit(1) from error


if __name__ == "__main__":
    main()
