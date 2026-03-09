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

echo "=========================================="
echo "Applying Security Updates"
echo "=========================================="
echo ""

if [ "${DRY_RUN:-false}" = "true" ]; then
    echo "  DRY RUN MODE - No actual changes will be made"
    echo ""
    python3 -c "from core.update_engine import check_versions; check_versions()"
    echo ""
    echo "Dry run complete. See reports/module-updates.json for available updates."
    exit 0
fi

read -p "  This will apply updates to your Drupal site. Continue? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Update cancelled."
    exit 0
fi

echo ""
echo "Running version check first..."
python3 -c "from core.update_engine import check_versions; check_versions()"

echo ""
echo "Applying updates..."
python3 -c "from core.update_engine import apply_updates; apply_updates()"

echo ""
echo " Updates applied successfully!"
echo "Report: reports/update-results.json"
echo ""
