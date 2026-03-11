#!/bin/bash
# Setup automation branch for Drupal project
# Creates 'suautomation' branch on first run and backs up code

set -e

PROJECT_PATH="${1:-/var/www/html/juvdev}"
BRANCH_NAME="${2:-suautomation}"
BACKUP_SUFFIX="${3:-_code_bkp}"

echo "=========================================="
echo "Project Branch Setup for Automation"
echo "=========================================="
echo "Project Path: $PROJECT_PATH"
echo "Branch Name: $BRANCH_NAME"
echo "=========================================="

# Verify project directory exists
if [ ! -d "$PROJECT_PATH" ]; then
    echo "❌ Error: Project directory does not exist: $PROJECT_PATH"
    exit 1
fi

cd "$PROJECT_PATH"

# Check if this is a git repository
if [ ! -d ".git" ]; then
    echo "❌ Error: Not a git repository: $PROJECT_PATH"
    exit 1
fi

# Get current branch
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
echo "Current branch: $CURRENT_BRANCH"

# Check if automation branch already exists
if git show-ref --verify --quiet "refs/heads/$BRANCH_NAME"; then
    echo "✅ Branch '$BRANCH_NAME' already exists"
    echo "Checking out to existing branch..."
    git checkout "$BRANCH_NAME"
    echo "✅ Switched to branch '$BRANCH_NAME'"
    echo "ℹ️  Skipping backup (already done on first run)"
else
    echo "🆕 First time setup detected"
    echo "Creating new branch '$BRANCH_NAME' from current branch..."
    
    # Ensure we're on the latest
    git fetch origin
    
    # Create new branch from current HEAD
    git checkout -b "$BRANCH_NAME"
    echo "✅ Created and switched to branch '$BRANCH_NAME'"
    
    # Push new branch to remote
    echo "Pushing new branch to remote..."
    git push -u origin "$BRANCH_NAME"
    echo "✅ Branch '$BRANCH_NAME' pushed to remote"
    
    # Create code backup (first time only)
    BACKUP_DIR="${PROJECT_PATH}${BACKUP_SUFFIX}"
    
    if [ -d "$BACKUP_DIR" ]; then
        echo "⚠️  Backup directory already exists: $BACKUP_DIR"
        echo "Skipping backup creation"
    else
        echo "📦 Creating code backup..."
        echo "Backup location: $BACKUP_DIR"
        
        # Create backup directory
        mkdir -p "$BACKUP_DIR"
        
        # Copy all files except .git, node_modules, vendor, and large directories
        rsync -av \
            --exclude='.git' \
            --exclude='node_modules' \
            --exclude='vendor' \
            --exclude='sites/default/files' \
            --exclude='*.sql' \
            --exclude='*.sql.gz' \
            "$PROJECT_PATH/" "$BACKUP_DIR/"
        
        # Create backup metadata
        cat > "$BACKUP_DIR/BACKUP_INFO.txt" << EOF
Backup Information
==================
Created: $(date)
Source: $PROJECT_PATH
Branch: $BRANCH_NAME
Commit: $(git rev-parse HEAD)
User: $(whoami)
Hostname: $(hostname)

This is a safety backup created during first-time automation setup.
EOF
        
        echo "✅ Code backup created successfully"
        echo "Backup size: $(du -sh "$BACKUP_DIR" | cut -f1)"
    fi
fi

# Display current status
echo ""
echo "=========================================="
echo "✅ Setup Complete"
echo "=========================================="
echo "Current branch: $(git rev-parse --abbrev-ref HEAD)"
echo "Latest commit: $(git log -1 --oneline)"
echo "Remote tracking: $(git rev-parse --abbrev-ref --symbolic-full-name @{u} 2>/dev/null || echo 'Not set')"
echo "=========================================="
