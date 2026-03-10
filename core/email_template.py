"""HTML email template generator for security update reports."""
from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any


def generate_html_email(
    before_data: dict[str, Any],
    after_data: dict[str, Any],
    update_data: dict[str, Any],
    environment: str,
    build_number: str,
    build_url: str,
) -> str:
    """Generate HTML email with before/after comparison."""
    
    # Extract key metrics
    before_modules = before_data.get("modules", [])
    after_modules = after_data.get("modules", [])
    updates_applied = update_data.get("updates", [])
    
    # Count security issues
    before_security_count = sum(1 for m in before_modules if m.get("security_update_required"))
    after_security_count = sum(1 for m in after_modules if m.get("security_update_required"))
    
    # Count outdated modules
    before_outdated = sum(1 for m in before_modules if m.get("installed_version") != m.get("latest_version"))
    after_outdated = sum(1 for m in after_modules if m.get("installed_version") != m.get("latest_version"))
    
    # Build update summary
    successful_updates = [u for u in updates_applied if u.get("exit_code") == 0]
    failed_updates = [u for u in updates_applied if u.get("exit_code") != 0]
    
    html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px 10px 0 0;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 28px;
        }}
        .header p {{
            margin: 10px 0 0 0;
            opacity: 0.9;
        }}
        .content {{
            background: #f8f9fa;
            padding: 30px;
            border-radius: 0 0 10px 10px;
        }}
        .section {{
            background: white;
            padding: 20px;
            margin-bottom: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .section h2 {{
            color: #667eea;
            margin-top: 0;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }}
        .comparison {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin: 20px 0;
        }}
        .metric {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 6px;
            text-align: center;
        }}
        .metric-label {{
            font-size: 12px;
            color: #666;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        .metric-value {{
            font-size: 32px;
            font-weight: bold;
            margin: 10px 0;
        }}
        .metric-value.good {{
            color: #28a745;
        }}
        .metric-value.warning {{
            color: #ffc107;
        }}
        .metric-value.danger {{
            color: #dc3545;
        }}
        .arrow {{
            font-size: 24px;
            margin: 0 10px;
        }}
        .arrow.down {{
            color: #28a745;
        }}
        .arrow.up {{
            color: #dc3545;
        }}
        .update-list {{
            list-style: none;
            padding: 0;
        }}
        .update-item {{
            padding: 10px;
            margin: 5px 0;
            border-left: 4px solid #28a745;
            background: #f8f9fa;
            border-radius: 4px;
        }}
        .update-item.failed {{
            border-left-color: #dc3545;
        }}
        .update-item strong {{
            color: #667eea;
        }}
        .info-grid {{
            display: grid;
            grid-template-columns: 150px 1fr;
            gap: 10px;
            margin: 10px 0;
        }}
        .info-label {{
            font-weight: bold;
            color: #666;
        }}
        .footer {{
            text-align: center;
            padding: 20px;
            color: #666;
            font-size: 12px;
        }}
        .button {{
            display: inline-block;
            padding: 12px 24px;
            background: #667eea;
            color: white;
            text-decoration: none;
            border-radius: 6px;
            margin: 10px 5px;
        }}
        .attachments {{
            background: #fff3cd;
            border: 1px solid #ffc107;
            padding: 15px;
            border-radius: 6px;
            margin: 20px 0;
        }}
        .attachments h3 {{
            margin-top: 0;
            color: #856404;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🔒 Automated Security Update Report</h1>
        <p>Build #{build_number} • Environment: {environment.upper()}</p>
        <p>{datetime.now().strftime("%B %d, %Y at %I:%M %p")}</p>
    </div>
    
    <div class="content">
        <!-- Summary Section -->
        <div class="section">
            <h2>📊 Update Summary</h2>
            <div class="comparison">
                <div>
                    <div class="metric">
                        <div class="metric-label">Security Issues</div>
                        <div class="metric-value danger">{before_security_count}</div>
                        <div>Before</div>
                    </div>
                </div>
                <div>
                    <div class="metric">
                        <div class="metric-label">Security Issues</div>
                        <div class="metric-value {'good' if after_security_count == 0 else 'warning'}">{after_security_count}</div>
                        <div>After</div>
                    </div>
                </div>
            </div>
            
            <div class="comparison">
                <div>
                    <div class="metric">
                        <div class="metric-label">Outdated Modules</div>
                        <div class="metric-value warning">{before_outdated}</div>
                        <div>Before</div>
                    </div>
                </div>
                <div>
                    <div class="metric">
                        <div class="metric-label">Outdated Modules</div>
                        <div class="metric-value {'good' if after_outdated == 0 else 'warning'}">{after_outdated}</div>
                        <div>After</div>
                    </div>
                </div>
            </div>
            
            <div class="info-grid">
                <div class="info-label">Updates Applied:</div>
                <div>{len(successful_updates)} successful, {len(failed_updates)} failed</div>
                
                <div class="info-label">Environment:</div>
                <div>{environment}</div>
                
                <div class="info-label">Build Number:</div>
                <div>#{build_number}</div>
            </div>
        </div>
        
        <!-- Updates Applied Section -->
        <div class="section">
            <h2>✅ Updates Applied</h2>
            {_generate_update_list(successful_updates, failed_updates)}
        </div>
        
        <!-- Before/After Comparison -->
        <div class="section">
            <h2>📈 Detailed Comparison</h2>
            <h3>Security Status</h3>
            <p><strong>Before:</strong> {before_security_count} module(s) with security vulnerabilities</p>
            <p><strong>After:</strong> {after_security_count} module(s) with security vulnerabilities</p>
            <p><strong>Improvement:</strong> {'✅ All security issues resolved!' if after_security_count == 0 else f'⚠️ {before_security_count - after_security_count} issue(s) resolved, {after_security_count} remaining'}</p>
            
            <h3>Module Updates</h3>
            <p><strong>Before:</strong> {before_outdated} outdated module(s)</p>
            <p><strong>After:</strong> {after_outdated} outdated module(s)</p>
            <p><strong>Updated:</strong> {before_outdated - after_outdated} module(s)</p>
        </div>
        
        <!-- Attachments Info -->
        <div class="attachments">
            <h3>📎 Attached Reports</h3>
            <p>The following JSON reports are attached to this email:</p>
            <ul>
                <li><strong>before-analysis.json</strong> - Site state before updates</li>
                <li><strong>after-analysis.json</strong> - Site state after updates</li>
                <li><strong>update-results.json</strong> - Detailed update results</li>
                <li><strong>testing-results.json</strong> - Automated testing results</li>
            </ul>
        </div>
        
        <!-- Actions -->
        <div class="section" style="text-align: center;">
            <h2>🔗 Quick Actions</h2>
            <a href="{build_url}" class="button">View Build Details</a>
            <a href="{build_url}artifact/reports/" class="button">Download All Reports</a>
        </div>
    </div>
    
    <div class="footer">
        <p>This is an automated email from Jenkins Automated Security Update Pipeline</p>
        <p>Generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
    </div>
</body>
</html>
"""
    return html


def _generate_update_list(successful: list[dict], failed: list[dict]) -> str:
    """Generate HTML list of updates."""
    if not successful and not failed:
        return "<p>No updates were applied.</p>"
    
    html = '<ul class="update-list">'
    
    for update in successful:
        module = update.get("module", "Unknown")
        html += f'<li class="update-item">✅ <strong>{module}</strong> updated successfully</li>'
    
    for update in failed:
        module = update.get("module", "Unknown")
        error = update.get("stderr", "Unknown error")
        html += f'<li class="update-item failed">❌ <strong>{module}</strong> failed: {error[:100]}...</li>'
    
    html += '</ul>'
    return html
