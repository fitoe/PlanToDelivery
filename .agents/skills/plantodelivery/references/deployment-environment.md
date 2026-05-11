# Deployment and Environment

Use this file when planning or reviewing environment, deployment, migration, release, and recovery decisions.

## Default Model

For most projects, start with:
- local environment
- production environment

Do not force test/staging environments unless project risk or operational needs justify them.

## Planning Goals

Define enough early that deployment does not become a late-stage surprise.

At minimum, planning should clarify:
- deployment target type
- environment variable inventory
- persistence assumptions
- migration expectations
- release verification
- rollback path
- backup and recovery baseline

## Environment Rules

- Local environment must be practical for day-to-day work.
- Production assumptions must be explicit before release planning.
- Sensitive configuration belongs in environment management, not source control.

## Deployment Strategy Rules

Choose deployment shape by project type.

Prefer lighter operations by default:
- hosted platform first for lightweight apps
- self-managed only when justified by constraints

Justify self-managed deployment with concrete reasons such as:
- networking constraints
- long-running infrastructure needs
- platform incompatibility
- compliance or operational requirements

## Environment Variable Rules

Maintain a strict variable inventory.

For each variable define:
- purpose
- sensitivity
- required/optional status
- where used
- default strategy

Do not allow deploy-time guessing.

## Migration Rules

If project has persistent data:
- define migration approach early
- define seed/init behavior
- define how local and production evolve safely

Migration planning should answer:
- what changes
- how it is applied
- how success is verified
- how failure is recovered

## Release Rules

Deployment success is not release success.

A release requires:
- pre-release checks
- post-deploy checks
- health verification
- critical flow verification
- rollback clarity

## Backup and Recovery Rules

Even lightweight projects should define:
- what must be recoverable
- what level of data loss is acceptable
- what basic recovery path exists

Scale depth by project risk, but do not leave it undefined.

## Anti-Patterns

Do not:
- defer all environment planning until first deploy
- commit secrets to source
- invent migrations ad hoc during release
- treat rollback as optional
- ship without a release checklist
