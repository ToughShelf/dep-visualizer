#!/bin/bash
# Mermaid для трёх пакетов реального репозитория PyPI.

set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

run_pkg() {
    local name="$1"
    local version="$2"
    echo "=== PyPI, ${name} ${version} ==="
    python3 -m src.visualizer \
        --package "$name" \
        --repo https://pypi.org/simple \
        --test-mode off \
        --package-version "$version"
    echo
}

run_pkg flask 3.0.3
run_pkg click 8.1.7
run_pkg blinker 1.8.2
