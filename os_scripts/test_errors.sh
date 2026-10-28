#!/bin/bash
# Демонстрация обработки ошибок для всех параметров.

set -u
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

run_case() {
    local title="$1"
    shift
    echo "=== ${title} ==="
    python3 -m src.visualizer "$@" || true
    echo
}

run_case "Имя пакета не задано" \
    --repo https://pypi.org/simple \
    --test-mode off \
    --package-version 3.0.3

run_case "Репозиторий не задан" \
    --package flask \
    --test-mode off \
    --package-version 3.0.3

run_case "Пустое имя пакета" \
    --package "" \
    --repo https://pypi.org/simple \
    --test-mode off \
    --package-version 3.0.3

run_case "Неверное имя пакета" \
    --package "bad name" \
    --repo https://pypi.org/simple \
    --test-mode off \
    --package-version 3.0.3

run_case "Пустой репозиторий" \
    --package flask \
    --repo "" \
    --test-mode off \
    --package-version 3.0.3

run_case "Путь вместо URL без тестового режима" \
    --package flask \
    --repo "$ROOT/repo/test_repo.json" \
    --test-mode off \
    --package-version 3.0.3

run_case "Неверный режим тестового репозитория" \
    --package flask \
    --repo https://pypi.org/simple \
    --test-mode maybe \
    --package-version 3.0.3

run_case "Тестовый режим без файла репозитория" \
    --package flask \
    --test-mode on \
    --package-version 3.0.3

run_case "Отсутствующий файл тестового репозитория" \
    --package flask \
    --repo "$ROOT/repo/missing.json" \
    --test-mode on \
    --package-version 3.0.3

run_case "Версия пакета не задана" \
    --package flask \
    --repo https://pypi.org/simple \
    --test-mode off

run_case "Пакет не найден в тестовом репозитории" \
    --package missing \
    --repo "$ROOT/repo/test_repo.json" \
    --test-mode on \
    --package-version 3.0.3

run_case "Версия не найдена в тестовом репозитории" \
    --package flask \
    --repo "$ROOT/repo/test_repo.json" \
    --test-mode on \
    --package-version 9.9.9

run_case "Пустая версия пакета" \
    --package flask \
    --repo https://pypi.org/simple \
    --test-mode off \
    --package-version ""

run_case "Неверный формат версии" \
    --package flask \
    --repo https://pypi.org/simple \
    --test-mode off \
    --package-version latest
