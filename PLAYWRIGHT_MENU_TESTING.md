# Playwright Menu Testing Integration

## Overview

The pipeline now includes **Playwright-based menu and page testing** to automatically test all menu links on your Drupal homepage during the testing stage.

---

## What It Does

### Automated Menu Link Testing

1. **Loads Homepage** - Opens your site's homepage
2. **Extracts Menu Links** - Finds all navigation links from:
   - `nav a` - Standard navigation elements
   - `.menu a` - Menu class elements
   - `.navbar a` - Bootstrap navbar
   - `header a` - Header links
   - `[role='navigation'] a` - Accessible navigation
3. **Tests Each Link** - Visits every unique link and checks:
   - HTTP status code (success = < 400)
   - Page title
   - Load time
   - Any errors or timeouts
4. **Generates Report** - Creates `menu-check.json` with:
   - Total links found
   - Total links tested
   - Successful links count
   - Failed links count
   - Detailed per-link results
5. **Includes in Email** - Attaches report to email notification

---

## Installation

### Step 1: Install Playwright Package

Playwright is already added to `requirements.txt`. Install it:

```bash
# Install Python package
pip3 install playwright>=1.42.0

# Install Chromium browser (required for headless testing)
python3 -m playwright install chromium

# Optional: Install system dependencies for better compatibility
python3 -m playwright install-deps chromium
```

### Step 2: Verify Installation

```bash
# Test Playwright import
python3 -c "from playwright.async_api import async_playwright; print('✅ Playwright installed')"

# Test browser availability
python3 -m playwright install --check-browsers
```

### Step 3: Jenkins Automatic Installation

The Jenkinsfile automatically installs Playwright browsers during the **Initialize** stage:

```groovy
# Install Playwright browsers for menu testing
echo "Installing Playwright browsers..."
python3 -m playwright install chromium --with-deps
```

No manual setup needed in Jenkins!

---

## How It Works

### Menu Testing Flow

```
Testing Stage
    ↓
Run HTTP checks
    ↓
Run headless checks
    ↓
Check watchdog logs
    ↓
Check entity schema
    ↓
Check config status
    ↓
🎯 RUN MENU TESTING WITH PLAYWRIGHT ← NEW
    ├─ Launch Chromium browser
    ├─ Load homepage
    ├─ Extract menu links
    ├─ Test each link
    └─ Generate menu-check.json
    ↓
Generate testing report
    ↓
Include menu results in email
```

### Code Integration

**File**: `core/menu_testing.py`
- Async Playwright implementation
- Extracts links from multiple selectors
- Tests each link with timeout handling
- Generates JSON report

**File**: `core/testing_engine.py`
- Calls `run_menu_tests()` during testing
- Loads `menu-check.json` report
- Includes results in `testing-results.json`
- Handles missing Playwright gracefully

**File**: `jenkins/Jenkinsfile`
- Installs Playwright browsers in Initialize stage
- Testing stage automatically runs menu tests
- Reports archived as artifacts

---

## Configuration

### Environment Variables

```bash
# Optional: Control Playwright behavior
export PLAYWRIGHT_HEADLESS=true        # Always headless (default)
export PLAYWRIGHT_TIMEOUT=30000        # Page load timeout (ms)
export PLAYWRIGHT_SLOW_MO=0            # Slow down actions (ms)
```

### Menu Selectors

The script looks for menu links in these selectors (in order):

```python
menu_selectors = [
    "nav a",                    # Standard <nav> element
    ".menu a",                  # CSS class "menu"
    ".navbar a",                # Bootstrap navbar
    ".navigation a",            # CSS class "navigation"
    "header a",                 # Header element
    "[role='navigation'] a",    # ARIA role
]
```

**To customize**, edit `core/menu_testing.py` line 47-54.

---

## Output Report

### Report Format: `reports/menu-check.json`

```json
{
  "timestamp": "2026-03-11T16:30:00.000Z",
  "site_url": "https://testauto.ddev.site:8443",
  "total_links_found": 12,
  "total_links_tested": 12,
  "successful_links": 11,
  "failed_links": 1,
  "links": [
    {
      "url": "https://testauto.ddev.site:8443/",
      "status": 200,
      "title": "Home | My Site",
      "success": true
    },
    {
      "url": "https://testauto.ddev.site:8443/about",
      "status": 200,
      "title": "About Us",
      "success": true
    },
    {
      "url": "https://testauto.ddev.site:8443/broken-link",
      "status": 404,
      "title": "Not Found",
      "success": false,
      "error": "HTTP 404"
    }
  ],
  "errors": []
}
```

### Report Fields

| Field | Description |
|-------|-------------|
| `timestamp` | When the test ran (ISO 8601) |
| `site_url` | The site being tested |
| `total_links_found` | Number of unique menu links extracted |
| `total_links_tested` | Number of links actually tested |
| `successful_links` | Links with status < 400 |
| `failed_links` | Links with status >= 400 or errors |
| `links[]` | Array of per-link results |
| `links[].url` | Full URL tested |
| `links[].status` | HTTP status code |
| `links[].title` | Page title |
| `links[].success` | Boolean: status < 400 |
| `links[].error` | Error message (if any) |
| `errors[]` | Overall test errors |

---

## Email Integration

### What's Included in Email

The email now includes menu testing results in the summary:

```
📊 Update Summary
├─ Security Issues: 3 → 0
├─ Outdated Modules: 10 → 2
├─ Updates Applied: 8 successful, 0 failed
├─ Menu Links Tested: 12
└─ Menu Links Failed: 1
```

### Attachments

The `menu-check.json` is automatically attached to the email for detailed review.

---

## Running Tests Manually

### Test Menu Links Directly

```bash
cd /var/www/html/testauto/automated-security-update

# Set environment variables
export DRUPAL_ROOT=/var/www/html/testauto/web
export SITE_URL=https://testauto.ddev.site:8443

# Run menu testing
python3 -c "from core.menu_testing import run_menu_tests; run_menu_tests()"

# View results
cat reports/menu-check.json | python3 -m json.tool
```

### Run Full Testing Suite

```bash
# Run all tests including menu testing
python3 -m core.testing_engine

# Check results
cat reports/testing-results.json | python3 -m json.tool
```

### Run in Jenkins

1. Go to: `http://localhost:8081/job/Automated-Security-Update/`
2. Click **Build with Parameters**
3. Set parameters and click **Build**
4. View console output for menu testing logs
5. Download `menu-check.json` from artifacts

---

## Troubleshooting

### Issue 1: "Playwright not installed"

**Symptom**: Warning in logs: "Playwright not installed, skipping menu testing"

**Solution**:
```bash
pip3 install playwright>=1.42.0
python3 -m playwright install chromium
```

### Issue 2: "Browser launch failed"

**Symptom**: Error: "Failed to launch browser"

**Solution**:
```bash
# Install system dependencies
python3 -m playwright install-deps chromium

# Or on Ubuntu:
sudo apt install -y libglib2.0-0 libx11-6 libxcb1 libxrandr2
```

### Issue 3: "Connection refused" or "Site not accessible"

**Symptom**: All links fail with connection errors

**Solution**:
1. Verify site is running: `ddev describe`
2. Check SITE_URL is correct in environment
3. For DDEV: Use `https://testauto.ddev.site:8443` (not localhost)
4. Check SSL certificate (Playwright ignores self-signed by default)

### Issue 4: "Timeout" errors

**Symptom**: Some links timeout after 30 seconds

**Solution**:
1. Check if pages are slow to load
2. Increase timeout in `core/menu_testing.py` line 96:
   ```python
   link_response = await page.goto(link_url, wait_until="networkidle", timeout=60000)  # 60s
   ```
3. Check for infinite redirects or slow endpoints

### Issue 5: "Links not found"

**Symptom**: "Found 0 unique menu links"

**Solution**:
1. Check menu uses standard selectors (nav, .menu, .navbar, etc.)
2. Add custom selector to `menu_selectors` in `core/menu_testing.py`
3. Verify homepage loads correctly
4. Check for JavaScript-rendered menus (Playwright handles JS)

---

## Advanced Usage

### Custom Menu Selectors

Edit `core/menu_testing.py` to add your custom selectors:

```python
menu_selectors = [
    "nav a",
    ".menu a",
    ".navbar a",
    ".navigation a",
    "header a",
    "[role='navigation'] a",
    ".custom-menu a",  # Add your custom selector
    "#main-nav a",     # Or ID-based selector
]
```

### Capture Screenshots

To add screenshot capture for each page:

```python
# In core/menu_testing.py, after page.goto():
screenshot_path = config.reports_dir / f"screenshots/{link_url.split('/')[-1]}.png"
screenshot_path.parent.mkdir(parents=True, exist_ok=True)
await page.screenshot(path=str(screenshot_path))
```

### Validate Page Content

To check for specific content on each page:

```python
# After page.goto(), add:
content = await page.content()
if "expected text" not in content:
    logger.warning("Expected content not found on %s", link_url)
```

### Test Form Submissions

To test interactive elements:

```python
# Fill and submit a form
await page.fill("input[name='search']", "test")
await page.click("button[type='submit']")
await page.wait_for_load_state("networkidle")
```

---

## Performance Notes

### Timing

- **Browser launch**: ~2-3 seconds
- **Per-link test**: ~1-2 seconds (depends on page complexity)
- **Total for 10 links**: ~15-25 seconds
- **Total for 20 links**: ~25-45 seconds

### Resource Usage

- **Memory**: ~100-200 MB per browser instance
- **CPU**: Minimal (headless browser)
- **Disk**: ~50-100 MB for Chromium installation

### Optimization Tips

1. **Parallel testing**: Modify to test multiple links concurrently
2. **Caching**: Cache Playwright browser between tests
3. **Selective testing**: Test only critical paths instead of all menu links

---

## Integration with CI/CD

### GitHub Actions

```yaml
- name: Install Playwright
  run: python3 -m playwright install chromium

- name: Run Tests
  run: python3 -m core.testing_engine
```

### GitLab CI

```yaml
test:
  script:
    - python3 -m playwright install chromium
    - python3 -m core.testing_engine
```

### Jenkins (Already Configured)

Jenkinsfile automatically handles Playwright installation and testing.

---

## Summary

✅ **What's New**:
- Playwright-based menu link testing
- Automatic browser installation in Jenkins
- JSON report generation
- Email integration with results
- Graceful fallback if Playwright not available

✅ **Benefits**:
- Comprehensive menu testing
- Catches broken links automatically
- Headless browser (no UI needed)
- Works in CI/CD pipelines
- Detailed reporting

✅ **Files Modified**:
- `requirements.txt` - Added playwright
- `core/menu_testing.py` - New menu testing module
- `core/testing_engine.py` - Integrated menu testing
- `jenkins/Jenkinsfile` - Added browser installation

**Menu testing is now fully integrated into your pipeline!** 🎉
