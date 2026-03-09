# Usage Guide

## Quick Start

### Run Full Pipeline

```bash
cd /var/www/html/automated-security-update
./scripts/run_full_pipeline.sh
```

This executes all 9 stages sequentially.

### Dry Run Mode

Test without making changes:

```bash
export DRY_RUN=true
./scripts/run_full_pipeline.sh
```

## Individual Stages

### Stage 1: Site Analysis

Analyze your Drupal site and collect comprehensive information.

```bash
./scripts/run_analysis.sh
```

**Output**: `reports/site-analysis.json`

**What it does**:
- Checks Drupal, PHP, and database versions
- Lists all enabled modules
- Identifies custom modules
- Scans for security vulnerabilities
- Checks configuration sync status
- Retrieves recent watchdog logs

**Example output**:
```json
{
  "timestamp": "2024-03-09T10:30:00Z",
  "drupal_root": "/var/www/html/drupal",
  "summary": {
    "drupal_core_version": "10.2.0",
    "php_version": "8.2.0",
    "database_version": "MySQL 8.0.35",
    "enabled_module_count": 87,
    "custom_module_count": 5
  },
  "security_vulnerabilities": [],
  "enabled_modules": [...]
}
```

### Stage 2: Version Check

Check for available module updates.

```bash
./scripts/run_version_check.sh
```

**Output**: `reports/module-updates.json`

**What it does**:
- Runs `composer outdated drupal/*`
- Checks `drush pm:security`
- Queries Drupal.org release history
- Identifies security updates

**Example output**:
```json
{
  "timestamp": "2024-03-09T10:31:00Z",
  "modules": [
    {
      "module_name": "webform",
      "installed_version": "6.2.0",
      "latest_version": "6.2.1",
      "security_update_required": true
    }
  ],
  "security_modules": ["webform"]
}
```

### Stage 3: Apply Updates

Apply security and regular updates.

```bash
./scripts/run_updates.sh
```

**Output**: `reports/update-results.json`

**What it does**:
- Updates modules via Composer
- Runs database updates (`drush updb`)
- Rebuilds cache (`drush cr`)
- Imports configuration (`drush cim`)

**Interactive mode**: Prompts for confirmation before applying updates.

**Non-interactive mode**:
```bash
export DRY_RUN=false
yes | ./scripts/run_updates.sh
```

### Stage 4: Run Tests

Execute automated tests.

```bash
./scripts/run_tests.sh
```

**Output**: `reports/testing-results.json`

**What it does**:
- HTTP status code checks for critical pages
- Headless browser testing (if enabled)
- Watchdog error analysis
- Entity schema update checks
- Configuration sync verification

**Example output**:
```json
{
  "timestamp": "2024-03-09T10:35:00Z",
  "summary": {
    "http_errors": 0,
    "watchdog_errors": 2
  },
  "http_checks": [
    {
      "url": "http://localhost/",
      "status_code": "200"
    }
  ]
}
```

### Stage 5: Generate Report

Create HTML and JSON reports.

```bash
python3 core/report_engine.py
```

**Output**: `reports/security-report.html`

**What it does**:
- Aggregates all stage results
- Generates human-readable HTML report
- Creates deployment summary

**View report**:
```bash
# Open in browser
xdg-open reports/security-report.html

# Or serve via Python
python3 -m http.server 8000 --directory reports
# Visit http://localhost:8000/security-report.html
```

### Stage 6: AI-Assisted Fixing

Use AI to propose fixes for detected errors.

```bash
python3 core/ai_fix_engine.py
```

**Requirements**: `OPENAI_API_KEY` environment variable

**Output**: 
- `patches/*.patch`
- `reports/ai-fix-results.json`

**What it does**:
- Detects errors from testing results
- Extracts error context
- Queries OpenAI GPT-4 for fixes
- Generates patch files
- Applies patches automatically

**Skip AI fixing**:
```bash
export SKIP_AI_FIX=true
./scripts/run_full_pipeline.sh
```

### Stage 7: Deployment

Deploy to target environment.

```bash
./scripts/deploy.sh <environment>
```

**Environments**: `local`, `dev`, `qc`, `prod`

**Examples**:
```bash
# Deploy to development
./scripts/deploy.sh dev

# Deploy to QC
./scripts/deploy.sh qc

# Deploy to production (requires confirmation)
./scripts/deploy.sh prod
```

**What it does**:
- Validates deployment readiness
- Creates backup (if enabled)
- Deploys code changes
- Runs post-deployment tasks
- Verifies deployment success

## Jenkins Pipeline

### Trigger Build

#### Via Jenkins UI

1. Navigate to job: `http://jenkins.example.com/job/Automated-Security-Update/`
2. Click "Build with Parameters"
3. Select options:
   - **ENVIRONMENT**: Target environment
   - **DRY_RUN**: Test mode
   - **SKIP_AI_FIX**: Skip AI fixing
4. Click "Build"

#### Via Jenkins CLI

```bash
java -jar jenkins-cli.jar -s http://jenkins.example.com/ \
  build Automated-Security-Update \
  -p ENVIRONMENT=dev \
  -p DRY_RUN=false
```

#### Via API

```bash
curl -X POST "http://jenkins.example.com/job/Automated-Security-Update/buildWithParameters" \
  --user admin:token \
  --data "ENVIRONMENT=dev&DRY_RUN=false"
```

### View Results

1. **Console Output**: Real-time build logs
2. **Security Report**: Published HTML report
3. **Artifacts**: JSON reports, logs, patches

### Schedule Automated Runs

Configure in Jenkins job:

```
# Daily at 2 AM
H 2 * * *

# Weekly on Monday at 2 AM
H 2 * * 1

# First day of month at 3 AM
H 3 1 * *
```

## Common Workflows

### Weekly Security Maintenance

```bash
#!/bin/bash
# weekly-maintenance.sh

export ENVIRONMENT=dev
export DRY_RUN=false
export SKIP_AI_FIX=false

cd /var/www/html/automated-security-update

# Run full pipeline
./scripts/run_full_pipeline.sh

# Email report
mail -s "Weekly Security Update Report" admin@example.com < reports/security-report.html
```

Schedule with cron:
```bash
0 2 * * 1 /path/to/weekly-maintenance.sh
```

### Emergency Security Patch

```bash
#!/bin/bash
# emergency-patch.sh

# 1. Analyze site
./scripts/run_analysis.sh

# 2. Check for security updates
./scripts/run_version_check.sh

# 3. Review updates
cat reports/module-updates.json | jq '.security_modules'

# 4. Apply updates
./scripts/run_updates.sh

# 5. Test
./scripts/run_tests.sh

# 6. Deploy to dev
./scripts/deploy.sh dev

# 7. If successful, deploy to prod
read -p "Deploy to production? (yes/no) " -r
if [[ $REPLY == "yes" ]]; then
  ./scripts/deploy.sh prod
fi
```

### Pre-Deployment Check

```bash
#!/bin/bash
# pre-deployment-check.sh

# Run analysis and tests only
./scripts/run_analysis.sh
./scripts/run_tests.sh

# Check results
python3 -c "
import json
from pathlib import Path

testing = json.loads(Path('reports/testing-results.json').read_text())
summary = testing.get('summary', {})

if summary.get('http_errors', 0) > 0 or summary.get('watchdog_errors', 0) > 0:
    print('❌ Site has errors - NOT ready for deployment')
    exit(1)
else:
    print('✅ Site is healthy - ready for deployment')
"
```

### Module-Specific Update

```bash
#!/bin/bash
# update-specific-module.sh

MODULE_NAME="webform"

cd $DRUPAL_ROOT

# Update specific module
composer update drupal/$MODULE_NAME --with-dependencies

# Run database updates
drush updb -y

# Clear cache
drush cr

# Test
cd /var/www/html/automated-security-update
./scripts/run_tests.sh
```

## Environment Variables

### Core Variables

```bash
# Drupal
DRUPAL_ROOT=/var/www/html/drupal
SITE_URL=http://localhost

# Binaries
DRUSH_BIN=drush
COMPOSER_BIN=composer
GIT_BIN=git
CURL_BIN=curl

# AI
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4

# Behavior
DRY_RUN=false
SKIP_AI_FIX=false
FAIL_ON_TEST_ERRORS=true
HEADLESS_ENABLED=false
VERIFY_SSL=true

# Performance
COMMAND_TIMEOUT=900
```

### Override in Scripts

```bash
# Temporary override
SITE_URL=https://dev.example.com ./scripts/run_tests.sh

# Multiple overrides
DRY_RUN=true SKIP_AI_FIX=true ./scripts/run_full_pipeline.sh
```

## Interpreting Results

### Site Analysis Report

**Key metrics**:
- `enabled_module_count`: Total enabled modules
- `custom_module_count`: Custom modules (not from drupal.org)
- `security_vulnerabilities`: Array of vulnerable modules

**Action items**:
- If `security_vulnerabilities` is not empty → Apply updates immediately
- If `custom_module_count` is high → Review custom code regularly

### Module Updates Report

**Key fields**:
- `security_update_required: true` → Critical, apply ASAP
- `installed_version` vs `latest_version` → Update available

**Priority**:
1. Security updates (highest priority)
2. Bug fix updates
3. Feature updates (lowest priority)

### Testing Results Report

**HTTP checks**:
- `200`: Success
- `301/302`: Redirect (usually OK)
- `404`: Page not found (investigate)
- `500`: Server error (critical)

**Watchdog errors**:
- `error`, `critical`, `alert`, `emergency`: Investigate immediately
- `warning`: Review and address
- `notice`, `info`: Informational

### AI Fix Results

**Fields**:
- `applied: true` → Patch applied successfully
- `applied: false` → Manual intervention required
- `failed: true` → AI couldn't generate fix

**Next steps**:
- Review generated patches in `patches/`
- Test thoroughly after AI fixes
- Commit successful patches to version control

## Best Practices

### 1. Always Test First

```bash
# Test in dev before production
./scripts/deploy.sh dev
# Verify, then:
./scripts/deploy.sh qc
# Verify, then:
./scripts/deploy.sh prod
```

### 2. Use Dry Run for Exploration

```bash
export DRY_RUN=true
./scripts/run_full_pipeline.sh
# Review reports, then run for real
```

### 3. Review Before Applying

```bash
# Check what will be updated
./scripts/run_version_check.sh
cat reports/module-updates.json | jq '.security_modules'

# Then apply
./scripts/run_updates.sh
```

### 4. Monitor Logs

```bash
# Watch logs in real-time
tail -f logs/*.log

# Check for errors
grep ERROR logs/*.log
```

### 5. Backup Before Major Updates

```bash
# Manual backup
drush sql:dump > backup-$(date +%Y%m%d).sql
tar -czf files-backup-$(date +%Y%m%d).tar.gz sites/default/files

# Then update
./scripts/run_updates.sh
```

### 6. Version Control Everything

```bash
# Commit before updates
git add -A
git commit -m "Pre-update snapshot"

# Apply updates
./scripts/run_updates.sh

# Commit changes
git add -A
git commit -m "Applied security updates"
```

## Troubleshooting

### Pipeline Fails at Update Stage

```bash
# Check Composer logs
cat logs/*update*.log

# Try manual update
cd $DRUPAL_ROOT
composer update drupal/* --dry-run

# Check for conflicts
composer why-not drupal/module_name version
```

### Tests Fail After Update

```bash
# Check specific errors
cat reports/testing-results.json | jq '.watchdog'

# Run Drupal status
drush status

# Check for pending updates
drush updatedb:status
```

### AI Fix Fails

```bash
# Verify API key
echo $OPENAI_API_KEY

# Check quota
curl https://api.openai.com/v1/usage \
  -H "Authorization: Bearer $OPENAI_API_KEY"

# Skip AI and fix manually
export SKIP_AI_FIX=true
```

### Deployment Fails

```bash
# Check SSH connectivity
ssh user@target-server

# Verify permissions
ls -la $DRUPAL_ROOT

# Check disk space
df -h
```

## Getting Help

1. **Check logs**: `logs/*.log`
2. **Review reports**: `reports/*.json`
3. **Enable debug mode**: `export LOG_LEVEL=DEBUG`
4. **Consult documentation**: `ARCHITECTURE.md`, `INSTALLATION.md`
5. **Check Drupal status**: `drush status`
