# Deckgen

KICKER: DECKS FROM REPOSITORIES
# Any repo can emit a deck
TAG: MARKDOWN
BADGE: DETERMINISTIC | accent
SUBTITLE: A Markdown slide spec renders into a pixel-perfect A4 landscape PDF — same spec, same PDF, every time.
META: DEMO DECK - RENDERED BY DECKGEN
---

KICKER: HOW IT WORKS
# One skill, three steps
- A Markdown spec declares slides: kicker, title, bullets, stats, images.
- A headless egui harness paints each slide with a fixed design system.
- A geometry gate checks the render's own rectangles before a human ever looks.
STAT: 5 | LAYOUT FAMILIES
STAT: 1 | BODY SIZE PER DECK
STAT: 3 | GENERATION BUDGET
---

KICKER: DESIGN
# Boring on purpose
- One design system: three typefaces, one accent ink, generous margins.
- Layouts differ by family, not by whim - executives get rhythm, not novelty.
---

KICKER: THE NUMBERS
# Determinism is the feature
HERO: 1.00 | REPRODUCIBILITY - THE SAME SPEC RENDERS THE SAME PDF
- Every defect in a render is a defect in the spec, so the fix loop converges.
---

KICKER: GET IT
# Install the plugin
CALLOUT: One command per host | Claude Code, Codex and oh-my-pi load the same skill payload; the Rust renderer builds on first use.
STAT: 3 | AGENT HOSTS
STAT: 17 | RENDERER TESTS
STAT: 5 | PAGES FROM ONE FILE
