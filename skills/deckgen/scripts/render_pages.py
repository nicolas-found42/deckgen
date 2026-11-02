#!/usr/bin/env python3
"""Rasterize a deckgen PDF's pages to PNGs for the look step.

The gate checks geometry by rectangle math; this produces what the gate cannot — the
pixels an executive reads. One PNG per page, named page-1.png, page-2.png, ...

Usage:
    render_pages.py deck.pdf /tmp/deck-pages [--dpi 100]

Exit 0 when every page produced a PNG; 1 otherwise, with the reason on stderr.
"""

import argparse
import sys
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf", help="the rendered deck PDF")
    ap.add_argument("outdir", help="directory for the PNGs (created if absent)")
    ap.add_argument("--dpi", type=int, default=100)
    args = ap.parse_args()

    pdf = Path(args.pdf)
    if not pdf.is_file():
        print(f"render_pages: no such file: {pdf}", file=sys.stderr)
        return 1

    try:
        import pymupdf  # PyMuPDF >= 1.26
    except ImportError:
        try:
            import fitz as pymupdf  # older name, deprecated but present
        except ImportError:
            print(
                "render_pages: needs PyMuPDF. Install with: pip install pymupdf",
                file=sys.stderr,
            )
            return 1

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    doc = pymupdf.open(pdf)
    failures = 0
    for i, page in enumerate(doc, start=1):
        pix = page.get_pixmap(dpi=args.dpi)
        target = outdir / f"page-{i}.png"
        pix.save(target)
        if not target.is_file() or target.stat().st_size == 0:
            print(f"render_pages: page {i} produced no output", file=sys.stderr)
            failures += 1
        else:
            print(target)
    if failures:
        print(f"render_pages: {failures} of {len(doc)} pages failed", file=sys.stderr)
        return 1
    print(f"render_pages: {len(doc)} pages -> {outdir}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
