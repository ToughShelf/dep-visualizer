# Dependency Visualizer — визуализатор графа зависимостей

Учебный проект: инструмент визуализации графа зависимостей
для менеджера пакетов (Вариант 29). Этап 4 — доп. операции.

Готовые средства (менеджеры пакетов, библиотеки) для получения
зависимостей не используются. Формат пакетов — Python (pip).

## Требования

- Python 3.10 или выше
- Запуск из корня проекта

## Быстрый старт

Прямой транзитивный граф:

```bash
python3 -m src.visualizer \
    --package A \
    --repo repo/graph_diamond.txt \
    --test-mode on \
    --package-version 1
```

Обратные зависимости пакета D:

```bash
python3 -m src.visualizer \
    --package D \
    --repo repo/graph_diamond.txt \
    --test-mode on \
    --package-version 1 \
    --reverse
```

| Параметр            | Назначение                                 |
|---------------------|--------------------------------------------|
| `--package`         | Имя анализируемого пакета                  |
| `--repo`            | URL или путь к тестовому репозиторию       |
| `--test-mode`       | Режим тестового репозитория (`on`/`off`)   |
| `--package-version` | Версия пакета                              |
| `--reverse`         | Обратные зависимости заданного пакета      |

`--reverse` работает в тестовом режиме. Обход тот же:
BFS с рекурсией по инвертированному графу.

## Тестовый репозиторий

Пакеты — заглавные латинские буквы. Форматы файла:

```
A: B C
B: D
C: D
D:
```

или JSON `{"A": ["B", "C"], ...}`.

Примеры: `graph_tree.txt`, `graph_diamond.txt`,
`graph_chain.txt`, `graph_cycle.txt`, `graph_self.txt`,
`graph_simple.json`, `graph_leaf.json`.

## Проверка этапов 3 и 4

```bash
chmod +x os_scripts/*.sh run.sh
./os_scripts/test_graph.sh
./os_scripts/test_reverse.sh
python3 -m unittest discover -s tests
```

## Этапы

1. Прототип с конфигурацией — CLI и проверка параметров
2. Сбор данных — прямые зависимости pip
3. Основные операции — BFS-граф и циклы
4. Доп. операции (текущий) — обратные зависимости
