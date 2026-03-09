.PHONY: help install test lint clean run-analysis run-updates run-tests deploy-dev deploy-qc

help:
	@echo "Automated Security Update - Makefile Commands"
	@echo ""
	@echo "Setup:"
	@echo "  make install          Install Python dependencies"
	@echo "  make setup            Complete setup (install + configure)"
	@echo ""
	@echo "Execution:"
	@echo "  make run-analysis     Run site analysis"
	@echo "  make run-updates      Apply security updates"
	@echo "  make run-tests        Run automated tests"
	@echo "  make run-pipeline     Run full pipeline"
	@echo ""
	@echo "Deployment:"
	@echo "  make deploy-dev       Deploy to development"
	@echo "  make deploy-qc        Deploy to QC"
	@echo "  make deploy-prod      Deploy to production (requires confirmation)"
	@echo ""
	@echo "Development:"
	@echo "  make test             Run unit tests"
	@echo "  make lint             Run linters"
	@echo "  make format           Format code"
	@echo "  make clean            Clean generated files"
	@echo ""

install:
	pip3 install -r requirements.txt

setup: install
	mkdir -p logs reports patches
	chmod +x scripts/*.sh
	@if [ ! -f .env ]; then cp .env.example .env; echo "Created .env - please configure"; fi
	@if [ ! -f config/config.yaml ]; then cp config/config.example.yaml config/config.yaml; echo "Created config.yaml - please configure"; fi

run-analysis:
	./scripts/run_analysis.sh

run-updates:
	./scripts/run_updates.sh

run-tests:
	./scripts/run_tests.sh

run-pipeline:
	./scripts/run_full_pipeline.sh

deploy-dev:
	./scripts/deploy.sh dev

deploy-qc:
	./scripts/deploy.sh qc

deploy-prod:
	./scripts/deploy.sh prod

test:
	pytest tests/ -v

lint:
	flake8 core/
	mypy core/
	shellcheck scripts/*.sh

format:
	black core/
	isort core/

clean:
	rm -rf __pycache__ core/__pycache__
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -f logs/*.log
	rm -f reports/*.json reports/*.html
	rm -f patches/*.patch
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

dry-run:
	DRY_RUN=true ./scripts/run_full_pipeline.sh

check-config:
	@echo "Checking configuration..."
	@python3 -c "from core.config import load_config; config = load_config(); print('✅ Configuration valid')"

verify:
	@echo "Verifying installation..."
	@which python3 || echo "❌ Python 3 not found"
	@which drush || echo "❌ Drush not found"
	@which composer || echo "❌ Composer not found"
	@which git || echo "❌ Git not found"
	@python3 -c "from core.config import load_config; print('✅ Python modules OK')"
	@echo "✅ Verification complete"
