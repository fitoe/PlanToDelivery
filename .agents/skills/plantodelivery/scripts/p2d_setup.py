#!/usr/bin/env python3
"""PlanToDelivery standalone setup for Hermes Kanban.

Creates/validates a Hermes Kanban board using only the public `hermes kanban`
CLI. This is safe to ship inside the skill: it never edits Hermes Agent source.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
from pathlib import Path


DEFAULT_BOARD = "plantodelivery"


def run(cmd: list[str], *, cwd: Path, env: dict[str, str], check: bool = True) -> subprocess.CompletedProcess[str]:
    proc = subprocess.run(cmd, cwd=str(cwd), env=env, text=True, capture_output=True, check=False)
    if check and proc.returncode != 0:
        raise SystemExit(f"command failed ({proc.returncode}): {' '.join(cmd)}\n{proc.stderr or proc.stdout}")
    return proc


def main() -> int:
    parser = argparse.ArgumentParser(description="Initialize PlanToDelivery's Hermes Kanban board.")
    parser.add_argument("--project-root", default=".", help="Project root associated with the board")
    parser.add_argument("--board", default=DEFAULT_BOARD, help="Hermes Kanban board slug")
    parser.add_argument("--hermes-home", default=None, help="Optional isolated HERMES_HOME")
    parser.add_argument("--write-state", action="store_true", help="Create project-state/kanban marker directory")
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    project_root.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ)
    if args.hermes_home:
        env["HERMES_HOME"] = str(Path(args.hermes_home).resolve())

    print(f"Project root: {project_root}")
    print(f"Board: {args.board}")

    run(["hermes", "kanban", "init"], cwd=project_root, env=env)
    boards_proc = run(["hermes", "kanban", "boards", "list", "--json"], cwd=project_root, env=env)
    boards = json.loads(boards_proc.stdout or "[]")
    if not any(item.get("slug") == args.board for item in boards if isinstance(item, dict)):
        run(["hermes", "kanban", "boards", "create", args.board, "--default-workdir", str(project_root)], cwd=project_root, env=env)
        print(f"Created board: {args.board}")
    else:
        print(f"Board already exists: {args.board}")

    if args.write_state:
        state_root = project_root / "project-state" / "kanban"
        state_root.mkdir(parents=True, exist_ok=True)
        marker = state_root / "README.md"
        if not marker.exists():
            marker.write_text(
                "# PlanToDelivery Kanban Overlay\n\n"
                "Hermes Kanban owns task lifecycle. This directory stores P2D semantic overlays, "
                "task envelopes, result manifests, and export/debug artifacts.\n",
                encoding="utf-8",
            )
        print(f"Ensured overlay state root: {state_root}")

    print("Setup complete. Run p2d_doctor.py or p2d_smoke.py to verify.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
