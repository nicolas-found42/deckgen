# AGENTS.md

deckgen turns a repository's content into an executive-grade A4-landscape PDF deck. One
Rust crate renders a Markdown slide spec through a headless egui harness with the ArtCraft
design tokens; a Python gate checks the render's own geometry; a look step reads the raster
pages. This repo is also an agent plugin installable into Claude Code, Codex, and oh-my-pi.

## Layout

- `core/` — the renderer crate. `cargo build --release --manifest-path core/Cargo.toml`
  puts the binary at `core/target/release/deckgen`. Usage:
  `deckgen <deck.md> [-o out.pdf] [--layout out.json]`.
- `skills/deckgen/` — the agent-facing skill (SKILL.md + syntax reference + template +
  `render_pages.py`). This directory is the plugin payload; host installers link or copy it.
- `workflows/` — the deckgen iteration loop: `deckgen-iteration.md` (the loop definition)
  and `deckgen-loop/SKILL.md` (the procedure; installed to `~/.omp/agent/skills/`).
- `scripts/` — `check_docs.py` (doc-consistency gate), `install.py` (host installers).
- `core/GRADE.md` — the frozen five-axis grading instrument. Byte-stable: changing it makes
  every prior score incomparable.
- `docs/deckgen-iterations.md` — the generation log (history from the tool's time inside
  the think-tank repo).
- `examples/demo.md` — a minimal self-contained deck for smoke tests.

## Commands

```bash
cargo build --release --manifest-path core/Cargo.toml
cargo test  --release --manifest-path core/Cargo.toml     # 17 behavioral tests
python3 scripts/check_docs.py                             # doc-consistency gate
python3 scripts/install.py --agent claude|codex|omp       # host install (--dry-run previews)
```

Rendering a deck needs PyMuPDF for the gate and the raster step; the skill's step 1 creates
a dedicated venv for it (`DECKGEN_VENV`, default `~/.cache/deckgen-venv`) because system
Pythons refuse pip installs (PEP 668).

## Rules that bite

- One deck-wide body size: the renderer fits the smallest size any slide needs and paints
  **all** body text at it. Adding copy to one slide shrinks every slide.
- A `": "` inside a bullet switches that slide to the two-column statement layout. Use it
  on purpose.
- `core/GRADE.md` is byte-frozen; the loop documents are single-sourced from it — never
  restate the five propositions elsewhere.
- Determinism: the same spec always produces the same PDF. Every defect in a render is a
  defect in the spec.
