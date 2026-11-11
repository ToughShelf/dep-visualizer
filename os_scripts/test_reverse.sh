#!/bin/bash
# Обратные зависимости на тестовых графах A-Z.

set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

run_rev() {
    local title="$1"
    local file="$2"
    local pkg="$3"
    echo "=== ${title} ==="
    python3 -m src.visualizer \
        --package "$pkg" \
        --repo "$ROOT/repo/${file}" \
        --test-mode on \
        --package-version 1 \
        --reverse
    echo
}

run_rev "Ромб, пакет D" "graph_diamond.txt" "D"
run_rev "Ромб, корень A" "graph_diamond.txt" "A"
run_rev "Цепочка, пакет C" "graph_chain.txt" "C"
run_rev "Цикл, пакет A" "graph_cycle.txt" "A"
run_rev "JSON с X и Y, пакет A" "graph_leaf.json" "A"
run_rev "JSON с X и Y, пакет D" "graph_leaf.json" "D"
run_rev "Дерево, лист B" "graph_tree.txt" "B"

echo "=== Без тестового режима ==="
python3 -m src.visualizer \
    --package flask \
    --repo https://pypi.org/simple \
    --test-mode off \
    --package-version 3.0.3 \
    --reverse || true
