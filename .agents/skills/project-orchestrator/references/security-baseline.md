# Security Baseline

Use this file during planning, milestone definition, implementation review, and security-sensitive testing.

## Security Depth Model

Security planning is risk-tiered.

Default:
- baseline security for all projects

Upgrade depth when project involves:
- sensitive data
- payments
- admin backends
- multi-tenant boundaries
- destructive operations
- externally exposed high-value flows

## Baseline Areas

At minimum, plan:
- authentication approach
- authorization model
- input validation
- output exposure control
- secret/config handling
- upload or rich-input boundaries if relevant
- security-focused tests

## Authentication Rules

Prefer mature solutions unless constraints justify deeper control.

Choose based on:
- integration needs
- deployment constraints
- compliance needs
- product complexity

Avoid casual self-built auth.

## Authorization Rules

Treat authn and authz separately.

Define:
- what resources exist
- what actions matter
- what roles or actors may perform them
- what conditions restrict access

This should be explicit, not hidden in feature prose.

## Input and Output Protection

Plan protection for:
- form/API inputs
- file uploads
- rich text or untrusted content
- error exposure
- sensitive field output

Do not allow "we will sanitize later" as a default.

## Secret Management

Secrets must not live in source control.

Define:
- secret sources
- exposure boundaries
- injection method
- minimal rotation/replacement expectation

## High-Risk Operations

If a milestone includes destructive or high-impact actions, define protection before implementation of that feature.

Examples:
- deletion
- bulk mutation
- export
- permission changes
- irreversible approval or confirmation

Protection may include:
- elevated permission
- confirmation step
- audit logging
- compensating/recovery strategy

## Security Testing

Include security-focused checks in test planning.

Baseline candidates:
- authz boundary checks
- forbidden action checks
- input validation checks
- upload restrictions
- sensitive output checks

## Anti-Patterns

Do not:
- rely on "internal only" as a security model
- combine authn/authz ambiguously
- commit secrets
- leave high-risk operations undefined until implementation
- omit security checks from milestone testing
