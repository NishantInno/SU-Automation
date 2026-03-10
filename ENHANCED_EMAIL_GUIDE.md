# Enhanced Email Notifications - Complete Guide

## Overview

The enhanced Jenkins pipeline now includes:
- ✅ **Before/After Comparison** - Captures site state before and after updates
- ✅ **Beautiful HTML Email Template** - Professional, responsive design
- ✅ **JSON Report Attachments** - All reports attached to email
- ✅ **Detailed Metrics** - Security issues, outdated modules, update status

---

## Step 1: Install Email Extension Plugin

1. **Go to Jenkins**: `http://localhost:8081`
2. **Manage Jenkins** → **Manage Plugins**
3. Click **Available plugins** tab
4. Search: `Email Extension Plugin`
5. Check the box and click **Install without restart**
6. Wait for installation to complete

---

## Step 2: Create Gmail SMTP Credentials

### Get Gmail App Password

1. Go to: https://myaccount.google.com/security
2. Enable **2-Step Verification** (if not enabled)
3. Go to: https://myaccount.google.com/apppasswords
4. Select app: **Mail**
5. Select device: **Other** → Enter "Jenkins"
6. Click **Generate**
7. **Copy the 16-character password** (e.g., `abcd efgh ijkl mnop`)
8. Save this password securely

---

## Step 3: Add Credentials to Jenkins

1. **Manage Jenkins** → **Manage Credentials**
2. Click **(global)** domain
3. Click **Add Credentials**
4. Fill in:
   - **Kind**: Username with password
   - **Username**: `your-email@gmail.com`
   - **Password**: Paste the 16-character App Password
   - **ID**: `gmail-smtp-credentials`
   - **Description**: Gmail SMTP
5. Click **Create**

---

## Step 4: Configure SMTP in Jenkins

1. **Manage Jenkins** → **Configure System**
2. Scroll to **Extended E-mail Notification**
3. Configure:
   - **SMTP server**: `smtp.gmail.com`
   - **SMTP Port**: `587`
   - Click **Advanced**
   - **Credentials**: Select `gmail-smtp-credentials`
   - Check **Use TLS**
   - **Default Recipients**: `your-email@gmail.com`
   - **Default Content Type**: `HTML (text/html)`
4. **Test**: Check "Test configuration" and send test email
5. Click **Save**

---

## Step 5: Use Enhanced Jenkinsfile

Replace your current Jenkinsfile with the enhanced version:

```bash
cd /var/www/html/testauto/automated-security-update
cp jenkins/Jenkinsfile-enhanced jenkins/Jenkinsfile
git add jenkins/Jenkinsfile
git commit -m "Use enhanced Jenkinsfile with email notifications"
git push origin main
```

---

## Step 6: Update Email Recipient

1. In Jenkins, go to your job: **Automated-Security-Update**
2. Click **Configure**
3. Update the **EMAIL_RECIPIENT** parameter default value to your email
4. Click **Save**

Or set it when running the build:
- Click **Build with Parameters**
- Set **EMAIL_RECIPIENT** to your email address

---

## What You'll Receive in Email

### Email Content:
1. **Header** - Build number, environment, timestamp
2. **Summary Section**:
   - Security issues before/after
   - Outdated modules before/after
   - Updates applied count
3. **Updates Applied** - List of successful/failed updates
4. **Detailed Comparison** - Before/after metrics
5. **Quick Actions** - Links to build details and reports

### Email Attachments:
- `before-analysis.json` - Site state before updates
- `after-analysis.json` - Site state after updates
- `update-results.json` - Detailed update results
- `testing-results.json` - Testing results
- `module-updates.json` - Module update information

---

## Email Template Features

### Visual Design:
- 📊 **Metrics Cards** - Color-coded status indicators
- ✅ **Update Lists** - Clear success/failure indicators
- 📈 **Comparison Charts** - Before/after visualization
- 🔗 **Action Buttons** - Quick access to Jenkins
- 📎 **Attachment Info** - Clear list of attached files

### Color Coding:
- 🟢 **Green** - Good status, no issues
- 🟡 **Yellow** - Warnings, needs attention
- 🔴 **Red** - Critical issues, failures

---

## Testing the Email Notifications

### Test Run:

1. **Go to Jenkins**: `http://localhost:8081`
2. Click **Automated-Security-Update**
3. Click **Build with Parameters**
4. Set:
   - **ENVIRONMENT**: `local`
   - **DRY_RUN**: ✅ Check (for testing)
   - **SKIP_AI_FIX**: ✅ Check
   - **EMAIL_RECIPIENT**: Your email
5. Click **Build**
6. Wait for build to complete
7. Check your email inbox

### What to Expect:

- **Subject**: `✅ Automated Security Update - SUCCESS - local - Build #XX`
- **Body**: Beautiful HTML email with metrics
- **Attachments**: 5 JSON files with detailed data

---

## Troubleshooting

### No Email Received?

1. **Check Jenkins Console Output**:
   - Look for email sending logs
   - Check for SMTP errors

2. **Check Spam Folder**:
   - Gmail may filter automated emails

3. **Verify SMTP Settings**:
   - Test configuration in Jenkins
   - Ensure credentials are correct

4. **Check Jenkins Logs**:
   ```bash
   sudo tail -f /var/log/jenkins/jenkins.log | grep -i email
   ```

### Email Plugin Not Showing?

1. **Install the plugin**:
   - Manage Jenkins → Manage Plugins
   - Search: "Email Extension Plugin"
   - Install and restart Jenkins

2. **Restart Jenkins**:
   ```bash
   sudo systemctl restart jenkins
   ```

### Attachments Not Working?

1. **Check file paths** in Jenkinsfile
2. **Verify reports exist** in workspace
3. **Check attachment pattern** in emailext configuration

---

## Alternative: Use MailHog for Testing

For local testing without Gmail:

```bash
# Run MailHog
docker run -d -p 1025:1025 -p 8025:8025 --name mailhog mailhog/mailhog

# Configure Jenkins:
# SMTP server: localhost
# SMTP Port: 1025
# No credentials needed

# View emails at: http://localhost:8025
```

---

## Email Template Customization

To customize the email template, edit:
```
core/email_template.py
```

You can modify:
- Colors and styling
- Metrics displayed
- Email layout
- Button links
- Additional sections

---

## Summary

Your enhanced pipeline now:
1. ✅ Captures site state **before** updates
2. ✅ Applies security updates
3. ✅ Captures site state **after** updates
4. ✅ Generates beautiful HTML email
5. ✅ Attaches all JSON reports
6. ✅ Sends to specified recipient

**All changes pushed to GitHub!** 🚀
