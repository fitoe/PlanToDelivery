# Kanban Provider Onboarding Checklist

Use this checklist before adding a provider to PlanToDelivery/Javis.

## Provider Identity

- [ ] Provider has a stable `provider_id`.
- [ ] Provider has `contracts/provider-manifest.json`.
- [ ] Manifest uses `provider-manifest/v1`.
- [ ] Manifest lists capabilities as neutral capability names.

## Task Contract

- [ ] Provider accepts `kanban-capability-task/v1` envelope.
- [ ] Required inputs are documented.
- [ ] Optional inputs are documented.
- [ ] Missing input behavior is documented.
- [ ] Examples include `task_id`, `correlation_id`, `capability`, `inputs`, and `orchestration`.

## Result Contract

- [ ] Provider returns `kanban-capability-result/v1` manifest.
- [ ] Artifacts are paths/URLs the orchestrator can surface.
- [ ] Evidence format is documented.
- [ ] `next_tasks` use capability names, not provider names.

## Review and Block Semantics

- [ ] Normal approval/review sets `review_required=true`.
- [ ] True missing prerequisite sets `blocked=true` with blocker details.
- [ ] Review is never mislabeled as blockage.
- [ ] Partial-but-useful output returns artifacts plus review requirement.

## Anti-Coupling Review

- [ ] PlanToDelivery does not import provider code.
- [ ] PlanToDelivery does not branch on provider internals.
- [ ] Provider does not manage kanban task graph.
- [ ] Provider can run standalone outside kanban.
- [ ] Tactical skills remain references, not providers unless explicitly onboarded.

## Verification

- [ ] Manifest validates as JSON.
- [ ] Required contract docs exist.
- [ ] Provider branch has a docs checkpoint.
- [ ] Runtime skill update is deferred until contract docs are accepted.
