# Complete Setup Guide for New Users
## Automated Drupal Security Update Tool with Jenkins

This guide will walk you through the **complete setup** from scratch, including all prerequisites, installation steps, and configuration.

---

## 📋 Table of Contents

1. [System Requirements](#system-requirements)
2. [Prerequisites Installation](#prerequisites-installation)
3. [DDEV Setup](#ddev-setup)
4. [Clone the Repository](#clone-the-repository)
5. [Python Dependencies](#python-dependencies)
6. [Jenkins Installation](#jenkins-installation)
7. [Jenkins Configuration](#jenkins-configuration)
8. [Email Notification Setup](#email-notification-setup)
9. [Running Your First Build](#running-your-first-build)
10. [Troubleshooting](#troubleshooting)

---

## 🖥️ System Requirements

### Minimum Requirements:
- **OS**: Ubuntu 20.04+ / Debian 11+ / macOS 11+
- **RAM**: 4GB minimum, 8GB recommended
- **Disk Space**: 10GB free space
- **CPU**: 2 cores minimum
- **Internet**: Required for downloading packages and updates

### Software Requirements:
- Python 3.8 or higher
- Docker and Docker Compose
- DDEV (for Drupal development)
- Git
- Jenkins
- Web browser (Chrome, Firefox, Safari)

---

## 📦 Prerequisites Installation

### Step 1: Update System Packages

```bash
# Update package list
sudo apt update

# Upgrade existing packages
sudo apt upgrade -y
```

### Step 2: Install Essential Tools

```bash
# Install essential development tools
sudo apt install -y \
    git \
    curl \
    wget \
    build-essential \
    software-properties-common \
    apt-transport-https \
    ca-certificates \
    gnupg \
    lsb-release
```

### Step 3: Install Python 3 and pip

```bash
# Install Python 3 and pip
sudo apt install -y python3 python3-pip python3-venv

# Verify installation
python3 --version
pip3 --version
```

**Expected Output**:
```
Python 3.10.x
pip 22.x.x
```

### Step 4: Install Docker

```bash
# Add Docker's official GPG key
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Set up the stable repository
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker Engine
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Verify Docker installation
docker --version
docker compose version
```

**Expected Output**:
```
Docker version 24.x.x
Docker Compose version v2.x.x
```

### Step 5: Configure Docker Permissions

```bash
# Add your user to docker group
sudo usermod -aG docker $USER

# Apply group changes (or logout/login)
newgrp docker

# Test Docker without sudo
docker run hello-world
```

**Expected Output**: "Hello from Docker!" message

---

## 🚀 DDEV Setup

### Step 1: Install DDEV

```bash
# Download DDEV installer
curl -fsSL https://ddev.com/install.sh | bash

# Verify installation
ddev version
```

**Expected Output**:
```
DDEV version v1.22.x
```

### Step 2: Set Up Your Drupal Site with DDEV

```bash
# Navigate to your Drupal project directory
cd /var/www/html/testauto

# Initialize DDEV (if not already done)
ddev config --project-type=drupal10 --docroot=web

# Start DDEV
ddev start

# Verify DDEV is running
ddev describe
```

**Expected Output**: Shows your site URL, database info, etc.

### Step 3: Test DDEV Commands

```bash
# Test drush
ddev drush status

# Test composer
ddev composer --version
```

---

## 📥 Clone the Repository

### Step 1: Clone from GitHub

```bash
# Navigate to your project directory
cd /var/www/html/testauto

# Clone the repository
git clone https://github.com/NishantInno/SU-Automation.git automated-security-update

# Navigate into the directory
cd automated-security-update

# Verify files
ls -la
```

**Expected Output**: You should see:
```
core/
jenkins/
reports/
scripts/
.env.example
requirements.txt
README.md
```

### Step 2: Set Up Environment Variables

```bash
# Copy example environment file
cp .env.example .env

# Edit .env file with your settings
nano .env
```

**Update these values**:
```bash
# Drupal Configuration
DRUPAL_ROOT=/var/www/html/testauto/web
SITE_URL=https://testauto.ddev.site:8443

# Command Binaries (for DDEV)
DRUSH_BIN=ddev drush
COMPOSER_BIN=ddev composer

# Testing Configuration
HEADLESS_ENABLED=false
FAIL_ON_TEST_ERRORS=false

# Security
VERIFY_SSL=true
```

**Save and exit**: `Ctrl+X`, then `Y`, then `Enter`

---

## 🐍 Python Dependencies

### Step 1: Create Virtual Environment (Optional but Recommended)

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Your prompt should now show (venv)
```

### Step 2: Install Python Packages

```bash
# Install required packages
pip3 install -r requirements.txt

# Verify installation
pip3 list
```

**Expected Packages**:
- requests
- python-dotenv
- beautifulsoup4
- lxml
- selenium (optional)

### Step 3: Test Python Modules

```bash
# Test analysis engine
python3 -c "from core.analysis_engine import run_site_analysis; print('✅ Analysis engine OK')"

# Test update engine
python3 -c "from core.update_engine import check_versions; print('✅ Update engine OK')"

# Test email template
python3 -c "from core.email_template import generate_html_email; print('✅ Email template OK')"
```

**Expected Output**: Three ✅ messages

---

## 🔧 Jenkins Installation

### Step 1: Install Java (Jenkins Requirement)

```bash
# Install OpenJDK 11
sudo apt install -y openjdk-11-jdk

# Verify Java installation
java -version
```

**Expected Output**:
```
openjdk version "11.0.x"
```

### Step 2: Add Jenkins Repository

```bash
# Add Jenkins GPG key
curl -fsSL https://pkg.jenkins.io/debian-stable/jenkins.io-2023.key | sudo tee \
  /usr/share/keyrings/jenkins-keyring.asc > /dev/null

# Add Jenkins repository
echo deb [signed-by=/usr/share/keyrings/jenkins-keyring.asc] \
  https://pkg.jenkins.io/debian-stable binary/ | sudo tee \
  /etc/apt/sources.list.d/jenkins.list > /dev/null
```

### Step 3: Install Jenkins

```bash
# Update package list
sudo apt update

# Install Jenkins
sudo apt install -y jenkins

# Start Jenkins service
sudo systemctl start jenkins

# Enable Jenkins to start on boot
sudo systemctl enable jenkins

# Check Jenkins status
sudo systemctl status jenkins
```

**Expected Output**: "Active: active (running)"

### Step 4: Configure Jenkins Port (Optional)

By default, Jenkins runs on port 8080. To change to 8081:

```bash
# Edit Jenkins configuration
sudo nano /etc/default/jenkins

# Find and change:
# HTTP_PORT=8080
# To:
# HTTP_PORT=8081

# Save and exit (Ctrl+X, Y, Enter)

# Restart Jenkins
sudo systemctl restart jenkins
```

### Step 5: Add Jenkins User to Docker Group

```bash
# Add jenkins user to docker group
sudo usermod -aG docker jenkins

# Restart Jenkins to apply changes
sudo systemctl restart jenkins

# Verify jenkins user can access docker
sudo -u jenkins docker ps
```

**Expected Output**: Docker container list (may be empty)

### Step 6: Get Jenkins Initial Password

```bash
# Display initial admin password
sudo cat /var/lib/jenkins/secrets/initialAdminPassword
```

**Copy this password** - you'll need it in the next step.

---

## ⚙️ Jenkins Configuration

### Step 1: Access Jenkins Web Interface

1. **Open browser** and go to: `http://localhost:8081`
2. **Paste the initial admin password** from previous step
3. Click **Continue**

### Step 2: Install Suggested Plugins

1. Click **"Install suggested plugins"**
2. Wait for installation to complete (5-10 minutes)
3. **Do NOT close the browser** during installation

### Step 3: Create Admin User

1. Fill in the form:
   - **Username**: `admin` (or your choice)
   - **Password**: Choose a strong password
   - **Full name**: Your name
   - **Email**: Your email address
2. Click **Save and Continue**

### Step 4: Configure Jenkins URL

1. **Jenkins URL**: `http://localhost:8081/`
2. Click **Save and Finish**
3. Click **Start using Jenkins**

### Step 5: Install Email Extension Plugin

1. Go to: **Manage Jenkins** → **Manage Plugins**
2. Click **Available plugins** tab
3. Search for: `Email Extension Plugin`
4. Check the box next to **Email Extension Plugin**
5. Click **Install without restart**
6. Wait for installation to complete
7. Go back to **Dashboard**

### Step 6: Create Jenkins Pipeline Job

1. Click **New Item** (top left)
2. **Enter name**: `Automated-Security-Update`
3. Select: **Pipeline**
4. Click **OK**

### Step 7: Configure Pipeline

1. Scroll to **Pipeline** section
2. **Definition**: Select `Pipeline script from SCM`
3. **SCM**: Select `Git`
4. **Repository URL**: `https://github.com/NishantInno/SU-Automation.git`
   - Or use your forked repository URL
5. **Branch Specifier**: `*/main`
6. **Script Path**: `jenkins/Jenkinsfile`
7. Click **Save**

### Step 8: Verify Pipeline Configuration

1. Click **Build Now** (left sidebar)
2. Watch the build progress
3. First build may take 5-10 minutes
4. Check **Console Output** for any errors

---

## 📧 Email Notification Setup

### Step 1: Create Gmail App Password

1. **Go to**: https://myaccount.google.com/security
2. **Enable 2-Step Verification** (if not already enabled)
3. **Go to**: https://myaccount.google.com/apppasswords
4. **Select app**: Mail
5. **Select device**: Other (Custom name)
6. **Enter**: `Jenkins SMTP`
7. Click **Generate**
8. **Copy the 16-character password** (e.g., `abcd efgh ijkl mnop`)
9. **Save this password securely**

### Step 2: Add SMTP Credentials to Jenkins

1. **Go to**: `http://localhost:8081/manage/credentials/store/system/domain/_/`
2. Click **(global)** domain
3. Click **Add Credentials** (left sidebar)
4. Fill in:
   - **Kind**: `Username with password`
   - **Scope**: `Global`
   - **Username**: `your-email@gmail.com`
   - **Password**: Paste the 16-character App Password (with spaces)
   - **ID**: `gmail-smtp-credentials`
   - **Description**: `Gmail SMTP for Jenkins`
5. Click **Create**

### Step 3: Configure Extended E-mail Notification

1. **Go to**: `http://localhost:8081/manage/configure`
2. Scroll to **Extended E-mail Notification** section
3. Fill in:
   - **SMTP server**: `smtp.gmail.com`
   - **SMTP Port**: `587`
4. Click **Advanced** button
5. Configure:
   - **Credentials**: Select `gmail-smtp-credentials`
   - Check ✅ **Use TLS**
   - **Default user e-mail suffix**: `@gmail.com`
   - **Default Recipients**: `your-email@gmail.com`
   - **Default Content Type**: `HTML (text/html)`

### Step 4: Test Email Configuration

1. In the **Extended E-mail Notification** section
2. Scroll down to **"Test configuration by sending test e-mail"**
3. Check the checkbox
4. **Test e-mail recipient**: `your-email@gmail.com`
5. Click **Test configuration**
6. Look for: **"Email was successfully sent"**
7. Check your inbox for test email

### Step 5: Configure Classic E-mail Notification (Optional)

1. Scroll to **E-mail Notification** section
2. Fill in:
   - **SMTP server**: `smtp.gmail.com`
3. Click **Advanced**
4. Configure:
   - Check ✅ **Use SMTP Authentication**
   - **User Name**: `your-email@gmail.com`
   - **Password**: Paste the 16-character App Password
   - Check ✅ **Use TLS**
   - **SMTP Port**: `587`
   - **Reply-To Address**: `your-email@gmail.com`
   - **Charset**: `UTF-8`

### Step 6: Save Configuration

Click **Save** at the bottom of the page

---

## 🎯 Running Your First Build

### Step 1: Update Email Recipient in Jenkinsfile

```bash
cd /var/www/html/testauto/automated-security-update

# Edit Jenkinsfile
nano jenkins/Jenkinsfile

# Find line with EMAIL_RECIPIENT and change to your email:
# defaultValue: 'your-email@gmail.com',

# Save and exit (Ctrl+X, Y, Enter)

# Commit changes
git add jenkins/Jenkinsfile
git commit -m "Update email recipient"
git push origin main
```

### Step 2: Run Build with Parameters

1. **Go to**: `http://localhost:8081/job/Automated-Security-Update/`
2. Click **Build with Parameters** (left sidebar)
3. Configure parameters:
   - **ENVIRONMENT**: `local`
   - **DRY_RUN**: ✅ Check (for first test run)
   - **SKIP_AI_FIX**: ✅ Check
   - **DRUPAL_ROOT**: `/var/www/html/testauto/web`
   - **SITE_URL**: `https://testauto.ddev.site:8443`
   - **EMAIL_RECIPIENT**: `your-email@gmail.com`
4. Click **Build**

### Step 3: Monitor Build Progress

1. Click on the build number (e.g., `#1`)
2. Click **Console Output**
3. Watch the pipeline execute each stage
4. Build should complete in 2-5 minutes

### Step 4: Check Email

1. Open your email inbox
2. Look for email with subject: **"✅ Automated Security Update - SUCCESS"**
3. Email should contain:
   - Before/After comparison metrics
   - Security issues status
   - Outdated modules status
   - List of updates applied
   - 5 JSON file attachments

### Step 5: View Reports in Jenkins

1. Go back to build page
2. Click **Artifacts** (if available)
3. Download and view:
   - `before-analysis.json`
   - `after-analysis.json`
   - `update-results.json`
   - `testing-results.json`
   - `email-report.html`

---

## 🔍 Verification Checklist

After completing the setup, verify everything works:

### System Verification

```bash
# Check Docker
docker --version
docker ps

# Check DDEV
ddev version
ddev describe

# Check Python
python3 --version
pip3 list | grep requests

# Check Jenkins
sudo systemctl status jenkins
curl -I http://localhost:8081
```

### Pipeline Verification

- [ ] Jenkins is accessible at `http://localhost:8081`
- [ ] Pipeline job `Automated-Security-Update` exists
- [ ] First build completed successfully
- [ ] Console output shows all stages executed
- [ ] Email notification received
- [ ] Email contains before/after comparison
- [ ] JSON attachments are present
- [ ] Reports are archived in Jenkins

### DDEV Verification

```bash
cd /var/www/html/testauto

# Test DDEV commands
ddev drush status
ddev composer --version

# Test site access
ddev launch
```

---

## 🐛 Troubleshooting

### Issue 1: Jenkins Won't Start

**Symptom**: `sudo systemctl status jenkins` shows "failed"

**Solution**:
```bash
# Check Java installation
java -version

# Check Jenkins logs
sudo journalctl -u jenkins -n 50

# Restart Jenkins
sudo systemctl restart jenkins
```

### Issue 2: Docker Permission Denied

**Symptom**: "permission denied while trying to connect to Docker"

**Solution**:
```bash
# Add user to docker group
sudo usermod -aG docker $USER
sudo usermod -aG docker jenkins

# Restart services
sudo systemctl restart docker
sudo systemctl restart jenkins

# Logout and login again
```

### Issue 3: DDEV Commands Not Found in Pipeline

**Symptom**: "ddev: command not found" in Jenkins console

**Solution**:
```bash
# Ensure DDEV is in PATH for jenkins user
sudo -u jenkins which ddev

# If not found, add to Jenkins environment
# Edit /etc/default/jenkins and add:
# PATH="/usr/local/bin:$PATH"

sudo systemctl restart jenkins
```

### Issue 4: Email Not Sending

**Symptom**: No email received after build

**Solution**:
1. Check SMTP credentials are correct
2. Verify App Password has spaces: `abcd efgh ijkl mnop`
3. Check Jenkins logs:
   ```bash
   sudo tail -f /var/log/jenkins/jenkins.log | grep -i email
   ```
4. Test SMTP connection:
   ```bash
   telnet smtp.gmail.com 587
   ```
5. Verify Email Extension Plugin is installed

### Issue 5: Python Module Import Errors

**Symptom**: "ModuleNotFoundError: No module named 'requests'"

**Solution**:
```bash
cd /var/www/html/testauto/automated-security-update

# Install for jenkins user
sudo -u jenkins pip3 install --user -r requirements.txt

# Or install system-wide
sudo pip3 install -r requirements.txt
```

### Issue 6: Reports Directory Not Found

**Symptom**: "FileNotFoundError: reports/email-report.html"

**Solution**:
```bash
# Ensure reports directory exists in workspace
cd /var/lib/jenkins/workspace/Automated-Security-Update
mkdir -p reports logs patches

# Or add to Jenkinsfile Initialize stage:
# mkdir -p reports logs patches
```

### Issue 7: Build Stuck or Hanging

**Symptom**: Build runs forever without completing

**Solution**:
1. Click **Console Output** to see where it's stuck
2. If stuck on DDEV command:
   ```bash
   # Check DDEV status
   ddev describe
   ddev restart
   ```
3. If stuck on Python command:
   - Check Python module imports
   - Verify environment variables
4. Abort build and run again

---

## 📚 Additional Resources

### Documentation Files

- **README.md** - Project overview
- **JENKINS_FLOW.md** - Pipeline visualization
- **JENKINS_SETUP_GUIDE.md** - Detailed Jenkins setup
- **JENKINS_COMPLETE_EMAIL_SETUP.md** - Email configuration
- **ENHANCED_EMAIL_GUIDE.md** - Email features guide
- **JENKINS_DOCKER_FIX.md** - Docker permission fixes
- **STANDALONE_INSTALLATION.md** - Standalone tool usage

### Useful Commands

```bash
# View Jenkins logs
sudo journalctl -u jenkins -f

# Restart Jenkins
sudo systemctl restart jenkins

# Check DDEV status
ddev describe

# Test Python modules
python3 -m core.analysis_engine

# View build artifacts
ls -la /var/lib/jenkins/workspace/Automated-Security-Update/reports/

# Git pull latest changes
cd /var/www/html/testauto/automated-security-update
git pull origin main
```

### Support

- **GitHub Repository**: https://github.com/NishantInno/SU-Automation
- **Issues**: Report bugs on GitHub Issues
- **DDEV Documentation**: https://ddev.readthedocs.io/
- **Jenkins Documentation**: https://www.jenkins.io/doc/

---

## 🎉 Congratulations!

You have successfully set up the Automated Drupal Security Update Tool with Jenkins!

### What You Can Do Now:

1. ✅ Run automated security updates on your Drupal site
2. ✅ Receive beautiful HTML email reports
3. ✅ Compare before/after site states
4. ✅ Track security vulnerabilities
5. ✅ Monitor outdated modules
6. ✅ View detailed JSON reports
7. ✅ Automate the entire update workflow

### Next Steps:

1. **Schedule Regular Builds**: Set up cron triggers in Jenkins
2. **Customize Email Template**: Edit `core/email_template.py`
3. **Add More Environments**: Configure dev, qc, prod environments
4. **Integrate with Git Hooks**: Auto-trigger on commits
5. **Set Up Monitoring**: Add Slack/Teams notifications

**Happy Automating! 🚀**
