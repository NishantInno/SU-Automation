"""Stage 6: AI-assisted issue fixing using OpenAI API."""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

import requests

from .command_runner import run_cmd
from .config import load_config
from .error_engine import detect_errors
from .logger import setup_logger
from .utils import ensure_dir, slugify, write_json


def _read_context(file_path: str, max_lines: int = 40) -> str:
    path = Path(file_path)
    if not path.is_file():
        return ""
    try:
        lines = path.read_text().splitlines()
    except Exception:
        return ""
    start = max(len(lines) - max_lines, 0)
    snippet = lines[start:]
    return "\n".join(snippet)


def _build_prompt(error: dict[str, Any], context: str) -> list[dict[str, str]]:
    message = error.get("message", "")
    file_path = error.get("file")
    content = f"""You are a Drupal core contributor. Provide a unified diff patch to fix this error.

Error:
{message}

File:
{file_path}

Context (last lines of file):
{context}

Return ONLY a unified diff patch. If unsure, propose the safest minimal fix."""
    return [
        {"role": "system", "content": "You produce precise Drupal-compatible patches."},
        {"role": "user", "content": content},
    ]


def _call_openai(messages: list[dict[str, str]], config) -> str:
    if not config.ai_api_key:
        raise RuntimeError("OPENAI_API_KEY not set")

    url = f"{config.ai_api_base}/chat/completions"
    headers = {
        "Authorization": f"Bearer {config.ai_api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": config.ai_model,
        "messages": messages,
        "temperature": 0.2,
    }
    response = requests.post(url, headers=headers, json=payload, timeout=config.ai_timeout)
    response.raise_for_status()
    data = response.json()
    return data["choices"][0]["message"]["content"]


def _extract_patch(text: str) -> str | None:
    if "diff --git" in text:
        return text[text.index("diff --git"):].strip()
    if "```" in text:
        parts = text.split("```")
        for part in parts:
            if part.strip().startswith("diff"):
                return part.strip()
    return None


def _write_patch(patch_text: str, patches_dir: Path, error_slug: str) -> Path:
    ensure_dir(patches_dir)
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    patch_path = patches_dir / f"{timestamp}-{error_slug}.patch"
    patch_path.write_text(patch_text)
    return patch_path


def _apply_patch(git_bin: str, patch_path: Path, cwd: Path) -> dict[str, Any]:
    check = run_cmd([git_bin, "apply", "--check", str(patch_path)], cwd=str(cwd))
    if check.exit_code != 0:
        return {"applied": False, "stderr": check.stderr, "stdout": check.stdout}
    apply = run_cmd([git_bin, "apply", str(patch_path)], cwd=str(cwd))
    return {"applied": apply.exit_code == 0, "stderr": apply.stderr, "stdout": apply.stdout}


def run_ai_fix_engine() -> Path:
    config = load_config()
    logger = setup_logger("ai_fix_engine", config.logs_dir)

    errors = detect_errors()
    results = []

    if not errors:
        logger.info("No errors detected; skipping AI fix engine")
        report_path = config.reports_dir / "ai-fix-results.json"
        write_json(report_path, {"timestamp": datetime.utcnow().isoformat() + "Z", "results": []})
        return report_path

    for error in errors:
        error_slug = slugify(error.get("message", "error"))[:50]
        context = _read_context(error.get("file") or "")
        messages = _build_prompt(error, context)
        try:
            logger.info("Requesting AI fix for error: %s", error.get("message"))
            response_text = _call_openai(messages, config)
            patch_text = _extract_patch(response_text)
            if not patch_text:
                raise RuntimeError("No patch found in AI response")
            patch_path = _write_patch(patch_text, config.patches_dir, error_slug)
            apply_result = _apply_patch(config.git_bin, patch_path, config.drupal_root)
            results.append(
                {
                    "error": error,
                    "patch_path": str(patch_path),
                    "applied": apply_result.get("applied"),
                    "stderr": apply_result.get("stderr"),
                }
            )
        except Exception as exc:  # noqa: BLE001
            logger.error("AI fix failed for error %s: %s", error.get("message"), exc)
            results.append({"error": error, "failed": True, "reason": str(exc)})

    report = {"timestamp": datetime.utcnow().isoformat() + "Z", "results": results}
    report_path = config.reports_dir / "ai-fix-results.json"
    write_json(report_path, report)
    logger.info("AI fix report written to %s", report_path)
    return report_path


if __name__ == "__main__":
    run_ai_fix_engine()
