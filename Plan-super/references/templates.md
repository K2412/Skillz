# Super Plan — Templates

## Research Cache

```markdown
# Research: {Topic}

**Date**: {date}
**Feature**: {feature name}

## Prior Art in Repo

- {file:line} — {what it does and why it's relevant}

## External Dependencies

- **{Package/API}**: {version, purpose, gotchas}

## Decisions Found

- {decision from git log or docs}: {why}

## Key Findings

{2-5 bullet points of most important findings}

## Open Questions

- {question that needs answering before implementation}
```

---

## PRD

```markdown
# PRD: {Feature Name}

**Status**: Draft | Review | Approved
**Owner**: {name}
**Date**: {date}

## Overview

{1-2 sentences: what this is and why it exists}

## Problem

{What user/business problem does this solve?}

## Goals

- {Measurable goal 1}
- {Measurable goal 2}

## Non-Goals

- {What we are explicitly NOT doing}

## Requirements

### Functional

- [ ] {Requirement 1}
- [ ] {Requirement 2}

### Non-Functional

- [ ] {Performance, security, accessibility requirements}

## Open Questions

- [ ] {Question that must be resolved before implementation}
```

---

## Ticket

```markdown
## T-{nn}: {Imperative title}

**Depends on**: T-{xx}, T-{yy} (or "none")
**Size**: S | M | L

### Context

{1-2 sentences explaining why this ticket exists}

### Acceptance Criteria

- [ ] {Verifiable criterion 1}
- [ ] {Verifiable criterion 2}
- [ ] {Verifiable criterion 3}

### Execution Notes

{Optional hints for implementing agent: files to touch, patterns to follow, gotchas}
```

---

## QA Checklist

```markdown
## QA: {Feature Name}

### Happy Path

- [ ] {Step}: expect {outcome}
- [ ] {Step}: expect {outcome}

### Edge Cases

- [ ] {Scenario}: expect {outcome}

### Regression

- [ ] {Existing behaviour that must not break}

### Performance

- [ ] {Load / response time check if relevant}
```
