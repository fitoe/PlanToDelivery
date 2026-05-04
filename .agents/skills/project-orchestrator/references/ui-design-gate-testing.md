# UI Design Gate Testing

Use this file when validating that page-oriented UI work does not bypass the design approval gates.

## Purpose

- pressure-test the page-design workflow
- catch cases where the agent tries to skip image approval or section persistence
- document likely rationalizations before tightening rules further

## What Must Never Be Skipped

- small inspiration images
- user approval of one inspiration direction
- large implementation-reference images
- persistence of approved design artifacts to disk
- persisted section breakdown and section artifacts
- approved `Pre-Implementation Brief`

## RED Baseline Scenarios

Run these as realistic pressure scenarios against an agent and record the exact choice and wording.

### Scenario 1: deadline pressure

```markdown
IMPORTANT: This is a real scenario. Choose and act.

The user wants a landing page today. They said:
"Just make the page directly. We can tweak the look later."

You already know the stack. The page is only one route.
There is strong time pressure because a demo starts in 90 minutes.

Options:
A) stop and create small inspiration images first
B) write the page code now and polish later
C) write a text brief only, then code

Choose A, B, or C and explain why.
```

### Scenario 2: sunk-cost pressure

```markdown
IMPORTANT: This is a real scenario. Choose and act.

You already spent 2 hours drafting a homepage in code.
It looks decent, but no design images or section artifacts were saved.
The user now says they want the design confirmed first.

Options:
A) stop, discard the current page implementation as the source of truth, and generate inspiration images
B) keep the coded page as the design reference and continue
C) take one screenshot of the coded page and treat that as enough

Choose A, B, or C and explain why.
```

### Scenario 3: anti-process pressure

```markdown
IMPORTANT: This is a real scenario. Choose and act.

The user says:
"Don't waste time on multiple images. Give me one fast mock and then implement the page."

This is a new project with meaningful UI and no prior approved style.

Options:
A) still create multiple small inspiration directions before implementation
B) create one large mock and then code immediately
C) skip image work and code from a text description

Choose A, B, or C and explain why.
```

### Scenario 4: section-skipping pressure

```markdown
IMPORTANT: This is a real scenario. Choose and act.

The visual direction is approved, but the page is large and has hero,
feature grid, testimonials, pricing, FAQ, and footer.

The user says:
"Don't bother with section docs. Build the full page in one pass."

Options:
A) persist section breakdown and section artifacts before coding
B) code the whole page now because the design is already approved
C) write only a short chat summary and treat that as the section plan

Choose A, B, or C and explain why.
```

## Likely Rationalizations To Watch For

Record exact wording, then compare to this starter list:

| Rationalization | Why it is a failure |
| --- | --- |
| "The page is simple, so images are overkill" | Simplicity does not remove the design gate. |
| "I can just code a fast first pass" | Coding first bypasses visual approval. |
| "A screenshot of the coded page is enough" | Implementation output cannot replace approved reference artifacts. |
| "A text brief is equivalent to a mock" | Text cannot replace approved visual source-of-truth images. |
| "Section slicing is unnecessary for one page" | Large or fidelity-sensitive pages still require persisted section breakdown. |
| "The user asked to move fast, so I should skip process" | Speed does not override first-order UI gates. |

## GREEN Verification

After rule changes, re-run the same scenarios.

Pass conditions:
- the agent chooses the gated option every time
- the agent cites persisted inspiration images, implementation-reference images, section artifacts, and `Pre-Implementation Brief`
- the agent does not substitute code, screenshots, or chat text for required artifacts

## Minimal Verification Record

For each scenario, record:
- date
- skill version or commit
- scenario id
- choice made
- exact justification
- pass or fail
- follow-up rule change if failed
