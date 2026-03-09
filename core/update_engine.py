"""Stage 2 and 3: Version checking and applying updates."""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any
import xml.etree.ElementTree as ET

import requests

from .command_runner import run_cmd
from .config import load_config
from .logger import setup_logger
from .utils import write_json


def _run_composer_outdated(composer_bin: str, cwd: Path, timeout: int) -> dict[str, Any]:
    result = run_cmd(
        [composer_bin, "outdated", "drupal/*", "--direct", "--format=json"],
        cwd=str(cwd),
        timeout=timeout,
    )
    if result.exit_code != 0:
        return {"error": result.stderr, "raw": result.stdout}
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return {"error": "Invalid JSON from composer", "raw": result.stdout}


def _run_drush_security(drush_bin: str, cwd: Path, timeout: int) -> list[str]:
    result = run_cmd([drush_bin, "pm:security", "--format=json"], cwd=str(cwd), timeout=timeout)
    if result.exit_code == 0 and result.stdout:
        try:
            data = json.loads(result.stdout)
            if isinstance(data, dict):
                return list(data.keys())
            if isinstance(data, list):
                return [item.get("name") for item in data if isinstance(item, dict)]
        except json.JSONDecodeError:
            pass
    # fallback to plain text parsing
    result = run_cmd([drush_bin, "pm:security"], cwd=str(cwd), timeout=timeout)
    modules = []
    for line in result.stdout.splitlines():
        if line.startswith("*"):
            modules.append(line.strip("* "))
    return modules


def _fetch_release_history(module_name: str, verify_ssl: bool) -> dict[str, Any]:
    url = f"https://updates.drupal.org/release-history/{module_name}/current"
    response = requests.get(url, timeout=20, verify=verify_ssl)
    response.raise_for_status()
    root = ET.fromstring(response.text)
    releases = []
    for release in root.findall(".//release"):
        version = release.findtext("version")
        status = release.findtext("status")
        security = release.findtext("terms/term/value")
        if version:
            releases.append({
                "version": version,
                "status": status,
                "security_term": security,
            })
    latest = releases[0] if releases else {}
    return {
        "latest_version": latest.get("version"),
        "latest_status": latest.get("status"),
        "latest_security_term": latest.get("security_term"),
        "release_count": len(releases),
    }


def check_versions() -> Path:
    config = load_config()
    logger = setup_logger("update_engine", config.logs_dir)

    logger.info("Running composer outdated")
    composer_data = _run_composer_outdated(
        config.composer_bin, config.drupal_root, config.command_timeout
    )

    logger.info("Running drush pm:security")
    security_modules = set(
        filter(None, _run_drush_security(config.drush_bin, config.drupal_root, config.command_timeout))
    )

    modules: list[dict[str, Any]] = []
    for package in composer_data.get("installed", []):
        name = package.get("name")
        if not name or not name.startswith("drupal/"):
            continue
        module_name = name.split("/", 1)[1]
        installed_version = package.get("version")
        latest_version = package.get("latest") or package.get("latest-version")

        release_info = {}
        try:
            release_info = _fetch_release_history(module_name, config.verify_ssl)
        except Exception as exc:  # noqa: BLE001
            logger.warning("Release history lookup failed for %s: %s", module_name, exc)

        security_required = module_name in security_modules
        modules.append(
            {
                "module_name": module_name,
                "installed_version": installed_version,
                "latest_version": latest_version or release_info.get("latest_version"),
                "security_update_required": security_required,
                "release_history": release_info,
            }
        )

    report = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "modules": modules,
        "security_modules": sorted(security_modules),
        "composer_raw": composer_data,
    }

    report_path = config.reports_dir / "module-updates.json"
    write_json(report_path, report)
    logger.info("Module updates report written to %s", report_path)
    return report_path


def apply_updates() -> Path:
    config = load_config()
    logger = setup_logger("update_engine", config.logs_dir)

    updates_report_path = config.reports_dir / "module-updates.json"
    if not updates_report_path.exists():
        check_versions()

    report_data = json.loads(updates_report_path.read_text())
    modules = report_data.get("modules", [])

    update_results = []
    for module in modules:
        module_name = module.get("module_name")
        if not module_name:
            continue
        update_needed = module.get("security_update_required") or (
            module.get("installed_version") != module.get("latest_version")
        )
        if not update_needed:
            continue

        logger.info("Updating module %s", module_name)
        result = run_cmd(
            [
                config.composer_bin,
                "update",
                f"drupal/{module_name}",
                "--with-dependencies",
            ],
            cwd=str(config.drupal_root),
            timeout=config.command_timeout,
        )
        update_results.append(
            {
                "module": module_name,
                "exit_code": result.exit_code,
                "stdout": result.stdout,
                "stderr": result.stderr,
            }
        )
        if result.exit_code != 0:
            logger.error("Composer update failed for %s", module_name)
            raise RuntimeError(f"Composer update failed for {module_name}")

    logger.info("Running drush updb, cr, cim")
    updb = run_cmd([config.drush_bin, "updb", "-y"], cwd=str(config.drupal_root))
    cr = run_cmd([config.drush_bin, "cr"], cwd=str(config.drupal_root))
    cim = run_cmd([config.drush_bin, "cim", "-y"], cwd=str(config.drupal_root))

    update_summary = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "updates": update_results,
        "post_update": {
            "updb": updb.exit_code,
            "cr": cr.exit_code,
            "cim": cim.exit_code,
        },
    }

    if any(code != 0 for code in [updb.exit_code, cr.exit_code, cim.exit_code]):
        raise RuntimeError("Post-update drush commands failed")

    report_path = config.reports_dir / "update-results.json"
    write_json(report_path, update_summary)
    logger.info("Update results written to %s", report_path)
    return report_path


if __name__ == "__main__":
    check_versions()
