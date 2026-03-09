# Standalone Installation Guide

## Install as a Separate Tool

This guide shows you how to install **Automated Security Update** as a standalone command-line tool that you can use to check any Drupal website's health.

---

## Installation Options

### Option 1: Local Installation (Recommended)

Installs to your home directory (`~/.local/share/`):

```bash
cd /var/www/html/testauto/automated-security-update
./install.sh
```

**What it does**:
- Installs to: `~/.local/share/automated-security-update`
- Creates command: `~/.local/bin/drupal-security-check`
- No root/sudo required
- Only available to your user

**Add to PATH** (if needed):
```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

### Option 2: System-Wide Installation

Installs for all users (requires sudo):

```bash
cd /var/www/html/testauto/automated-security-update
sudo ./install.sh --system
```

**What it does**:
- Installs to: `/opt/automated-security-update`
- Creates command: `/usr/local/bin/drupal-security-check`
- Available to all users
- Requires root privileges

---

## After Installation

### Configure Your First Site

Run the interactive setup:

```bash
drupal-security-check install
```

You'll be asked:
- **Drupal root path**: `/var/www/html/drupal`
- **Site URL**: `http://localhost`

This creates the configuration file.

---

## Using the Tool

### Quick Health Check

```bash
# Analyze any Drupal site
drupal-security-check analyze /var/www/html/drupal

# Check for security updates
drupal-security-check check /var/www/html/drupal

# Run health tests
drupal-security-check test /var/www/html/drupal

# Online security verification (no AI)
drupal-security-check verify /var/www/html/drupal
```

### Full Security Audit

```bash
# Complete pipeline (safe mode - no changes)
drupal-security-check full /var/www/html/drupal --dry-run

# View reports
cat ~/.local/share/automated-security-update/reports/security-report.html
```

### Apply Updates

```bash
# Interactive update (asks for confirmation)
drupal-security-check update /var/www/html/drupal
```

---

## Command Reference

### Available Commands

```bash
drupal-security-check analyze [PATH]    # Analyze Drupal site
drupal-security-check check [PATH]      # Check for updates
drupal-security-check test [PATH]       # Run health tests
drupal-security-check verify [PATH]     # Security verification
drupal-security-check update [PATH]     # Apply updates
drupal-security-check report [PATH]     # Generate report
drupal-security-check full [PATH]       # Complete pipeline

drupal-security-check install          # Setup wizard
drupal-security-check config            # Show configuration
drupal-security-check version           # Show version
drupal-security-check help              # Show help
```

### Options

```bash
--dry-run           # Run without making changes
--site-url URL      # Override site URL
--skip-tests        # Skip testing stage
```

---

## Use Cases

### 1. Check Multiple Sites

```bash
# Site 1
drupal-security-check analyze /var/www/site1

# Site 2
drupal-security-check analyze /var/www/site2

# Site 3
drupal-security-check analyze /var/www/site3
```

### 2. Weekly Security Audit

```bash
# Add to crontab
crontab -e

# Weekly check (Monday 2 AM)
0 2 * * 1 drupal-security-check full /var/www/html/drupal --dry-run
```

### 3. Pre-Deployment Check

```bash
# Before deploying
drupal-security-check test /var/www/html/drupal

# Check exit code
if [ $? -eq 0 ]; then
    echo "✓ Site healthy - safe to deploy"
else
    echo "✗ Issues found - check reports"
fi
```

### 4. Quick Health Status

```bash
# One-liner health check
drupal-security-check analyze /var/www/html/drupal && \
drupal-security-check verify /var/www/html/drupal && \
echo "✓ Site is healthy"
```

---

## Reports Location

### Local Installation
```
~/.local/share/automated-security-update/reports/
├── site-analysis.json
├── module-updates.json
├── testing-results.json
├── online-verification.json
└── security-report.html
```

### System Installation
```
/opt/automated-security-update/reports/
├── site-analysis.json
├── module-updates.json
├── testing-results.json
├── online-verification.json
└── security-report.html
```

---

## Configuration

### View Current Config

```bash
drupal-security-check config
```

### Edit Configuration

**Local installation**:
```bash
nano ~/.local/share/automated-security-update/.env
```

**System installation**:
```bash
sudo nano /opt/automated-security-update/.env
```

### Configuration Options

```bash
DRUPAL_ROOT=/var/www/html/drupal     # Drupal path
SITE_URL=http://localhost             # Site URL
DRY_RUN=true                          # Safe mode
USE_ONLINE_VERIFICATION=true          # No AI needed
CHECK_DRUPAL_ORG=true                 # Security checks
```

---

## Examples

### Example 1: Daily Health Check Script

```bash
#!/bin/bash
# daily-health-check.sh

SITE_PATH="/var/www/html/drupal"

echo "Running daily health check..."

# Analyze site
drupal-security-check analyze "$SITE_PATH"

# Check for updates
drupal-security-check check "$SITE_PATH"

# Verify security
drupal-security-check verify "$SITE_PATH"

# Generate report
drupal-security-check report "$SITE_PATH"

echo "Reports available in: ~/.local/share/automated-security-update/reports/"
```

### Example 2: Multiple Site Monitor

```bash
#!/bin/bash
# monitor-all-sites.sh

SITES=(
    "/var/www/site1"
    "/var/www/site2"
    "/var/www/site3"
)

for site in "${SITES[@]}"; do
    echo "Checking: $site"
    drupal-security-check analyze "$site"
    drupal-security-check verify "$site"
    echo "---"
done
```

### Example 3: Pre-Update Validation

```bash
#!/bin/bash
# pre-update-check.sh

SITE_PATH="/var/www/html/drupal"

# Run full check
drupal-security-check full "$SITE_PATH" --dry-run

# Check if passed
if [ $? -eq 0 ]; then
    echo "✓ All checks passed"
    echo "Safe to apply updates"
    
    read -p "Apply updates now? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        drupal-security-check update "$SITE_PATH"
    fi
else
    echo "✗ Issues found - review reports before updating"
fi
```

---

## Integration with Other Tools

### Use with Git Hooks

```bash
# .git/hooks/pre-commit
#!/bin/bash

drupal-security-check test /var/www/html/drupal

if [ $? -ne 0 ]; then
    echo "Health check failed - commit aborted"
    exit 1
fi
```

### Use with CI/CD

```yaml
# .gitlab-ci.yml
security_check:
  script:
    - drupal-security-check full /var/www/html/drupal --dry-run
  artifacts:
    paths:
      - reports/
```

---

## Uninstallation

### Local Installation

```bash
rm -rf ~/.local/share/automated-security-update
rm ~/.local/bin/drupal-security-check
```

### System Installation

```bash
sudo rm -rf /opt/automated-security-update
sudo rm /usr/local/bin/drupal-security-check
```

---

## Troubleshooting

### Command not found

**Local installation**:
```bash
# Add to PATH
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

**System installation**:
```bash
# Check if installed
ls -la /usr/local/bin/drupal-security-check
```

### Permission denied

```bash
# Make executable
chmod +x ~/.local/bin/drupal-security-check
```

### Configuration not found

```bash
# Run setup wizard
drupal-security-check install
```

---

## Advantages of Standalone Installation

✅ **Use anywhere** - Check any Drupal site  
✅ **Simple command** - `drupal-security-check analyze /path/to/site`  
✅ **Multiple sites** - Monitor many sites easily  
✅ **Automation** - Easy to script and schedule  
✅ **No AI needed** - Free online verification  
✅ **Portable** - Works on any Linux system  

---

## Quick Reference Card

```bash
# Installation
./install.sh                    # Local install
sudo ./install.sh --system      # System install

# Setup
drupal-security-check install   # Configure

# Daily Use
drupal-security-check analyze /path/to/drupal
drupal-security-check check /path/to/drupal
drupal-security-check verify /path/to/drupal

# Full Audit
drupal-security-check full /path/to/drupal --dry-run

# Apply Updates
drupal-security-check update /path/to/drupal

# Help
drupal-security-check help
```

---

**Install now and start checking your Drupal sites!** 🚀
