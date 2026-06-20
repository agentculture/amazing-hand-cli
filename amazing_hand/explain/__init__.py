"""Explain catalog — markdown keyed by command-path tuples (stable-contract).

Every noun/verb registered in the CLI should have a catalog entry.
"""

from __future__ import annotations

from amazing_hand.cli._errors import EXIT_USER_ERROR, CliError
from amazing_hand.explain.catalog import ENTRIES


def resolve(path: tuple[str, ...]) -> str:
    if path in ENTRIES:
        return ENTRIES[path]
    display = " ".join(path) if path else "<root>"
    raise CliError(
        code=EXIT_USER_ERROR,
        message=f"no explain entry for: {display}",
        remediation="list entries with: amazing-hand explain amazing-hand",
    )


def known_paths() -> list[tuple[str, ...]]:
    return list(ENTRIES.keys())
