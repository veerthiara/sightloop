"""CLI script for running the local camera pipeline."""

from __future__ import annotations

import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = BACKEND_ROOT / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


def run() -> int:
    from sightloop_vision.app.runner import main

    return main()


if __name__ == "__main__":
    raise SystemExit(run())
