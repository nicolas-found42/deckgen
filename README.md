# deckgen

Render an executive-grade A4-landscape PDF deck from any repository's content. One agent
skill drives a deterministic Rust renderer: Markdown slide spec → headless egui render with
ArtCraft design tokens → geometry gate → raster pages you actually look at.

Pages are raster images: layouts stay pixel-perfect everywhere, at the cost of selectable
text (stated up front, not discovered later).

## Install

Pick your host; the installer prints the commands and runs them (`--dry-run` to preview):

```sh
# Claude Code (plugin)
python3 scripts/install.py --agent claude

# Codex (plugin)
python3 scripts/install.py --agent codex

# oh-my-pi (skill, symlinked so repo edits propagate)
python3 scripts/install.py --agent omp

# any other Agent Skills host
python3 scripts/install.py --agent skills --destination ~/.my-agent/skills/deckgen
```

All hosts load the same payload: [`skills/deckgen/SKILL.md`](skills/deckgen/SKILL.md).
The Rust renderer builds on first use (skill step 1: clone → `cargo build` → a dedicated
PyMuPDF venv); nothing system-wide is written.

Manual plugin install, without the script:

```sh
claude plugin marketplace add nicolas-found42/deckgen && claude plugin install deckgen@deckgen-plugins
codex plugin marketplace add nicolas-found42/deckgen && codex plugin add deckgen@deckgen-plugins
```

## Use

Ask your agent: *"make a deck from this repo"* or *"presentation of the architecture"* —
the skill triggers on deck/briefing/presentation asks. Claude Code also exposes a
`/deckgen [repo]` command.

The flow: mine the repo for its story → author the Markdown spec → render → gate on
rectangle math → read every rendered page → fix the weakest slide (3-generation budget) →
deliver PDF + spec + limits.

## Deck spec

Markdown, `---`-separated slides, a handful of directives (`KICKER:`, `STAT: 4 | LABEL`,
`IMG: path`, `HERO: 1.00 | label`, `CALLOUT:`, `DIVIDER:`). Full directive table:
[`skills/deckgen/references/slide-syntax.md`](skills/deckgen/references/slide-syntax.md).
Worked skeleton: [`skills/deckgen/assets/deck.template.md`](skills/deckgen/assets/deck.template.md).
A minimal example lives at [`examples/demo.md`](examples/demo.md).

## Development

```bash
cargo build --release --manifest-path core/Cargo.toml
cargo test --release --manifest-path core/Cargo.toml    # 17 behavioral tests
python3 scripts/check_docs.py                           # doc-consistency gate
```

See [AGENTS.md](AGENTS.md) for the layout and the rules that bite, and
[workflows/deckgen-iteration.md](workflows/deckgen-iteration.md) for the quality loop
(five-axis grade instrument, generation log in `docs/deckgen-iterations.md`).

## Provenance

Built and iterated inside [nickth3man/think-tank](https://github.com/nickth3man/think-tank)
(gens 1–17 in `docs/deckgen-iterations.md`); extracted to this standalone plugin repo.
