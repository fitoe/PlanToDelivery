# Integrations

Use this file when planning or implementing third-party or external system integrations.

## Depth Model

Integration planning is risk-tiered.

Low-risk integrations may stay light.

Upgrade planning depth for:
- payments
- identity/auth providers
- file storage
- notifications
- AI services
- webhooks
- systems that block core product value

## Core Contract Rule

For important integrations, define the contract before implementation.

Capture:
- input expectations
- output expectations
- success semantics
- failure semantics
- idempotency expectations
- rate-limit or quota concerns

Do not guess from ad hoc trial and error alone.

## Failure and Degradation

Every important integration should define:
- timeout handling
- retry policy
- non-retryable failures
- degradation behavior
- user-visible consequences
- compensation path if needed

## Local/Test Strategy

Plan whether work uses:
- real service
- sandbox
- mock

Define:
- when each mode is used
- how switching works
- what must still be verified against the real contract

This protects development speed and test stability.

## Validation and Monitoring

Important integrations should define:
- how success is verified
- what failures are logged
- what failures are monitored or alerted
- whether callback/webhook or follow-up confirmation is needed

## Anti-Patterns

Do not:
- integrate critical services without a written contract summary
- rely on real third-party availability for every local workflow
- ignore failure paths
- assume a successful happy-path call proves the integration is robust
