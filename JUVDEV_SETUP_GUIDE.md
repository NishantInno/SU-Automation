# JUVDEV Project Setup Guide
## Automated Security Updates with Branch Isolation

This guide explains how to set up automated security updates for the **JUVDEV** project with a dedicated automation branch.

---

## 🎯 Overview

### Key Features

1. **Branch Isolation** - All automation changes go to `suautomation` branch
2. **First-Time Setup** - Automatic branch creation and code backup on first run
3. **Safe Updates** - Main branch remains untouched, no conflicts with other developers
4. **Complete Backup** - Full code backup created locally for safety
5. **Automated Workflow** - Jenkins handles everything automatically

---

## 📋 Prerequisites

Before starting, ensure:

- ✅ JUVDEV project is cloned at `/var/www/html/juvdev`
- ✅ DDEV is set up and running (`ddev start`)
- ✅ Jenkins is installed and configured
- ✅ This automation repo is cloned and accessible
- ✅ SMTP credentials are configured in Jenkins

---

## 🚀 Quick Start

### Step 1: Verify JUVDEV Project

```bash
# Check project exists
ls -la /var/www/html/juvdev

# Verify DDEV is running
cd /var/www/html/juvdev
ddev describe

# Check current branch
git branch
```

### Step 2: Create Jenkins Job for JUVDEV

1. **Go to Jenkins**: `http://localhost:8081`
2. Click **New Item**
3. **Name**: `Automated-Security-Update-JUVDEV`
4. **Type**: Pipeline
5. Click **OK**

### Step 3: Configure Pipeline

1. Scroll to **Pipeline** section
2. **Definition**: `Pipeline script from SCM`
3. **SCM**: `Git`
4. **Repository URL**: `https://github.com/NishantInno/SU-Automation.git`
5. **Branch**: `*/main`
6. **Script Path**: `jenkins/Jenkinsfile-juvdev`
7. Click **Save**

### Step 4: Run First Build

1. Click **Build with Parameters**
2. Verify parameters:
   - **ENVIRONMENT**: `local`
   - **DRY_RUN**: ✅ (Check for first test)
   - **SKIP_AI_FIX**: ✅ (Check)
   - **DRUPAL_ROOT**: `/var/www/html/juvdev/web`
   - **SITE_URL**: `https://juvdev.ddev.site:8443`
   - **EMAIL_RECIPIENT**: `your-email@example.com`
   - **PROJECT_PATH**: `/var/www/html/juvdev`
   - **AUTOMATION_BRANCH**: `suautomation`
3. Click **Build**

---

## 🔧 What Happens on First Run

### Stage: Setup Project Branch

The pipeline automatically:

1. **Checks if `suautomation` branch exists**
   - If NO (first run):
     - Creates new branch `suautomation` from current branch
     - Pushes branch to remote
     - Creates code backup at `/var/www/html/juvdev_code_bkp`
     - Logs backup metadata
   - If YES (subsequent runs):
     - Checks out existing `suautomation` branch
     - Skips backup (already done)

### Code Backup Details

**Location**: `/var/www/html/juvdev_code_bkp`

**Contents**:
- Complete project code (excluding `.git`, `node_modules`, `vendor`)
- `BACKUP_INFO.txt` with metadata:
  - Creation date
  - Source path
  - Branch name
  - Git commit hash
  - User and hostname

**Exclusions** (to save space):
- `.git/` directory
- `node_modules/`
- `vendor/`
- `sites/default/files/`
- `*.sql` and `*.sql.gz` files

---

## 📊 Pipeline Stages

### 1. Initialize
- Creates workspace directories
- Installs Python dependencies
- Installs Playwright browsers

### 2. Setup Project Branch ⭐ NEW
- Creates `suautomation` branch (first run only)
- Creates code backup (first run only)
- Checks out to automation branch

### 3. BEFORE Analysis
- Captures site state before updates
- Generates `before-analysis.json`

### 4. Version Check
- Checks for available security updates
- Lists outdated modules

### 5. Apply Security Updates
- Runs Composer updates (if DRY_RUN=false)
- Updates Drupal core and modules

### 6. Database Updates
- Runs `drush updb` (if DRY_RUN=false)
- Clears cache

### 7. AFTER Analysis
- Captures site state after updates
- Generates `after-analysis.json`

### 8. Automated Testing
- HTTP status checks
- Playwright menu testing
- Watchdog error checks
- Generates `testing-results.json` and `menu-check.json`

### 9. Generate Report
- Creates comprehensive update report

### 10. Commit Changes to Automation Branch ⭐ NEW
- Commits all changes to `suautomation` branch
- Pushes to remote
- Main branch remains untouched

### 11. Generate Email HTML
- Creates beautiful HTML email report
- Includes before/after comparison
- Attaches JSON reports

---

## 🌿 Git Workflow

### Branch Structure

```
juvdev (repository)
├── main (or master)           ← Other developers work here
│   └── (untouched by automation)
│
└── suautomation               ← Automation branch
    └── (all automation changes go here)
```

### First Run Flow

```
1. Pipeline starts
2. Detects no 'suautomation' branch exists
3. Creates 'suautomation' from current branch
4. Pushes 'suautomation' to remote
5. Creates code backup at /var/www/html/juvdev_code_bkp
6. Runs updates
7. Commits changes to 'suautomation'
8. Pushes 'suautomation' to remote
```

### Subsequent Runs Flow

```
1. Pipeline starts
2. Detects 'suautomation' branch exists
3. Checks out 'suautomation'
4. Skips backup (already done)
5. Runs updates
6. Commits changes to 'suautomation'
7. Pushes 'suautomation' to remote
```

### Merging Changes to Main

When you're ready to merge automation changes to main:

```bash
cd /var/www/html/juvdev

# Switch to main branch
git checkout main

# Pull latest changes
git pull origin main

# Merge automation branch
git merge suautomation

# Resolve any conflicts if needed
# ...

# Push to main
git push origin main
```

Or create a **Pull Request** on GitHub/GitLab for review.

---

## 📁 File Locations

### JUVDEV Project

```
/var/www/html/juvdev/
├── .ddev/                     # DDEV configuration
├── web/                       # Drupal root
│   ├── core/
│   ├── modules/
│   ├── themes/
│   └── sites/
├── vendor/                    # Composer dependencies
├── composer.json
└── .git/                      # Git repository
```

### Code Backup (First Run Only)

```
/var/www/html/juvdev_code_bkp/
├── web/                       # Drupal code backup
├── composer.json
├── composer.lock
├── BACKUP_INFO.txt            # Backup metadata
└── (all project files)
```

### Automation Repo

```
/var/lib/jenkins/workspace/Automated-Security-Update-JUVDEV/
├── core/                      # Python modules
├── jenkins/
│   └── Jenkinsfile-juvdev     # JUVDEV-specific pipeline
├── scripts/
│   └── setup_project_branch.sh  # Branch setup script
├── reports/                   # Generated reports
└── logs/                      # Execution logs
```

---

## 🔍 Verification

### Check Branch Setup

```bash
cd /var/www/html/juvdev

# List all branches
git branch -a

# Should show:
# * suautomation
#   main
#   remotes/origin/suautomation
#   remotes/origin/main

# Check current branch
git rev-parse --abbrev-ref HEAD
# Should output: suautomation
```

### Check Code Backup

```bash
# Verify backup exists
ls -la /var/www/html/juvdev_code_bkp

# View backup info
cat /var/www/html/juvdev_code_bkp/BACKUP_INFO.txt

# Check backup size
du -sh /var/www/html/juvdev_code_bkp
```

### Check Jenkins Build

1. Go to: `http://localhost:8081/job/Automated-Security-Update-JUVDEV/`
2. Click latest build number
3. Click **Console Output**
4. Look for:
   ```
   ✅ Created and switched to branch 'suautomation'
   ✅ Branch 'suautomation' pushed to remote
   ✅ Code backup created successfully
   ```

---

## 🛠️ Customization

### Change Branch Name

To use a different branch name (e.g., `auto-updates`):

1. In Jenkins job parameters, change:
   - **AUTOMATION_BRANCH**: `auto-updates`
2. Or edit `Jenkinsfile-juvdev` line 43:
   ```groovy
   defaultValue: 'auto-updates',
   ```

### Change Backup Location

Edit `scripts/setup_project_branch.sh` line 3:

```bash
BACKUP_SUFFIX="${3:-_my_custom_backup}"
```

Or pass as parameter in Jenkinsfile stage:

```groovy
bash scripts/setup_project_branch.sh \
  "${params.PROJECT_PATH}" \
  "${params.AUTOMATION_BRANCH}" \
  "_my_custom_backup"
```

### Exclude More Files from Backup

Edit `scripts/setup_project_branch.sh` lines 60-66:

```bash
rsync -av \
    --exclude='.git' \
    --exclude='node_modules' \
    --exclude='vendor' \
    --exclude='sites/default/files' \
    --exclude='*.sql' \
    --exclude='*.sql.gz' \
    --exclude='custom_large_dir' \  # Add your exclusions
    "$PROJECT_PATH/" "$BACKUP_DIR/"
```

---

## 🐛 Troubleshooting

### Issue 1: "Branch already exists" on First Run

**Symptom**: Pipeline says branch exists but you expected first-time setup

**Cause**: Branch was created manually or in a previous test

**Solution**:
```bash
cd /var/www/html/juvdev

# Delete local branch
git branch -D suautomation

# Delete remote branch
git push origin --delete suautomation

# Run pipeline again
```

### Issue 2: Backup Directory Already Exists

**Symptom**: "Backup directory already exists" message

**Cause**: Backup was created in a previous run

**Solution**:
```bash
# Remove old backup
rm -rf /var/www/html/juvdev_code_bkp

# Run pipeline again
```

### Issue 3: Permission Denied on Backup Creation

**Symptom**: "Permission denied" when creating backup

**Solution**:
```bash
# Ensure Jenkins user has write access
sudo chown -R jenkins:jenkins /var/www/html/

# Or run as current user
sudo -u jenkins bash scripts/setup_project_branch.sh /var/www/html/juvdev suautomation
```

### Issue 4: Git Push Failed

**Symptom**: "Failed to push branch to remote"

**Cause**: No remote configured or authentication issue

**Solution**:
```bash
cd /var/www/html/juvdev

# Check remote
git remote -v

# Add remote if missing
git remote add origin <repository-url>

# Configure credentials
git config credential.helper store
```

### Issue 5: Changes Not Committed

**Symptom**: "No changes to commit" but files were modified

**Cause**: Files may be in `.gitignore`

**Solution**:
```bash
cd /var/www/html/juvdev

# Check git status
git status

# Check what's ignored
git status --ignored

# Force add if needed
git add -f <file>
```

---

## 📧 Email Notifications

After each build, you'll receive an email with:

- ✅ **Subject**: Success/Failure/Unstable status
- 📊 **Body**: HTML report with before/after comparison
- 📎 **Attachments**: 
  - `before-analysis.json`
  - `after-analysis.json`
  - `update-results.json`
  - `testing-results.json`
  - `menu-check.json`

---

## 🔐 Security Notes

1. **Branch Isolation**: Main branch is never modified by automation
2. **Code Backup**: Full backup created before any changes
3. **Review Before Merge**: Always review `suautomation` branch before merging to main
4. **Test Environment**: Run in `local` or `dev` first before `prod`
5. **Email Alerts**: Immediate notification of any failures

---

## 📚 Related Documentation

- `NEW_USER_COMPLETE_SETUP_GUIDE.md` - Complete setup from scratch
- `JENKINS_COMPLETE_EMAIL_SETUP.md` - Email configuration
- `PLAYWRIGHT_MENU_TESTING.md` - Menu testing details
- `JENKINS_FLOW.md` - Pipeline visualization

---

## ✅ Summary

**What's Different for JUVDEV**:
- ✅ Dedicated `Jenkinsfile-juvdev` pipeline
- ✅ Automatic `suautomation` branch creation
- ✅ Code backup on first run
- ✅ All changes isolated from main branch
- ✅ Safe for multi-developer environments

**First Run**:
- Creates `suautomation` branch
- Creates `/var/www/html/juvdev_code_bkp` backup
- Runs updates and commits to `suautomation`

**Subsequent Runs**:
- Uses existing `suautomation` branch
- Skips backup
- Commits changes to `suautomation`

**Your main branch stays clean!** 🎉
