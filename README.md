# Automated Security Update

**AI-Assisted DevOps Tool for Drupal Security Maintenance**

## Overview

Automated Security Update is a production-grade tool designed to automatically analyze Drupal websites, detect security vulnerabilities, update modules, test the site, detect errors, propose AI-assisted fixes, and deploy updates safely through a Jenkins CI/CD pipeline.

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     JENKINS CI/CD PIPELINE                      │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  STAGE 1: SITE ANALYSIS                                         │
│  - Drupal version detection                                     │
│  - Module inventory                                             │
│  - Security vulnerability scan                                  │
│  - Configuration status                                         │
│  - Watchdog log analysis                                        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  STAGE 2: VERSION CHECKING                                      │
│  - Compare installed vs latest versions                         │
│  - Query Drupal.org release history                             │
│  - Identify security updates                                    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  STAGE 3: APPLY SECURITY UPDATES                                │
│  - Composer update with dependencies                            │
│  - Database updates (drush updb)                                │
│  - Cache rebuild                                                │
│  - Configuration import                                         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  STAGE 4: AUTOMATED TESTING                                     │
│  - HTTP status code checks                                      │
│  - PHP error detection                                          │
│  - Database schema validation                                   │
│  - Configuration sync verification                              │
│  - Critical page testing                                        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  STAGE 5: ISSUE REPORTING                                       │
│  - Aggregate all results                                        │
│  - Generate HTML/JSON reports                                   │
│  - Identify failures and errors                                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  STAGE 6: AI ASSISTED FIXING                                    │
│  - Extract error messages                                       │
│  - Query AI model for fixes                                     │
│  - Generate patch files                                         │
│  - Apply patches automatically                                  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  STAGE 7: RE-VERIFY AND DEPLOY                                  │
│  - Re-run all tests                                             │
│  - Validate deployment readiness                                │
│  - Deploy to target environment                                 │
│  - LOCAL → DEV → QC → PROD                                      │
└─────────────────────────────────────────────────────────────────┘
```

## Features

- ✅ **Automated Security Scanning**: Detect vulnerabilities using Drush and Composer
- ✅ **Intelligent Update Management**: Apply updates with dependency resolution
- ✅ **Comprehensive Testing**: HTTP checks, PHP error detection, database validation
- ✅ **AI-Powered Debugging**: Automatic error analysis and patch generation
- ✅ **Multi-Environment Support**: LOCAL → DEV → QC → PROD deployment flow
- ✅ **Detailed Reporting**: HTML and JSON reports with actionable insights
- ✅ **Drupal 9/10/11 Support**: Compatible with all modern Drupal versions

## Requirements

- Python 3.8+
- Drush 11+ or 12+
- Composer 2.x
- Jenkins 2.x
- Git
- PHP 8.1+ (for Drupal 10/11)
- OpenAI API key (for AI-assisted fixing)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd automated-security-update
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
```bash
cp config/config.example.yaml config/config.yaml
# Edit config.yaml with your settings
```

4. Set up OpenAI API key:
```bash
export OPENAI_API_KEY="your-api-key-here"
```

## Configuration

Edit `config/config.yaml`:

```yaml
drupal:
  site_path: "/var/www/html/drupal"
  drush_path: "/usr/local/bin/drush"
  
environments:
  local: "http://localhost"
  dev: "https://dev.example.com"
  qc: "https://qc.example.com"
  prod: "https://www.example.com"

ai:
  provider: "openai"
  model: "gpt-4"
  
testing:
  critical_pages:
    - "/"
    - "/admin"
    - "/node"
    - "/contact"
```

## Usage

### Manual Execution

Run individual stages:

```bash
# Stage 1: Site Analysis
./scripts/run_analysis.sh

# Stage 2: Version Check
./scripts/run_version_check.sh

# Stage 3: Apply Updates
./scripts/run_updates.sh

# Stage 4: Run Tests
./scripts/run_tests.sh

# Full Pipeline
./scripts/run_full_pipeline.sh
```

### Jenkins Pipeline

1. Create a new Jenkins Pipeline job
2. Point to `jenkins/Jenkinsfile`
3. Configure parameters:
   - `ENVIRONMENT`: Target environment (local/dev/qc)
   - `DRY_RUN`: Test mode without applying changes
   - `SKIP_AI_FIX`: Skip AI-assisted fixing

## Project Structure

```
automated-security-update/
├── core/
│   ├── __init__.py
│   ├── analysis_engine.py      # Site analysis and data collection
│   ├── update_engine.py         # Module update management
│   ├── testing_engine.py        # Automated testing suite
│   ├── ai_fix_engine.py         # AI-powered error fixing
│   ├── report_engine.py         # Report generation
│   └── utils.py                 # Shared utilities
├── scripts/
│   ├── run_analysis.sh
│   ├── run_version_check.sh
│   ├── run_updates.sh
│   ├── run_tests.sh
│   └── run_full_pipeline.sh
├── jenkins/
│   └── Jenkinsfile
├── config/
│   ├── config.yaml
│   └── config.example.yaml
├── templates/
│   └── report_template.html
├── reports/                     # Generated reports
├── patches/                     # AI-generated patches
├── logs/                        # Execution logs
├── requirements.txt
└── README.md
```

## Reports

The tool generates comprehensive reports in `reports/`:

- `site-analysis.json`: Complete site inventory
- `module-updates.json`: Available updates
- `testing-results.json`: Test execution results
- `security-report.html`: Human-readable security report
- `deployment-summary.json`: Deployment status

## Safety Features

- **No Direct Production Deployment**: Enforced deployment flow
- **Automatic Rollback**: On critical failures
- **Dry-Run Mode**: Test without applying changes
- **Comprehensive Logging**: Full audit trail
- **Error Detection**: Multi-layer validation

## Deployment Flow

```
LOCAL (development) 
  ↓ (tests pass)
DEV (development server)
  ↓ (tests pass)
QC (quality control)
  ↓ (manual approval)
PROD (production)
```

## Troubleshooting

### Common Issues

**Issue**: Drush commands fail
- Check Drush version compatibility
- Verify site path in config.yaml

**Issue**: AI fixes not generated
- Verify OPENAI_API_KEY is set
- Check API quota and permissions

**Issue**: Tests fail after update
- Review `reports/testing-results.json`
- Check `logs/` for detailed error messages

## Contributing

This tool follows Drupal coding standards and best practices.

## License

MIT License

## Support

For issues and questions, please refer to the documentation or create an issue in the repository.
