#!/usr/bin/env python3
"""PlanToDelivery enforcement CLI.

This script is intentionally standalone-friendly: it imports the in-project
runtime when available and drives the public Hermes Kanban CLI through
HermesKanbanBackend. Use it as the mandatory Kanban constraint wrapper instead of calling
`hermes kanban complete` directly for P2D cards.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path


def _repo_root() -> Path:
    script = Path(__file__).resolve()
    # Source checkout: <repo>/.agents/skills/plantodelivery/scripts/p2d_enforce.py
    for parent in script.parents:
        if (parent / "plantodelivery" / "kanban_runtime.py").exists():
            return parent
    # Installed skill copy: runtime is expected in --project-root / cwd.
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


def _json(data: object) -> None:
    print(json.dumps(data, ensure_ascii=False, indent=2))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="P2D Hermes Kanban constraint enforcement")
    parser.add_argument("--project-root", default=os.getcwd(), help="Project root containing project-state/kanban")
    parser.add_argument("--board", default="plantodelivery", help="Hermes Kanban board slug")
    parser.add_argument("--hermes-home", default=None, help="Optional HERMES_HOME override")
    sub = parser.add_subparsers(dest="command", required=True)

    claim = sub.add_parser("claim", help="Claim/start a P2D card before provider work")
    claim.add_argument("task_id")
    claim.add_argument("--ttl", type=int, default=3600)

    ingest = sub.add_parser("ingest", help="Validate and ingest provider result manifest")
    ingest.add_argument("result_manifest")

    approve = sub.add_parser("approve", help="Approve a review-required result and close the Hermes card")
    approve.add_argument("task_id")
    approve.add_argument("--evidence", action="append", required=True, help="Review evidence; repeatable")

    prewrite = sub.add_parser("prewrite", help="Hard-stop guard before provider writes protected files")
    prewrite.add_argument("--task-envelope", required=True, help="Path to task-envelope.json")
    prewrite.add_argument("--active-slice-digest", required=True, help="Path to active-slice-digest.json")
    prewrite.add_argument("--execution-permit", default=None, help="Path to execution-permit.json; defaults to output_root/execution-permit.json")
    prewrite.add_argument("--expected-capability", default=None, help="Optional expected provider capability")
    prewrite.add_argument("--changed-file", action="append", required=True, help="File the provider intends to mutate; repeatable")
    prewrite.add_argument("--review-required", action=argparse.BooleanOptionalAction, default=True, help="Whether the provider result will require review before completion")

    audit = sub.add_parser("audit", help="Audit board for P2D bypasses")
    audit.add_argument("--fail-on-violation", action="store_true", default=False)
    audit.add_argument("--strict-digest", action="store_true", default=False, help="Require active-slice-digest.json for every P2D card")
    audit.add_argument("--strict-provenance", action="store_true", default=False, help="Verify result provenance sha256 links for task envelope, active-slice digest, and produced artifacts")

    approval_packet = sub.add_parser("approval-packet", help="Build a review packet from a task envelope and provider result")
    approval_packet.add_argument("--task-envelope", required=True)
    approval_packet.add_argument("--result-manifest", required=True)
    approval_packet.add_argument("--output", required=True)
    approval_packet.add_argument("--review-prompt", default=None)

    resume = sub.add_parser("resume", help="Write a deterministic P2D resume snapshot")
    resume.add_argument("--state-root", default=None)
    resume.add_argument("--output", required=True)
    return parser


def main() -> int:
    pre_parser = argparse.ArgumentParser(add_help=False)
    pre_parser.add_argument("--project-root", default=os.getcwd())
    pre_args, _ = pre_parser.parse_known_args()
    _load_runtime(Path(pre_args.project_root))
    from plantodelivery.kanban_runtime import (
        HermesKanbanBackend,
        KanbanContractError,
        build_approval_packet,
        build_resume_snapshot,
    )

    args = build_parser().parse_args()
    backend = HermesKanbanBackend(
        project_root=Path(args.project_root),
        board=args.board,
        hermes_home=Path(args.hermes_home) if args.hermes_home else None,
    )
    try:
        if args.command == "claim":
            _json(backend.claim_task(args.task_id, ttl_seconds=args.ttl))
            return 0
        if args.command == "ingest":
            manifest = json.loads(Path(args.result_manifest).read_text(encoding="utf-8"))
            path = backend.record_result(manifest)
            _json({"ok": True, "result_path": str(path), "kanban_status": backend.load_index()["tasks"][manifest["task_id"]]["kanban_status"]})
            return 0
        if args.command == "approve":
            backend.approve_review(args.task_id, list(args.evidence))
            _json({"ok": True, "task_id": args.task_id, "kanban_status": "completed", "evidence": list(args.evidence)})
            return 0
        if args.command == "prewrite":
            from plantodelivery.provider_guard import assert_provider_write_allowed, validate_provider_execution_context

            context = validate_provider_execution_context(
                task_envelope_path=args.task_envelope,
                active_slice_digest_path=args.active_slice_digest,
                expected_capability=args.expected_capability,
                hermes_backend=backend,
                require_running=True,
                execution_permit_path=args.execution_permit,
            )
            assert_provider_write_allowed(
                context,
                list(args.changed_file),
                review_required=bool(args.review_required),
            )
            _json({
                "ok": True,
                "task_id": context.task_id,
                "capability": context.capability,
                "guard": "prewrite",
                "changed_files": list(args.changed_file),
                "execution_permit_path": str(context.execution_permit_path) if context.execution_permit_path else None,
            })
            return 0
        if args.command == "audit":
            report = backend.audit_enforcement(strict_digest=args.strict_digest, strict_provenance=args.strict_provenance)
            _json(report)
            return 1 if args.fail_on_violation and not report["ok"] else 0
        if args.command == "approval-packet":
            packet = build_approval_packet(
                task_envelope_path=args.task_envelope,
                result_manifest_path=args.result_manifest,
                review_prompt=args.review_prompt,
            )
            output = Path(args.output)
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(json.dumps(packet, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            _json({"ok": True, "approval_packet_path": str(output), "task_id": packet["task_id"]})
            return 0
        if args.command == "resume":
            snapshot = build_resume_snapshot(project_root=Path(args.project_root), state_root=Path(args.state_root) if args.state_root else None)
            output = Path(args.output)
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            _json({"ok": True, "resume_snapshot_path": str(output), "counts_by_status": snapshot["counts_by_status"]})
            return 0
    except (KanbanContractError, OSError, json.JSONDecodeError) as exc:
        print(f"p2d_enforce: {exc}", file=sys.stderr)
        return 2
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
