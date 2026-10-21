# Dependency Visualizer — визуализатор графа зависимостей

Учебный проект: инструмент визуализации графа зависимостей
для менеджера пакетов (Вариант 29).
Этап 1 — минимальный прототип с конфигурацией.

Готовые средства (менеджеры пакетов, библиотеки) для получения
зависимостей не используются.

## Требования

- Python 3.10 или выше
- Запуск из корня проекта

## Быстрый старт

```bash
chmod +x run.sh
./run.sh
```

Параметры командной строки:

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

| Параметр            | Назначение                                              |
|---------------------|---------------------------------------------------------|
| `--package`         | Имя анализируемого пакета                               |
| `--repo`            | URL репозитория или путь к файлу тестового репозитория  |
| `--test-mode`       | Режим работы с тестовым репозиторием (`on`/`off`)       |
| `--package-version` | Версия пакета                                           |

При запуске печатаются все настраиваемые пользователем параметры
в формате ключ-значение. Незаданный параметр помечается как
`(не задан)`.

## Структура проекта

```
PythonProject2/
├── src/
│   ├── __init__.py
│   ├── config.py
│   ├── visualizer.py
│   └── main.py
├── os_scripts/
│   ├── test_defaults.sh
│   ├── test_params.sh
│   └── test_errors.sh
├── repo/
│   └── test_repo.json
├── tests/
│   ├── __init__.py
│   └── test_config.py
├── README.md
├── .gitignore
└── run.sh
```

## Обработка ошибок

```
Ошибка: имя пакета не задано
Ошибка: неверное имя пакета: bad name
Ошибка: ожидается URL репозитория, получен путь: repo/test_repo.json
Ошибка: файл тестового репозитория не найден: repo/missing.json
error: argument --test-mode: неверное значение режима тестового репозитория: maybe
Ошибка: неверный формат версии: latest
```

- `--test-mode on` требует существующий файл репозитория
- `--test-mode off` требует URL с схемой `http` или `https`

## Проверка этапа 1

```bash
chmod +x os_scripts/*.sh run.sh
./os_scripts/test_defaults.sh
./os_scripts/test_params.sh
./os_scripts/test_errors.sh
python3 -m unittest discover -s tests
```

## Этапы

### Этап 1 — прототип с конфигурацией (текущий)

- CLI
- Параметры `--package`, `--repo`, `--test-mode`, `--package-version`
- Отладочный вывод параметров
- Обработка ошибок для всех параметров
