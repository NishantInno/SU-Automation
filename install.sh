#!/bin/bash
set -e

echo "=========================================="
echo "Automated Security Update - Installation"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running as root for system-wide install
INSTALL_TYPE="local"
if [ "$1" = "--system" ]; then
    if [ "$EUID" -ne 0 ]; then 
        echo -e "${RED}Error: --system flag requires root privileges${NC}"
        echo "Run: sudo ./install.sh --system"
        exit 1
    fi
    INSTALL_TYPE="system"
fi

# Detect installation directory
if [ "$INSTALL_TYPE" = "system" ]; then
    INSTALL_DIR="/opt/automated-security-update"
    BIN_DIR="/usr/local/bin"
    echo -e "${GREEN}Installing system-wide to: $INSTALL_DIR${NC}"
else
    INSTALL_DIR="$HOME/.local/share/automated-security-update"
    BIN_DIR="$HOME/.local/bin"
    echo -e "${GREEN}Installing locally to: $INSTALL_DIR${NC}"
fi

echo ""
echo "Step 1/7: Checking dependencies..."

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}✗ Python 3 not found${NC}"
    echo "Install: sudo apt install python3"
    exit 1
fi
echo -e "${GREEN}✓ Python 3 found: $(python3 --version)${NC}"

# Check Drush
if ! command -v drush &> /dev/null; then
    echo -e "${YELLOW}⚠ Drush not found (required for Drupal sites)${NC}"
    echo "Install: composer global require drush/drush"
else
    echo -e "${GREEN}✓ Drush found: $(drush --version | head -1)${NC}"
fi

# Check Composer
if ! command -v composer &> /dev/null; then
    echo -e "${YELLOW}⚠ Composer not found (required for updates)${NC}"
    echo "Install: https://getcomposer.org/download/"
else
    echo -e "${GREEN}✓ Composer found: $(composer --version | head -1)${NC}"
fi

echo ""
echo "Step 2/7: Creating installation directory..."
mkdir -p "$INSTALL_DIR"
mkdir -p "$BIN_DIR"
echo -e "${GREEN}✓ Directories created${NC}"

echo ""
echo "Step 3/7: Copying files..."
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Copy core files
cp -r "$SCRIPT_DIR/core" "$INSTALL_DIR/"
cp -r "$SCRIPT_DIR/scripts" "$INSTALL_DIR/"
cp -r "$SCRIPT_DIR/templates" "$INSTALL_DIR/"
cp -r "$SCRIPT_DIR/config" "$INSTALL_DIR/"
cp "$SCRIPT_DIR/requirements.txt" "$INSTALL_DIR/"

# Create directories
mkdir -p "$INSTALL_DIR/logs"
mkdir -p "$INSTALL_DIR/reports"
mkdir -p "$INSTALL_DIR/patches"

echo -e "${GREEN}✓ Files copied${NC}"

echo ""
echo "Step 4/7: Installing Python dependencies..."
if pip3 install -r "$INSTALL_DIR/requirements.txt" --user --quiet 2>/dev/null; then
    echo -e "${GREEN}✓ Dependencies installed${NC}"
else
    echo -e "${YELLOW}⚠ Using system Python packages (install manually if needed)${NC}"
    echo "  pip3 install -r $INSTALL_DIR/requirements.txt --user"
fi

echo ""
echo "Step 5/7: Making scripts executable..."
chmod +x "$INSTALL_DIR/scripts"/*.sh
echo -e "${GREEN}✓ Scripts made executable${NC}"

echo ""
echo "Step 6/7: Creating command-line tool..."

# Create main executable
cat > "$BIN_DIR/drupal-security-check" << 'EOFMAIN'
#!/bin/bash
INSTALL_DIR="__INSTALL_DIR__"
export PYTHONPATH="$INSTALL_DIR"

show_help() {
    cat << EOF
Drupal Security Check - Automated Security Update Tool

Usage: drupal-security-check [COMMAND] [OPTIONS]

Commands:
    analyze [PATH]          Analyze Drupal site
    check [PATH]            Check for available updates
    test [PATH]             Run health tests
    verify [PATH]           Run online security verification
    update [PATH]           Apply security updates (interactive)
    report [PATH]           Generate security report
    full [PATH]             Run complete pipeline
    
    install                 Interactive setup wizard
    config                  Show current configuration
    version                 Show version information
    help                    Show this help message

Options:
    --dry-run               Run without making changes
    --site-url URL          Override site URL
    --skip-tests            Skip testing stage
    
Examples:
    # Quick health check
    drupal-security-check analyze /var/www/html/drupal
    
    # Check for updates
    drupal-security-check check /var/www/html/drupal
    
    # Run full pipeline (safe mode)
    drupal-security-check full /var/www/html/drupal --dry-run
    
    # Apply updates
    drupal-security-check update /var/www/html/drupal

For more information: https://github.com/automated-security-update
EOF
}

case "$1" in
    analyze)
        DRUPAL_ROOT="${2:-$(pwd)}"
        export DRUPAL_ROOT
        cd "$INSTALL_DIR"
        python3 -m core.analysis_engine
        echo ""
        echo "Report: $INSTALL_DIR/reports/site-analysis.json"
        ;;
    
    check)
        DRUPAL_ROOT="${2:-$(pwd)}"
        export DRUPAL_ROOT
        cd "$INSTALL_DIR"
        python3 -c "from core.update_engine import check_versions; check_versions()"
        echo ""
        echo "Report: $INSTALL_DIR/reports/module-updates.json"
        ;;
    
    test)
        DRUPAL_ROOT="${2:-$(pwd)}"
        export DRUPAL_ROOT
        cd "$INSTALL_DIR"
        python3 -m core.testing_engine
        echo ""
        echo "Report: $INSTALL_DIR/reports/testing-results.json"
        ;;
    
    verify)
        DRUPAL_ROOT="${2:-$(pwd)}"
        export DRUPAL_ROOT
        cd "$INSTALL_DIR"
        python3 -m core.online_verification
        echo ""
        echo "Report: $INSTALL_DIR/reports/online-verification.json"
        ;;
    
    update)
        DRUPAL_ROOT="${2:-$(pwd)}"
        export DRUPAL_ROOT
        export DRY_RUN=false
        cd "$INSTALL_DIR"
        ./scripts/run_updates.sh
        ;;
    
    report)
        DRUPAL_ROOT="${2:-$(pwd)}"
        export DRUPAL_ROOT
        cd "$INSTALL_DIR"
        python3 -m core.report_engine
        echo ""
        echo "Report: $INSTALL_DIR/reports/security-report.html"
        ;;
    
    full)
        DRUPAL_ROOT="${2:-$(pwd)}"
        export DRUPAL_ROOT
        if [[ "$*" == *"--dry-run"* ]]; then
            export DRY_RUN=true
        fi
        cd "$INSTALL_DIR"
        ./scripts/run_full_pipeline.sh
        ;;
    
    config)
        echo "Installation: $INSTALL_DIR"
        echo "Configuration: $INSTALL_DIR/.env"
        if [ -f "$INSTALL_DIR/.env" ]; then
            cat "$INSTALL_DIR/.env"
        else
            echo "No configuration file found. Run: drupal-security-check install"
        fi
        ;;
    
    version)
        echo "Drupal Security Check v1.0.0"
        echo "Installation: $INSTALL_DIR"
        ;;
    
    install)
        echo "Interactive Setup Wizard"
        echo ""
        read -p "Drupal root path: " drupal_root
        read -p "Site URL (e.g., http://localhost): " site_url
        
        cat > "$INSTALL_DIR/.env" << ENVEOF
DRUPAL_ROOT=$drupal_root
SITE_URL=$site_url
DRUSH_BIN=drush
COMPOSER_BIN=composer
GIT_BIN=git
CURL_BIN=curl
HEADLESS_ENABLED=false
FAIL_ON_TEST_ERRORS=false
VERIFY_SSL=true
COMMAND_TIMEOUT=900
ENVIRONMENT=local
DRY_RUN=true
SKIP_AI_FIX=true
USE_ONLINE_VERIFICATION=true
CHECK_DRUPAL_ORG=true
CHECK_SECURITY_ADVISORIES=true
LOG_LEVEL=INFO
ENVEOF
        
        echo ""
        echo "✓ Configuration saved to: $INSTALL_DIR/.env"
        echo ""
        echo "Test your setup:"
        echo "  drupal-security-check analyze $drupal_root"
        ;;
    
    help|--help|-h|"")
        show_help
        ;;
    
    *)
        echo "Unknown command: $1"
        echo "Run 'drupal-security-check help' for usage information"
        exit 1
        ;;
esac
EOFMAIN

# Replace placeholder with actual install dir
sed -i "s|__INSTALL_DIR__|$INSTALL_DIR|g" "$BIN_DIR/drupal-security-check"
chmod +x "$BIN_DIR/drupal-security-check"

echo -e "${GREEN}✓ Command created: drupal-security-check${NC}"

echo ""
echo "Step 7/7: Creating default configuration..."
if [ ! -f "$INSTALL_DIR/.env" ]; then
    cat > "$INSTALL_DIR/.env" << 'EOF'
# Automated Security Update Configuration
# Edit this file to customize settings

DRUPAL_ROOT=/var/www/html/drupal
SITE_URL=http://localhost

DRUSH_BIN=drush
COMPOSER_BIN=composer
GIT_BIN=git
CURL_BIN=curl

HEADLESS_ENABLED=false
FAIL_ON_TEST_ERRORS=false
VERIFY_SSL=true
COMMAND_TIMEOUT=900

ENVIRONMENT=local
DRY_RUN=true
SKIP_AI_FIX=true

USE_ONLINE_VERIFICATION=true
CHECK_DRUPAL_ORG=true
CHECK_SECURITY_ADVISORIES=true

LOG_LEVEL=INFO
EOF
    echo -e "${GREEN}✓ Default configuration created${NC}"
else
    echo -e "${YELLOW}⚠ Configuration already exists, skipping${NC}"
fi

echo ""
echo "=========================================="
echo -e "${GREEN}✓ Installation Complete!${NC}"
echo "=========================================="
echo ""
echo "Installation directory: $INSTALL_DIR"
echo "Command installed: drupal-security-check"
echo ""

if [ "$INSTALL_TYPE" = "local" ]; then
    # Check if ~/.local/bin is in PATH
    if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
        echo -e "${YELLOW}⚠ Add to your PATH:${NC}"
        echo "  echo 'export PATH=\"\$HOME/.local/bin:\$PATH\"' >> ~/.bashrc"
        echo "  source ~/.bashrc"
        echo ""
    fi
fi

echo "Quick Start:"
echo ""
echo "  1. Configure your site:"
echo "     drupal-security-check install"
echo ""
echo "  2. Run health check:"
echo "     drupal-security-check analyze /var/www/html/drupal"
echo ""
echo "  3. Check for updates:"
echo "     drupal-security-check check /var/www/html/drupal"
echo ""
echo "  4. Run full pipeline:"
echo "     drupal-security-check full /var/www/html/drupal --dry-run"
echo ""
echo "For help:"
echo "  drupal-security-check help"
echo ""
echo -e "${GREEN}Happy Drupal security checking!${NC}"
