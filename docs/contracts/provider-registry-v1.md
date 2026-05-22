# Provider Registry v1

The provider registry maps requested capabilities to provider manifests without hard-coding provider internals into PlanToDelivery.

## Registry Shape

`load_provider_registry(...)` accepts the canonical `schema` field and the legacy `schema_version` field for compatibility. Newly generated artifacts should prefer `schema`.

```json
{
  "schema": "provider-registry/v1",
  "providers": [
    {
      "provider_id": "idea-to-design",
      "manifest_path": "contracts/provider-manifest.json",
      "capabilities": ["product_visual_design", "visual_source_creation"],
      "priority": 50,
      "enabled": true
    },
    {
      "provider_id": "idea-to-tech",
      "manifest_path": "contracts/provider-manifest.json",
      "capabilities": ["technical_blueprint", "implementation_planning", "verification_strategy"],
      "priority": 50,
      "enabled": true
    },
    {
      "provider_id": "design-to-code",
      "manifest_path": "contracts/provider-manifest.json",
      "capabilities": ["visual_implementation"],
      "priority": 50,
      "enabled": true
    }
  ]
}
```

## Provider Selection

1. Filter enabled providers by requested `capability`.
2. Verify the provider manifest declares the capability.
3. Prefer higher priority only when multiple providers can satisfy the same capability.
4. If no provider matches, move the kanban task to `blocked` with a missing-provider blocker.
5. If exactly one provider matches, dispatch using the neutral task envelope.
6. If multiple providers tie, request review/escalation rather than hard-coding a provider ID.

## Anti-Coupling Rules

- PlanToDelivery must not branch on provider internals such as `if provider_id == "design-to-code"` for execution behavior.
- Provider ID may be logged, displayed, or used for manifest lookup only.
- Task requirements must be expressed as capability + acceptance criteria.
- Provider-specific commands belong in provider docs, not in registry logic.

## Registry Validation

A registry is valid when:

- `schema` is `provider-registry/v1` (`schema_version` is still accepted for legacy registries).
- Every provider has `provider_id`, `manifest_path`, `capabilities`, and `enabled`.
- Every capability is a non-empty string.
- Duplicate provider IDs are rejected.
- Missing manifests are blockers before dispatch.

## Cross-Provider Alignment

Default registry entries must stay aligned with provider-side manifests and collaboration docs:

| Provider | Provider-side manifest | Collaboration doc |
|---|---|---|
| `idea-to-design` | `IdeaToDesign/contracts/provider-manifest.json` | `IdeaToDesign/docs/provider-collaboration-v2.md` |
| `idea-to-tech` | `IdeaToTech/contracts/provider-manifest.json` | `IdeaToTech/docs/provider-collaboration-v2.md` |
| `design-to-code` | `DesignToCode/contracts/provider-manifest.json` | `DesignToCode/docs/provider-collaboration-v2.md` |

PlanToDelivery owns only the normalized registry snapshot and canonical Hermes Kanban lifecycle decisions. Provider repositories own their own task/result contract details. When a provider changes capability names, review semantics, or result fields, update both the provider manifest and this registry contract before dispatching new tasks.
