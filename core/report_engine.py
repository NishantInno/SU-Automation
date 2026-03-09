"""Stage 5: Issue reporting and HTML generation."""
from __future__ import annotations

from datetime import datetime
from pathlib import Path

from .config import load_config
from .logger import setup_logger
from .utils import read_json


def _html_escape(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def generate_report() -> Path:
    config = load_config()
    logger = setup_logger("report_engine", config.logs_dir)

    analysis = read_json(config.reports_dir / "site-analysis.json", {})
    updates = read_json(config.reports_dir / "module-updates.json", {})
    testing = read_json(config.reports_dir / "testing-results.json", {})
    ai_fixes = read_json(config.reports_dir / "ai-fix-results.json", {})
    update_results = read_json(config.reports_dir / "update-results.json", {})

    vulnerabilities = analysis.get("security_vulnerabilities", [])
    http_errors = [
        item for item in testing.get("http_checks", []) if item.get("status_code") not in {"200", "301", "302"}
    ]
    watchdog = testing.get("watchdog", [])
    php_errors = []
    db_issues = []
    if isinstance(watchdog, list):
        for item in watchdog:
            if not isinstance(item, dict):
                continue
            message = str(item.get("message") or item.get("message_plain") or "")
            if "PHP" in message or "Fatal error" in message:
                php_errors.append(message)
            if "SQLSTATE" in message or "database" in message.lower():
                db_issues.append(message)

    html = [
        "<html><head><meta charset='utf-8'><title>Automated Security Update Report</title>",
        "<style>body{font-family:Arial,sans-serif;margin:20px;}h2{border-bottom:1px solid #ccc;}table{border-collapse:collapse;width:100%;}th,td{border:1px solid #ddd;padding:8px;}th{background:#f4f4f4;}</style>",
        "</head><body>",
        f"<h1>Automated Security Update Report</h1>",
        f"<p>Generated: {_html_escape(datetime.utcnow().isoformat() + 'Z')}</p>",
        "<h2>Security Vulnerabilities</h2>",
    ]

    if vulnerabilities:
        html.append("<ul>")
        for item in vulnerabilities:
            html.append(f"<li>{_html_escape(str(item))}</li>")
        html.append("</ul>")
    else:
        html.append("<p>No vulnerabilities detected by Drush.</p>")

    html.append("<h2>Module Updates</h2>")
    html.append("<table><tr><th>Module</th><th>Installed</th><th>Latest</th><th>Security Update</th></tr>")
    for module in updates.get("modules", []):
        html.append(
            "<tr>"
            f"<td>{_html_escape(module.get('module_name',''))}</td>"
            f"<td>{_html_escape(str(module.get('installed_version','')))}</td>"
            f"<td>{_html_escape(str(module.get('latest_version','')))}</td>"
            f"<td>{'Yes' if module.get('security_update_required') else 'No'}</td>"
            "</tr>"
        )
    html.append("</table>")

    html.append("<h2>Update Failures</h2>")
    failures = [u for u in update_results.get("updates", []) if u.get("exit_code") != 0]
    if failures:
        html.append("<ul>")
        for fail in failures:
            html.append(f"<li>{_html_escape(fail.get('module',''))}: {_html_escape(fail.get('stderr',''))}</li>")
        html.append("</ul>")
    else:
        html.append("<p>No update failures recorded.</p>")

    html.append("<h2>HTTP Errors</h2>")
    if http_errors:
        html.append("<ul>")
        for err in http_errors:
            html.append(f"<li>{_html_escape(err.get('url',''))}: {_html_escape(err.get('status_code',''))}</li>")
        html.append("</ul>")
    else:
        html.append("<p>No HTTP errors detected.</p>")

    html.append("<h2>Configuration Conflicts</h2>")
    config_status = testing.get("config_status", {})
    html.append(f"<pre>{_html_escape(str(config_status))}</pre>")

    html.append("<h2>PHP Errors</h2>")
    if php_errors:
        html.append("<ul>")
        for err in php_errors:
            html.append(f"<li>{_html_escape(err)}</li>")
        html.append("</ul>")
    else:
        html.append("<p>No PHP errors detected.</p>")

    html.append("<h2>Database Issues</h2>")
    entity_updates = testing.get("entity_updates", {})
    if db_issues or entity_updates:
        if db_issues:
            html.append("<ul>")
            for err in db_issues:
                html.append(f"<li>{_html_escape(err)}</li>")
            html.append("</ul>")
        html.append(f"<pre>{_html_escape(str(entity_updates))}</pre>")
    else:
        html.append("<p>No database issues detected.</p>")

    html.append("<h2>AI Fix Attempts</h2>")
    results = ai_fixes.get("results", [])
    if results:
        html.append("<ul>")
        for res in results:
            html.append(
                f"<li>{_html_escape(str(res.get('error','')))} - Applied: {res.get('applied')}</li>"
            )
        html.append("</ul>")
    else:
        html.append("<p>No AI fixes executed.</p>")

    html.append("</body></html>")

    report_path = config.reports_dir / "security-report.html"
    report_path.write_text("\n".join(html))
    logger.info("Security report written to %s", report_path)
    return report_path


if __name__ == "__main__":
    generate_report()
