# Easiest Way to Connect Jenkins - 3 Steps

## Step 1: Install Jenkins (Choose One Method)

### Method A: Docker (Easiest - Recommended)

```bash
cd /var/www/html/testauto/automated-security-update
docker-compose up -d jenkins
```

**That's it!** Jenkins is now running.

### Method B: Native Installation

```bash
# Install Jenkins
sudo apt update
sudo apt install jenkins -y

# Start Jenkins
sudo systemctl start jenkins
sudo systemctl enable jenkins
```

---

## Step 2: Access Jenkins and Get Password

### Open Jenkins in Browser

```
http://localhost:8080
```

### Get Initial Password

**For Docker:**
```bash
docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword
```

**For Native:**
```bash
sudo cat /var/lib/jenkins/secrets/initialAdminPassword
```

Copy the password and paste it in the browser.

---

## Step 3: Quick Setup

### 3.1 Install Plugins
- Click **"Install suggested plugins"**
- Wait 2-3 minutes for installation

### 3.2 Create Admin User
- Username: `admin`
- Password: `admin123` (or your choice)
- Full name: `Admin`
- Email: `admin@localhost`
- Click **"Save and Continue"**

### 3.3 Jenkins URL
- Keep default: `http://localhost:8080/`
- Click **"Save and Finish"**
- Click **"Start using Jenkins"**

---

## Step 4: Create Your Pipeline Job (2 Minutes)

### 4.1 Create New Job

1. Click **"New Item"** (top left)
2. Enter name: `Automated-Security-Update`
3. Select **"Pipeline"**
4. Click **"OK"**

### 4.2 Configure Pipeline

Scroll down to **"Pipeline"** section:

**Definition**: Select `Pipeline script from SCM`

**SCM**: Select `Git`

**Repository URL**: 
```
git@github.com:NishantInno/SU-Automation.git
```

**Branch**: `*/main`

**Script Path**: `jenkins/Jenkinsfile`

Click **"Save"**

---

## Step 5: Run Your First Build

### 5.1 Build with Parameters

1. Click **"Build with Parameters"** (left sidebar)
2. You'll see:
   - **ENVIRONMENT**: Select `local`
   - **DRY_RUN**: Check ✅ (safe mode)
   - **SKIP_AI_FIX**: Check ✅
   - **FORCE_DEPLOY**: Leave unchecked
3. Click **"Build"**

### 5.2 Watch the Pipeline

You'll see the pipeline running with stages:

```
┌──────┬──────┬──────┬──────┬──────┐
│Setup │Analyze│Check│Test │Report│
│ ✅   │ 🔵   │ ⏳  │ ⏳  │ ⏳   │
└──────┴──────┴──────┴──────┴──────┘
```

- ✅ Green = Completed
- 🔵 Blue = Running
- ⏳ Gray = Waiting

### 5.3 View Results

After build completes:
1. Click on build number (e.g., **#1**)
2. Click **"Console Output"** to see logs
3. Click **"Artifacts"** to download reports

---

## That's It! ✅

Your Jenkins is now connected and running the pipeline!

---

## Quick Reference

### Start Jenkins
```bash
# Docker
docker-compose up -d jenkins

# Native
sudo systemctl start jenkins
```

### Access Jenkins
```
http://localhost:8080
```

### Stop Jenkins
```bash
# Docker
docker-compose stop jenkins

# Native
sudo systemctl stop jenkins
```

### View Logs
```bash
# Docker
docker logs jenkins -f

# Native
sudo journalctl -u jenkins -f
```

---

## Troubleshooting

### Can't Access http://localhost:8080

**Check if Jenkins is running:**
```bash
# Docker
docker ps | grep jenkins

# Native
sudo systemctl status jenkins
```

**If not running, start it:**
```bash
# Docker
docker-compose up -d jenkins

# Native
sudo systemctl start jenkins
```

### Port 8080 Already in Use

**Change port in docker-compose.yml:**
```yaml
ports:
  - "8081:8080"  # Use 8081 instead
```

Then access: `http://localhost:8081`

### Git Authentication Failed

**Use HTTPS instead:**

In Jenkins job configuration, change repository URL to:
```
https://github.com/NishantInno/SU-Automation.git
```

---

## Visual Guide

### What You'll See

**1. Jenkins Dashboard**
```
┌─────────────────────────────────────┐
│ Welcome to Jenkins!                 │
│                                     │
│ [New Item]  [Manage Jenkins]       │
│                                     │
│ Jobs:                               │
│ • Automated-Security-Update         │
└─────────────────────────────────────┘
```

**2. Build with Parameters**
```
┌─────────────────────────────────────┐
│ Build with Parameters               │
│                                     │
│ ENVIRONMENT:     [local ▼]         │
│ DRY_RUN:         [✓]               │
│ SKIP_AI_FIX:     [✓]               │
│ FORCE_DEPLOY:    [ ]               │
│                                     │
│           [Build]                   │
└─────────────────────────────────────┘
```

**3. Pipeline Running**
```
┌─────────────────────────────────────┐
│ Build #1                            │
│ ────────────────────────────────    │
│                                     │
│ Setup      ✅ 10s                   │
│ Analyze    ✅ 30s                   │
│ Check      🔵 Running...            │
│ Test       ⏳ Pending               │
│ Report     ⏳ Pending               │
│                                     │
│ Console Output | Artifacts          │
└─────────────────────────────────────┘
```

---

## Next Steps

### Enable Blue Ocean (Modern UI)

1. Go to **"Manage Jenkins"** → **"Manage Plugins"**
2. Click **"Available"** tab
3. Search for **"Blue Ocean"**
4. Check the box and click **"Install without restart"**
5. Access at: `http://localhost:8080/blue`

### Schedule Automatic Builds

1. Go to job → **"Configure"**
2. Check **"Build periodically"**
3. Schedule: `0 2 * * 1` (Every Monday at 2 AM)
4. Click **"Save"**

### Email Notifications

1. Go to **"Manage Jenkins"** → **"Configure System"**
2. Scroll to **"E-mail Notification"**
3. Configure SMTP settings
4. Test configuration

---

## Summary

**3 Easy Steps:**

1. **Install**: `docker-compose up -d jenkins` or `sudo apt install jenkins`
2. **Access**: Open `http://localhost:8080` and complete setup wizard
3. **Create Job**: New Item → Pipeline → Point to GitHub repo
4. **Run**: Build with Parameters → Watch it work!

**Total Time**: 5-10 minutes

**Your pipeline is now connected to Jenkins!** 🚀
