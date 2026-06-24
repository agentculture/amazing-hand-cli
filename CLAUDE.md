# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

**amazing-hand-cli** is an AgentCulture mesh agent cloned from `culture-agent-template`.
Its *intended* domain is an "Agent and CLI for controlling the Amazing Hand robotic
hand (Pollen Robotics)" — **but that domain is not built yet.** Runtime
`dependencies = []` and the only code present is the generic agent-first CLI
*scaffold*: the introspection verbs `whoami`, `learn`, `explain`, `overview`,
`doctor`, and the `cli` noun group. There is no hardware/serial/kinematics code.

When you build the hand-control domain, add it as a new noun group (see
[Adding a command or domain](#adding-a-command-or-domain)) — do not rewrite the
scaffold verbs; they satisfy the agent-first rubric the CI gate enforces.

## Commands

The project uses **uv**. The console command is **`amazing-hand`** (not
`amazing-hand-cli` — see [the naming split](#the-three-name-split-important)).

```bash
uv sync                                            # create .venv, install dev deps
uv run pytest -n auto -q                           # full test suite (xdist parallel)
uv run pytest tests/test_cli.py::test_whoami_text  # a single test
uv run amazing-hand whoami                          # run the CLI (any verb)
uv run python -m amazing_hand whoami                # same, via module entry point

# Lint gates CI runs (all must pass — see .github/workflows/tests.yml):
uv run black --check amazing_hand tests
uv run isort --check-only amazing_hand tests
uv run flake8 amazing_hand tests
uv run bandit -c pyproject.toml -r amazing_hand
markdownlint-cli2 "**/*.md" "#node_modules" "#.local" "#.claude/skills" "#.teken"
uv run teken cli doctor . --strict                 # the agent-first rubric gate

# Coverage (CI flags; fail_under = 60 in pyproject.toml):
uv run pytest -n auto --cov=amazing_hand --cov-report=xml:coverage.xml --cov-report=term
```

Use the `run-tests` skill (`uv run pytest` + xdist + coverage) and `sonarclaude`
skill for quality-gate queries instead of re-deriving the invocations.

## Architecture

The CLI is a thin argparse dispatcher with a strict, agent-readable I/O contract.
Understanding it requires reading these files together:

- **`amazing_hand/cli/__init__.py`** — `main()` → `_build_parser()` →
  `_dispatch()`. Each verb registers itself; `_dispatch` calls the handler and
  translates exceptions to exit codes. `_CliArgumentParser` overrides
  `.error()` so even argparse-level errors (unknown verb, bad flag) route through
  the structured `error:`/`hint:` format and exit 1 — never argparse's default
  stderr/exit-2. `--json` is peeked from raw argv *before* parsing (the
  `_json_hint` class attr) so parse-time errors still honour JSON mode.
- **`amazing_hand/cli/_commands/*.py`** — one module per verb. Each exposes a
  `register(sub)` that adds its subparser and `set_defaults(func=...)`. This is
  the **only** extension seam: add a verb by writing a module with `register()`
  and calling it from `_build_parser()`. Handlers return `None`/`0` for success
  or raise `CliError`; any other exception is caught and wrapped so no traceback
  leaks.
- **`amazing_hand/cli/_errors.py`** — `CliError(code, message, remediation)` plus
  the exit-code policy: `0` success, `1` user error, `2` environment error, `3+`
  reserved. This is the single source of truth for exit codes.
- **`amazing_hand/cli/_output.py`** — the **stdout/stderr split is an invariant**:
  results → stdout, errors/diagnostics → stderr, *never mixed*. In `--json` mode
  both stay structured. Agents parse output by relying on this; don't print
  progress to stdout or interleave a human line into JSON.
- **`amazing_hand/explain/catalog.py`** — `ENTRIES` maps command-path tuples
  (`("whoami",)`, `("cli", "overview")`) to verbatim markdown. `explain` resolves
  against it. **Every registered noun/verb must have a catalog entry**, and the
  root key must match the console command name (this is what the rubric checks —
  see below). `tests/test_cli.py::test_every_catalog_path_resolves` guards that
  every key resolves.
- **`amazing_hand/cli/_commands/whoami.py`** — reads identity from `culture.yaml`
  by **hand-parsing the YAML** (no PyYAML), because the runtime must keep
  `dependencies = []`. `find_culture_yaml()` walks up from `__file__` (not CWD) so
  it reports *this agent's* identity; a wheel install with no `culture.yaml`
  falls back to literal defaults. If you ever need richer config, preserve the
  zero-runtime-deps constraint (parse by hand or gate behind an optional extra).
- **`amazing_hand/cli/_commands/doctor.py`** — mirrors the invariants
  `steward doctor` checks: `backend` in `culture.yaml` must map to its prompt file
  (`claude`→`CLAUDE.md`, `colleague`→`AGENTS.colleague.md`, `acp`→`AGENTS.md`,
  `gemini`→`GEMINI.md`) and `.claude/skills/` must be present. Exits 1 when
  unhealthy.

### The agent-first rubric (the CI gate that breaks easily)

`uv run teken cli doctor . --strict` (CI's `afi rubric gate` step) enforces seven
bundles the scaffold is designed to pass: `learn` ≥200 chars mentioning purpose /
exit codes / `--json` / `explain`; structured `error:`/`hint:` on failure with no
traceback; a global `overview` *and* a `cli overview` noun; descriptive verbs that
never hard-fail on a bad path (`overview <bogus>` still exits 0); `doctor`
emitting `{healthy, checks:[{id,passed,severity,message,remediation}]}`; and
`explain <command>` resolving (the `explain_self` check). When you add a verb,
re-run the gate — it's the fastest way to catch a missing catalog entry or a
contract violation.

## The three-name split (important)

Like the sibling AgentCulture CLIs (`ec2-cli`, `cloudai-cli`, `ec2bedrock-cli`),
three names are deliberately distinct:

| Name | Value | Where |
|------|-------|-------|
| Console command | `amazing-hand` | `[project.scripts]` — what users type |
| Dist / PyPI / mesh nick | `amazing-hand-cli` | `pyproject.toml` name, `culture.yaml` suffix, sonar key `agentculture_amazing-hand-cli`, URLs, `_FALLBACK_NICK`, `_ISSUES_URL` |
| Python package | `amazing_hand` | the importable module |

**Reconciled (rubric green).** The command-surface strings were swept to
`amazing-hand`: argparse `prog`/description, the `explain` catalog bodies + root
heading (`("amazing-hand",)` is the **primary** key; `("amazing-hand-cli",)`
remains a back-compat alias), the `learn` `_TEXT`/`tool`/`explain_pointer`, the
`overview`/`cli` subjects, `doctor` output text, the `explain` remediation, and
the README examples. `amazing-hand-cli` is kept **only** as the dist/nick
identity: the `_pkg_version` lookup in `amazing_hand/__init__.py`, `_ISSUES_URL`,
`_FALLBACK_NICK` / the `whoami` nick (sourced from `culture.yaml` suffix), the
catalog alias, and the `nick:` test assertions. If you re-run the sweep after a
fresh template re-clone, preserve exactly that keep-list — moving any of it to
`amazing-hand` breaks the PyPI metadata lookup or the mesh nick.

## Identity & prompt files

`culture.yaml` declares **`backend: colleague`** (model
`sakamakismile/Qwen3.6-27B-Text-NVFP4-MTP`), so the mesh runtime prompt for the
*resident agent* is **`AGENTS.colleague.md`**, not this file. **This `CLAUDE.md`
is the prompt for Claude Code (you) when editing the repo.** Keep both in sync
when the agent's domain or invariants change. (The old seed text claimed
`backend: claude` / `CLAUDE.md` — that was stale; `doctor` maps `colleague` →
`AGENTS.colleague.md`, and the file exists, so `doctor` is healthy.)

## Conventions

- **Every PR bumps the version**, even docs/config/CI-only PRs — CI's
  `version-check` job compares `pyproject.toml`'s version against `origin/main`
  and fails (with a sticky PR comment) if unchanged. Use the `version-bump` skill
  (updates `pyproject.toml` + prepends a Keep-a-Changelog entry to `CHANGELOG.md`)
  before opening a PR. Current version: `0.3.2`.
- **Skills are cite-don't-import.** `.claude/skills/` (11 skills) is vendored
  verbatim from **guildmaster** (skills supplier; `steward` keeps the alignment
  role). Provenance and the re-sync procedure live in
  [`docs/skill-sources.md`](docs/skill-sources.md) — read it before touching a
  vendored `SKILL.md`. Don't edit script bodies; lift changes upstream into
  guildmaster and re-vendor. Two tracked divergences: `agex`→`devex` rename and
  `ask-colleague` vendored directly from `colleague`. Every `SKILL.md` must carry
  `type: command` (load-bearing — `core.skill_loader` silently skips files
  without it).
- **PR lane:** use the `cicd` skill (`devex pr` under the hood + SonarCloud
  gating). It signs PR replies as `- amazing-hand-cli (Claude)` via
  `_resolve-nick.sh` (resolved from `culture.yaml`); don't hand-sign inside the
  body. `communicate` handles cross-repo issues and mesh messages.
- **Reach for `ask-colleague` reflexively** for a diverse second opinion: `review`
  a committed diff before opening a PR, `explore` an unfamiliar area. Read-only
  `review`/`explore` are always safe (throwaway worktree); side-effecting
  `write --apply`/`--pr` needs the user's go-ahead.
- **CI quality gates:** SonarCloud (`sonar.qualitygate.wait=true`; skipped on
  token-less/fork PRs), coverage `fail_under = 60` with `relative_files = true`
  so paths map to `sonar.sources=amazing_hand`, line length 100 (black + flake8 +
  isort black profile). PyPI publish is Trusted-Publishing OIDC (TestPyPI on PR,
  PyPI on push to main when `pyproject.toml`/`amazing_hand/**` change).

## Adding a command or domain

1. Create `amazing_hand/cli/_commands/<verb>.py` with a `register(sub)` that adds
   the subparser, `add_argument("--json", action="store_true")`, and
   `set_defaults(func=<handler>)`. Raise `CliError` on failure; emit via
   `_output.emit_result` / `emit_error`; support `--json`.
2. Call its `register()` from `_build_parser()` in `amazing_hand/cli/__init__.py`.
3. Add a catalog entry in `amazing_hand/explain/catalog.py` for the new path(s).
4. If it's a *noun* group with action-verbs, it must also expose `overview`
   (the rubric's `overview_cli_noun_exists` check — see `_commands/cli.py` for the
   pattern).
5. Add tests in `tests/` and re-run `uv run teken cli doctor . --strict`.

For the hand-control **domain**, put the hardware/logic layer in its own package
(e.g. `amazing_hand/hand/`, mirroring how `amazing_hand/explain/` is split from
the CLI), keep heavy deps (serial, kinematics) behind an **optional extra** so
runtime `dependencies` stays `[]`, and lazy-import them inside handlers so
`whoami`/`learn` keep working without the extra installed.

## Clone / rename procedure

This repo is a template clone; the template name is hard-coded in ~100 places.
To re-target a fresh clone, discover every occurrence first:

```bash
git grep -nw amazing_hand        # the Python package name
git grep -n  amazing-hand-cli    # dist/nick/sonar/url occurrences
git grep -n  amazing-hand        # the console-command occurrences
```

Then rename across `pyproject.toml` (`name`, `[project.scripts]`,
`[tool.hatch.build.targets.wheel]`, `known_first_party`, coverage `source`), the
`amazing_hand/` package dir, `tests/`, `sonar-project.properties`, `culture.yaml`
(`suffix`/`backend`), the prompt file, and `README.md`. Re-vendor only the skills
you need (`docs/skill-sources.md`).

## Conventions and workflow

**Memory discipline — recall before, remember after.** This repo keeps its
eidetic memory **in-repo and public**: records resolve to
`<repo-root>/.eidetic/memory` — committed, and shared with the team and mesh
peers (the `claude` and `colleague` backends both read the same
`amazing-hand-cli` scope), so memory travels with the repo, not a private
home-dir store. Make it a per-task habit:

- **`/recall` before you start.** Search the store for the area you're about
  to touch — prior decisions, gotchas, "have we done this before?" — so you
  build on what's already known instead of re-deriving it. Do this before
  non-trivial tasks, not just when asked.
- **`/remember` when something worth keeping surfaces.** A non-obvious
  decision and its rationale, a constraint, a fix and *why* it was needed, a
  gotcha that cost time, a fact the next session would otherwise re-learn.
  Capture it as it happens, not at the end when it's faded.

A plain `/remember` lands the note in `./.eidetic/memory` in this repo — no
flag needed (the wrappers here default to `--visibility public`; in-repo
routing needs `eidetic >= 0.10.0`, older CLIs keep records in `$HOME`). Keep
something out of the committed store only by passing `--visibility private`
(routes to `$HOME/.eidetic/memory`, never committed); `/recall` reads both
stores and merges. Don't store what the repo already records (code structure,
git history, what's already in this file or `CHANGELOG.md`) — store what you'd
have to re-derive. These are the `recall`/`remember` skills (`.claude/skills/`),
backed by the `eidetic` store.
