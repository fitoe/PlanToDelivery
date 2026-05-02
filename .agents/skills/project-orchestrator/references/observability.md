# Observability

Use this file when planning logs, diagnostics, event instrumentation, health checks, and alerting.

## Purpose

Make the system explain itself well enough that debugging, verification, and release confidence are practical.

## Depth Model

Observability is risk-tiered.

Default baseline:
- structured logs
- error classification
- key event instrumentation
- minimal health/diagnostics

Upgrade for:
- multi-step workflows
- async/background jobs
- admin systems
- payment or business-critical flows
- production systems with real operational stakes

## Logging Rules

Default to structured logging.

Define:
- log levels
- common fields
- request/task correlation information
- restrictions on sensitive data in logs

Avoid unstructured print-debugging as the only strategy.

## Error Taxonomy

Classify at least:
- business errors
- system errors
- external dependency errors
- security/permission errors

Define:
- what is logged
- what is surfaced
- what is alert-worthy
- whether trace or error IDs are used

## Event Instrumentation

Track key business events, not every event.

Good candidates:
- completion of critical user flows
- failure at critical checkpoints
- important lifecycle transitions
- high-value side effects

Use instrumentation to support:
- verification
- debugging
- product understanding

## Health and Diagnostics

Define minimum diagnostics early:
- basic health/readiness check if relevant
- dependency status visibility if relevant
- minimal environment/runtime visibility

## Alerting Rules

Define what should:
- be logged only
- surface as an error
- require human attention
- block release or trigger rollback

Not every error deserves alerting.

## Anti-Patterns

Do not:
- postpone all observability to after shipping
- log without structure
- alert on everything
- ignore correlation between logs and user-visible failures
- rely solely on manual reproduction for operations insight
