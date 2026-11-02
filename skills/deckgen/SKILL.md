---
name: deckgen
description: Renders an executive-grade A4-landscape PDF deck from any repository's content using the deckgen CLI (Markdown slide spec → headless egui render → raster pages → PDF, ArtCraft design tokens). Use when the user asks for a slide deck, executive briefing, presentation, one-pager, or architecture overview generated from a codebase or project — e.g. "make a deck from this repo", "presentation of the architecture", "briefing PDF from these docs". Covers mining the repo for narrative, authoring the Markdown slide spec, rendering, geometry-gating, and a look-and-fix loop. Don't use for: editing existing .pptx/.gslides files, HTML/reveal.js slide decks, or any deck whose text must be selectable or searchable — deckgen pages are raster images.
---

# deckgen: repo → executive PDF deck

Turn a repository's content into a styled A4-landscape PDF deck. The renderer is
deterministic: the same spec always produces the same PDF, so every defect found in a
render is a defect in the spec, and the fix loop converges.

Vocabulary used throughout: the **spec** is the Markdown slide file, the **render** is the
PDF it produces, the **gate** is the rectangle-math check on the render's own geometry,
and a **generation** is one spec edit → render → gate → look cycle.

## 1. Acquire the renderer

The deckgen CLI ships in this repo; any repo can use it. Prerequisite: a Rust
toolchain (`rustup` from rustup.rs) and a POSIX shell (macOS/Linux natively; Windows via
WSL or Git Bash). Without the toolchain, install it first — every later step needs the
built binary.

```bash
export DECKGEN_HOME=${DECKGEN_HOME:-$HOME/.cache/deckgen-tool}
export DECKGEN_VENV=${DECKGEN_VENV:-$HOME/.cache/deckgen-venv}
export DECKGEN_REF=${DECKGEN_REF:-main}   # pin a commit SHA here for reproducible builds
if [ ! -d "$DECKGEN_HOME" ]; then
  git clone --depth 1 --branch "$DECKGEN_REF" https://github.com/nicolas-found42/deckgen "$DECKGEN_HOME" 2>/dev/null \
    || git clone https://github.com/nicolas-found42/deckgen "$DECKGEN_HOME"
  (cd "$DECKGEN_HOME" && git checkout -q "$DECKGEN_REF")
fi
cargo build --release --manifest-path "$DECKGEN_HOME/core/Cargo.toml"
# a dedicated venv carries PyMuPDF (the gate and the look step rasterize the PDF);
# system Pythons increasingly refuse pip installs (PEP 668), so don't target them
python3 -m venv "$DECKGEN_VENV"
"$DECKGEN_VENV/bin/pip" install --quiet pymupdf
```

Done when: `cargo build` exits 0, `$DECKGEN_HOME/core/target/release/deckgen` exists, and
`"$DECKGEN_VENV/bin/python" -c "import pymupdf"` exits 0.
The install writes only to `$DECKGEN_HOME`, `$DECKGEN_VENV`, and cargo's own cache —
nothing system-wide, nothing into the target repo.
Subsequent runs on this machine skip straight to step 2.

## 2. Mine the repo for the deck's story

Read, in the target repo: `README*`, `AGENTS.md` / `CLAUDE.md` / `CONTRIBUTING*`, the
package manifest (`Cargo.toml`, `package.json`, `pyproject.toml`, …), and the entry points
they name. Extract: what the project does, who it serves, the load-bearing numbers (agent
counts, thresholds, budgets, coverage), and the one claim the project is proudest of —
that claim is the hero slide.

Done when: an outline names one title slide and 4–8 content slides, each with a layout
family (title, list, image split, statement, hero — pick from
`references/slide-syntax.md`) and the specific stats or images it will carry.

## 3. Author the spec

First, read `references/slide-syntax.md` — the full directive table and layout families.
Then copy `assets/deck.template.md` beside your working notes and fill it in. The authoring
rules that bite, stated once:

- Every slide carries a `KICKER:` — it orients the reader across the deck.
- Bullets are 2–3 lines, not paragraphs. Adding copy shrinks the body size for **every**
  slide (one body size, deck-wide); shorten the crowded slide instead.
- A `": "` in a bullet silently switches that slide to the two-column statement layout —
  the text before the colon becomes a tracked header. Use it on purpose; watch for prose
  colons that trigger it by accident. Full rule: `references/slide-syntax.md`.
- At most 4 `STAT:` cards per slide. Numbers are the deck's evidence; labels 1–3 words.
- `IMG:` paths resolve relative to the spec file's directory.

Done when: the spec parses — first block has `# Title`, `KICKER:`, and `SUBTITLE:`; every
other block has a `KICKER:`; every `IMG:` path exists on disk.

## 4. Render

```bash
"$DECKGEN_HOME/core/target/release/deckgen" deck.md -o deck.pdf --layout /tmp/deck.layout.json
```

Done when: exit 0, the last stdout line reports `N pages`, and `deck.pdf` and
`/tmp/deck.layout.json` both exist. The PDF page count must equal the layout page count —
a truncated render fails here even when it looks fine.

## 5. Gate, then look

```bash
"$DECKGEN_VENV/bin/python" "$DECKGEN_HOME/core/scripts/check_deck.py" deck.pdf --layout /tmp/deck.layout.json
"$DECKGEN_VENV/bin/python" "$DECKGEN_HOME/skills/deckgen/scripts/render_pages.py" deck.pdf /tmp/deck-pages
```

The gate is rectangle math over the render's own geometry: safe-area bounds, footer
breaches, overlapping content, text intruding into stat cards. A `PASS` is necessary, not
sufficient — open every PNG in `/tmp/deck-pages` and read it as an executive would:
crowded slides, weak title slide, a stat row that closes nothing, an image that
letterboxes instead of filling its frame.

Done when: the gate prints `PASS` **and** every page has been read with defects listed
(even if the list is empty — say so explicitly).

## 6. Fix the weakest slide, then re-verify

One generation changes one thing: the weakest slide, or the defect the look step named.
Re-render, re-gate, re-look — the gate passing on a geometry change is not quality
passing; the look step decides. Budget 3 generations by default; a generation that moves
nothing is the design's ceiling, not a reason to churn.

Done when: gate `PASS`, every page reads clean, or the 3-generation budget is spent with
the residual named.

## 7. Deliver

Report: the PDF path, the spec path, the page count, and the known limits — pages are
raster images, so the text is not selectable or searchable, and file size runs ~1 MB per
deck. If the user needs searchable text, say so now, not after they open it.
