"""Stage 1: Site analysis using Drush."""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from .command_runner import run_cmd
from .config import load_config
from .logger import setup_logger
from .utils import write_json


def _run_drush_json(drush_bin: str, args: list[str], cwd: Path, timeout: int) -> tuple[Any | None, str, str, int]:
    cmd = [drush_bin, *args, "--format=json"]
    result = run_cmd(cmd, cwd=str(cwd), timeout=timeout)
    if result.exit_code == 0 and result.stdout:
        try:
            return json.loads(result.stdout), result.stdout, result.stderr, result.exit_code
        except json.JSONDecodeError:
            pass
    return None, result.stdout, result.stderr, result.exit_code


def _run_drush_text(drush_bin: str, args: list[str], cwd: Path, timeout: int) -> tuple[str, str, int]:
    result = run_cmd([drush_bin, *args], cwd=str(cwd), timeout=timeout)
    return result.stdout, result.stderr, result.exit_code


def _parse_status_fallback(text: str) -> dict[str, str]:
    data: dict[str, str] = {}
    for line in text.splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            data[key.strip().lower().replace(" ", "_")] = value.strip()
    return data


def run_site_analysis() -> Path:
    config = load_config()
    logger = setup_logger("analysis_engine", config.logs_dir)

    analysis: dict[str, Any] = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "drupal_root": str(config.drupal_root),
        "site_url": config.site_url,
        "drush_status": {},
        "enabled_modules": [],
        "custom_modules": [],
        "security_vulnerabilities": [],
        "config_status": {},
        "watchdog": [],
        "watchdog_summary": {},
        "raw_outputs": {},
    }

    logger.info("Running drush status")
    status_json, status_stdout, status_stderr, status_code = _run_drush_json(
        config.drush_bin, ["status"], config.drupal_root, config.command_timeout
    )
    if status_json is not None:
        analysis["drush_status"] = status_json
    else:
        analysis["drush_status"] = _parse_status_fallback(status_stdout)
    analysis["raw_outputs"]["drush_status"] = {
        "stdout": status_stdout,
        "stderr": status_stderr,
        "exit_code": status_code,
    }

    logger.info("Collecting enabled modules")
    modules_json, modules_stdout, modules_stderr, modules_code = _run_drush_json(
        config.drush_bin,
        ["pm:list", "--status=enabled"],
        config.drupal_root,
        config.command_timeout,
    )
    enabled_modules = []
    custom_modules = []
    if isinstance(modules_json, dict):
        for name, info in modules_json.items():
            module_info = {
                "name": name,
                "type": info.get("type"),
                "status": info.get("status"),
                "version": info.get("version"),
                "path": info.get("path"),
                "package": info.get("package"),
            }
            enabled_modules.append(module_info)
            path = (info.get("path") or "").replace("\\", "/")
            if "/modules/custom/" in path:
                custom_modules.append(module_info)
    else:
        analysis["raw_outputs"]["modules_list"] = {
            "stdout": modules_stdout,
            "stderr": modules_stderr,
            "exit_code": modules_code,
        }

    analysis["enabled_modules"] = enabled_modules
    analysis["custom_modules"] = custom_modules

    logger.info("Checking security advisories")
    security_json, security_stdout, security_stderr, security_code = _run_drush_json(
        config.drush_bin,
        ["pm:security"],
        config.drupal_root,
        config.command_timeout,
    )
    if security_json is not None:
        analysis["security_vulnerabilities"] = security_json
    else:
        analysis["security_vulnerabilities"] = security_stdout.splitlines()
    analysis["raw_outputs"]["pm_security"] = {
        "stdout": security_stdout,
        "stderr": security_stderr,
        "exit_code": security_code,
    }

    logger.info("Checking config synchronization status")
    config_json, config_stdout, config_stderr, config_code = _run_drush_json(
        config.drush_bin,
        ["config:status"],
        config.drupal_root,
        config.command_timeout,
    )
    if config_json is not None:
        analysis["config_status"] = config_json
    else:
        analysis["config_status"] = {"raw": config_stdout}
    analysis["raw_outputs"]["config_status"] = {
        "stdout": config_stdout,
        "stderr": config_stderr,
        "exit_code": config_code,
    }

    logger.info("Fetching watchdog logs")
    watchdog_json, watchdog_stdout, watchdog_stderr, watchdog_code = _run_drush_json(
        config.drush_bin,
        ["watchdog:show", "--count=200"],
        config.drupal_root,
        config.command_timeout,
    )
    if watchdog_json is None:
        watchdog_json, _, _, _ = _run_drush_json(
            config.drush_bin,
            ["ws", "--count=200"],
            config.drupal_root,
            config.command_timeout,
        )
    if watchdog_json is not None:
        analysis["watchdog"] = watchdog_json
    else:
        analysis["watchdog"] = watchdog_stdout.splitlines()
    analysis["raw_outputs"]["watchdog"] = {
        "stdout": watchdog_stdout,
        "stderr": watchdog_stderr,
        "exit_code": watchdog_code,
    }

    status = analysis.get("drush_status", {})
    drupal_version = status.get("drupal_version") or status.get("drupal-version")
    php_version = status.get("php") or status.get("php_version")
    db_version = status.get("database") or status.get("database_version")

    analysis["summary"] = {
        "drupal_core_version": drupal_version,
        "php_version": php_version,
        "database_version": db_version,
        "enabled_module_count": len(enabled_modules),
        "custom_module_count": len(custom_modules),
    }

    report_path = config.reports_dir / "site-analysis.json"
    write_json(report_path, analysis)
    logger.info("Site analysis report written to %s", report_path)
    return report_path


if __name__ == "__main__":
    run_site_analysis()
