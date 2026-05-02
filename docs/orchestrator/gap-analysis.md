# Gap Analysis

## Target State
The repository should support a durable `project-orchestrator` workflow that can:

- understand the real project scope
- manage milestone-based planning
- resume across sessions
- drive implementation with strong gates and verification

## Current State
- Orchestrator skill skeleton exists
- Initial durable docs exist
- The local skill package is partially landed
- Some referenced assets are still missing

## Gaps

### Gap 1: Referenced reference files missing
- Missing: several `references/*.md` files mentioned by routing or design
- Impact: Progressive loading paths are incomplete

### Gap 2: Referenced templates missing
- Missing: several `templates/*.md` files mentioned by routing or intended workflow
- Impact: Skill cannot fully scaffold downstream artifacts

### Gap 3: Optional skill metadata missing
- Missing: agent-facing metadata such as `agents/openai.yaml`
- Impact: Skill is less polished and less discoverable in UI-driven environments

### Gap 4: Bootstrap docs could be mistaken for product docs
- Missing: clearer distinction between skill bootstrap state and separate product-planning state
- Impact: Future sessions may misread intent

## Recommended Next Stage
- `execution`

## Recommended Next Actions
1. Add the missing core reference files
2. Add the missing core templates
3. Add minimal agent metadata for the skill
4. Re-check file completeness against routing references
