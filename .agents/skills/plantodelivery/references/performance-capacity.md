# Performance and Capacity

Use this file when planning performance targets, sensitive paths, efficiency strategies, and validation.

## Depth Model

Performance planning is risk-tiered.

Default:
- define basic targets
- identify sensitive paths
- choose obvious strategies early

Upgrade depth when project involves:
- high concurrency
- large datasets
- search-heavy usage
- file-heavy usage
- real-time interactions
- operationally expensive background processing

## Dual Target Model

Define both:
- user experience targets
- system behavior targets

Examples:
- perceived page response
- API latency
- job duration
- throughput or queue stability where relevant

## Sensitive Paths

Every project should identify important performance-sensitive paths.

Typical examples:
- dashboards
- large lists
- search
- uploads/downloads
- batch actions
- async processing

This focuses strategy and testing effort.

## Strategy Planning

Choose strategy per sensitive path.

Candidates:
- pagination
- caching
- batching
- async offloading
- lazy loading
- rate limiting or throttling
- query/index discipline

Do not add all strategies everywhere. Add the right strategy where justified.

## Validation Rules

Performance targets need validation plans.

Define:
- what is measured
- when it is checked
- whether lightweight or deeper validation is needed
- what counts as acceptable

## Capacity Assumptions

Even light projects should record:
- expected user or request scale
- expected data volumes
- likely file size ranges
- obvious growth thresholds

This helps avoid obviously mismatched design choices.

## Anti-Patterns

Do not:
- treat performance as only a late optimization concern
- ignore user-visible responsiveness
- declare targets with no validation path
- overdesign for huge scale with no evidence
