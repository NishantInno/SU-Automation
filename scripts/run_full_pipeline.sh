#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "=========================================="
echo "Automated Security Update - Full Pipeline"
echo "=========================================="
echo ""

cd "$PROJECT_ROOT"

export PYTHONPATH="$PROJECT_ROOT"

if [ -f .env ]; then
    echo "Loading environment variables from .env"
    set -a
    source .env
    set +a
fi

mkdir -p logs reports patches

echo "[1/9] Stage 1: Site Analysis"
python3 -m core.analysis_engine || { echo "Site analysis failed"; exit 1; }
echo ""

echo "[2/9] Stage 2: Version Check"
python3 -c "from core.update_engine import check_versions; check_versions()" || { echo "Version check failed"; exit 1; }
echo ""

if [ "${DRY_RUN:-false}" != "true" ]; then
    echo "[3/9] Stage 3: Apply Security Updates"
    python3 -c "from core.update_engine import apply_updates; apply_updates()" || { echo "Update failed"; exit 1; }
    echo ""
else
    echo "[3/9] Stage 3: Apply Security Updates (SKIPPED - DRY RUN)"
    echo ""
fi

echo "[4/9] Stage 4: Run Tests"
python3 -m core.testing_engine || { echo "Testing failed"; exit 1; }
echo ""

echo "[5/9] Stage 5: Generate Report"
python3 -m core.report_engine || { echo "Report generation failed"; exit 1; }
echo ""

if [ "${USE_ONLINE_VERIFICATION:-true}" = "true" ]; then
    echo "[6/9] Stage 6: Online Verification (No AI Required)"
    python3 -m core.online_verification || echo "Online verification completed with warnings"
    echo ""
else
    echo "[6/9] Stage 6: Online Verification (SKIPPED)"
    echo ""
fi

if [ "${SKIP_AI_FIX:-false}" != "true" ] && [ "${DRY_RUN:-false}" != "true" ]; then
    echo "[7/9] Stage 7: Re-verification"
    python3 -m core.testing_engine || { echo "Re-verification failed"; exit 1; }
    echo ""
else
    echo "[7/9] Stage 7: Re-verification (SKIPPED)"
    echo ""
fi

if [ "${DRY_RUN:-false}" != "true" ]; then
    echo "[8/9] Stage 8: Deployment"
    ENVIRONMENT="${ENVIRONMENT:-local}"
    python3 -c "from core.deploy_engine import deploy; deploy('$ENVIRONMENT')" || { echo "Deployment failed"; exit 1; }
    echo ""
else
    echo "[8/9] Stage 8: Deployment (SKIPPED - DRY RUN)"
    echo ""
fi

echo "[9/9] Stage 9: Final Verification"
python3 -m core.testing_engine || { echo "Final verification failed"; exit 1; }
echo ""

echo "=========================================="
echo "✅ Pipeline completed successfully!"
echo "=========================================="
echo ""
echo "Reports available in: $PROJECT_ROOT/reports/"
echo "Logs available in: $PROJECT_ROOT/logs/"
echo "Patches available in: $PROJECT_ROOT/patches/"
echo ""
