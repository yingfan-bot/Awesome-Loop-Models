#!/usr/bin/env python3
"""Generate the repository paper-count growth SVG asset."""

from __future__ import annotations

import argparse
from pathlib import Path

import build


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments for the plot wrapper."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=build.PAPER_GROWTH_SVG_OUT)
    return parser.parse_args()


def main() -> int:
    """Load normalized paper metadata and write the growth SVG."""
    args = parse_args()
    papers = build.load_papers()
    args.output.write_text(build.render_paper_growth_svg(papers), encoding="utf-8")
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
