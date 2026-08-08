# Profile Banner — animated SVG hero for a GitHub README

A premium GitHub profile hero banner built as **pure SVG with SMIL animations only**. Two
files, identical layout and timing, different palettes: `dark.svg` and `light.svg`.

Both are generated from a single Python script (`gen.py`) so the two themes can never drift
apart. **Edit `gen.py` and regenerate — do not hand-edit the SVGs.**

---

## Files

```
profile-banner/
├── gen.py               # single source of truth — builds both SVGs
├── ascii_from_photo.py  # photo -> the ASCII list, stdlib only
├── README.md            # this file
├── README-snippet.md    # the markdown to paste into your profile README
└── assets/
    ├── dark-v2.svg      # generated, ~52 KB
    └── light-v2.svg     # generated, ~52 KB
```

Regenerate:

```bash
python3 gen.py     # writes dark-$VERSION.svg + light-$VERSION.svg, validates XML
```

No third-party dependencies (stdlib only). Output goes to `assets/` next to the script — change
`OUT_DIR` at the top of `gen.py` to point somewhere else.

---

## Embedding in a README

```html
<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="profile-banner/assets/dark-v2.svg">
    <source media="(prefers-color-scheme: light)" srcset="profile-banner/assets/light-v2.svg">
    <img alt="Eshwar — AI/ML Engineer" src="profile-banner/assets/dark-v2.svg" width="100%">
  </picture>
</p>
```

---

## Hard constraints — do not break these

| Rule | Why |
| --- | --- |
| No JavaScript, no `<script>` | GitHub renders README SVGs as images; scripts never execute |
| No `<foreignObject>` | Not rendered in image context — content silently disappears |
| No external `<image href>` or webfont `@import` | Cross-origin fetches are blocked by the image proxy |
| Animations must be SMIL (`animate`, `animateTransform`, `animateMotion`) | CSS keyframes are unreliable through the proxy |
| Fonts must be system stacks | See `MONO` / `SANS` constants at the top of `gen.py` |
| Every `id` must stay unique within a file | Clip paths and gradients are referenced by id |
| Keep `viewBox="0 0 1180 610"` + `width="100%"` | This is what makes it responsive in a README |

**Filenames carry a `VERSION` suffix** (`VERSION = "v2"` in `gen.py`). GitHub caches an image
URL hard enough that a fixed SVG can keep rendering the broken old bytes for a long time. Bump
`VERSION`, regenerate, update the two paths in the root `README.md`, and delete the old pair.

**Clip widths need a pad past the last glyph.** A clip sized to exactly `n × 12px` puts the final
character on the boundary and hinting shaves its right edge (`Builde|r`). The pad is kept narrower
than the cursor block drawn at the same position, so it never uncovers the next character.

**Never let `clip-path` be the only thing separating two overlapping elements.** WebKit renders
README SVGs as images and drops `clip-path` on `<text>` in that mode while still running the SMIL
opacity animations — so anything relying on a clip to stay hidden gets painted. The five role
phrases share one baseline, and on Safari that showed up as all five stacked into an unreadable
blur. The role phrases share one baseline, so they now carry three independent guards, and the
element renders correctly if *any one* of them survives:

1. the clip — character-by-character typing,
2. a discrete `opacity` window per phrase,
3. a discrete `translate` that parks inactive phrases at `x -6000`, outside the viewBox, which
   the outermost `<svg>` clips away in every renderer.

**Base attribute values must be the safe state, not the hidden state.** These texts are written
`opacity="1"`; with `opacity="0"` a renderer that ignores the animation shows nothing at all.
Worst case now is a single static phrase — never five stacked into a blur. If you add another
element that overlaps a sibling, give it the same treatment.

Two known limitations that are **not** bugs:

- **Hover does nothing on GitHub.** The `.pill:hover` / `.soc:hover` rules in the `<style>` block
  only fire when the SVG is opened directly or inlined on a website. Through GitHub's image
  proxy, an SVG is a flat image. Put real links in markdown below the banner.
- **The `<a xlink:href>` wrappers on the social icons are inert on GitHub** for the same reason.
  They work on a personal site.

If a change doesn't show up on GitHub, it's the image proxy cache — hard-refresh, or bump the
filename (`dark.svg` → `dark-v2.svg`).

---

## Layout map

Canvas `1180 × 610`, corner radius `26`.

```
┌──────────────────────────────────────────────────────────────────────┐
│  ● ● ●  portrait.asc     │  ● ● ●   eshwar@dev — zsh — 96×32         │
│  ──────────────────────  │  ─────────────────────────────────────    │
│                          │  HI THERE 👋                              │
│      ASCII PORTRAIT      │  I'm Eshwar               ← gradient, 46px │
│      (18 lines, types    │  > Agentic Workflows…     ← typing loop    │
│       in line by line,   │  ─────────────────────────────────────    │
│       floats, scanline)  │  ⌖ LOCATION    India                      │
│                          │  ⌖ EDUCATION   B.Tech · Computer Science  │
│                          │  ⌖ FOCUS       Multimodal AI …            │
│                          │  ⌖ GITHUB      github.com/Eshwar1502      │
│  RENDER COMPLETE ▌       │                                           │
│  ══════════════════      │  STACK                                    │
│                          │  ( Python )( PyTorch )( TensorFlow ) …    │
│                          │  ( Docker )( PostgreSQL )( OpenCV ) …     │
│                          │  ◯ ◯              Thanks for stopping by. │
└──────────────────────────────────────────────────────────────────────┘
   left panel 28,28 392×554      right panel 444,28 708×554
```

Key coordinates, all defined as constants near the top of `gen.py`:

| Element | Value |
| --- | --- |
| Left panel | `LP = x 28, y 28, w 392, h 554, r 20` |
| Right panel | `RP = x 444, y 28, w 708, h 554, r 20` |
| Right content column | `CX = 478`, width `CW = 640` |
| ASCII font size / char width | auto-fit from `MAXLEN`, currently `15.5px` / `9.3px` |
| ASCII first baseline | `ATOP = 128`, line height `AFS × 1.26` |
| Name baseline | `y 172` · role line `y 222` · divider `y 252` |
| Info rows | block centred in the `282..414` band; step = `min(38, 132/(n-1))` |
| STACK label | `y 450` · pill rows top `460` and `496`, height `28` |
| Social icons | `cy 556`, `r 16`, starting `cx 498`, step `48` (2 icons) |

---

## Palette

Defined in the `PAL` dict in `gen.py`. Change colours there, never in the SVGs.

| Token | Dark | Light |
| --- | --- | --- |
| Background | `#030712` | `#FFFFFF` |
| Panel | `#0F172A` → `#0B1220` | `#F8FAFC` → `#FFFFFF` |
| Border | `rgba(255,255,255,.08)` | `rgba(15,23,42,.08)` |
| Text | `#F8FAFC` | `#0F172A` |
| Muted / dim | `#94A3B8` / `#64748B` | `#475569` / `#94A3B8` |
| Accent 1 | `#7C3AED` | `#2563EB` |
| Accent 2 | `#22D3EE` | `#06B6D4` |
| Accent 3 | `#10B981` | `#10B981` |

The light theme also lowers `glow`, `blob`, `scan`, and `shadow` intensity so the effects read as
soft rather than neon. Keep that relationship if you add a new effect: light mode needs roughly
half the opacity of dark mode to look equally subtle.

---

## Animation inventory

| Effect | Implementation | Loop |
| --- | --- | --- |
| ASCII line-by-line typing | one `clipPath` per line + per-line `opacity` fallback | 16s |
| ASCII gradient shift | animated `stop-color` on three stops + `gradientTransform` translate | 12s / 7s |
| ASCII float | `animateTransform` translate with `keySplines` easing | 7s |
| Role typing | discrete clip `width` per character (`n×12 + 9` pad) + per-phrase `opacity` window | 24s (6 × 4s) |
| Typing cursor | discrete `x` animation on the same keyTimes + 1s blink | 24s / 1s |
| Sequential reveal | `opacity` + translate with `fill="freeze"`, staggered `begin` | once |
| Background blobs | three `radialGradient` ellipses on translate loops | 18/22/26s |
| Particles | 18 circles, `cy` drift + `opacity` pulse, seeded `random(11)` | 9–20s |
| Scanline | gradient rect animating `y`, one per card and one per left panel | 6s / 4.5s |
| Border shimmer | `userSpaceOnUse` gradient with animated `x1`/`x2` on the card stroke | 7s |
| Glass sheen | same technique, swept across the terminal panel | 11s |
| Noise | `feTurbulence` + `feColorMatrix saturate 0`, `mix-blend-mode: overlay` | 8s breathe |
| Pill glow | `stroke-opacity` pulse, desynced per pill | 3.4–4.8s |

Durations are deliberately coprime-ish so the composition never visibly re-syncs.

---

## Content to personalise

All of this lives in the constants block at the top of `gen.py`:

```python
NAME   = "Eshwar"
ROLES  = [...]   # 6 phrases in the typing loop — keep under ~34 chars each;
                 # the loop length is derived (4s each), so adding one is safe
INFO   = [...]   # (icon, label, value) — icons: pin, cap, target, globe, mail
SKILLS = [...]   # pills; the packer keeps 2 rows, extras past that are dropped
socials = [...]  # (icon key, url) — icon keys: github, linkedin, x, globe
```

Live values: GitHub and LinkedIn URLs are real. `India` and `B.Tech · Computer Science` are
still generic — swap them if you want something more specific. The Portfolio and Email info
rows plus the X / portfolio social icons were removed because their values were placeholders;
add them back in `INFO` / `socials` once you have real URLs.

Adding or removing an `INFO` row is safe: the rows are centred inside a fixed `282..414` band
with an adaptive step, so the gap down to `STACK` never changes.

The ASCII portrait was generated from a photo with `ascii_from_photo.py` (stdlib only, same rule
as `gen.py`). It takes a PNG, so convert first:

```bash
sips -s format png --resampleHeight 800 --out raw.png photo.jpg
python3 ascii_from_photo.py raw.png --rot cw --crop 0.42,0.63,0.66,0.90 \
        --cols 48 --rows 24 --clip 1,60 --preview crop.png
```

`--crop` is `x0,y0,x1,y1` as fractions and is applied *before* `--rot`; `--preview` writes the
cropped, rotated greyscale so the framing can be checked without guessing. Two things that decide
whether the result reads as a face:

- **`--clip` must span the subject, not the frame.** With a blown-out background the wall owns the
  top of the range and skin and hair both fall in the dense half — one grey blob. Clipping at
  `1,60` throws the background away and spends the whole ramp on the person.
- **Column count trades detail against legibility.** The font auto-fits, so more columns means
  smaller glyphs, and GitHub scales the 1180px banner down to roughly 890px on top of that. 48
  columns (10.3px, ~7.7px as displayed) is about the limit; 64 turns to mush at display size.

The ASCII portrait is the `ASCII` list — 18 strings. Lines are right-padded to the longest line
and the font size auto-fits to the panel, so you can swap in any ASCII art without touching
coordinates. Stick to plain ASCII (`. : = + * % @ #`); block-drawing characters like `▓█` are
missing from some system monospace fonts and will render as tofu.

---

## Things you might ask for next

- Replace the ASCII portrait with art generated from a real photo (`jp2a`, `ascii-image-converter`)
- Swap the info rows for live GitHub stats (would need a build step or a stats service — the SVG
  itself can't fetch anything)
- A compact `520px`-tall variant for repo READMEs rather than a profile README
- Prefers-reduced-motion static fallback as a third file
- Recolour to a different accent triad — change `a1`/`a2`/`a3` in `PAL` and regenerate

## Verification checklist after any edit

1. `python3 gen.py` exits 0 (it parses its own output and will raise on malformed XML)
2. Open both SVGs directly in a browser — animations play, nothing clips outside the panels
3. Check the two panels' bottom edge: pills end at `y 524`, icons at `y 572`, panel at `y 582`.
   If you add a row, re-check that gap before shipping.
