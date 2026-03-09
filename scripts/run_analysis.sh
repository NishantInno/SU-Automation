#!/usr/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"
export PYTHONPATH="$PROJECT_ROOT"

if [ -f .env ]; then
    echo "Loading environment variables from .env"
    set -a
    source .env
    set +a
fi

mkdir -p logs reports patches

echo "=========================================="
echo "Running Site Analysis"
echo "=========================================="
echo ""

python3 -m core.analysis_engine

echo ""
echo " Site analysis complete!"
echo "Report: reports/site-analysis.json"
echo ""
