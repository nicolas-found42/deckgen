# Slide syntax reference

Full directive table and layout families for the deckgen spec. Read this before authoring
the first slide. The renderer derives everything else — font metrics, card geometry, the
deck-wide body size — from the content.

## Spec structure

Slides are separated by a line containing only `---`. The first block is the title slide.
Blank blocks are skipped, so a trailing `---` is harmless.

## Directives

| Directive | Effect | Notes |
| :--- | :--- | :--- |
| `# Title` | Slide display heading | Archivo Display on content slides, oversized on the title slide. |
| `KICKER: text` | Tracked uppercase label above the title | Every slide carries one. |
| `SUBTITLE: text` | Secondary summary line | Title slide and section dividers. |
| `META: text` | Bottom-anchored footer line | Title slide only. |
| `- bullet` | List item at the deck-wide body size | 2–3 lines. A `": "` splits the bullet into a tracked header + claim (see layout families). |
| `STAT: value \| label` | Metric card, bottom-anchored | Max 4 per slide; they share the content width equally. Labels 1–3 words. |
| `HERO: value \| label` | One oversized number with claims stacked at right | The hero claim column compresses and steps its size down rather than overprinting cards. |
| `IMG: path` | Framed image in a split layout | Relative to the spec file. The frame centre-crops the source to its aspect — the image fills the frame instead of letterboxing. |
| `TAG: text` | Control pill, top-right | Toolbar-pill frame. |
| `BADGE: text \| tone` | Status badge under the tag | Tones: `accent` (default), `beta`, `bad`, `neutral`. |
| `CALLOUT: heading \| body` | Bordered feature panel with corner registration marks | Stat cards stand beside it when they cannot stack. |
| plain paragraph | Body text | Treated as narrative copy, not a list item. |

## Layout families (chosen automatically from content)

1. **Title** — the first block. Kicker, display title, subtitle, bottom meta anchor; the
   block is centred in the space above the anchor.
2. **Section divider** — a block with only `# Title` and no body, stats, or image.
3. **List** — bullets plus stat cards. Three or more bullets set in two aligned columns.
4. **Image split** — text left, framed image right; the frame fills its half of the content
   width and the band above the card row.
5. **Statement** — any body text containing `": "` on a slide with no `IMG:`. Each claim
   line splits at its **first** colon: before becomes a tracked header (INK_STRONG), after
   becomes the claim (MUTED). Headered claims pair into two columns — evidence left,
   interpretation right; an odd unheadered claim spans full width. The family closes with
   one full-width band divided by hairlines instead of a card row. Because the trigger is
   any prose colon, a foreign sentence like "Note: this changed" silently converts the
   slide — write colons deliberately.
6. **Hero** — `HERO:` with the remaining claims stacked right.

## Invariants the renderer enforces

- **One body size, deck-wide.** The size is fitted against the tightest slide and painted
  everywhere; a slide that cannot hold it steps down rather than overflowing. Crowding one
  slide shrinks the whole deck — shorten the slide instead. `DECKGEN_VERBOSE=1` prints the
  chosen size.
- **Cards close the composition.** The stat row spans the full content width (2 cards =
  half each, 4 = quarter each) and hangs 26 pt under the last line of copy.
- **Page count equals layout page count.** A stale or truncated render fails the gate even
  with clean geometry.
