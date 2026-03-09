"""Error detection engine that aggregates errors across reports and logs."""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from .config import load_config
from .logger import setup_logger
from .utils import read_json

ERROR_PATTERNS = [
    re.compile(r"(Fatal error|TypeError|Parse error|Exception|PDOException)", re.IGNORECASE),
    re.compile(r"SQLSTATE\[[A-Z0-9]+\]"),
]

FILE_PATTERN = re.compile(r"File:\s*(\S+)")


def _extract_errors_from_text(text: str) -> list[dict[str, Any]]:
    errors = []
    for line in text.splitlines():
        if any(p.search(line) for p in ERROR_PATTERNS):
            file_match = FILE_PATTERN.search(line)
            errors.append(
                {
                    "message": line.strip(),
                    "file": file_match.group(1) if file_match else None,
                }
            )
    return errors


def _extract_errors_from_watchdog(watchdog: Any) -> list[dict[str, Any]]:
    if isinstance(watchdog, dict):
        items = watchdog.values()
    elif isinstance(watchdog, list):
        items = watchdog
    else:
        return _extract_errors_from_text(str(watchdog))

    errors = []
    for item in items:
        if not isinstance(item, dict):
            continue
        severity = str(item.get("severity") or "").lower()
        message = str(item.get("message") or item.get("message_plain") or "").strip()
        if not message:
            continue
        if severity in {"error", "critical", "alert", "emergency"} or any(
            p.search(message) for p in ERROR_PATTERNS
        ):
            errors.append(
                {
                    "message": message,
                    "file": item.get("file") or None,
                    "severity": severity,
                }
            )
    return errors


def detect_errors() -> list[dict[str, Any]]:
    config = load_config()
    logger = setup_logger("error_engine", config.logs_dir)

    errors: list[dict[str, Any]] = []

    testing_report = read_json(config.reports_dir / "testing-results.json", {})
    watchdog = testing_report.get("watchdog")
    if watchdog:
        errors.extend(_extract_errors_from_watchdog(watchdog))

    for log_file in config.logs_dir.glob("*.log"):
        try:
            text = log_file.read_text()
        except Exception as exc:  # noqa: BLE001
            logger.warning("Could not read log %s: %s", log_file, exc)
            continue
        errors.extend(_extract_errors_from_text(text))

    # de-duplicate
    unique = []
    seen = set()
    for error in errors:
        key = (error.get("message"), error.get("file"))
        if key in seen:
            continue
        seen.add(key)
        unique.append(error)

    logger.info("Detected %s unique errors", len(unique))
    return unique


if __name__ == "__main__":
    print(json.dumps(detect_errors(), indent=2))
