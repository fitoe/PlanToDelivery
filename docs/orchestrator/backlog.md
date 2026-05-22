# Backlog

## Must Handle Now
- Complete repository intake for the selected real trial project before dispatch.
- Fill core orchestrator planning docs with real project content.
- Keep WSL canonical source references current for PlanToDelivery and provider skills.

## Next Milestone Candidates
- Create milestone-specific spec and test plan after intake.
- Add a first-class `init-project` command that writes project aliases, bootstraps provider registry from WSL canonical providers, initializes the Hermes Kanban board, and emits doctor/resume/audit evidence in one safe flow.
- Improve `p2d_doctor.py` so it can accept an explicit provider-registry file path or auto-detect `project-state/provider-registry.json` without treating a file path as a directory.
- Add a Feishu-friendly human approval packet renderer on top of `p2d-approval-packet/v1` so user review shows confirm targets, unlocks, choices, and evidence clearly.
- Add a Markdown audit report command that summarizes Ready / Review / Blocked / Running / Next Action rather than only emitting machine JSON.

## M2 Trial Notes
- 2026-05-22: Trial preparation against `若水` was intentionally paused before starting real project execution because the user said not to start 若水 yet.
- Preparation performed before pause: project aliases and provider registry evidence were written under the 若水 project-state, and setup/doctor/resume/audit commands were exercised.
- Friction found during preparation: `p2d_doctor.py --project-root <provider-registry.json>` fails because the script always calls `mkdir()` on `--project-root`; this confirms the need for explicit `--provider-registry` or file-path handling.
- Friction found during preparation: a cold project with no P2D overlay tasks produces an empty resume snapshot and a passing audit; the human-facing report should explain “no trial card has been started” instead of looking like a completed flow.

## Future Ideas
- Expand the local orchestrator skill with remaining templates and references only when real trial use shows a concrete need.
- Auto-discover provider manifests from `/home/imjzq/Projects/{IdeaToDesign,DesignToCode,DesignToTypst,IdeaToTech}` and normalize them into project-local snapshots.
- Add tests that prevent docs from regressing to Windows-mounted canonical source references for PlanToDelivery.

## Not Doing
- Full project implementation before intake and decision closure.
- Starting the 若水 M2 trial until the user explicitly resumes that project.
