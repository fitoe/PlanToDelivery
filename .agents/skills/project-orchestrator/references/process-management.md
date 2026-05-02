# Process Management

Use this file during execution, debugging, verification, and handoff.

## Goals

- prevent shell/process sprawl
- keep long-lived processes intentional
- make sessions resumable

## Rules

- Short-lived commands run in foreground.
- Long-lived processes must have a clear purpose.
- Reuse existing dev servers and watchers when possible.
- Do not launch duplicate services casually.
- Record long-lived process command, purpose, and port.
- Clean up temporary processes before ending the session unless they must persist.

## Long-Lived Process Examples

Allowed when justified:
- local dev server
- mock service
- required background worker
- watch-mode test process

## Not Worth Backgrounding

- one-off tests
- one-off build commands
- one-off scripts
- single-run lint or verification commands
