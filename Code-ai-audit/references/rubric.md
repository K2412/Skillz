# Codebase AI Love — Scoring Rubric

Score each dimension 0–5. Use half-points if needed (e.g., 3.5).

---

## 1. Feedback Loops (0–5)

How quickly can an agent verify that a change is correct?

| Score | Criteria |
|---|---|
| 5 | Full suite runs in <30s; typecheck + lint + tests all configured; CI mirrors local |
| 4 | Full suite runs in <2min; all gates present but CI differs slightly |
| 3 | Tests exist and pass; suite takes 2–10min or some gates missing |
| 2 | Tests exist but are slow, fragile, or require manual setup |
| 1 | Some tests but unreliable or incomplete |
| 0 | No automated feedback; manual verification only |

**Key signals**: `Makefile`/`justfile` with standard targets, fast test suite, `mypy`/`phpstan`/`tsc` configured, `ruff`/`phpcs`/`eslint` configured.

---

## 2. Navigability (0–5)

Can an agent find what it needs quickly from file names and structure alone?

| Score | Criteria |
|---|---|
| 5 | Files named for what they do; one concept per file; clear domain boundaries; useful README |
| 4 | Mostly clear structure with minor navigation friction |
| 3 | Understandable with some exploration; mixed naming conventions |
| 2 | Flat or overly nested; unclear file responsibilities |
| 1 | Very difficult to navigate; requires reading many files to understand intent |
| 0 | No discernible structure |

**Key signals**: Domain-separated directories, consistent naming convention, short files (<300 lines), clear entry points.

---

## 3. Deep Modules (0–5)

Are public interfaces simple and stable while implementations are hidden?

| Score | Criteria |
|---|---|
| 5 | All public APIs are minimal; implementation is hidden; easy to swap internals |
| 4 | Most modules are deep; occasional leaky abstraction |
| 3 | Mix of deep and shallow modules; some unnecessary exposure |
| 2 | Many shallow modules; callers must know implementation details |
| 1 | Mostly pass-through; every change ripples widely |
| 0 | No abstraction; everything is public and coupled |

**Key signals**: Few public methods per class, stable interfaces, internal helpers are private, DTOs/value objects used at boundaries.

---

## 4. Boundary Integrity (0–5)

Are module/layer contracts explicit and enforced?

| Score | Criteria |
|---|---|
| 5 | Layer boundaries enforced (e.g., deptrac, import-linter); contracts documented |
| 4 | Boundaries mostly respected; occasional cross-layer calls without enforcement |
| 3 | Informal boundaries exist and are mostly followed |
| 2 | Some layering but frequently violated |
| 1 | Boundaries exist in name only |
| 0 | No boundaries; everything depends on everything |

**Key signals**: Dependency analysis tools configured, interface/contract types at boundaries, no direct DB calls from controllers.

---

## 5. Grey-box Tests (0–5)

Do tests exist at internal seams, not just at HTTP endpoints?

| Score | Criteria |
|---|---|
| 5 | Tests at every meaningful internal boundary; seam tests for all key integrations |
| 4 | Good seam coverage; minor gaps |
| 3 | Some seam tests; mostly happy-path only |
| 2 | Mostly end-to-end; internal boundaries untested |
| 1 | Only smoke tests or integration tests at the outermost layer |
| 0 | No tests or only UI-level tests |

**Key signals**: Unit tests for service/action/use-case classes, contract tests for external integrations, test doubles at boundaries.
