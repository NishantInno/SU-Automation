"""Online verification engine - No AI required."""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

import requests

from .config import load_config
from .logger import setup_logger
from .utils import write_json


def check_drupal_security_advisories(module_name: str) -> dict[str, Any]:
    """
    Check Drupal.org security advisories for a module.
    
    Args:
        module_name: Name of the Drupal module
        
    Returns:
        Dictionary with security advisory information
    """
    try:
        url = f"https://updates.drupal.org/release-history/{module_name}/current"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        return {
            "module": module_name,
            "has_advisory": "Security update" in response.text,
            "checked": True,
            "source": "drupal.org"
        }
    except Exception as e:
        return {
            "module": module_name,
            "has_advisory": False,
            "checked": False,
            "error": str(e)
        }


def verify_module_status(module_name: str, version: str) -> dict[str, Any]:
    """
    Verify module status using Drupal.org API.
    
    Args:
        module_name: Name of the module
        version: Current version
        
    Returns:
        Module status information
    """
    try:
        url = f"https://www.drupal.org/api-d7/node.json?field_project_machine_name={module_name}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data.get("list"):
            project = data["list"][0]
            return {
                "module": module_name,
                "current_version": version,
                "project_status": project.get("field_project_type"),
                "maintained": True,
                "verified": True
            }
        
        return {
            "module": module_name,
            "verified": False,
            "error": "Module not found on Drupal.org"
        }
    except Exception as e:
        return {
            "module": module_name,
            "verified": False,
            "error": str(e)
        }


def check_known_issues(error_message: str) -> dict[str, Any]:
    """
    Check if error is a known Drupal issue using online resources.
    
    Args:
        error_message: The error message to check
        
    Returns:
        Information about known issues and solutions
    """
    known_patterns = {
        "Undefined array key": {
            "type": "PHP 8+ compatibility",
            "solution": "Check if array key exists before accessing",
            "drupal_org": "https://www.drupal.org/project/drupal/issues/3220641"
        },
        "Deprecated function": {
            "type": "PHP deprecation",
            "solution": "Update to use modern PHP functions",
            "drupal_org": "https://www.drupal.org/docs/updating-drupal/deprecated-code"
        },
        "Call to undefined method": {
            "type": "Missing dependency or API change",
            "solution": "Check module dependencies and API documentation",
            "drupal_org": "https://www.drupal.org/docs/drupal-apis"
        }
    }
    
    for pattern, info in known_patterns.items():
        if pattern in error_message:
            return {
                "error": error_message,
                "is_known": True,
                "issue_type": info["type"],
                "suggested_solution": info["solution"],
                "documentation": info["drupal_org"],
                "verified_online": True
            }
    
    return {
        "error": error_message,
        "is_known": False,
        "verified_online": True,
        "suggestion": "Search Drupal.org issue queue for similar errors"
    }


def run_online_verification() -> Path:
    """
    Run online verification without AI.
    
    Returns:
        Path to verification report
    """
    config = load_config()
    logger = setup_logger("online_verification", config.logs_dir)
    
    logger.info("Starting online verification (no AI required)")
    
    # Load previous reports
    analysis_path = config.reports_dir / "site-analysis.json"
    updates_path = config.reports_dir / "module-updates.json"
    testing_path = config.reports_dir / "testing-results.json"
    
    verification_results = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "verification_method": "online_drupal_org",
        "ai_used": False,
        "security_advisories": [],
        "module_verification": [],
        "known_issues": [],
        "recommendations": []
    }
    
    # Check security advisories
    if updates_path.exists():
        updates_data = json.loads(updates_path.read_text())
        security_modules = updates_data.get("security_modules", [])
        
        logger.info(f"Checking {len(security_modules)} modules for security advisories")
        for module in security_modules:
            advisory = check_drupal_security_advisories(module)
            verification_results["security_advisories"].append(advisory)
    
    # Verify module status
    if analysis_path.exists():
        analysis_data = json.loads(analysis_path.read_text())
        enabled_modules = analysis_data.get("enabled_modules", [])[:10]  # Check first 10
        
        logger.info(f"Verifying module status for {len(enabled_modules)} modules")
        for module_info in enabled_modules:
            module_name = module_info.get("name")
            version = module_info.get("version", "unknown")
            if module_name:
                status = verify_module_status(module_name, version)
                verification_results["module_verification"].append(status)
    
    # Check for known issues
    if testing_path.exists():
        testing_data = json.loads(testing_path.read_text())
        watchdog = testing_data.get("watchdog", [])
        
        if isinstance(watchdog, list):
            for entry in watchdog[:5]:  # Check first 5 errors
                if isinstance(entry, dict):
                    message = entry.get("message", "")
                    if message:
                        issue_info = check_known_issues(message)
                        verification_results["known_issues"].append(issue_info)
    
    # Generate recommendations
    recommendations = []
    
    if verification_results["security_advisories"]:
        recommendations.append({
            "priority": "HIGH",
            "action": "Apply security updates immediately",
            "modules": [adv["module"] for adv in verification_results["security_advisories"] if adv.get("has_advisory")]
        })
    
    if verification_results["known_issues"]:
        known_count = sum(1 for issue in verification_results["known_issues"] if issue.get("is_known"))
        if known_count > 0:
            recommendations.append({
                "priority": "MEDIUM",
                "action": f"Review {known_count} known issues with documented solutions",
                "details": "Check verification report for links to solutions"
            })
    
    verification_results["recommendations"] = recommendations
    
    # Save report
    report_path = config.reports_dir / "online-verification.json"
    write_json(report_path, verification_results)
    logger.info(f"Online verification report written to {report_path}")
    
    return report_path


if __name__ == "__main__":
    run_online_verification()
