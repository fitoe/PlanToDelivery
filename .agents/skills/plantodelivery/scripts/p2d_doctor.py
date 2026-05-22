#!/usr/bin/env python3
"""PlanToDelivery standalone doctor for Hermes Kanban installations.

This script intentionally depends only on Python stdlib plus the public
`hermes kanban` CLI. It does not import Hermes Agent internals and does not
modify Hermes Agent source code.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path


DEFAULT_BOARD = "plantodelivery"


def _repo_root() -> Path:
    script = Path(__file__).resolve()
    for parent in script.parents:
        if (parent / "plantodelivery" / "kanban_runtime.py").exists():
            return parent
    return Path.cwd()


def _load_runtime(project_root: Path | None = None) -> None:
    candidates = []
    if project_root is not None:
        candidates.append(project_root.resolve())
    candidates.append(_repo_root())
    candidates.append(Path.cwd().resolve())
    for root in candidates:
        if str(root) not in sys.path:
            sys.path.insert(0, str(root))


def run(cmd: list[str], *, cwd: Path, env: dict[str, str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=str(cwd), env=env, text=True, capture_output=True, check=False)


def check(label: str, ok: bool, detail: str) -> bool:
    icon = "OK" if ok else "FAIL"
    print(f"[{icon}] {label}: {detail}")
    return ok


def main() -> int:
    parser = argparse.ArgumentParser(description="Check whether PlanToDelivery can run against Hermes Kanban.")
    parser.add_argument("--project-root", default=".", help="Project root to use for cwd and provider discovery")
    parser.add_argument("--board", default=DEFAULT_BOARD, help="Hermes Kanban board slug to inspect/create in setup")
    parser.add_argument("--hermes-home", default=None, help="Optional isolated HERMES_HOME for the check")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON summary")
    parser.add_argument("--required-capability", action="append", default=[], help="Provider capability that must be present; repeatable")
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    _load_runtime(project_root)
    project_root.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ)
    if args.hermes_home:
        env["HERMES_HOME"] = str(Path(args.hermes_home).resolve())

    results: list[dict[str, object]] = []

    def record(name: str, ok: bool, detail: str) -> None:
        results.append({"name": name, "ok": ok, "detail": detail})
        if not args.json:
            check(name, ok, detail)

    hermes_path = shutil.which("hermes")
    record("hermes command", bool(hermes_path), hermes_path or "not found on PATH")
    if not hermes_path:
        if args.json:
            print(json.dumps({"ok": False, "checks": results}, ensure_ascii=False, indent=2))
        return 1

    help_proc = run(["hermes", "kanban", "--help"], cwd=project_root, env=env)
    record("hermes kanban CLI", help_proc.returncode == 0, (help_proc.stderr or help_proc.stdout).strip().splitlines()[0] if (help_proc.stderr or help_proc.stdout).strip() else "available")

    init_proc = run(["hermes", "kanban", "init"], cwd=project_root, env=env)
    record("kanban init", init_proc.returncode == 0, (init_proc.stderr or init_proc.stdout).strip().splitlines()[0] if (init_proc.stderr or init_proc.stdout).strip() else "initialized")

    boards_proc = run(["hermes", "kanban", "boards", "list", "--json"], cwd=project_root, env=env)
    boards_ok = False
    board_exists = False
    detail = boards_proc.stderr.strip() or boards_proc.stdout.strip()
    if boards_proc.returncode == 0:
        try:
            boards = json.loads(boards_proc.stdout or "[]")
            boards_ok = isinstance(boards, list)
            board_exists = any(item.get("slug") == args.board for item in boards if isinstance(item, dict))
            detail = f"{len(boards)} board(s); {args.board} exists={board_exists}"
        except json.JSONDecodeError as exc:
            detail = f"invalid JSON: {exc}"
    record("boards JSON", boards_ok, detail)
    record("target board", board_exists, f"{args.board} present" if board_exists else f"{args.board} missing; run p2d_setup.py before any Javis/P2D execution")

    provider_candidates = [
        project_root / "provider-registry.json",
        project_root / "project-state" / "provider-registry.json",
        project_root / "contracts" / "provider-manifest.json",
    ]
    provider_dirs = list(project_root.glob("*/contracts/provider-manifest.json"))
    provider_ok = any(path.exists() for path in provider_candidates) or bool(provider_dirs)
    record("provider contracts", provider_ok, "found provider registry/manifests" if provider_ok else "optional but recommended before dispatch")

    provider_report = None
    try:
        from plantodelivery.kanban_runtime import diagnose_provider_registry

        provider_report = diagnose_provider_registry(project_root, required_capabilities=list(args.required_capability))
        detail = f"{len(provider_report['capabilities'])} capability(s); missing={provider_report['missing_capabilities']}"
        record("provider registry doctor", bool(provider_report["ok"]), detail)
    except Exception as exc:  # noqa: BLE001 - doctor must surface actionable diagnostics instead of crashing.
        record("provider registry doctor", False, str(exc))

    overall = all(item["ok"] for item in results if item["name"] != "provider contracts")
    if args.json:
        payload = {"ok": overall, "checks": results}
        if provider_report is not None:
            payload["provider_registry"] = provider_report
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if overall else 1


if __name__ == "__main__":
    raise SystemExit(main())
