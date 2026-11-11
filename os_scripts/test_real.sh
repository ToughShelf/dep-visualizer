
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "=== PyPI, flask 3.0.3 ==="
python3 -m src.visualizer \
    --package flask \
    --repo https://pypi.org/simple \
    --test-mode off \
    --package-version 3.0.3
