"""Configuration management for Automated Security Update."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _env_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Config:
    drupal_root: Path
    site_url: str
    drush_bin: str
    composer_bin: str
    git_bin: str
    curl_bin: str
    logs_dir: Path
    reports_dir: Path
    patches_dir: Path
    ai_api_key: str | None
    ai_api_base: str
    ai_model: str
    ai_timeout: int
    command_timeout: int
    verify_ssl: bool
    headless_enabled: bool
    fail_on_test_errors: bool
    critical_paths: list[str]
    deployment_flow: list[str]


def load_config() -> Config:
    drupal_root = Path(os.getenv("DRUPAL_ROOT", os.getcwd())).resolve()
    site_url = os.getenv("SITE_URL", "http://localhost")

    logs_dir = PROJECT_ROOT / "logs"
    reports_dir = PROJECT_ROOT / "reports"
    patches_dir = PROJECT_ROOT / "patches"

    critical_paths = [
        "/",
        "/admin",
        "/node",
        "/contact",
        "/events",
        "/news",
    ]

    deployment_flow = ["local", "dev", "qc", "prod"]

    return Config(
        drupal_root=drupal_root,
        site_url=site_url.rstrip("/"),
        drush_bin=os.getenv("DRUSH_BIN", "drush"),
        composer_bin=os.getenv("COMPOSER_BIN", "composer"),
        git_bin=os.getenv("GIT_BIN", "git"),
        curl_bin=os.getenv("CURL_BIN", "curl"),
        logs_dir=logs_dir,
        reports_dir=reports_dir,
        patches_dir=patches_dir,
        ai_api_key=os.getenv("OPENAI_API_KEY"),
        ai_api_base=os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1"),
        ai_model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
        ai_timeout=int(os.getenv("OPENAI_TIMEOUT", "60")),
        command_timeout=int(os.getenv("COMMAND_TIMEOUT", "900")),
        verify_ssl=_env_bool("VERIFY_SSL", True),
        headless_enabled=_env_bool("HEADLESS_ENABLED", False),
        fail_on_test_errors=_env_bool("FAIL_ON_TEST_ERRORS", True),
        critical_paths=critical_paths,
        deployment_flow=deployment_flow,
    )
