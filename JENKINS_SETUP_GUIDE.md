# Jenkins Setup and Visualization Guide

## Quick Jenkins Setup

### Option 1: Docker Installation (Recommended)

```bash
# Install docker-compose if not installed
sudo apt install docker-compose

# Start Jenkins
cd /var/www/html/testauto/automated-security-update
docker-compose up -d jenkins

# Access Jenkins
open http://localhost:8080
```

### Option 2: Native Installation

```bash
# Add Jenkins repository
wget -q -O - https://pkg.jenkins.io/debian-stable/jenkins.io.key | sudo apt-key add -
sudo sh -c 'echo deb https://pkg.jenkins.io/debian-stable binary/ > /etc/apt/sources.list.d/jenkins.list'

# Install Jenkins
sudo apt update
sudo apt install jenkins

# Start Jenkins
sudo systemctl start jenkins
sudo systemctl enable jenkins

# Access Jenkins
open http://localhost:8080
```

---

## Initial Jenkins Configuration

### 1. Get Initial Admin Password

```bash
# For Docker installation
docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword

# For native installation
sudo cat /var/lib/jenkins/secrets/initialAdminPassword
```

### 2. Access Jenkins

Open browser: `http://localhost:8080`

Enter the initial admin password.

### 3. Install Suggested Plugins

Click "Install suggested plugins" and wait for installation to complete.

### 4. Create Admin User

- Username: `admin`
- Password: (your choice)
- Full name: `Admin`
- Email: `admin@localhost`

---

## Create Pipeline Job

### Step 1: New Item

1. Click "New Item" in Jenkins dashboard
2. Enter name: `Automated-Security-Update`
3. Select "Pipeline"
4. Click "OK"

### Step 2: Configure Pipeline

#### General Settings

- ✅ Check "This project is parameterized"
- Add parameters:

**Parameter 1: ENVIRONMENT**
- Type: Choice Parameter
- Name: `ENVIRONMENT`
- Choices (one per line):
  ```
  local
  dev
  qc
  prod
  ```
- Description: `Target deployment environment`

**Parameter 2: DRY_RUN**
- Type: Boolean Parameter
- Name: `DRY_RUN`
- Default: `true`
- Description: `Run without making changes (safe mode)`

**Parameter 3: SKIP_AI_FIX**
- Type: Boolean Parameter
- Name: `SKIP_AI_FIX`
- Default: `true`
- Description: `Skip AI-assisted fixing (uses online verification)`

**Parameter 4: FORCE_DEPLOY**
- Type: Boolean Parameter
- Name: `FORCE_DEPLOY`
- Default: `false`
- Description: `Force deployment even with warnings`

#### Pipeline Definition

- Definition: `Pipeline script from SCM`
- SCM: `Git`
- Repository URL: `git@github.com:NishantInno/SU-Automation.git`
- Branch: `*/main`
- Script Path: `jenkins/Jenkinsfile`

### Step 3: Save Configuration

Click "Save" at the bottom.

---

## Viewing Pipeline Flow

### Classic View

Access: `http://localhost:8080/job/Automated-Security-Update/`

Shows:
- Build history
- Stage view
- Console output
- Artifacts

### Blue Ocean View (Modern UI)

Install Blue Ocean plugin:
1. Manage Jenkins → Manage Plugins
2. Available tab → Search "Blue Ocean"
3. Install without restart

Access: `http://localhost:8080/blue/organizations/jenkins/Automated-Security-Update/activity`

Features:
- ✅ Visual pipeline flow
- ✅ Stage-by-stage progress
- ✅ Real-time logs
- ✅ Branch visualization
- ✅ Artifact browser

---

## Pipeline Visualization in Jenkins

### Stage View

When you run the pipeline, you'll see:

```
┌──────────────┬──────────────┬──────────────┬──────────────┐
│ Environment  │ Site         │ Version      │ Apply        │
│ Setup        │ Analysis     │ Check        │ Updates      │
│              │              │              │              │
│ ✅ 10s       │ ✅ 30s       │ ✅ 45s       │ ⏭️ SKIPPED   │
└──────────────┴──────────────┴──────────────┴──────────────┘

┌──────────────┬──────────────┬──────────────┬──────────────┐
│ Automated    │ Generate     │ Online       │ Re-verify    │
│ Testing      │ Report       │ Verification │              │
│              │              │              │              │
│ ✅ 1m        │ ✅ 15s       │ ✅ 10s       │ ⏭️ SKIPPED   │
└──────────────┴──────────────┴──────────────┴──────────────┘

┌──────────────┬──────────────┐
│ Deployment   │ Final        │
│              │ Verification │
│              │              │
│ ⏭️ SKIPPED   │ ✅ 30s       │
└──────────────┴──────────────┘
```

### Color Coding

- 🟢 **Green**: Stage completed successfully
- 🔵 **Blue**: Stage is running
- 🔴 **Red**: Stage failed
- ⚪ **Gray**: Stage skipped
- 🟡 **Yellow**: Stage unstable (warnings)

---

## Running the Pipeline

### Method 1: Jenkins UI

1. Go to `http://localhost:8080/job/Automated-Security-Update/`
2. Click "Build with Parameters"
3. Select parameters:
   - ENVIRONMENT: `local`
   - DRY_RUN: `true` (safe mode)
   - SKIP_AI_FIX: `true`
   - FORCE_DEPLOY: `false`
4. Click "Build"

### Method 2: Jenkins CLI

```bash
# Download Jenkins CLI
wget http://localhost:8080/jnlpJars/jenkins-cli.jar

# Run build
java -jar jenkins-cli.jar -s http://localhost:8080/ build Automated-Security-Update \
  -p ENVIRONMENT=local \
  -p DRY_RUN=true \
  -p SKIP_AI_FIX=true \
  -p FORCE_DEPLOY=false
```

### Method 3: API Call

```bash
curl -X POST http://localhost:8080/job/Automated-Security-Update/buildWithParameters \
  --user admin:your-api-token \
  --data ENVIRONMENT=local \
  --data DRY_RUN=true \
  --data SKIP_AI_FIX=true \
  --data FORCE_DEPLOY=false
```

---

## Viewing Build Results

### Console Output

1. Click on build number (e.g., #1, #2)
2. Click "Console Output"
3. See real-time logs

### Stage Logs

1. Click on build number
2. Click "Pipeline Steps"
3. Click on any stage to see its logs

### Reports

1. Click on build number
2. Click "Artifacts"
3. Download reports:
   - `site-analysis.json`
   - `module-updates.json`
   - `testing-results.json`
   - `online-verification.json`
   - `security-report.html`

### HTML Report

1. Install "HTML Publisher" plugin
2. Reports appear in build page
3. Click "Security Report" to view

---

## Pipeline Flow Visualization

### Real-Time Progress

When pipeline runs, you see:

```
Stage 1: Environment Setup ✅
  ├─ Load environment variables ✅
  ├─ Validate Drupal root ✅
  ├─ Check Drush ✅
  └─ Create directories ✅

Stage 2: Site Analysis 🔵 (Running...)
  ├─ Run drush status ✅
  ├─ Collect modules ⏳
  ├─ Check security ⏳
  └─ Fetch logs ⏳

Stage 3: Version Check ⏳ (Pending)
Stage 4: Apply Updates ⏳ (Pending)
...
```

### Completed Pipeline

```
✅ Environment Setup (10s)
✅ Site Analysis (30s)
✅ Version Check (45s)
⏭️ Apply Updates (SKIPPED - DRY_RUN)
✅ Automated Testing (1m)
✅ Generate Report (15s)
✅ Online Verification (10s)
⏭️ Re-verification (SKIPPED)
⏭️ Deployment (SKIPPED - DRY_RUN)
✅ Final Verification (30s)

Total Duration: 3m 20s
Status: SUCCESS ✅
```

---

## Dashboard Widgets

### Add Build Status Widget

1. Go to Jenkins dashboard
2. Click "+" to add view
3. Select "List View"
4. Add "Automated-Security-Update" job
5. Configure columns:
   - Status
   - Weather (trend)
   - Name
   - Last Success
   - Last Failure
   - Last Duration

### Build Trend Graph

Shows:
- Success/failure rate over time
- Average build duration
- Stage performance trends

---

## Email Notifications

### Configure Email

1. Manage Jenkins → Configure System
2. Scroll to "E-mail Notification"
3. Configure SMTP:
   - SMTP server: `smtp.gmail.com`
   - Use SSL: `true`
   - Port: `465`
   - Username: `your-email@gmail.com`
   - Password: `app-password`

### Test Email

Click "Test configuration" to verify.

### Email Content

Emails include:
- Build status (SUCCESS/FAILURE)
- Stage results
- Error summary
- Links to reports
- Console output excerpt

---

## Monitoring and Alerts

### Build Monitors

Install "Build Monitor Plugin":
1. Manage Jenkins → Manage Plugins
2. Search "Build Monitor"
3. Install

Create monitor view:
1. New View → Build Monitor View
2. Add "Automated-Security-Update"
3. Full-screen dashboard showing build status

### Slack Integration

Install "Slack Notification Plugin":
1. Get Slack webhook URL
2. Configure in Jenkins
3. Add to Jenkinsfile:
```groovy
slackSend(
    color: 'good',
    message: "Security update completed successfully"
)
```

---

## Scheduled Builds

### Weekly Security Check

Configure in Jenkins job:
1. Build Triggers → Build periodically
2. Schedule: `0 2 * * 1` (Monday 2 AM)

### Cron Syntax

```
# Format: minute hour day month weekday
0 2 * * 1     # Monday 2 AM
0 2 * * *     # Daily 2 AM
0 */6 * * *   # Every 6 hours
```

---

## Troubleshooting

### Jenkins Not Starting

```bash
# Check status
sudo systemctl status jenkins

# View logs
sudo journalctl -u jenkins -f

# Restart
sudo systemctl restart jenkins
```

### 404 Error

**Cause**: Jenkins not installed or not running

**Fix**:
```bash
# Check if running
sudo systemctl status jenkins

# Start if stopped
sudo systemctl start jenkins
```

### Pipeline Not Found

**Cause**: Jenkinsfile path incorrect

**Fix**: Verify path is `jenkins/Jenkinsfile` in repository

### Permission Denied

**Cause**: Jenkins user lacks permissions

**Fix**:
```bash
# Add Jenkins to www-data group
sudo usermod -a -G www-data jenkins

# Restart Jenkins
sudo systemctl restart jenkins
```

---

## Best Practices

### 1. Use Parameters

Always use parameters for flexibility:
- Environment selection
- Dry-run mode
- Feature toggles

### 2. Archive Artifacts

Archive all reports for history:
```groovy
archiveArtifacts artifacts: 'reports/**/*'
```

### 3. Publish Reports

Use HTML Publisher for readable reports:
```groovy
publishHTML([
    reportDir: 'reports',
    reportFiles: 'security-report.html',
    reportName: 'Security Report'
])
```

### 4. Email Notifications

Always notify on failures:
```groovy
post {
    failure {
        emailext(
            subject: "Pipeline Failed",
            body: "Check console output"
        )
    }
}
```

### 5. Timeout Protection

Set timeouts to prevent hanging:
```groovy
options {
    timeout(time: 1, unit: 'HOURS')
}
```

---

## Visual Pipeline Example

### Blue Ocean View Screenshot

When you access Blue Ocean, you'll see:

```
┌─────────────────────────────────────────────────────────────┐
│  Automated-Security-Update                                   │
│  ────────────────────────────────────────────────────────   │
│                                                              │
│  ┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐         │
│  │Setup │→ │Analyze│→ │Check │→ │Test  │→ │Report│         │
│  │ ✅   │  │ ✅   │  │ ✅   │  │ ✅   │  │ ✅   │         │
│  └──────┘  └──────┘  └──────┘  └──────┘  └──────┘         │
│                                                              │
│  ┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐                   │
│  │Verify│→ │Deploy│→ │Final │→ │Done  │                   │
│  │ ✅   │  │ ⏭️   │  │ ✅   │  │ ✅   │                   │
│  └──────┘  └──────┘  └──────┘  └──────┘                   │
│                                                              │
│  Duration: 3m 20s                    Status: SUCCESS ✅     │
└─────────────────────────────────────────────────────────────┘
```

---

## Quick Reference

### Access URLs

- **Jenkins Dashboard**: `http://localhost:8080`
- **Pipeline Job**: `http://localhost:8080/job/Automated-Security-Update/`
- **Blue Ocean**: `http://localhost:8080/blue`
- **Build #1**: `http://localhost:8080/job/Automated-Security-Update/1/`

### Common Actions

```bash
# Start Jenkins (Docker)
docker-compose up -d jenkins

# Start Jenkins (Native)
sudo systemctl start jenkins

# View logs
sudo journalctl -u jenkins -f

# Restart Jenkins
sudo systemctl restart jenkins

# Stop Jenkins
sudo systemctl stop jenkins
```

---

**Your pipeline is ready to visualize in Jenkins!** 🚀

Access: `http://localhost:8080`
