# Security Policy

## Scope

This repository primarily contains a workflow skill package, templates, and repository-side orchestration docs.

Security issues may still matter when they affect:

- secret handling guidance
- auth/authz guidance
- unsafe workflow recommendations
- repository-level sensitive data exposure
- generated templates that encourage insecure defaults

## Reporting

If you find a security issue:

1. Do not publish exploit details immediately in a public issue.
2. Report the problem privately to the repository owner first.
3. Include:
   - affected file(s)
   - issue summary
   - impact
   - reproduction or reasoning
   - suggested mitigation if known

## Good Security Reports

A useful report includes:

- exact location
- why it is risky
- realistic impact
- whether it is documentation-only or workflow-affecting

## Examples of Relevant Issues

- templates that encourage committing secrets
- workflow guidance that weakens auth/authz boundaries
- recovery/docs flow that leaks sensitive information
- recommendations that create unsafe deployment or integration defaults

## Response Expectations

Security-related issues should be triaged before normal enhancement work when the impact is credible.
