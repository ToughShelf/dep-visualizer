# Dependency Visualizer — визуализатор графа зависимостей

Учебный проект: инструмент визуализации графа зависимостей
для менеджера пакетов (Вариант 29). Этап 3 — основные операции.

Готовые средства (менеджеры пакетов, библиотеки) для получения
зависимостей не используются. Формат пакетов — Python (pip).

## Требования

- Python 3.10 или выше
- Запуск из корня проекта

## Быстрый старт

```bash
python3 -m src.visualizer \
    --package A \
    --repo repo/graph_diamond.txt \
    --test-mode on \
    --package-version 1
```

| Параметр            | Назначение                                 |
|---------------------|--------------------------------------------|
| `--package`         | Имя анализируемого пакета                  |
| `--repo`            | URL или путь к тестовому репозиторию       |
| `--test-mode`       | Режим тестового репозитория (`on`/`off`)   |
| `--package-version` | Версия пакета                              |

Программа строит транзитивный граф зависимостей обходом BFS
с рекурсией и печатает рёбра и циклы.

## Тестовый репозиторий

В `--test-mode on` вместо URL указывается файл описания графа.
Пакеты называются заглавными латинскими буквами:

```
A: B C
B: D
C: D
D:
```

Примеры: `repo/graph_tree.txt`, `graph_diamond.txt`,
`graph_chain.txt`, `graph_cycle.txt`, `graph_self.txt`.

## Структура проекта

```
dep-visualizer/
├── src/
│   ├── config.py
│   ├── graph.py
│   ├── repository.py
│   └── visualizer.py
├── tests/
│   ├── test_config.py
│   ├── test_graph.py
│   └── test_repository.py
├── os_scripts/
│   ├── test_graph.sh
│   └── ...
├── repo/
│   ├── graph_tree.txt
│   ├── graph_diamond.txt
│   ├── graph_chain.txt
│   ├── graph_cycle.txt
│   └── graph_self.txt
├── README.md
├── .gitignore
└── run.sh
```

## Проверка этапа 3

```bash
chmod +x os_scripts/*.sh run.sh
./os_scripts/test_graph.sh
python3 -m unittest discover -s tests
```

## Этапы

1. Прототип с конфигурацией — CLI и проверка параметров
2. Сбор данных — прямые зависимости pip
3. Основные операции (текущий) — BFS-граф и циклы
