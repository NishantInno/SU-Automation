# Fix Jenkins Docker Permission Issue

## Problem
Jenkins cannot run `ddev` commands because the `jenkins` user doesn't have permission to access Docker.

Error:
```
Docker error: permission denied while trying to connect to the docker API at unix:///var/run/docker.sock
```

## Solution

Add the `jenkins` user to the `docker` group:

```bash
# Add jenkins user to docker group
sudo usermod -aG docker jenkins

# Restart Jenkins to apply changes
sudo systemctl restart jenkins

# Verify jenkins user is in docker group
groups jenkins
```

## Alternative: Run Jenkins as Current User

If you want Jenkins to run as your current user (who already has Docker access):

```bash
# Stop Jenkins
sudo systemctl stop jenkins

# Edit Jenkins service
sudo systemctl edit jenkins --full

# Find the line:
# User=jenkins
# Group=jenkins

# Change to your username (e.g., ino-lap-244):
# User=ino-lap-244
# Group=ino-lap-244

# Save and exit

# Reload systemd
sudo systemctl daemon-reload

# Change ownership of Jenkins directories
sudo chown -R ino-lap-244:ino-lap-244 /var/lib/jenkins
sudo chown -R ino-lap-244:ino-lap-244 /var/cache/jenkins
sudo chown -R ino-lap-244:ino-lap-244 /var/log/jenkins

# Start Jenkins
sudo systemctl start jenkins
```

## Quick Fix (Recommended)

Run this one command:

```bash
sudo usermod -aG docker jenkins && sudo systemctl restart jenkins
```

Wait 30 seconds for Jenkins to restart, then run your build again.

## Verify Fix

After applying the fix, test with:

```bash
# Switch to jenkins user
sudo -u jenkins bash

# Test docker access
docker ps

# Test ddev
cd /var/www/html/testauto
ddev describe

# Exit jenkins user
exit
```

If these commands work, Jenkins will be able to run DDEV commands!
