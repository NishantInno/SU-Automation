"""Command runner with structured results and logging."""
from __future__ import annotations

from dataclasses import dataclass
import subprocess
import time
from typing import Sequence


@dataclass
class CommandResult:
    command: str
    exit_code: int
    stdout: str
    stderr: str
    duration: float


class CommandError(RuntimeError):
    def __init__(self, result: CommandResult):
        super().__init__(f"Command failed ({result.exit_code}): {result.command}")
        self.result = result


def run_cmd(
    cmd: Sequence[str] | str,
    cwd: str | None = None,
    env: dict[str, str] | None = None,
    timeout: int | None = None,
    check: bool = False,
) -> CommandResult:
    start = time.time()
    shell = isinstance(cmd, str)
    
    # If cmd is a list and first element contains spaces, split it properly
    if isinstance(cmd, (list, tuple)) and cmd and ' ' in str(cmd[0]):
        # Split the first element and combine with rest
        first_parts = str(cmd[0]).split()
        cmd = first_parts + list(cmd[1:])
    
    command_str = cmd if isinstance(cmd, str) else " ".join(cmd)

    proc = subprocess.run(
        cmd,
        cwd=cwd,
        env=env,
        capture_output=True,
        text=True,
        timeout=timeout,
        shell=shell,
    )
    duration = time.time() - start
    result = CommandResult(
        command=command_str,
        exit_code=proc.returncode,
        stdout=proc.stdout.strip(),
        stderr=proc.stderr.strip(),
        duration=duration,
    )
    if check and proc.returncode != 0:
        raise CommandError(result)
    return result
