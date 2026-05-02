# Data and Permissions

Use this file during full definition, decision closure, milestone spec work, and testing planning for data-heavy or permissioned systems.

## Purpose

Define data behavior early enough that APIs, UI, tests, and security do not drift apart.

## Data Modeling Depth

Default planning depth:
- core entities
- key fields
- lifecycle

Do not stop at entity names alone.

For each core entity, define:
- purpose
- key fields
- ownership
- major relationships
- lifecycle events
- state behavior where relevant

## Permissions Model

Use a mixed model:
- define resources and actions first
- then map them to roles

This keeps behavior clear while allowing role-based execution.

## Ownership and Visibility

All core objects should define:
- who owns them
- who can view them
- who can modify them
- who can delete/archive them
- whether tenant/team boundaries apply

Do not leave these implicit for later implementation.

## State Machine Rules

If an entity has business state, define:
- allowed states
- valid transitions
- invalid transitions
- which actor can trigger which transition

State behavior affects:
- UI states
- API behavior
- tests
- audit/recovery rules

## Data Governance Rules

For each core object define:
- hard delete vs soft delete
- archive behavior if needed
- audit expectations if needed
- retention implications if relevant

Do not discover late that important records cannot safely be deleted.

## Consistency and Concurrency

For sensitive write paths, define early:
- idempotency expectations
- overwrite rules
- transaction boundaries if relevant
- concurrency handling assumptions
- stale-update handling if relevant

Not every object needs deep concurrency strategy, but high-risk writes do.

## Testing Implications

Data and permission planning should drive:
- ownership tests
- permission boundary tests
- state transition tests
- invalid transition rejection tests
- deletion/archive behavior tests
- consistency-sensitive integration tests

## Anti-Patterns

Do not:
- define permissions only as vague role names
- defer ownership rules to implementation
- leave state transitions implicit
- ignore delete/archive/audit behavior for important records
- assume concurrency can be solved later for critical writes
