# Vue Progress Overlay MVP Implementation Plan

> **For Hermes:** Implement directly in this repository, then sync the updated `project-orchestrator` skill to global `plantodelivery`.

**Goal:** Add a Vue-only progress overlay MVP to PlanToDelivery with one Vue component template and one JSON progress template.

**Architecture:** PlanToDelivery remains the progress authority. The target Vue project receives a copied `DeliveryProgressOverlay.vue` and a copied `public/orchestrator/project-progress.json`; the component polls the JSON and displays progress.

**Tech Stack:** Markdown skill docs, JSON template, Vue 3 single-file component with no external dependencies.

---

## Task 1: Add approved design document

**Objective:** Preserve the agreed MVP scope before implementation.

**Files:**
- Create: `docs/superpowers/specs/2026-05-10-vue-progress-overlay-design.md`

**Steps:**
1. Write the design document with scope, non-goals, data model, refresh strategy, integration pattern, and acceptance criteria.
2. Review for placeholders and contradictions.
3. Commit together with implementation after verification.

## Task 2: Add JSON progress template

**Objective:** Provide a minimal valid JSON file that PlanToDelivery can copy into target Vue projects.

**Files:**
- Create: `.agents/skills/project-orchestrator/templates/progress-overlay/project-progress.template.json`

**Steps:**
1. Include `schemaVersion`, `updatedAt`, `project`, `milestone`, `layers`, `blockers`, and `recent`.
2. Keep field names aligned with the design document.
3. Validate with `python -m json.tool`.

## Task 3: Add Vue overlay component template

**Objective:** Provide a self-contained Vue 3 component that reads the progress JSON and renders a floating overlay.

**Files:**
- Create: `.agents/skills/project-orchestrator/templates/progress-overlay/vue/DeliveryProgressOverlay.vue`

**Steps:**
1. Use `<script setup lang="ts">`.
2. Add props: `src`, `pollInterval`, `initialOpen`, `position`.
3. Poll `src` with cache busting.
4. Keep last valid data on fetch failure.
5. Render collapsed and expanded states.
6. Style with scoped CSS only.

## Task 4: Document skill usage rules

**Objective:** Teach PlanToDelivery when and how to use the overlay templates.

**Files:**
- Modify: `.agents/skills/project-orchestrator/SKILL.md`
- Create: `.agents/skills/project-orchestrator/references/vue-progress-overlay.md`

**Steps:**
1. Add core principle and execution rule for progress overlay.
2. Reference the new guide under UI/visible-first execution.
3. Document copy paths and checkpoint update rule.

## Task 5: Verify and sync

**Objective:** Confirm the templates are valid, commit, push, and sync the global skill copy.

**Commands:**

```bash
python -m json.tool .agents/skills/project-orchestrator/templates/progress-overlay/project-progress.template.json >/tmp/progress.json
python - <<'PY'
from pathlib import Path
p = Path('.agents/skills/project-orchestrator/templates/progress-overlay/vue/DeliveryProgressOverlay.vue')
text = p.read_text(encoding='utf-8')
assert '<script setup lang="ts">' in text
assert '<template>' in text
assert '<style scoped>' in text
PY
git diff --check
git status --short
```

**Expected:** all commands pass; only intended files changed.

**Commit:**

```bash
git add docs/superpowers/specs/2026-05-10-vue-progress-overlay-design.md docs/plans/2026-05-10-vue-progress-overlay-mvp.md .agents/skills/project-orchestrator/SKILL.md .agents/skills/project-orchestrator/references/vue-progress-overlay.md .agents/skills/project-orchestrator/templates/progress-overlay/
git commit -m "feat: add vue progress overlay templates"
git push
```
