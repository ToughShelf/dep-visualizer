#!/bin/bash
# Поочерёдная проверка каждого параметра командной строки.

set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "=== Только --package ==="
python3 -m src.visualizer --package flask || true

echo "=== Только --repo ==="
python3 -m src.visualizer --repo https://pypi.org/simple || true

echo "=== Пакет и репозиторий ==="
python3 -m src.visualizer \
    --package flask \
    --repo https://pypi.org/simple || true

echo "=== Только --test-mode ==="
python3 -m src.visualizer \
    --package flask \
    --repo https://pypi.org/simple \
    --test-mode off || true

echo "=== Только --package-version ==="
python3 -m src.visualizer \
    --package flask \
    --repo "$ROOT/repo/test_repo.json" \
    --test-mode on \
    --package-version 3.0.3

echo "=== Все параметры ==="
python3 -m src.visualizer \
    --package flask \
    --repo "$ROOT/repo/test_repo.json" \
    --test-mode on \
    --package-version 3.0.3
