#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"
export PYTHONPATH="$PROJECT_ROOT"

if [ -f .env ]; then
    set -a
    source .env
    set +a
fi

echo "Running version check..."
python3 -c "from core.update_engine import check_versions; check_versions()"

echo ""
echo "Version check complete. Report: reports/module-updates.json"
