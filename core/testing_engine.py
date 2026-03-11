"""Stage 4: Automated testing and health checks."""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from .command_runner import run_cmd
from .config import load_config
from .logger import setup_logger
from .utils import write_json


def _curl_status(curl_bin: str, url: str, timeout: int) -> dict[str, Any]:
    result = run_cmd(
        [curl_bin, "-s", "-o", "/dev/null", "-w", "%{http_code}", url],
        timeout=timeout,
    )
    status_code = result.stdout.strip() if result.stdout else "000"
    return {
        "url": url,
        "status_code": status_code,
        "exit_code": result.exit_code,
        "stderr": result.stderr,
    }


def _run_drush_json(drush_bin: str, args: list[str], cwd: Path, timeout: int) -> Any:
    result = run_cmd([drush_bin, *args, "--format=json"], cwd=str(cwd), timeout=timeout)
    if result.exit_code == 0 and result.stdout:
        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError:
            return {"raw": result.stdout}
    return {"raw": result.stderr or result.stdout, "exit_code": result.exit_code}


def _headless_check(url: str) -> dict[str, Any]:
    try:
        from playwright.sync_api import sync_playwright  # type: ignore
    except Exception:
        return {"url": url, "status": "skipped", "reason": "playwright not installed"}

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        response = page.goto(url, wait_until="domcontentloaded", timeout=30_000)
        status = response.status if response else None
        page.close()
        browser.close()
    return {"url": url, "status": "ok" if status and status < 500 else "error", "http_status": status}


def run_tests() -> None:
    """Run all tests and generate report."""
    config = load_config()
    logger = setup_logger("testing_engine", config.logs_dir)
    logger.info("Starting automated testing")

    logger.info("Running HTTP status checks")
    http_results = []
    for path in config.critical_paths:
        url = f"{config.site_url}{path}"
        http_results.append(_curl_status(config.curl_bin, url, config.command_timeout))

    logger.info("Running headless browser checks")
    headless_results = []
    if config.headless_enabled:
        for path in config.critical_paths:
            url = f"{config.site_url}{path}"
            headless_results.append(_headless_check(url))
    else:
        headless_results.append({"status": "skipped", "reason": "HEADLESS_ENABLED=false"})

    logger.info("Checking watchdog logs")
    watchdog = _run_drush_json(
        config.drush_bin,
        ["ws", "--count=200"],
        config.drupal_root,
        config.command_timeout,
    )

    logger.info("Checking entity schema updates")
    entity_updates = _run_drush_json(
        config.drush_bin,
        ["entity:updates"],
        config.drupal_root,
        config.command_timeout,
    )

    logger.info("Checking config status")
    config_status = _run_drush_json(
        config.drush_bin,
        ["config:status"],
        config.drupal_root,
        config.command_timeout,
    )

    # Run menu testing with Playwright
    menu_results = {}
    try:
        logger.info("Running menu link testing with Playwright")
        from .menu_testing import run_menu_tests
        run_menu_tests()
        # Load the generated report
        menu_report_path = config.reports_dir / "menu-check.json"
        if menu_report_path.exists():
            menu_results = json.loads(menu_report_path.read_text())
            logger.info("✅ Menu testing completed: %d links tested, %d successful, %d failed",
                       menu_results.get("total_links_tested", 0),
                       menu_results.get("successful_links", 0),
                       menu_results.get("failed_links", 0))
    except ImportError:
        logger.warning("⚠️ Playwright not installed, skipping menu testing")
        logger.info("Install with: pip install playwright")
        menu_results = {"status": "skipped", "reason": "Playwright not installed"}
    except Exception as e:
        logger.warning("⚠️ Menu testing failed: %s", str(e))
        menu_results = {"status": "error", "error": str(e)}

    error_pages = [item for item in http_results if item.get("status_code") not in {"200", "301", "302"}]
    watchdog_errors = []
    if isinstance(watchdog, list):
        watchdog_errors = [item for item in watchdog if isinstance(item, dict) and str(item.get("severity", "")).lower() in {"error", "critical", "alert", "emergency"}]
    elif isinstance(watchdog, dict):
        watchdog_errors = [
            item for item in watchdog.values()
            if isinstance(item, dict) and str(item.get("severity", "")).lower() in {"error", "critical", "alert", "emergency"}
        ]

    report = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "http_checks": http_results,
        "headless_checks": headless_results,
        "watchdog": watchdog,
        "entity_updates": entity_updates,
        "config_status": config_status,
        "menu_checks": menu_results,
        "summary": {
            "http_errors": len(error_pages),
            "headless_enabled": config.headless_enabled,
            "watchdog_errors": len(watchdog_errors),
            "menu_links_tested": menu_results.get("total_links_tested", 0),
            "menu_links_failed": menu_results.get("failed_links", 0),
        },
    }

    report_path = config.reports_dir / "testing-results.json"
    write_json(report_path, report)
    logger.info("Testing report written to %s", report_path)

    if config.fail_on_test_errors and (error_pages or watchdog_errors):
        raise RuntimeError("Testing detected HTTP or watchdog errors")
    return report_path


if __name__ == "__main__":
    run_tests()
