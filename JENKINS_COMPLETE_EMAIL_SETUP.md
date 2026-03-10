# Complete Jenkins Email Setup with SMTP Credentials

## Step 1: Install Email Extension Plugin

1. **Go to Jenkins Dashboard**: `http://localhost:8081`
2. **Manage Jenkins** → **Manage Plugins**
3. Click **Available plugins** tab
4. Search for: **Email Extension Plugin**
5. Check the box next to **Email Extension Plugin**
6. Click **Install without restart**
7. Wait for installation to complete
8. Go back to **Dashboard**

---

## Step 2: Create Gmail SMTP Credentials

### A. Enable 2-Step Verification (if not already enabled)

1. Go to: https://myaccount.google.com/security
2. Click **2-Step Verification**
3. Follow the steps to enable it

### B. Create App Password

1. Go to: https://myaccount.google.com/apppasswords
2. **Select app**: Mail
3. **Select device**: Other (Custom name)
4. Enter: `Jenkins SMTP`
5. Click **Generate**
6. **Copy the 16-character password** (e.g., `abcd efgh ijkl mnop`)
7. **Save this password** - you'll need it in Jenkins

---

## Step 3: Configure SMTP in Jenkins

### A. Add SMTP Credentials to Jenkins

1. **Go to**: `http://localhost:8081`
2. **Manage Jenkins** → **Manage Credentials**
3. Click **(global)** domain
4. Click **Add Credentials**
5. Fill in:
   - **Kind**: Username with password
   - **Scope**: Global
   - **Username**: `your-email@gmail.com`
   - **Password**: Paste the 16-character App Password from Step 2
   - **ID**: `gmail-smtp-credentials`
   - **Description**: Gmail SMTP for Jenkins
6. Click **Create**

### B. Configure Extended E-mail Notification

1. **Manage Jenkins** → **Configure System**
2. Scroll to **Extended E-mail Notification**
3. Configure:
   - **SMTP server**: `smtp.gmail.com`
   - **SMTP Port**: `587`
   - Click **Advanced**
   - **Credentials**: Select `gmail-smtp-credentials`
   - Check **Use TLS**
   - **Default user e-mail suffix**: `@gmail.com`
   - **Default Recipients**: `your-email@gmail.com`
   - **Reply-To Address**: `your-email@gmail.com`
   - **Default Content Type**: `HTML (text/html)`

4. **Test Configuration**:
   - Scroll down in Extended E-mail section
   - Check **Test configuration by sending test e-mail**
   - Enter your email address
   - Click **Test configuration**
   - Check your inbox for test email

### C. Configure Classic E-mail Notification

1. Scroll to **E-mail Notification** section
2. Configure:
   - **SMTP server**: `smtp.gmail.com`
   - Click **Advanced**
   - Check **Use SMTP Authentication**
   - **User Name**: `your-email@gmail.com`
   - **Password**: Paste the 16-character App Password
   - Check **Use TLS**
   - **SMTP Port**: `587`
   - **Reply-To Address**: `your-email@gmail.com`
   - **Charset**: `UTF-8`

3. **Test**:
   - Check **Test configuration by sending test e-mail**
   - Enter your email
   - Click **Test configuration**

4. Click **Save**

---

## Step 4: Alternative - Use Office 365 / Outlook

If using Office 365 or Outlook.com:

1. **SMTP server**: `smtp.office365.com`
2. **SMTP Port**: `587`
3. **Use TLS**: Yes
4. **Username**: Your full Office 365 email
5. **Password**: Your Office 365 password (or App Password if 2FA enabled)

---

## Step 5: Alternative - Use Local Mail Server (Testing)

For local testing without external SMTP:

```bash
# Install and run MailHog (catches all emails)
docker run -d -p 1025:1025 -p 8025:8025 --name mailhog mailhog/mailhog

# In Jenkins, configure:
# SMTP server: localhost
# SMTP Port: 1025
# No authentication needed
# No TLS/SSL

# View all emails at: http://localhost:8025
```

---

## Troubleshooting

### "Could not connect to SMTP host"

1. Check firewall allows port 587:
   ```bash
   sudo ufw allow 587/tcp
   ```

2. Test SMTP connection:
   ```bash
   telnet smtp.gmail.com 587
   ```

### "Authentication failed"

1. Verify you're using **App Password**, not regular password
2. Check username is complete email address
3. Verify 2-Step Verification is enabled

### "Emails not sending from pipeline"

1. Check Jenkins logs:
   ```bash
   sudo tail -f /var/log/jenkins/jenkins.log
   ```

2. Verify Email Extension Plugin is installed:
   - **Manage Jenkins** → **Manage Plugins** → **Installed plugins**
   - Search for "Email Extension"

3. Check pipeline syntax - use `emailext` not `mail`

---

## Quick Reference

### Gmail SMTP Settings
- **Server**: smtp.gmail.com
- **Port**: 587 (TLS) or 465 (SSL)
- **Authentication**: Required
- **Username**: Full email address
- **Password**: 16-character App Password

### Office 365 SMTP Settings
- **Server**: smtp.office365.com
- **Port**: 587
- **Authentication**: Required
- **TLS**: Required

### Test Email Command

```bash
# Test from command line
echo "Test email" | mail -s "Test" your-email@gmail.com
```
