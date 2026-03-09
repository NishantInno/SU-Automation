#!/usr/bin/env bash
set -euo pipefail
if [[ $# -lt 1 ]]; then
  echo "Usage: deploy.sh <local|dev|qc|prod>" >&2
  exit 1
fi
TARGET="$1"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
export PYTHONPATH="$ROOT"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"
export PYTHONPATH="$PROJECT_ROOT"

if [ -f .env ]; then
    set -a
    source .env
    set +a
fi

ENVIRONMENT="${TARGET:-local}"

echo "=========================================="
echo "Deploying to: $ENVIRONMENT"
echo "=========================================="
echo ""

if [ "$ENVIRONMENT" = "prod" ]; then
    echo "  WARNING: You are about to deploy to PRODUCTION!"
    echo ""
    read -p "Are you absolutely sure? Type 'DEPLOY TO PROD' to continue: " -r
    if [ "$REPLY" != "DEPLOY TO PROD" ]; then
        echo "Deployment cancelled."
        exit 0
    fi
    echo ""
fi

echo "Running pre-deployment checks..."
python3 "$ROOT/core/testing_engine.py" || { echo "Pre-deployment tests failed!"; exit 1; }

echo ""
echo "Deploying..."
python3 "$ROOT/core/deploy_engine.py" "$ENVIRONMENT"

echo ""
echo " Deployment to $ENVIRONMENT complete!"
echo ""
