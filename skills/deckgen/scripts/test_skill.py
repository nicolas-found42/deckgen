#!/usr/bin/env python3
"""Tests for the deckgen skill's own assets.

The skill instructs agents to run scripts/render_pages.py and to read the reference and
template; a regression in either breaks every deck run. Each case asserts observable
behavior, not source text.

Run (no extra dependency beyond PyMuPDF, which the skill installs anyway):
    python3 -m unittest scripts.test_skill -v
or as a plain script — exits 1 on any failure.

The render test builds its own two-page PDF with PyMuPDF, so the suite needs no deckgen
checkout and no network.
"""

import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parents[1]
RENDER = SKILL_DIR / "scripts/render_pages.py"
SKILL_MD = SKILL_DIR / "SKILL.md"


def run_render(*args):
    return subprocess.run(
        [sys.executable, str(RENDER), *map(str, args)],
        capture_output=True,
        text=True,
    )


def make_pdf(path: Path, pages: int = 2) -> Path:
    import pymupdf

    doc = pymupdf.open()
    for i in range(pages):
        page = doc.new_page(width=842, height=595)
        page.insert_text((72, 72), f"page {i + 1}")
    doc.save(path)
    return path


class RenderPagesTest(unittest.TestCase):
    def test_renders_one_png_per_page(self):
        with tempfile.TemporaryDirectory() as tmp:
            pdf = make_pdf(Path(tmp) / "deck.pdf")
            out = run_render(pdf, Path(tmp) / "pages")
            self.assertEqual(out.returncode, 0, out.stderr)
            pngs = sorted((Path(tmp) / "pages").glob("page-*.png"))
            self.assertEqual(len(pngs), 2, out.stdout + out.stderr)
            for png in pngs:
                self.assertGreater(png.stat().st_size, 0, png)

    def test_missing_input_exits_1_with_reason(self):
        out = run_render("/nonexistent/deck.pdf", "/tmp/nowhere")
        self.assertEqual(out.returncode, 1)
        self.assertIn("no such file", out.stderr)


class SkillConsistencyTest(unittest.TestCase):
    def test_referenced_files_exist(self):
        body = SKILL_MD.read_text()
        for rel in re.findall(r"`((?:references|assets|scripts)/[\w./-]+)`", body):
            self.assertTrue((SKILL_DIR / rel).is_file(), f"SKILL.md names a missing file: {rel}")

    def test_frontmatter_names_the_directory(self):
        head = SKILL_MD.read_text().split("---", 2)[1]
        name = re.search(r"^name:\s*(\S+)", head, re.M)
        self.assertIsNotNone(name, "frontmatter has no name")
        self.assertEqual(name.group(1), SKILL_DIR.name)

    def test_description_within_router_budget(self):
        head = SKILL_MD.read_text().split("---", 2)[1]
        desc = re.search(r"^description:\s*(.+)$", head, re.M)
        self.assertIsNotNone(desc, "frontmatter has no description")
        self.assertLessEqual(len(desc.group(1)), 1024, "description exceeds 1024 chars")

    def test_no_docs_files(self):
        for banned in ("README.md", "CHANGELOG.md", "INSTALLATION_GUIDE.md"):
            self.assertFalse((SKILL_DIR / banned).exists(), f"skills ship no {banned}")

    def test_acquire_defaults_expand_to_absolute_paths(self):
        """Tilde inside ${var:-~/...} stays literal in bash and zsh; the acquire
        block must default to absolute paths or first runs clone into a dir named ~."""
        body = SKILL_MD.read_text()
        block = body.split("```bash", 1)[1].split("```", 1)[0]
        for var in ("DECKGEN_HOME", "DECKGEN_VENV"):
            line = next(l for l in block.splitlines() if l.startswith(f"export {var}="))
            out = subprocess.run(
                ["bash", "-c", f"unset {var}; {line}; printf %s ${var}"],
                capture_output=True, text=True,
            )
            self.assertTrue(out.stdout.startswith("/"),
                            f"{var} default is not absolute: {out.stdout!r}")


def main() -> int:
    program = unittest.main(exit=False, verbosity=2)
    return 0 if program.result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(main())
