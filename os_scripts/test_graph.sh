#!/bin/bash
# Демонстрация BFS-графа на тестовых репозиториях A-Z.

set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

run_graph() {
    local title="$1"
    local file="$2"
    local pkg="$3"
    echo "=== ${title} ==="
    python3 -m src.visualizer \
        --package "$pkg" \
        --repo "$ROOT/repo/${file}" \
        --test-mode on \
        --package-version 1
    echo
}

run_graph "Дерево" "graph_tree.txt" "A"
run_graph "Ромб (транзитивность)" "graph_diamond.txt" "A"
run_graph "Цепочка" "graph_chain.txt" "A"
run_graph "Цикл" "graph_cycle.txt" "A"
run_graph "Петля" "graph_self.txt" "A"
run_graph "Лист без зависимостей" "graph_tree.txt" "B"
run_graph "JSON-граф" "graph_simple.json" "A"
