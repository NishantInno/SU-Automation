# Jenkins Email Notification Setup

## Problem
Email notifications are not being sent from Jenkins pipeline.

## Solution

### Step 1: Configure Jenkins Email Settings

1. **Go to Jenkins Dashboard**
   - Navigate to: `http://localhost:8081`

2. **Configure System Settings**
   - Click: **Manage Jenkins** → **Configure System**

3. **Extended E-mail Notification**
   - Scroll to **Extended E-mail Notification** section
   - **SMTP server**: `smtp.gmail.com` (or your SMTP server)
   - **SMTP Port**: `465` (for SSL) or `587` (for TLS)
   - Click **Advanced**
   - Check: **Use SSL** or **Use TLS**
   - **Credentials**: Click **Add** → **Jenkins**
     - Kind: **Username with password**
     - Username: Your email address
     - Password: Your app password (not regular password)
     - ID: `email-credentials`
     - Description: Email credentials
   - Select the credentials you just created
   - **Default user e-mail suffix**: `@gmail.com` (or your domain)
   - **Default Recipients**: Your email address

4. **E-mail Notification (Classic)**
   - Scroll to **E-mail Notification** section
   - **SMTP server**: `smtp.gmail.com`
   - Click **Advanced**
   - Check: **Use SMTP Authentication**
   - **User Name**: Your email
   - **Password**: Your app password
   - Check: **Use SSL**
   - **SMTP Port**: `465`
   - **Reply-To Address**: Your email
   - **Charset**: `UTF-8`

5. **Test Configuration**
   - Check: **Test configuration by sending test e-mail**
   - **Test e-mail recipient**: Your email
   - Click **Test configuration**
   - You should receive a test email

6. **Save**
   - Click **Save** at the bottom

---

## Gmail App Password Setup

If using Gmail, you need an **App Password** (not your regular password):

1. Go to: https://myaccount.google.com/security
2. Enable **2-Step Verification** (if not already enabled)
3. Go to: https://myaccount.google.com/apppasswords
4. Select app: **Mail**
5. Select device: **Other** (enter "Jenkins")
6. Click **Generate**
7. Copy the 16-character password
8. Use this password in Jenkins credentials

---

## Alternative: Use Local Mail Server

For testing without external SMTP:

```bash
# Install mailhog (local mail testing server)
docker run -d -p 1025:1025 -p 8025:8025 mailhog/mailhog

# In Jenkins, configure:
# SMTP server: localhost
# SMTP port: 1025
# No authentication needed

# View emails at: http://localhost:8025
```

---

## Update Jenkinsfile Recipients

Edit your Jenkinsfile to set email recipients:

```groovy
emailext(
  subject: "✅ Automated Security Update - SUCCESS",
  body: "...",
  to: 'your-email@example.com',  // Change this
  mimeType: 'text/html'
)
```

Or set default recipients in Jenkins:
- **Manage Jenkins** → **Configure System**
- **Extended E-mail Notification**
- **Default Recipients**: `your-email@example.com`

---

## Troubleshooting

### Emails not sending?

1. **Check Jenkins logs**:
   ```bash
   sudo tail -f /var/log/jenkins/jenkins.log
   ```

2. **Check SMTP credentials**:
   - Verify username/password are correct
   - For Gmail, use App Password, not regular password

3. **Check firewall**:
   ```bash
   # Allow SMTP ports
   sudo ufw allow 587/tcp
   sudo ufw allow 465/tcp
   ```

4. **Test SMTP connection**:
   ```bash
   telnet smtp.gmail.com 587
   ```

5. **Check Jenkins Extended Email Plugin**:
   - **Manage Jenkins** → **Manage Plugins**
   - Ensure **Email Extension Plugin** is installed

---

## Quick Test

After configuration, test with a simple pipeline:

```groovy
pipeline {
  agent any
  stages {
    stage('Test') {
      steps {
        echo 'Testing email'
      }
    }
  }
  post {
    always {
      emailext(
        subject: 'Test Email from Jenkins',
        body: 'This is a test email',
        to: 'your-email@example.com'
      )
    }
  }
}
```

Run this pipeline and check if you receive the email.
