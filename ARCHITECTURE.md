# System Architecture

## Overview

The Automated Security Update tool is a comprehensive DevOps automation system designed to maintain Drupal websites through continuous security monitoring, automated updates, intelligent testing, and AI-assisted error resolution.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         JENKINS CI/CD PIPELINE                       │
│                                                                       │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐│
│  │ Parameters  │  │   Options   │  │ Environment │  │ Credentials ││
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘│
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                          STAGE 1: INITIALIZE                         │
│  • Load configuration                                                │
│  • Setup environment                                                 │
│  • Install dependencies                                              │
│  • Create directories                                                │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      STAGE 2: SITE ANALYSIS                          │
│                                                                       │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │ analysis_engine.py                                           │   │
│  │                                                              │   │
│  │  • drush status          → Drupal/PHP/DB versions          │   │
│  │  • drush pm:list         → Enabled modules inventory       │   │
│  │  • drush pm:security     → Security vulnerabilities        │   │
│  │  • drush config:status   → Configuration sync status       │   │
│  │  • drush watchdog:show   → Recent error logs               │   │
│  │                                                              │   │
│  │  Output: reports/site-analysis.json                         │   │
│  └──────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    STAGE 3: VERSION CHECKING                         │
│                                                                       │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │ update_engine.py::check_versions()                          │   │
│  │                                                              │   │
│  │  • composer outdated drupal/*                               │   │
│  │  • drush pm:security                                        │   │
│  │  • Query updates.drupal.org API                             │   │
│  │                                                              │   │
│  │  For each module:                                           │   │
│  │    - Current version                                        │   │
│  │    - Latest version                                         │   │
│  │    - Security update required?                              │   │
│  │    - Release history                                        │   │
│  │                                                              │   │
│  │  Output: reports/module-updates.json                        │   │
│  └──────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                 STAGE 4: APPLY SECURITY UPDATES                      │
│                                                                       │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │ update_engine.py::apply_updates()                           │   │
│  │                                                              │   │
│  │  For each module requiring update:                          │   │
│  │    1. composer update drupal/MODULE --with-dependencies     │   │
│  │    2. Log results                                           │   │
│  │                                                              │   │
│  │  Post-update operations:                                    │   │
│  │    3. drush updb -y      (database updates)                │   │
│  │    4. drush cr           (cache rebuild)                   │   │
│  │    5. drush cim -y       (config import)                   │   │
│  │                                                              │   │
│  │  Output: reports/update-results.json                        │   │
│  └──────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    STAGE 5: AUTOMATED TESTING                        │
│                                                                       │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │ testing_engine.py                                           │   │
│  │                                                              │   │
│  │  HTTP Status Checks:                                        │   │
│  │    • curl each critical page                                │   │
│  │    • Verify 200/301/302 status codes                        │   │
│  │                                                              │   │
│  │  Headless Browser Testing (optional):                       │   │
│  │    • Playwright/Selenium checks                             │   │
│  │    • JavaScript execution                                   │   │
│  │    • DOM validation                                         │   │
│  │                                                              │   │
│  │  Drupal Health Checks:                                      │   │
│  │    • drush ws             (watchdog errors)                │   │
│  │    • drush entity:updates (schema updates)                 │   │
│  │    • drush config:status  (config sync)                    │   │
│  │                                                              │   │
│  │  Output: reports/testing-results.json                       │   │
│  └──────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     STAGE 6: ISSUE REPORTING                         │
│                                                                       │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │ report_engine.py                                            │   │
│  │                                                              │   │
│  │  Aggregate data from:                                       │   │
│  │    • site-analysis.json                                     │   │
│  │    • module-updates.json                                    │   │
│  │    • update-results.json                                    │   │
│  │    • testing-results.json                                   │   │
│  │                                                              │   │
│  │  Generate reports:                                          │   │
│  │    • security-report.html (human-readable)                 │   │
│  │    • deployment-summary.json (machine-readable)            │   │
│  │                                                              │   │
│  │  Include:                                                   │   │
│  │    - Security vulnerabilities                               │   │
│  │    - Update failures                                        │   │
│  │    - PHP errors                                             │   │
│  │    - HTTP errors                                            │   │
│  │    - Database issues                                        │   │
│  │    - Config conflicts                                       │   │
│  └──────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                  STAGE 7: AI-ASSISTED FIXING                         │
│                                                                       │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │ ai_fix_engine.py                                            │   │
│  │                                                              │   │
│  │  1. Error Detection:                                        │   │
│  │     • Parse testing results                                 │   │
│  │     • Extract error messages                                │   │
│  │     • Identify file paths and line numbers                  │   │
│  │                                                              │   │
│  │  2. Context Gathering:                                      │   │
│  │     • Read relevant source files                            │   │
│  │     • Extract surrounding code                              │   │
│  │                                                              │   │
│  │  3. AI Query:                                               │   │
│  │     • Build structured prompt                               │   │
│  │     • Call OpenAI API (GPT-4)                              │   │
│  │     • Request unified diff patch                            │   │
│  │                                                              │   │
│  │  4. Patch Application:                                      │   │
│  │     • Validate patch format                                 │   │
│  │     • git apply --check                                     │   │
│  │     • git apply (if valid)                                  │   │
│  │                                                              │   │
│  │  Output:                                                    │   │
│  │    • patches/*.patch                                        │   │
│  │    • reports/ai-fix-results.json                           │   │
│  └──────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    STAGE 8: RE-VERIFICATION                          │
│                                                                       │
│  • Re-run testing_engine.py                                          │
│  • Verify AI fixes resolved issues                                   │
│  • Ensure no new errors introduced                                   │
│  • Update testing-results.json                                       │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      STAGE 9: DEPLOYMENT                             │
│                                                                       │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │ deploy_engine.py                                            │   │
│  │                                                              │   │
│  │  Deployment Flow:                                           │   │
│  │    LOCAL → DEV → QC → PROD                                  │   │
│  │                                                              │   │
│  │  For each environment:                                      │   │
│  │    1. Pre-deployment validation                             │   │
│  │    2. Create backup (if enabled)                            │   │
│  │    3. Deploy code changes                                   │   │
│  │    4. Run drush updb, cr, cim                              │   │
│  │    5. Post-deployment testing                               │   │
│  │    6. Rollback on failure (if enabled)                      │   │
│  │                                                              │   │
│  │  Production Deployment:                                     │   │
│  │    • Requires manual approval                               │   │
│  │    • Additional safety checks                               │   │
│  │                                                              │   │
│  │  Output: reports/deployment-summary.json                    │   │
│  └──────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

## Component Details

### Core Engines

#### 1. analysis_engine.py
- **Purpose**: Comprehensive Drupal site analysis
- **Dependencies**: Drush
- **Key Functions**:
  - `run_site_analysis()`: Main entry point
  - `_run_drush_json()`: Execute Drush with JSON output
  - `_parse_status_fallback()`: Parse text output when JSON fails

#### 2. update_engine.py
- **Purpose**: Version checking and update application
- **Dependencies**: Composer, Drush, Drupal.org API
- **Key Functions**:
  - `check_versions()`: Compare installed vs available versions
  - `apply_updates()`: Apply security and regular updates
  - `_fetch_release_history()`: Query Drupal.org API

#### 3. testing_engine.py
- **Purpose**: Automated testing and health checks
- **Dependencies**: curl, optional Playwright
- **Key Functions**:
  - `run_tests()`: Execute all test suites
  - `_curl_status()`: HTTP status code checks
  - `_headless_check()`: Browser-based testing

#### 4. ai_fix_engine.py
- **Purpose**: AI-assisted error resolution
- **Dependencies**: OpenAI API, Git
- **Key Functions**:
  - `run_ai_fix_engine()`: Main orchestration
  - `_call_openai()`: Query AI model
  - `_apply_patch()`: Apply generated patches

#### 5. report_engine.py
- **Purpose**: Report generation and aggregation
- **Dependencies**: Jinja2 (optional)
- **Key Functions**:
  - `generate_report()`: Create HTML/JSON reports
  - Aggregates all stage outputs

#### 6. deploy_engine.py
- **Purpose**: Multi-environment deployment
- **Dependencies**: SSH, rsync, Git
- **Key Functions**:
  - `deploy()`: Deploy to target environment
  - Backup and rollback capabilities

### Configuration System

#### config.py
- Centralized configuration management
- Environment variable support
- Dataclass-based type safety

#### config.yaml
- YAML-based configuration
- Multi-environment support
- Override capabilities

### Utility Modules

#### command_runner.py
- Safe command execution
- Timeout handling
- Output capture

#### logger.py
- Structured logging
- File and console output
- Log rotation

#### utils.py
- JSON read/write
- File system operations
- String utilities

#### error_engine.py
- Error detection and parsing
- Pattern matching
- Error categorization

## Data Flow

```
Configuration → Analysis → Version Check → Updates → Testing
                                                         ↓
                                                    Errors? → AI Fix
                                                         ↓
                                                    Re-test
                                                         ↓
                                                    Deploy
```

## Security Considerations

1. **No Direct Production Deployment**: Enforced deployment flow
2. **Manual Approval Gates**: Production requires explicit confirmation
3. **Backup Before Deploy**: Automatic backup creation
4. **Rollback Capability**: Automatic rollback on failure
5. **API Key Security**: Environment variables, never hardcoded
6. **SSL Verification**: Configurable but enabled by default
7. **Command Injection Prevention**: Parameterized command execution

## Scalability

- **Parallel Execution**: Independent stages can run concurrently
- **Caching**: Composer and Drush caching enabled
- **Incremental Updates**: Only update modules that need it
- **Resource Limits**: Configurable timeouts and limits

## Monitoring and Observability

- **Structured Logging**: JSON logs for parsing
- **Metrics Collection**: Duration, success/failure rates
- **Report Archiving**: Historical report retention
- **Email Notifications**: Success/failure alerts
- **Slack Integration**: Real-time notifications

## Error Handling

- **Graceful Degradation**: Continue on non-critical failures
- **Retry Logic**: Automatic retry for transient failures
- **Error Categorization**: Critical vs warning vs info
- **Detailed Error Messages**: Context and remediation steps

## Technology Stack

- **Language**: Python 3.8+
- **CI/CD**: Jenkins
- **CMS**: Drupal 9/10/11
- **Package Manager**: Composer 2.x
- **CLI Tool**: Drush 11+/12+
- **AI**: OpenAI GPT-4
- **Version Control**: Git
- **Testing**: curl, Playwright (optional)

## Deployment Environments

1. **LOCAL**: Developer workstation
2. **DEV**: Development server
3. **QC**: Quality control/staging
4. **PROD**: Production (requires approval)
