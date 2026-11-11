#!/bin/bash
# Mermaid-диаграммы для трёх разных пакетов.

set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

run_pkg() {
    local title="$1"
    local pkg="$2"
    local file="$3"
    echo "=== ${title}: ${pkg} ==="
    python3 -m src.visualizer \
        --package "$pkg" \
        --repo "$ROOT/repo/${file}" \
        --test-mode on \
        --package-version 1
    echo
}

run_pkg "Ромб" "A" "graph_diamond.txt"
run_pkg "Цепочка" "C" "graph_chain.txt"
run_pkg "Цикл" "B" "graph_cycle.txt"
