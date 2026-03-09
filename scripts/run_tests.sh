#!/usr/bin/env bash
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

mkdir -p logs reports

echo "=========================================="
echo "Running Automated Tests"
echo "=========================================="
echo ""

python3 -m core.testing_engine

echo ""
echo "✅ Testing complete!"
echo "Report: reports/testing-results.json"
echo ""

python3 -c "
import json
from pathlib import Path

report_path = Path('reports/testing-results.json')
if report_path.exists():
    report = json.loads(report_path.read_text())
    summary = report.get('summary', {})
    http_errors = summary.get('http_errors', 0)
    watchdog_errors = summary.get('watchdog_errors', 0)
    
    print('Test Summary:')
    print(f'  HTTP Errors: {http_errors}')
    print(f'  Watchdog Errors: {watchdog_errors}')
    print('')
    
    if http_errors > 0 or watchdog_errors > 0:
        print('⚠️  Tests completed with errors!')
        exit(1)
    else:
        print('✅ All tests passed!')
"
