# 🛠️ Install as Standalone Tool - Quick Guide

## One-Command Installation

```bash
cd /var/www/html/testauto/automated-security-update
./install.sh
```

That's it! The tool is now installed as `drupal-security-check`.

---

## What Gets Installed

✅ **Command**: `drupal-security-check`  
✅ **Location**: `~/.local/bin/` (local) or `/usr/local/bin/` (system)  
✅ **Files**: `~/.local/share/automated-security-update/`  
✅ **Reports**: Auto-generated in installation directory  

---

## First Time Setup

After installation, configure your site:

```bash
drupal-security-check install
```

Enter:
- Drupal root: `/var/www/html/testauto/web`
- Site URL: `http://localhost`

---

## Use It Right Away

### Check Website Health

```bash
drupal-security-check analyze /var/www/html/testauto/web
```

**Output**:
```
✓ Drupal 11.2.6 detected
✓ PHP 8.3.30
✓ 87 modules enabled
✓ No security vulnerabilities
Report: ~/.local/share/automated-security-update/reports/site-analysis.json
```

### Check for Security Updates

```bash
drupal-security-check check /var/www/html/testauto/web
```

### Run Security Verification (No AI)

```bash
drupal-security-check verify /var/www/html/testauto/web
```

### Full Health Audit

```bash
drupal-security-check full /var/www/html/testauto/web --dry-run
```

---

## Real-World Usage

### Monitor Multiple Sites

```bash
# Check all your Drupal sites
drupal-security-check analyze /var/www/site1
drupal-security-check analyze /var/www/site2
drupal-security-check analyze /var/www/site3
```

### Automated Daily Checks

```bash
# Add to crontab
crontab -e

# Daily at 2 AM
0 2 * * * drupal-security-check full /var/www/html/drupal --dry-run
```

### Pre-Deployment Validation

```bash
# Before deploying changes
drupal-security-check test /var/www/html/drupal

if [ $? -eq 0 ]; then
    echo "✓ Safe to deploy"
    git push
fi
```

---

## All Available Commands

```bash
drupal-security-check analyze [PATH]    # Site analysis
drupal-security-check check [PATH]      # Update check
drupal-security-check test [PATH]       # Health tests
drupal-security-check verify [PATH]     # Security verification
drupal-security-check update [PATH]     # Apply updates
drupal-security-check full [PATH]       # Complete audit

drupal-security-check help              # Show help
drupal-security-check version           # Show version
drupal-security-check config            # Show config
```

---

## Installation Types

### Local (Default)
```bash
./install.sh
```
- Installs to: `~/.local/share/automated-security-update`
- Command: `~/.local/bin/drupal-security-check`
- No sudo needed
- Only for your user

### System-Wide
```bash
sudo ./install.sh --system
```
- Installs to: `/opt/automated-security-update`
- Command: `/usr/local/bin/drupal-security-check`
- Requires sudo
- Available to all users

---

## Why Install as Standalone Tool?

✅ **Easy to use** - Simple command: `drupal-security-check analyze /path`  
✅ **Works anywhere** - Check any Drupal site on your system  
✅ **Multiple sites** - Monitor many sites easily  
✅ **Scriptable** - Easy to automate  
✅ **No AI needed** - Free online verification  
✅ **Portable** - Copy to other servers  

---

## Quick Start Example

```bash
# 1. Install
cd /var/www/html/testauto/automated-security-update
./install.sh

# 2. Setup
drupal-security-check install
# Enter: /var/www/html/testauto/web
# Enter: http://localhost

# 3. Check health
drupal-security-check analyze /var/www/html/testauto/web

# 4. View report
cat ~/.local/share/automated-security-update/reports/site-analysis.json
```

---

## View Reports

```bash
# List all reports
ls -lh ~/.local/share/automated-security-update/reports/

# View security report
cat ~/.local/share/automated-security-update/reports/online-verification.json

# Open HTML report
xdg-open ~/.local/share/automated-security-update/reports/security-report.html
```

---

## Uninstall

```bash
# Local installation
rm -rf ~/.local/share/automated-security-update
rm ~/.local/bin/drupal-security-check

# System installation
sudo rm -rf /opt/automated-security-update
sudo rm /usr/local/bin/drupal-security-check
```

---

## Get Help

```bash
drupal-security-check help
```

---

**Install now and start checking your Drupal sites!** 🚀

```bash
./install.sh
```
