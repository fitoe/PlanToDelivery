#!/usr/bin/env python3
"""PlanToDelivery standalone Hermes Kanban smoke test.

The smoke test creates an isolated temporary Hermes home by default, creates a
board and a task card with a P2D_META marker, claims it, completes it, and checks
that the card reaches `done`.
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import subprocess
import tempfile
from pathlib import Path


DEFAULT_BOARD = "p2d-smoke"


def b64url(data: dict[str, object]) -> str:
    raw = json.dumps(data, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")


def run(cmd: list[str], *, cwd: Path, env: dict[str, str]) -> subprocess.CompletedProcess[str]:
    proc = subprocess.run(cmd, cwd=str(cwd), env=env, text=True, capture_output=True, check=False)
    if proc.returncode != 0:
        raise SystemExit(f"command failed ({proc.returncode}): {' '.join(cmd)}\n{proc.stderr or proc.stdout}")
    return proc


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a minimal PlanToDelivery/Hermes Kanban smoke test.")
    parser.add_argument("--project-root", default=".", help="Project root associated with the smoke board")
    parser.add_argument("--board", default=DEFAULT_BOARD, help="Smoke board slug")
    parser.add_argument("--hermes-home", default=None, help="Use an existing Hermes home instead of a temporary isolated one")
    parser.add_argument("--keep-home", action="store_true", help="Print and keep the temporary Hermes home path")
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    project_root.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ)
    temp_dir: tempfile.TemporaryDirectory[str] | None = None
    if args.hermes_home:
        hermes_home = Path(args.hermes_home).resolve()
    else:
        temp_dir = tempfile.TemporaryDirectory(prefix="p2d-hermes-")
        hermes_home = Path(temp_dir.name)
    env["HERMES_HOME"] = str(hermes_home)

    run(["hermes", "kanban", "init"], cwd=project_root, env=env)
    run(["hermes", "kanban", "boards", "create", args.board, "--default-workdir", str(project_root)], cwd=project_root, env=env)

    meta = {
        "schema": "p2d-meta/v1",
        "task_id": "p2d-smoke-task",
        "capability": "technical_blueprint",
        "active_slice": {"goal": "standalone smoke"},
        "provider": "idea-to-tech",
        "output_root": str(project_root / "project-state" / "kanban" / "tasks" / "p2d-smoke-task"),
        "input_artifact_refs": [],
        "expected_outputs": ["result-manifest.json"],
        "verification_expectations": ["Hermes Kanban card reaches done"],
        "allowed_side_effects": ["temporary smoke board only"],
    }
    body = "P2D standalone smoke\n<!-- P2D_META " + b64url(meta) + " P2D_META -->"
    created = run([
        "hermes", "kanban", "--board", args.board, "create", "p2d-smoke-task",
        "--body", body,
        "--assignee", "idea-to-tech",
        "--workspace", f"dir:{project_root}",
        "--created-by", "plantodelivery",
        "--json",
    ], cwd=project_root, env=env)
    task_id = json.loads(created.stdout)["id"]
    run(["hermes", "kanban", "--board", args.board, "claim", task_id, "--ttl", "30"], cwd=project_root, env=env)
    run([
        "hermes", "kanban", "--board", args.board, "complete", task_id,
        "--result", "completed",
        "--summary", "PlanToDelivery standalone smoke completed",
    ], cwd=project_root, env=env)
    shown = run(["hermes", "kanban", "--board", args.board, "show", task_id, "--json"], cwd=project_root, env=env)
    status = json.loads(shown.stdout)["task"]["status"]
    if status != "done":
        raise SystemExit(f"unexpected final status: {status}")

    print(json.dumps({"ok": True, "board": args.board, "task_id": task_id, "status": status, "hermes_home": str(hermes_home)}, ensure_ascii=False, indent=2))
    if temp_dir is not None and args.keep_home:
        temp_dir.cleanup = lambda: None  # type: ignore[method-assign]
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
