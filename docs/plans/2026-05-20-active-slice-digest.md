# Active Slice Digest Implementation Plan

> **For Hermes:** Use subagent-driven-development skill to implement this plan task-by-task.

**Goal:** Add a compact, file-backed `active-slice digest` mechanism so PlanToDelivery / Javis can dispatch providers with short context instead of relying on long chat history.

**Architecture:** Extend `plantodelivery.kanban_runtime` with a deterministic digest builder that reads a task envelope, selected artifact metadata, and optional project-state summary, then writes a small `active-slice-digest/v1` artifact. The digest path is attached to the provider task/result evidence and can be stored in Hermes Kanban `P2D_META` without adding custom board fields. Provider prompts should receive the digest path plus the task envelope path, not full conversation history.

**Tech Stack:** Python stdlib, existing `plantodelivery/kanban_runtime.py`, existing JSON artifact overlay, pytest.

---

## Scope

### In scope

- Define `active-slice-digest/v1` schema.
- Generate compact digest files from `kanban-capability-task/v1` envelopes.
- Include only short, bounded fields:
  - task id and capability
  - active slice summary
  - input artifact refs
  - expected outputs
  - verification expectations
  - allowed side effects
  - blockers / cautions / stop rules
  - provider handoff instruction
- Add digest path to dispatch artifacts and `P2D_META` where appropriate.
- Add tests that prove digest size stays bounded and does not include long chat/context blobs.
- Document provider usage in PlanToDelivery skill/reference.

### Out of scope

- Full semantic summarization of arbitrary project history.
- LLM-generated summaries as source of truth.
- Replacing Hermes Kanban state.
- Adding custom Hermes Kanban fields.
- Reworking provider skills into hard-gated standalone execution.

---

## Proposed schema

File path convention:

```text
project-state/kanban/tasks/<task_id>/active-slice-digest.json
```

Schema:

```json
{
  "schema": "active-slice-digest/v1",
  "task_id": "task_001",
  "capability": "visual_implementation",
  "active_slice": {},
  "context_budget": {
    "max_chars": 6000,
    "policy": "artifact-paths-over-inline-history"
  },
  "read_first": [
    "project-state/kanban/tasks/task_001/task-envelope.json"
  ],
  "input_artifact_refs": [],
  "expected_outputs": [],
  "verification_expectations": [],
  "allowed_side_effects": [],
  "stop_rules": [],
  "handoff": {
    "provider_prompt": "Use this digest and referenced artifacts only; do not rely on prior chat history.",
    "result_manifest_path": "project-state/kanban/tasks/task_001/result-manifest.json"
  }
}
```

Rules:

- The digest is an execution hint, not canonical state.
- The task envelope and Hermes Kanban card remain canonical for dispatch/constraint.
- The digest must prefer paths over inline content.
- Large artifact content must never be copied into the digest.
- If required context cannot fit, list the artifact path under `read_first` instead of embedding it.

---

## Task 1: Add digest constants and validator

**Objective:** Introduce `ACTIVE_SLICE_DIGEST_SCHEMA` and validation helpers.

**Files:**

- Modify: `plantodelivery/kanban_runtime.py`
- Test: `tests/test_kanban_runtime.py`

**Steps:**

1. Add constant:

```python
ACTIVE_SLICE_DIGEST_SCHEMA = "active-slice-digest/v1"
```

2. Add helper `validate_active_slice_digest(digest: dict[str, Any]) -> dict[str, Any]`.

3. Validate required fields:

- `schema`
- `task_id`
- `capability`
- `active_slice`
- `context_budget`
- `read_first`
- `handoff`

4. Reject unsupported schema.

5. Add focused tests:

- valid digest passes
- missing field fails
- unsupported schema fails

**Verification:**

```bash
PYTHONPATH=. pytest tests/test_kanban_runtime.py -q
```

---

## Task 2: Build digest from task envelope

**Objective:** Generate a compact digest from a validated task envelope.

**Files:**

- Modify: `plantodelivery/kanban_runtime.py`
- Test: `tests/test_kanban_runtime.py`

**Implementation outline:**

Add:

```python
def build_active_slice_digest(
    envelope: dict[str, Any],
    *,
    task_path: str | Path | None = None,
    max_chars: int = 6000,
    stop_rules: list[str] | None = None,
) -> dict[str, Any]:
    ...
```

Behavior:

- Validate envelope schema is `kanban-capability-task/v1`.
- Copy only bounded structured fields.
- Put `task_path` into `read_first` if provided.
- Include provider prompt instruction:
  `Use this digest and referenced artifacts only; do not rely on prior chat history.`
- Include `result_manifest_path` based on envelope `output_root` or task path directory.
- Serialize once and reject if over `max_chars`.

**Tests:**

- digest contains active slice and expected outputs
- digest includes task envelope path in `read_first`
- digest rejects oversized inline payload
- digest does not include unknown `conversation`, `chat_history`, or `messages` fields from envelope extras

**Verification:**

```bash
PYTHONPATH=. pytest tests/test_kanban_runtime.py -q
```

---

## Task 3: Persist digest during dispatch

**Objective:** Write `active-slice-digest.json` beside `task-envelope.json` whenever a task is dispatched.

**Files:**

- Modify: `plantodelivery/kanban_runtime.py`
- Test: `tests/test_kanban_runtime.py`

**Implementation outline:**

1. Extend `KanbanStateStore.record_task(...)`:
   - after writing `task-envelope.json`, build digest
   - write `active-slice-digest.json`
   - add `digest_path` to index task entry

2. Extend `DispatchRecord` dataclass:

```python
@dataclass(frozen=True)
class DispatchRecord:
    provider: str
    capability: str
    envelope: dict[str, Any]
    task_path: Path
    output_root: Path
    digest_path: Path | None = None
```

3. Ensure `KanbanOrchestrator.dispatch_task(...)` returns the digest path.

4. For `HermesKanbanBackend`, include digest path in overlay evidence and optionally in `P2D_META.input_artifact_refs` or a new optional `digest_path` field if cleanly supported.

**Tests:**

- dispatch creates `active-slice-digest.json`
- returned `DispatchRecord.digest_path` exists
- overlay index includes `digest_path`
- Hermes backend dispatch still creates a card with valid `P2D_META`

**Verification:**

```bash
PYTHONPATH=. pytest tests/test_kanban_runtime.py -q
```

---

## Task 4: Add prompt handoff helper

**Objective:** Provide a short provider prompt / instruction string that references digest paths instead of embedding long context.

**Files:**

- Modify: `plantodelivery/kanban_runtime.py`
- Test: `tests/test_kanban_runtime.py`

**Implementation outline:**

Add:

```python
def render_provider_handoff_prompt(digest_path: str | Path, task_path: str | Path) -> str:
    return (
        "Use the active-slice digest and task envelope below. "
        "Do not rely on prior chat history. Read referenced artifacts as needed.\n"
        f"- Active slice digest: {digest_path}\n"
        f"- Task envelope: {task_path}\n"
        "Return a kanban-capability-result/v1 manifest with evidence paths."
    )
```

**Tests:**

- prompt includes digest path
- prompt includes task path
- prompt includes `kanban-capability-result/v1`
- prompt remains under a small fixed size, e.g. `< 1000` chars

**Verification:**

```bash
PYTHONPATH=. pytest tests/test_kanban_runtime.py -q
```

---

## Task 5: Add enforcement/audit checks

**Objective:** Ensure dispatched tasks have digest artifacts and review audit can flag missing digest where expected.

**Files:**

- Modify: `plantodelivery/kanban_runtime.py`
- Modify: `.agents/skills/plantodelivery/scripts/p2d_enforce.py`
- Test: `tests/test_kanban_runtime.py`

**Implementation outline:**

1. Extend `audit_enforcement()` to include a warning or violation for missing digest on P2D-created tasks.
2. Keep this non-breaking for legacy tasks unless `--strict-digest` is passed.
3. Add optional CLI flag to `p2d_enforce.py audit`:

```bash
--strict-digest
```

4. In strict mode, fail if any task with `P2D_META` lacks digest evidence.

**Tests:**

- audit passes legacy task without strict digest
- audit fails missing digest with strict mode
- audit passes when digest exists

**Verification:**

```bash
PYTHONPATH=. pytest tests/test_kanban_runtime.py -q
python3 .agents/skills/plantodelivery/scripts/p2d_enforce.py --project-root . --board plantodelivery audit --fail-on-violation --strict-digest
```

---

## Task 6: Update docs and runtime skill

**Objective:** Make the short-context workflow visible to users and providers.

**Files:**

- Modify: `.agents/skills/plantodelivery/SKILL.md`
- Modify: `.agents/skills/plantodelivery/references/standalone-installation.md`
- Optional create: `.agents/skills/plantodelivery/references/active-slice-digest.md`
- Sync runtime copies under `/home/imjzq/.hermes/skills/PlanToDelivery/`

**Content to add:**

- Active-slice digest is the standard short-context handoff artifact.
- Providers should receive digest path + task envelope path, not chat history.
- Digest is not canonical state; Hermes Kanban remains canonical.
- Large context must be referenced by artifact path.
- Missing critical context should become a blocker instead of guessing.

**Verification:**

```bash
cmp -s .agents/skills/plantodelivery/SKILL.md /home/imjzq/.hermes/skills/PlanToDelivery/SKILL.md
PYTHONPATH=. pytest tests/test_kanban_runtime.py -q
```

---

## Task 7: Final regression and checkpoint

**Objective:** Verify the implementation and create a clean git checkpoint.

**Commands:**

```bash
git status --short --branch
git diff --check
PYTHONPATH=. pytest tests/test_kanban_runtime.py -q
python3 -m py_compile plantodelivery/kanban_runtime.py .agents/skills/plantodelivery/scripts/p2d_enforce.py
python3 .agents/skills/plantodelivery/scripts/p2d_enforce.py --project-root . --board plantodelivery audit --fail-on-violation

git add plantodelivery/kanban_runtime.py tests/test_kanban_runtime.py .agents/skills/plantodelivery/SKILL.md .agents/skills/plantodelivery/references/standalone-installation.md .agents/skills/plantodelivery/references/active-slice-digest.md .agents/skills/plantodelivery/scripts/p2d_enforce.py docs/plans/2026-05-20-active-slice-digest.md
git commit -m "feat: add active slice digest handoff"
git push origin kanban
git fetch origin kanban
git rev-parse HEAD origin/kanban
```

**Expected result:**

- Tests pass.
- Enforcement audit passes.
- Runtime skill is synchronized.
- `HEAD` equals `origin/kanban`.

---

## Acceptance criteria

- [ ] Every newly dispatched P2D task gets an `active-slice-digest.json` artifact.
- [ ] Provider handoff can be expressed as digest path + task envelope path.
- [ ] Digest schema is validated by tests.
- [ ] Digest size is bounded and excludes chat history.
- [ ] Hermes Kanban remains the canonical execution constraint.
- [ ] Result manifests still drive ingestion and review.
- [ ] Runtime PlanToDelivery skill documents the short-context workflow.
- [ ] Strict audit can flag missing digest artifacts when enabled.

## Notes

This plan intentionally avoids adding a new database or custom Kanban fields. The digest is just a compact handoff artifact tied to the existing task envelope, result manifest, and Hermes Kanban card lifecycle.
