# nate-game-engine Constitution

This constitution governs the `nate-game-engine` Python package (import name `nge2`):
a reusable toolkit for game-scripting primitives (input control, vision, OCR,
find-image / find-color). It binds Spec Kit planning and implementation. Feature
specs define *what* to build; this document defines *non-negotiable how*.

Chinese companion (human-readable only): [`constitution.zh-CN.md`](./constitution.zh-CN.md).
Agents executing Spec Kit workflows MUST use this English file as the sole authority.

## Core Principles

### I. Library-First Public API

- Ship a stable, importable Python library under `src/nge2/`. Consumer game scripts
  are out of scope for this repository; they use the package, they are not the package.
- Every feature lands as library surface first. Optional CLIs or demos are thin wrappers
  only and MUST NOT own core logic.
- Public symbols are intentional: export via package `__init__` / `__all__`, document with
  docstrings, and prefer typed signatures on all public callables and data structures.
- Do not add modules whose only purpose is organizational convenience without a clear
  consumer-facing contract.

### II. Side-Effect Isolation (NON-NEGOTIABLE)

- Capabilities that touch the OS or desktop (keyboard, mouse, screen capture, OCR engines)
  MUST live behind narrow interfaces so pure logic (matching, geometry, retries, policies)
  can run without hardware.
- Default construction of value types MUST NOT send keys, move the mouse, or capture the
  screen. Engine construction MAY open required device/backends declared by the caller
  (e.g. HID serial, capture backend); further side effects happen only when the caller
  invokes an explicit action.
- Tests for pure logic MUST use fakes/mocks at the I/O boundary. Hardware-dependent checks
  are optional, explicitly marked (e.g. pytest markers), and never required for a green CI
  on a headless runner unless the feature’s own plan says otherwise.
- Package domains (`capture`, `control`, `ocr`, `yolo`, `find`, `log`, `geom`, `window`,
  `time`) stay separable at the API boundary so each can be reasoned about and tested in
  isolation even when installed together.

### III. Test Discipline

- New behavior and bug fixes include automated tests before merge/implement completion.
- Prefer fast unit tests for algorithms and policy. Use contract tests at public API edges
  when changing exported signatures or return shapes.
- Do not treat manual desktop verification as a substitute for automated coverage of
  testable logic.
- Follow pytest conventions already configured in the repo (`tests/`, `src` layout).

### IV. Full Default Install & Simplicity

- The default package install is **full**: runtime dependencies required by supported
  modules ship in the base dependency set (not optional extras), unless a later ratified
  amendment changes this.
- Prefer standard library and well-maintained dependencies. Every new runtime dependency
  needs a one-line justification in the feature plan.
- Avoid speculative abstractions and framework-shaped layers until a second real use case
  appears (YAGNI).

### V. Semantic Versioning & Compatibility

- Versioning follows SemVer (`MAJOR.MINOR.PATCH`) for the published package.
- The **git tag** (`vMAJOR.MINOR.PATCH`, optional pre-release/build suffix) is the sole source of
  truth for a published version. Local `pyproject.toml` version may be a placeholder; CI injects
  the tag before build.
- Published artifacts MUST be produced by the repository’s release CI (GitHub Release assets and
  upload to the public PyPI project `nate-game-engine`). Do not hand-publish a conflicting build
  for a tag that CI already owns.
- A version that already exists on PyPI or as a published GitHub Release MUST NOT be reused or
  overwritten. Cut a new tag for corrections.
- Breaking changes to documented public API require a MAJOR bump, a changelog note, and an
  explicit callout in the feature spec/plan.
- Prefer additive evolution (new parameters with defaults, new modules) over silent behavior
  changes. Deprecations get a documented grace period when practical.
- Unsupported platforms or environments MUST be stated clearly rather than implied.

### VI. Bilingual Requirement Documents (NON-NEGOTIABLE)

- Every requirement-facing Markdown artifact produced by Spec Kit (including but not limited
  to `spec.md`, `plan.md`, `tasks.md`, checklists, and clarify/analyze reports under feature
  directories) MUST exist in **both** an English edition and a Simplified Chinese edition.
- Naming: English files keep the canonical Spec Kit names (e.g. `spec.md`). Chinese files
  use the same basename with a `.zh-CN` suffix before the extension (e.g. `spec.zh-CN.md`).
- Any create or update of a requirement Markdown file MUST update the English and Chinese
  editions in the **same change**. Divergent or single-language-only updates are not allowed.
- Content MUST stay information-equivalent across the pair (same intent, scope, acceptance
  criteria, and constraints). Wording may be localized; facts MUST NOT drift.
- **Execution authority**: when planning, implementing, analyzing, or converging, agents
  MUST read and follow **English** Markdown only. Chinese editions (any `*.zh-CN.md`) are
  for the human maintainer whose native language is Chinese; they have **no operational
  effect** and MUST be ignored for Spec Kit execution decisions.

### VII. Bilingual Constitution (NON-NEGOTIABLE)

- This constitution is maintained as a bilingual pair:
  - English (authoritative for agents): `.specify/memory/constitution.md`
  - Simplified Chinese (human-readable only): `.specify/memory/constitution.zh-CN.md`
- Every amendment MUST update **both** files in the same change, keep them
  information-equivalent, bump **Version**, and set **Last Amended** identically on both.
- Spec Kit skills and implement/converge flows MUST treat the English constitution as the
  only binding source. The Chinese constitution MUST NOT be used as an execution input.

## Platform & Runtime Constraints

- **Primary target**: Windows. Design, test, and document against Windows first.
- **Python**: `>=3.11` as declared in `pyproject.toml`. Do not use newer syntax without
  raising the requires-python floor in the same change.
- **Packaging**: `src/` layout and `pyproject.toml` are the source of truth. Do not introduce
  a parallel packaging system without amending this constitution.
- **Import package name**: `nge2` (PyPI distribution name remains `nate-game-engine`).
- **Non-goals unless specified**: multi-OS parity, GUI application shell, full game engine,
  or shipping end-user game bots as first-class products of this package.

## Quality Gates

- Public API changes: types + docstrings + tests updated in the same change set.
- Lint/format/tooling configured for the repo (e.g. Ruff) MUST pass when present in the
  plan’s Definition of Done.
- Complexity that is not forced by a requirement MUST be rejected or deferred; justify
  exceptions in the plan.
- Spec Kit flow for features: constitution compliance is checked during plan, tasks, and
  implement/converge—not only at the end.
- Bilingual pairs: a change that touches requirement Markdown or the constitution is
  incomplete if either language edition is missing or stale.

## Governance

- This constitution supersedes informal chat agreements and ad-hoc coding preferences when
  they conflict.
- Amendments update **both** `constitution.md` and `constitution.zh-CN.md`, bump the
  constitution **Version**, and set **Last Amended**. Material rule changes should be called
  out in the next feature plan that relies on them.
- `/speckit-plan`, `/speckit-tasks`, `/speckit-implement`, and `/speckit-converge` MUST NOT
  introduce designs that violate these principles without an explicit, documented amendment.
- When unsure whether a rule applies, prefer the narrower public API, fewer dependencies
  beyond the full default set, and stronger side-effect isolation.

**Version**: 1.3.0 | **Ratified**: 2026-09-26 | **Last Amended**: 2026-09-30
