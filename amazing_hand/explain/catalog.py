"""Markdown catalog for ``amazing-hand explain <path>``.

Each entry is verbatim markdown. Keys are command-path tuples. The empty tuple
and ``("amazing-hand",)`` both resolve to the root entry.

Keep bodies self-contained: an agent reading one entry should get enough
context without chaining reads.
"""

from __future__ import annotations

_ROOT = """\
# amazing-hand

A clonable template for AgentCulture mesh agents. It carries an agent-first CLI
(cited from the teken `python-cli` reference), a mesh identity (`culture.yaml` +
`CLAUDE.md`), the canonical guildmaster skill kit under `.claude/skills/`, and a
buildable/deployable package baseline. Clone it, rename the package, edit
`culture.yaml`, and you have a new agent.

## Verbs

- `amazing-hand whoami` — identity probe from `culture.yaml`.
- `amazing-hand learn` — structured self-teaching prompt.
- `amazing-hand explain <path>` — markdown docs for any noun/verb.
- `amazing-hand overview` — descriptive snapshot of the agent.
- `amazing-hand doctor` — check the agent-identity invariants.
- `amazing-hand cli overview` — describe the CLI surface.

## Exit-code policy

- `0` success
- `1` user-input error
- `2` environment / setup error
- `3+` reserved

## See also

- `amazing-hand explain whoami`
- `amazing-hand explain doctor`
"""

_WHOAMI = """\
# amazing-hand whoami

Reports the agent's identity from `culture.yaml`: nick (`suffix`), backend,
served model, and the package version. Read-only.

## Usage

    amazing-hand whoami
    amazing-hand whoami --json
"""

_LEARN = """\
# amazing-hand learn

Prints a structured self-teaching prompt covering purpose, command map,
exit-code policy, `--json` support, and the `explain` pointer.

## Usage

    amazing-hand learn
    amazing-hand learn --json
"""

_EXPLAIN = """\
# amazing-hand explain <path>

Prints markdown documentation for any noun/verb path. Unlike `--help` (terse,
positional), `explain` is global and addressable by path.

## Usage

    amazing-hand explain amazing-hand
    amazing-hand explain whoami
    amazing-hand explain --json <path>
"""

_OVERVIEW = """\
# amazing-hand overview

Read-only descriptive snapshot of the agent: identity (from `culture.yaml`), the
verb surface, and the sibling-pattern artifacts the template carries. Accepts an
ignored `target` so a stray path never hard-fails.

## Usage

    amazing-hand overview
    amazing-hand overview --json
"""

_DOCTOR = """\
# amazing-hand doctor

Checks the agent-identity invariants `steward doctor` verifies:
prompt-file-present and backend-consistency (`claude` → `CLAUDE.md`), plus a
skills-present check. Exits 1 when unhealthy.

## Usage

    amazing-hand doctor
    amazing-hand doctor --json
"""

_CLI = """\
# amazing-hand cli

Noun group for CLI-surface introspection. `cli overview` describes the CLI
itself (distinct from the global `overview`, which describes the agent).

## Usage

    amazing-hand cli overview
    amazing-hand cli overview --json
"""


ENTRIES: dict[tuple[str, ...], str] = {
    (): _ROOT,
    ("amazing-hand",): _ROOT,
    ("amazing-hand-cli",): _ROOT,  # back-compat alias for the dist/nick name
    ("whoami",): _WHOAMI,
    ("learn",): _LEARN,
    ("explain",): _EXPLAIN,
    ("overview",): _OVERVIEW,
    ("doctor",): _DOCTOR,
    ("cli",): _CLI,
    ("cli", "overview"): _CLI,
}
