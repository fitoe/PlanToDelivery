# Release Checklist

Use before releasing changes to any of the coordinated skills.

Check:
- standalone usage still works for `idea-to-design`
- standalone usage still works for `design-to-code`
- `PlanToDelivery` still routes by artifact evidence, not hard dependency
- contract version changes are documented
- artifact manifest shape remains compatible
- approval record shape remains compatible
- gate checks still block missing approvals
- installed skill directories are synced when local release is intended
- acceptance scenarios were reviewed

Do not release if:
- a specialized skill requires `PlanToDelivery` to run
- `PlanToDelivery` requires one specific producer when equivalent artifacts exist
- gate bypass can happen without explicit user risk acceptance
