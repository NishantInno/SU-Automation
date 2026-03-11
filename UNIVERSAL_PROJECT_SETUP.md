# Universal Project Setup Guide
## Use This Automation for ANY Drupal Project

This guide shows how to use the **same automation** for **any Drupal project** with automatic branch isolation and code backup.

---

## 🎯 Key Concept

**One automation repo → Many Drupal projects**

You don't need to copy this repo into each project. Just point it at different projects using Jenkins parameters.

---

## ✨ What Happens Automatically

### First Run (Any New Project)
1. ✅ Creates `suautomation` branch from current branch
2. ✅ Pushes branch to remote
3. ✅ Creates code backup at `{project}_code_bkp`
4. ✅ Runs security updates
5. ✅ Commits changes to `suautomation` branch
6. ✅ Main branch stays untouched

### Subsequent Runs
1. ✅ Checks out existing `suautomation` branch
2. ✅ Skips backup (already done)
3. ✅ Runs security updates
4. ✅ Commits changes to `suautomation` branch
5. ✅ Main branch stays untouched

---

## 🚀 Quick Setup for Any Project

### Example 1: Project "testauto"

**Jenkins Job Parameters**:
```
ENVIRONMENT: local
DRY_RUN: false
DRUPAL_ROOT: /var/www/html/testauto/web
SITE_URL: https://testauto.ddev.site:8443
PROJECT_PATH: /var/www/html/testauto
AUTOMATION_BRANCH: suautomation
EMAIL_RECIPIENT: your-email@example.com
```

**Result**:
- Branch created: `suautomation` in `/var/www/html/testauto`
- Backup created: `/var/www/html/testauto_code_bkp`
- All changes committed to `suautomation` branch

---

### Example 2: Project "juvdev"

**Jenkins Job Parameters**:
```
ENVIRONMENT: local
DRY_RUN: false
DRUPAL_ROOT: /var/www/html/juvdev/web
SITE_URL: https://juvdev.ddev.site:8443
PROJECT_PATH: /var/www/html/juvdev
AUTOMATION_BRANCH: suautomation
EMAIL_RECIPIENT: your-email@example.com
```

**Result**:
- Branch created: `suautomation` in `/var/www/html/juvdev`
- Backup created: `/var/www/html/juvdev_code_bkp`
- All changes committed to `suautomation` branch

---

### Example 3: Project "mysite" (Production)

**Jenkins Job Parameters**:
```
ENVIRONMENT: prod
DRY_RUN: false
DRUPAL_ROOT: /var/www/html/mysite/web
SITE_URL: https://www.mysite.com
PROJECT_PATH: /var/www/html/mysite
AUTOMATION_BRANCH: security-updates
EMAIL_RECIPIENT: devops@mysite.com
```

**Result**:
- Branch created: `security-updates` in `/var/www/html/mysite`
- Backup created: `/var/www/html/mysite_code_bkp`
- All changes committed to `security-updates` branch

---

## 📋 Step-by-Step for New Project

### Step 1: Verify Project Setup

```bash
# Check project exists
ls -la /var/www/html/{your-project}

# Verify DDEV is running
cd /var/www/html/{your-project}
ddev describe

# Check git repository
git status
git remote -v
```

### Step 2: Create Jenkins Job

1. Go to: `http://localhost:8081`
2. Click **New Item**
3. Name: `Automated-Security-Update-{ProjectName}`
4. Type: **Pipeline**
5. Click **OK**

### Step 3: Configure Pipeline

1. Scroll to **Pipeline** section
2. **Definition**: `Pipeline script from SCM`
3. **SCM**: `Git`
4. **Repository URL**: `https://github.com/NishantInno/SU-Automation.git`
5. **Branch**: `*/main`
6. **Script Path**: `jenkins/Jenkinsfile`
7. Click **Save**

### Step 4: Run Build with Parameters

1. Click **Build with Parameters**
2. Fill in your project details:
   - **ENVIRONMENT**: Choose environment
   - **DRY_RUN**: ✅ for first test
   - **DRUPAL_ROOT**: `/var/www/html/{project}/web`
   - **SITE_URL**: Your site URL
   - **PROJECT_PATH**: `/var/www/html/{project}`
   - **AUTOMATION_BRANCH**: `suautomation` (or custom name)
   - **EMAIL_RECIPIENT**: Your email
3. Click **Build**

### Step 5: Verify First Run

```bash
cd /var/www/html/{your-project}

# Check branch was created
git branch -a
# Should show: suautomation

# Check current branch
git rev-parse --abbrev-ref HEAD
# Should output: suautomation

# Check backup was created
ls -la /var/www/html/{your-project}_code_bkp
cat /var/www/html/{your-project}_code_bkp/BACKUP_INFO.txt
```

---

## 🌿 Git Workflow

### Branch Structure (Same for All Projects)

```
{project} (repository)
├── main (or master)           ← Other developers work here
│   └── (untouched by automation)
│
└── suautomation               ← Automation branch
    └── (all automation changes go here)
```

### Merging to Main (When Ready)

```bash
cd /var/www/html/{your-project}

# Switch to main
git checkout main

# Pull latest
git pull origin main

# Merge automation branch
git merge suautomation

# Resolve conflicts if any
# ...

# Push to main
git push origin main
```

Or create a **Pull Request** for team review.

---

## 📊 Multiple Projects Example

### Scenario: Managing 5 Projects

| Project | Path | Site URL | Branch | Backup |
|---------|------|----------|--------|--------|
| testauto | `/var/www/html/testauto` | `https://testauto.ddev.site:8443` | `suautomation` | `/var/www/html/testauto_code_bkp` |
| juvdev | `/var/www/html/juvdev` | `https://juvdev.ddev.site:8443` | `suautomation` | `/var/www/html/juvdev_code_bkp` |
| client1 | `/var/www/html/client1` | `https://client1.com` | `auto-updates` | `/var/www/html/client1_code_bkp` |
| client2 | `/var/www/html/client2` | `https://client2.com` | `security-patches` | `/var/www/html/client2_code_bkp` |
| internal | `/var/www/html/internal` | `https://internal.company.com` | `suautomation` | `/var/www/html/internal_code_bkp` |

**One automation repo, 5 Jenkins jobs, 5 projects managed!**

---

## 🎯 Parameters Reference

### Required Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| `DRUPAL_ROOT` | Absolute path to Drupal web root | `/var/www/html/mysite/web` |
| `SITE_URL` | Full site URL with protocol | `https://mysite.ddev.site:8443` |
| `PROJECT_PATH` | Path to DDEV project root (has `.ddev` folder) | `/var/www/html/mysite` |

### Optional Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `ENVIRONMENT` | `local` | Environment: local, dev, qc, prod |
| `DRY_RUN` | `false` | Test mode (no actual changes) |
| `SKIP_AI_FIX` | `true` | Skip AI-powered fixes |
| `AUTOMATION_BRANCH` | `suautomation` | Git branch for automation |
| `EMAIL_RECIPIENT` | `smtptest@innoppl.com` | Email for notifications |

---

## 🔧 Customization Per Project

### Different Branch Names

**Project A**: Use `auto-updates`
```
AUTOMATION_BRANCH: auto-updates
```

**Project B**: Use `security-patches`
```
AUTOMATION_BRANCH: security-patches
```

**Project C**: Use `jenkins-updates`
```
AUTOMATION_BRANCH: jenkins-updates
```

### Different Backup Locations

The backup is automatically named: `{PROJECT_PATH}_code_bkp`

Examples:
- `/var/www/html/testauto` → `/var/www/html/testauto_code_bkp`
- `/var/www/html/juvdev` → `/var/www/html/juvdev_code_bkp`
- `/home/user/mysite` → `/home/user/mysite_code_bkp`

---

## 📁 File Structure

### Automation Repo (One Copy)

```
/var/lib/jenkins/workspace/Automated-Security-Update/
├── core/                      # Python modules (universal)
├── jenkins/
│   └── Jenkinsfile            # Universal pipeline
├── scripts/
│   └── setup_project_branch.sh  # Branch setup (universal)
├── reports/                   # Generated per build
└── logs/                      # Execution logs
```

### Project 1: testauto

```
/var/www/html/testauto/
├── .ddev/                     # DDEV config
├── web/                       # Drupal root
│   ├── core/
│   ├── modules/
│   └── sites/
├── vendor/
└── .git/
    └── refs/heads/
        ├── main
        └── suautomation       # Automation branch

/var/www/html/testauto_code_bkp/  # Backup (first run only)
```

### Project 2: juvdev

```
/var/www/html/juvdev/
├── .ddev/                     # DDEV config
├── web/                       # Drupal root
│   ├── core/
│   ├── modules/
│   └── sites/
├── vendor/
└── .git/
    └── refs/heads/
        ├── main
        └── suautomation       # Automation branch

/var/www/html/juvdev_code_bkp/    # Backup (first run only)
```

---

## 🐛 Troubleshooting

### Issue: "Branch already exists" on First Run

**Cause**: Branch was created manually or in previous test

**Solution**:
```bash
cd /var/www/html/{project}

# Delete local branch
git branch -D suautomation

# Delete remote branch
git push origin --delete suautomation

# Run pipeline again
```

### Issue: Different Project Paths

**Symptom**: Pipeline fails with "directory not found"

**Solution**: Ensure `PROJECT_PATH` parameter matches actual project location:
```bash
# Find your project
ls -la /var/www/html/

# Use exact path in Jenkins parameter
PROJECT_PATH: /var/www/html/{exact-folder-name}
```

### Issue: DDEV Not Found

**Symptom**: "ddev: command not found"

**Solution**: Ensure DDEV is running for the project:
```bash
cd /var/www/html/{project}
ddev start
ddev describe
```

### Issue: Permission Denied on Backup

**Symptom**: "Permission denied" when creating backup

**Solution**:
```bash
# Ensure Jenkins user has write access
sudo chown -R jenkins:jenkins /var/www/html/

# Or create backup directory manually
sudo mkdir /var/www/html/{project}_code_bkp
sudo chown jenkins:jenkins /var/www/html/{project}_code_bkp
```

---

## 📧 Email Notifications

Every build sends an email with:

**Subject**: `✅ Automated Security Update - SUCCESS - {ProjectName} - Build #{number}`

**Body**: HTML report with:
- Before/After comparison
- Security metrics
- Update results
- Menu testing results

**Attachments**:
- `before-analysis.json`
- `after-analysis.json`
- `update-results.json`
- `testing-results.json`
- `menu-check.json`

---

## 🔐 Security Best Practices

### 1. Branch Isolation
- ✅ Main branch never touched
- ✅ All changes in dedicated automation branch
- ✅ Review before merging to main

### 2. Code Backup
- ✅ Full backup before first run
- ✅ Stored locally for quick recovery
- ✅ Metadata tracked (commit hash, date, user)

### 3. Testing
- ✅ DRY_RUN mode for testing
- ✅ Automated tests run before commit
- ✅ Email notifications on failure

### 4. Multi-Environment
- ✅ Test in `local` first
- ✅ Then `dev`, `qc`
- ✅ Finally `prod` with approval

---

## 📚 Related Documentation

- `NEW_USER_COMPLETE_SETUP_GUIDE.md` - Complete setup from scratch
- `JUVDEV_SETUP_GUIDE.md` - JUVDEV-specific example
- `PLAYWRIGHT_MENU_TESTING.md` - Menu testing details
- `JENKINS_COMPLETE_EMAIL_SETUP.md` - Email configuration
- `JENKINS_FLOW.md` - Pipeline visualization

---

## ✅ Summary

### One Automation Repo Works for All Projects

**Same Code**:
- ✅ Same Jenkinsfile
- ✅ Same Python modules
- ✅ Same branch setup script
- ✅ Same email templates

**Different Parameters**:
- ✅ Different `PROJECT_PATH`
- ✅ Different `DRUPAL_ROOT`
- ✅ Different `SITE_URL`
- ✅ Different `AUTOMATION_BRANCH` (optional)

**Result**:
- ✅ Each project gets its own automation branch
- ✅ Each project gets its own code backup
- ✅ Main branches stay clean
- ✅ Safe for team environments

**No need to copy automation code into each project!** 🎉

---

## 🎯 Quick Reference Card

```bash
# For ANY new project:

1. Verify project exists and DDEV is running
   cd /var/www/html/{project}
   ddev describe

2. Create Jenkins job
   Name: Automated-Security-Update-{ProjectName}
   Type: Pipeline
   SCM: https://github.com/NishantInno/SU-Automation.git
   Script Path: jenkins/Jenkinsfile

3. Build with parameters:
   DRUPAL_ROOT: /var/www/html/{project}/web
   SITE_URL: https://{project}.ddev.site:8443
   PROJECT_PATH: /var/www/html/{project}
   AUTOMATION_BRANCH: suautomation

4. First run creates:
   - Branch: suautomation
   - Backup: /var/www/html/{project}_code_bkp

5. Subsequent runs:
   - Use existing branch
   - Skip backup
   - Commit changes

Done! 🚀
```
