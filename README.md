# Dependency Visualizer — визуализатор графа зависимостей

Учебный проект: инструмент визуализации графа зависимостей
для менеджера пакетов (Вариант 29). Этап 2 — сбор данных.

Готовые средства (менеджеры пакетов, библиотеки) для получения
зависимостей не используются. Формат пакетов — Python (pip).

## Требования

- Python 3.10 или выше
- Запуск из корня проекта

## Быстрый старт

```bash
chmod +x run.sh
./run.sh \
    --package flask \
    --repo https://pypi.org/simple \
    --test-mode off \
    --package-version 3.0.3
```

```bash
python3 -m src.visualizer \
    --package flask \
    --repo https://pypi.org/simple \
    --test-mode off \
    --package-version 3.0.3
```

Тестовый репозиторий:

```bash
python3 -m src.visualizer \
    --package flask \
    --repo repo/test_repo.json \
    --test-mode on \
    --package-version 3.0.3
```

| Параметр            | Назначение                                 |
|---------------------|--------------------------------------------|
| `--package`         | Имя анализируемого пакета                  |
| `--repo`            | URL или путь к тестовому репозиторию       |
| `--test-mode`       | Режим тестового репозитория (`on`/`off`)   |
| `--package-version` | Версия пакета                              |

`--package`, `--repo` и `--package-version` обязательны.
Программа запрашивает метаданные указанной версии пакета
по URL репозитория (JSON-API pip/PyPI) или из тестового файла
и печатает прямые зависимости.

## Структура проекта

```
dep-visualizer/
├── src/
│   ├── __init__.py
│   ├── config.py
│   ├── repository.py
│   ├── visualizer.py
│   └── main.py
├── tests/
│   ├── __init__.py
│   ├── test_config.py
│   └── test_repository.py
├── os_scripts/
│   ├── test_defaults.sh
│   ├── test_params.sh
│   ├── test_errors.sh
│   └── test_deps.sh
├── repo/
│   └── test_repo.json
├── README.md
├── .gitignore
└── run.sh
```

## Сбор зависимостей

pip и сторонние библиотеки не используются. Зависимости читаются:

- из JSON-API репозитория: `{repo}/pypi/{пакет}/{версия}/json`
- либо из файла тестового репозитория при `--test-mode on`

Печатаются только прямые зависимости заданной версии.

## Обработка ошибок

```
Ошибка: имя пакета не задано
Ошибка: репозиторий не задан
Ошибка: версия пакета не задана
Ошибка: пакет не найден: missing
Ошибка: версия не найдена: flask 9.9.9
Ошибка: пакет или версия не найдены
```

## Проверка этапа 2

```bash
chmod +x os_scripts/*.sh run.sh
./os_scripts/test_defaults.sh
./os_scripts/test_params.sh
./os_scripts/test_errors.sh
./os_scripts/test_deps.sh
python3 -m unittest discover -s tests
```

## Этапы

1. Прототип с конфигурацией — CLI и проверка параметров
2. Сбор данных (текущий) — прямые зависимости pip
