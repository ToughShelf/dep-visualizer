#!/bin/bash
# Проверка запуска без параметров и со всеми параметрами.

set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "=== Без параметров ==="
python3 -m src.visualizer || true

echo "=== Все параметры (URL) ==="
python3 -m src.visualizer \
    --package flask \
    --repo https://pypi.org/simple \
    --test-mode off \
    --package-version 3.0.3

echo "=== Все параметры (тестовый репозиторий) ==="
python3 -m src.visualizer \
    --package flask \
    --repo "$ROOT/repo/test_repo.json" \
    --test-mode on \
    --package-version 3.0.3
