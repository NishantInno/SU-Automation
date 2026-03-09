# Quick Start Guide

Get the Automated Security Update tool running in 5 minutes.

## Prerequisites Check

```bash
# Verify required tools
python3 --version  # Should be 3.8+
drush --version    # Should be 11+ or 12+
composer --version # Should be 2.x
git --version      # Should be 2.x
```

## Installation (3 steps)

### 1. Clone and Setup

```bash
cd /var/www/html
git clone <repository-url> automated-security-update
cd automated-security-update
pip3 install -r requirements.txt
```

### 2. Configure

```bash
# Copy configuration files
cp .env.example .env
cp config/config.example.yaml config/config.yaml

# Edit .env with your settings
nano .env
```

**Minimum required in `.env`**:
```bash
DRUPAL_ROOT=/var/www/html/drupal
SITE_URL=http://localhost
OPENAI_API_KEY=your-key-here  # Optional, for AI fixes
```

### 3. Create Directories

```bash
mkdir -p logs reports patches
chmod +x scripts/*.sh
```

## First Run

### Test Site Analysis

```bash
./scripts/run_analysis.sh
```

**Expected output**: `reports/site-analysis.json`

### Check for Updates

```bash
./scripts/run_version_check.sh
```

**Expected output**: `reports/module-updates.json`

### Run Tests

```bash
./scripts/run_tests.sh
```

**Expected output**: `reports/testing-results.json`

## Dry Run (Safe Testing)

```bash
export DRY_RUN=true
./scripts/run_full_pipeline.sh
```

This runs all stages without making changes.

## Apply Updates (For Real)

```bash
./scripts/run_updates.sh
```

**Warning**: This will modify your Drupal site. Backup first!

## View Reports

```bash
# Open HTML report in browser
xdg-open reports/security-report.html

# Or view JSON
cat reports/site-analysis.json | jq
```

## Jenkins Setup (Optional)

### Quick Jenkins Setup

```bash
# Using Docker
docker-compose up -d jenkins

# Access Jenkins
open http://localhost:8080

# Create pipeline job pointing to jenkins/Jenkinsfile
```

## Common Commands

```bash
# Full pipeline
make run-pipeline

# Individual stages
make run-analysis
make run-updates
make run-tests

# Deploy to dev
make deploy-dev

# Clean up
make clean
```

## Troubleshooting

### "Drush not found"
```bash
# Install Drush globally
composer global require drush/drush
export PATH="$HOME/.composer/vendor/bin:$PATH"
```

### "Permission denied"
```bash
chmod +x scripts/*.sh
chmod 755 logs reports patches
```

### "Configuration error"
```bash
# Verify configuration
python3 -c "from core.config import load_config; load_config()"
```

## Next Steps

1. ✅ Review generated reports in `reports/`
2. ✅ Configure Jenkins for automation
3. ✅ Set up email notifications
4. ✅ Schedule weekly runs
5. ✅ Read full documentation in `USAGE.md`

## Getting Help

- **Documentation**: See `README.md`, `INSTALLATION.md`, `USAGE.md`
- **Examples**: Check `examples/` directory
- **Issues**: Create a GitHub issue
- **Architecture**: See `ARCHITECTURE.md`

## Safety Reminders

- ✅ Always backup before updates
- ✅ Test in dev before production
- ✅ Use dry-run mode first
- ✅ Review AI-generated patches
- ✅ Never skip testing stage
- ✅ Production requires manual approval

---

**You're ready!** Start with a dry run to familiarize yourself with the tool.
