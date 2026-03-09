# Installation Guide

## Prerequisites

### System Requirements

- **Operating System**: Linux (Ubuntu 20.04+, Debian 10+, CentOS 8+, RHEL 8+)
- **Python**: 3.8 or higher
- **PHP**: 8.1+ (for Drupal 10/11) or 7.4+ (for Drupal 9)
- **Composer**: 2.x
- **Drush**: 11+ or 12+
- **Git**: 2.x
- **Jenkins**: 2.x (for CI/CD pipeline)

### Drupal Requirements

- Drupal 9, 10, or 11
- Composer-based installation
- Drush installed and configured
- Git repository for version control

### Optional Requirements

- **Playwright**: For headless browser testing
- **OpenAI API Key**: For AI-assisted error fixing

## Installation Steps

### 1. Clone the Repository

```bash
cd /var/www/html
git clone <repository-url> automated-security-update
cd automated-security-update
```

### 2. Install Python Dependencies

```bash
# Using pip
pip3 install -r requirements.txt

# Or using virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
# Copy example configuration files
cp .env.example .env
cp config/config.example.yaml config/config.yaml

# Edit .env with your settings
nano .env
```

#### Required Environment Variables

```bash
# Drupal Configuration
DRUPAL_ROOT=/var/www/html/drupal
SITE_URL=http://localhost

# Binary Paths (adjust if needed)
DRUSH_BIN=drush
COMPOSER_BIN=composer
GIT_BIN=git
CURL_BIN=curl

# OpenAI Configuration (for AI-assisted fixing)
OPENAI_API_KEY=your-api-key-here
OPENAI_MODEL=gpt-4

# Testing Configuration
HEADLESS_ENABLED=false
FAIL_ON_TEST_ERRORS=true

# Security
VERIFY_SSL=true

# Performance
COMMAND_TIMEOUT=900
```

### 4. Create Required Directories

```bash
mkdir -p logs reports patches
chmod 755 logs reports patches
```

### 5. Make Scripts Executable

```bash
chmod +x scripts/*.sh
```

### 6. Verify Installation

```bash
# Test Python imports
python3 -c "from core.config import load_config; print('✅ Configuration loaded successfully')"

# Test Drush
drush --version

# Test Composer
composer --version

# Test site access
./scripts/run_analysis.sh
```

## Jenkins Setup

### 1. Install Jenkins Plugins

Required plugins:
- Pipeline
- Git
- Email Extension
- HTML Publisher
- Credentials Binding

```bash
# Install via Jenkins CLI
java -jar jenkins-cli.jar -s http://localhost:8080/ install-plugin pipeline git email-ext htmlpublisher credentials-binding
```

### 2. Create Jenkins Job

1. Open Jenkins web interface
2. Click "New Item"
3. Enter job name: "Automated-Security-Update"
4. Select "Pipeline"
5. Click "OK"

### 3. Configure Pipeline

1. In "Pipeline" section:
   - Definition: "Pipeline script from SCM"
   - SCM: Git
   - Repository URL: `<your-repo-url>`
   - Script Path: `jenkins/Jenkinsfile`

2. In "Build Triggers":
   - ✅ Poll SCM: `H 2 * * *` (daily at 2 AM)
   - ✅ Build periodically: `H 2 * * 1` (weekly on Monday)

3. In "Parameters":
   - Add parameters as defined in Jenkinsfile

### 4. Configure Credentials

1. Go to Jenkins → Credentials
2. Add credentials:
   - **OpenAI API Key**: Secret text
   - **SSH Keys**: SSH Username with private key (for deployments)
   - **Email**: Username with password (for notifications)

### 5. Test Pipeline

```bash
# Trigger a test build
curl -X POST http://localhost:8080/job/Automated-Security-Update/build \
  --user admin:token \
  --data-urlencode json='{"parameter": [{"name":"DRY_RUN", "value":"true"}]}'
```

## Configuration

### Basic Configuration

Edit `config/config.yaml`:

```yaml
drupal:
  site_path: "/var/www/html/drupal"
  site_url: "http://localhost"
  drush_path: "drush"
  composer_path: "composer"

environments:
  local:
    url: "http://localhost"
  dev:
    url: "https://dev.example.com"
    ssh_host: "dev-server.example.com"
  qc:
    url: "https://qc.example.com"
    ssh_host: "qc-server.example.com"
  prod:
    url: "https://www.example.com"
    ssh_host: "prod-server.example.com"
    requires_approval: true

ai:
  provider: "openai"
  model: "gpt-4"
  enabled: true

testing:
  critical_pages:
    - "/"
    - "/admin"
    - "/node"
  fail_on_errors: true
```

### Advanced Configuration

#### Custom Critical Pages

Add pages specific to your site:

```yaml
testing:
  critical_pages:
    - "/"
    - "/admin"
    - "/admin/content"
    - "/user/login"
    - "/products"
    - "/checkout"
    - "/api/status"
```

#### Module Exclusions

Exclude specific modules from updates:

```yaml
updates:
  exclude_modules:
    - "custom_module_1"
    - "patched_module_2"
```

#### Email Notifications

```yaml
notifications:
  email_enabled: true
  email_to: "admin@example.com"
  email_from: "noreply@example.com"
  smtp_host: "smtp.gmail.com"
  smtp_port: 587
```

## Optional Components

### Headless Browser Testing

Install Playwright for JavaScript testing:

```bash
pip install playwright
playwright install chromium
```

Enable in `.env`:

```bash
HEADLESS_ENABLED=true
```

### Slack Notifications

Configure Slack webhook:

```yaml
notifications:
  slack_enabled: true
  slack_webhook_url: "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
```

## Troubleshooting

### Common Issues

#### Issue: "Drush not found"

```bash
# Check Drush installation
which drush

# If not found, install globally
composer global require drush/drush

# Or specify full path in .env
DRUSH_BIN=/path/to/drush
```

#### Issue: "Permission denied"

```bash
# Fix script permissions
chmod +x scripts/*.sh

# Fix directory permissions
chmod 755 logs reports patches
```

#### Issue: "OpenAI API error"

```bash
# Verify API key
echo $OPENAI_API_KEY

# Test API connection
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

#### Issue: "Composer timeout"

```bash
# Increase timeout in .env
COMMAND_TIMEOUT=1800

# Or configure Composer
composer config --global process-timeout 1800
```

### Debug Mode

Enable verbose logging:

```bash
export LOG_LEVEL=DEBUG
./scripts/run_full_pipeline.sh
```

Check logs:

```bash
tail -f logs/*.log
```

## Verification

### Test Individual Stages

```bash
# Stage 1: Site Analysis
./scripts/run_analysis.sh

# Stage 2: Version Check
./scripts/run_version_check.sh

# Stage 3: Testing
./scripts/run_tests.sh
```

### Dry Run

Test without making changes:

```bash
export DRY_RUN=true
./scripts/run_full_pipeline.sh
```

### Full Pipeline

Run complete pipeline:

```bash
./scripts/run_full_pipeline.sh
```

## Security Hardening

### 1. Protect Sensitive Files

```bash
chmod 600 .env
chmod 600 config/config.yaml
```

### 2. Use Environment-Specific Credentials

Never commit credentials to Git:

```bash
# Add to .gitignore
echo ".env" >> .gitignore
echo "config/config.yaml" >> .gitignore
echo "*.log" >> .gitignore
```

### 3. Restrict Jenkins Access

- Enable authentication
- Use role-based access control
- Limit production deployment permissions

### 4. Secure API Keys

Use Jenkins credentials binding:

```groovy
environment {
  OPENAI_API_KEY = credentials('openai-api-key')
}
```

## Maintenance

### Log Rotation

Configure logrotate:

```bash
sudo nano /etc/logrotate.d/automated-security-update
```

```
/var/www/html/automated-security-update/logs/*.log {
    daily
    rotate 90
    compress
    delaycompress
    notifempty
    create 0644 www-data www-data
}
```

### Report Cleanup

Add cron job:

```bash
crontab -e
```

```
# Clean old reports (keep 30 days)
0 3 * * * find /var/www/html/automated-security-update/reports -mtime +30 -delete
```

### Update Tool

Keep the tool updated:

```bash
cd /var/www/html/automated-security-update
git pull origin main
pip install -r requirements.txt --upgrade
```

## Next Steps

1. ✅ Complete installation
2. ✅ Configure environment
3. ✅ Test individual stages
4. ✅ Run dry-run pipeline
5. ✅ Configure Jenkins
6. ✅ Set up notifications
7. ✅ Schedule automated runs
8. ✅ Monitor first production run

## Support

For issues and questions:
- Check logs in `logs/`
- Review reports in `reports/`
- Consult `ARCHITECTURE.md` for system details
- Review `README.md` for usage examples
