"""Stage 7: Re-verify and deploy updates in a controlled sequence."""
from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path

from .command_runner import run_cmd
from .config import load_config
from .logger import setup_logger
from .utils import read_json, write_json


def _state_path(config) -> Path:
    return config.reports_dir / "deploy-state.json"


def _load_state(config) -> dict:
    return read_json(_state_path(config), {"last_env": None})


def _save_state(config, env_name: str) -> None:
    write_json(_state_path(config), {"last_env": env_name, "timestamp": datetime.utcnow().isoformat() + "Z"})


def _ensure_flow(config, target: str) -> None:
    flow = config.deployment_flow
    if target not in flow:
        raise ValueError(f"Unsupported deployment target: {target}")
    if target == flow[0]:
        return
    state = _load_state(config)
    required_prev = flow[flow.index(target) - 1]
    if state.get("last_env") != required_prev:
        raise RuntimeError(
            f"Deployment flow violation: last_env={state.get('last_env')} required={required_prev}"
        )


def _deploy_local(config) -> None:
    run_cmd([config.composer_bin, "install", "--no-dev", "--optimize-autoloader"], cwd=str(config.drupal_root))
    run_cmd([config.drush_bin, "updb", "-y"], cwd=str(config.drupal_root))
    run_cmd([config.drush_bin, "cim", "-y"], cwd=str(config.drupal_root))
    run_cmd([config.drush_bin, "cr"], cwd=str(config.drupal_root))


def _deploy_remote(config, target: str) -> None:
    target_key = target.upper()
    source_path = Path(config.drupal_root).expanduser()
    host_env = f"DEPLOY_{target_key}_HOST"
    user_env = f"DEPLOY_{target_key}_USER"
    path_env = f"DEPLOY_{target_key}_PATH"
    port_env = f"DEPLOY_{target_key}_SSH_PORT"

    host_val = os.getenv(host_env)
    user_val = os.getenv(user_env)
    path_val = os.getenv(path_env)
    port_val = os.getenv(port_env, "22")

    if not all([host_val, user_val, path_val]):
        raise RuntimeError(
            f"Missing deployment env vars for {target}: {host_env}, {user_env}, {path_env}"
        )

    remote = f"{user_val}@{host_val}"
    source = str(source_path)
    if not source.endswith("/"):
        source = source + "/"
    rsync_cmd = [
        "rsync",
        "-az",
        "--delete",
        "--exclude=reports",
        "--exclude=logs",
        "--exclude=patches",
        "--exclude=vendor",
        "--exclude=.git",
        source,
        f"{remote}:{path_val}",
    ]
    run_cmd(rsync_cmd, cwd=str(config.drupal_root))

    remote_cmd = (
        f"cd {path_val} && composer install --no-dev --optimize-autoloader && "
        f"drush updb -y && drush cim -y && drush cr"
    )
    run_cmd(["ssh", "-p", port_val, remote, remote_cmd])


def deploy(target: str) -> Path:
    config = load_config()
    logger = setup_logger("deploy_engine", config.logs_dir)

    _ensure_flow(config, target)
    logger.info("Deploying to %s", target)

    if target == "local":
        _deploy_local(config)
    else:
        _deploy_remote(config, target)

    _save_state(config, target)
    report_path = config.reports_dir / "deploy-report.json"
    write_json(report_path, {"timestamp": datetime.utcnow().isoformat() + "Z", "target": target})
    logger.info("Deployment to %s completed", target)
    return report_path


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        raise SystemExit("Usage: deploy_engine.py <local|dev|qc|prod>")
    deploy(sys.argv[1])
