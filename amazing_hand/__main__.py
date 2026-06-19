"""Entry point for ``python -m amazing_hand``."""

from __future__ import annotations

import sys

from amazing_hand.cli import main

if __name__ == "__main__":
    sys.exit(main())
