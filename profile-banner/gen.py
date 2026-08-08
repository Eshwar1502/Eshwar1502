#!/usr/bin/env python3
# Generates dark.svg + light.svg — a pure-SVG (SMIL only) GitHub profile hero banner.
import os, random, xml.etree.ElementTree as ET

# Where the generated SVGs are written (relative to this script).
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")

W, H = 1180, 610
NAME = "Eshwar"

# Bump when you want the README to fetch a fresh copy — GitHub caches the old
# filename hard. Output becomes dark-<VERSION>.svg / light-<VERSION>.svg.
VERSION = "v2"

MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,&apos;DejaVu Sans Mono&apos;,monospace"
SANS = "Inter,-apple-system,BlinkMacSystemFont,&apos;Segoe UI&apos;,Roboto,Helvetica,Arial,sans-serif"

ASCII = [
    "          .:=+*####*+=:.",
    "       :=*%@@@@@@@@@@%*=:",
    "     :*%@@@@@@@@@@@@@@@@%*:",
    "   .=%@@@@@@@@@@@@@@@@@@@@%=.",
    "  .*@@@@@@@@@@@@@@@@@@@@@@@@*.",
    "  =@@@@@@@@@@@@@@@@@@@@@@@@@@=",
    " .%@@@%=:....:%@@%:....:=%@@@%.",
    " :@@@@:  ()  :@@@@:  ()  :@@@@:",
    " =@@@@%=:...:=%@@%=:...:=%@@@@=",
    " =@@@@@@@@@@@@@@@@@@@@@@@@@@@@=",
    " :@@@@@@@@@@@@#..#@@@@@@@@@@@@:",
    " .%@@@@@@@@@@@#..#@@@@@@@@@@@%.",
    "  =@@@@@@@@@@@@@@@@@@@@@@@@@@=",
    "  .*@@@@@%+::......::+%@@@@@*.",
    "   .=%@@@@@%*+======+*%@@@@@%=.",
    "     :*%@@@@@@@@@@@@@@@@%*:",
    "       :=*%@@@@@@@@@@%*=:",
    "          .:=+*####*+=:.",
]

ROLES = [
    "AI/ML Engineer",
    "Applied ML & NLP",
    "Generative AI Builder",
    "Multimodal AI Explorer",
    "Agentic Workflows & LLM Tooling",
]

INFO = [
    ("pin",   "Location",  "India"),
    ("cap",   "Education", "B.Tech · Computer Science"),
    ("target","Focus",     "Multimodal AI · Vision + Language"),
    ("globe", "GitHub",    "github.com/Eshwar1502"),
]

SKILLS = ["Python", "PyTorch", "TensorFlow", "scikit-learn", "Pandas", "Vertex AI",
          "Docker", "PostgreSQL", "OpenCV", "React", "Node.js", "Git", "Linux"]

PAL = {
    "dark": dict(
        bg="#030712", panel="#0F172A", panel2="#0B1220",
        border="rgba(255,255,255,.08)", border2="rgba(255,255,255,.14)",
        text="#F8FAFC", muted="#94A3B8", dim="#64748B",
        a1="#7C3AED", a2="#22D3EE", a3="#10B981",
        glow=0.55, blob=0.30, grid=0.05, noise=0.05,
        glass="#FFFFFF", glassop=0.07, scan=0.10, pillbg="#111C31", pillop=0.75,
        shadow=0.55,
    ),
    "light": dict(
        bg="#FFFFFF", panel="#F8FAFC", panel2="#FFFFFF",
        border="rgba(15,23,42,.08)", border2="rgba(15,23,42,.14)",
        text="#0F172A", muted="#475569", dim="#94A3B8",
        a1="#2563EB", a2="#06B6D4", a3="#10B981",
        glow=0.28, blob=0.16, grid=0.04, noise=0.035,
        glass="#FFFFFF", glassop=0.55, scan=0.06, pillbg="#FFFFFF", pillop=0.92,
        shadow=0.12,
    ),
}

# ---------- geometry ----------
LP = dict(x=28, y=28, w=392, h=554, r=20)          # left panel
RP = dict(x=444, y=28, w=708, h=554, r=20)         # right panel
PADX = 34
CX = RP["x"] + PADX                                 # 478 content left edge
CW = RP["w"] - 2 * PADX                             # 640 content width

MAXLEN = max(len(l) for l in ASCII)
AFS = min(15.5, 296 / (MAXLEN * 0.6))               # ascii font-size
ACW = AFS * 0.6                                     # ascii char width
AW = MAXLEN * ACW
AX = LP["x"] + (LP["w"] - AW) / 2
ALH = AFS * 1.26
ATOP = 128                                          # first baseline


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def keyed_pairs(pts, total, on="0 0", off="-6000 0"):
    """pts: [(t, is_on)] -> (values, keyTimes) for a discrete translate track."""
    out = []
    for t, flag in pts:
        t = max(0.0, min(total, t))
        if out and abs(out[-1][0] - t) < 1e-6:
            out[-1] = (t, flag)
        else:
            out.append((t, flag))
    if out[0][0] > 0:
        out.insert(0, (0.0, out[0][1]))
    if out[-1][0] < total:
        out.append((total, out[-1][1]))
    vals = ";".join(on if f else off for _, f in out)
    kts = ";".join("{:.4f}".format(t / total) for t, _ in out)
    return vals, kts


def keyed(pts, total):
    """pts: [(t, value)] -> (values, keyTimes) strings, discrete-safe."""
    out = []
    for t, v in pts:
        t = max(0.0, min(total, t))
        if out and abs(out[-1][0] - t) < 1e-6:
            out[-1] = (t, v)
        else:
            out.append((t, v))
    if out[0][0] > 0:
        out.insert(0, (0.0, out[0][1]))
    if out[-1][0] < total:
        out.append((total, out[-1][1]))
    vals = ";".join("{:.2f}".format(v) for _, v in out)
    kts = ";".join("{:.4f}".format(t / total) for t, _ in out)
    return vals, kts


def typing_points(n, slot, total, tin=1.45, hold=1.85, tout=0.45, gap=0.25):
    """char-count timeline for one role phrase inside its slot."""
    pts = [(0.0, 0), (slot, 0)]
    for k in range(1, n + 1):
        pts.append((slot + tin * k / n, k))
    pts.append((slot + tin + hold, n))
    for k in range(n - 1, -1, -1):
        pts.append((slot + tin + hold + tout * (n - k) / n, k))
    pts.append((slot + tin + hold + tout + gap, 0))
    pts.append((total, 0))
    return pts


ICONS = {
    "pin":   '<path d="M0 6.5C0 6.5 -5.2 0.6 -5.2 -2.6a5.2 5.2 0 1 1 10.4 0C5.2 0.6 0 6.5 0 6.5Z"/><circle cx="0" cy="-2.6" r="1.9"/>',
    "cap":   '<path d="M-7 -2.2 0 -5.6 7 -2.2 0 1.2Z"/><path d="M-4 -0.7v3.6c0 1.5 8 1.5 8 0V-0.7"/>',
    "target":'<circle cx="0" cy="0" r="6"/><circle cx="0" cy="0" r="2.3"/>',
    "globe": '<circle cx="0" cy="0" r="6"/><path d="M-6 0h12"/><path d="M0 -6c3 3.2 3 8.8 0 12c-3 -3.2 -3 -8.8 0 -12Z"/>',
    "mail":  '<rect x="-7" y="-5" width="14" height="10" rx="2"/><path d="M-7 -4 0 1.4 7 -4"/>',
}


def build(theme):
    c = PAL[theme]
    random.seed(11)
    s = []
    A = s.append

    A('<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
      'viewBox="0 0 {} {}" width="100%" role="img" aria-labelledby="t d" '
      'preserveAspectRatio="xMidYMid meet" font-family="{}">'.format(W, H, SANS))
    A('<title id="t">{} — AI/ML Engineer</title>'.format(NAME))
    A('<desc id="d">Animated profile banner: ASCII portrait and a terminal panel listing role, '
      'location, focus, skills and links.</desc>')

    # ---------------- defs ----------------
    A('<defs>')
    # accent gradient (animated sweep)
    A('<linearGradient id="acc" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="420" y2="60">'
      '<stop offset="0" stop-color="{a1}"/><stop offset=".5" stop-color="{a2}"/>'
      '<stop offset="1" stop-color="{a3}"/>'
      '<animate attributeName="x1" values="-160;420;-160" dur="9s" repeatCount="indefinite"/>'
      '<animate attributeName="x2" values="420;1000;420" dur="9s" repeatCount="indefinite"/>'
      '</linearGradient>'.format(**c))
    # ascii gradient (shifting colours + travelling sweep)
    A('<linearGradient id="asc" gradientUnits="userSpaceOnUse" '
      'x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}">'.format(
          x1=AX, y1=ATOP - 20, x2=AX + AW, y2=ATOP + ALH * len(ASCII)))
    A('<stop offset="0" stop-color="{a2}"><animate attributeName="stop-color" '
      'values="{a2};{a1};{a3};{a2}" dur="12s" repeatCount="indefinite"/></stop>'.format(**c))
    A('<stop offset=".55" stop-color="{a1}"><animate attributeName="stop-color" '
      'values="{a1};{a3};{a2};{a1}" dur="12s" repeatCount="indefinite"/></stop>'.format(**c))
    A('<stop offset="1" stop-color="{a3}"><animate attributeName="stop-color" '
      'values="{a3};{a2};{a1};{a3}" dur="12s" repeatCount="indefinite"/></stop>'.format(**c))
    A('<animateTransform attributeName="gradientTransform" type="translate" '
      'values="-70 0;70 0;-70 0" dur="7s" repeatCount="indefinite"/>')
    A('</linearGradient>')
    # panel fills
    A('<linearGradient id="pnl" x1="0" y1="0" x2="0.6" y2="1">'
      '<stop offset="0" stop-color="{panel}"/><stop offset="1" stop-color="{panel2}"/>'
      '</linearGradient>'.format(**c))
    # glass reflection
    A('<linearGradient id="glass" x1="0" y1="0" x2="0.35" y2="1">'
      '<stop offset="0" stop-color="{glass}" stop-opacity="{o:.3f}"/>'
      '<stop offset=".45" stop-color="{glass}" stop-opacity="0"/>'
      '</linearGradient>'.format(glass=c["glass"], o=c["glassop"]))
    # border shimmer
    A('<linearGradient id="shim" gradientUnits="userSpaceOnUse" x1="-500" y1="0" x2="-140" y2="610">'
      '<stop offset="0" stop-color="{a2}" stop-opacity="0"/>'
      '<stop offset=".5" stop-color="{a2}" stop-opacity=".9"/>'
      '<stop offset="1" stop-color="{a1}" stop-opacity="0"/>'
      '<animate attributeName="x1" values="-500;1180;-500" dur="7s" repeatCount="indefinite"/>'
      '<animate attributeName="x2" values="-140;1540;-140" dur="7s" repeatCount="indefinite"/>'
      '</linearGradient>'.format(**c))
    # background blobs
    for i, (col, key) in enumerate([("a1", "b1"), ("a2", "b2"), ("a3", "b3")]):
        A('<radialGradient id="{k}"><stop offset="0" stop-color="{col}" stop-opacity="{o:.3f}"/>'
          '<stop offset="1" stop-color="{col}" stop-opacity="0"/></radialGradient>'.format(
              k=key, col=c[col], o=c["blob"]))
    # scanline
    A('<linearGradient id="scanG" x1="0" y1="0" x2="0" y2="1">'
      '<stop offset="0" stop-color="{a2}" stop-opacity="0"/>'
      '<stop offset=".5" stop-color="{a2}" stop-opacity="{o:.3f}"/>'
      '<stop offset="1" stop-color="{a2}" stop-opacity="0"/></linearGradient>'.format(
          a2=c["a2"], o=c["scan"]))
    # sheen sweep across whole card
    A('<linearGradient id="sheen" gradientUnits="userSpaceOnUse" x1="-400" y1="0" x2="-200" y2="610">'
      '<stop offset="0" stop-color="#FFFFFF" stop-opacity="0"/>'
      '<stop offset=".5" stop-color="#FFFFFF" stop-opacity="{o:.3f}"/>'
      '<stop offset="1" stop-color="#FFFFFF" stop-opacity="0"/>'
      '<animate attributeName="x1" values="-400;1300;-400" dur="11s" repeatCount="indefinite"/>'
      '<animate attributeName="x2" values="-200;1500;-200" dur="11s" repeatCount="indefinite"/>'
      '</linearGradient>'.format(o=0.05 if theme == "dark" else 0.35))
    # filters
    A('<filter id="soft" x="-60%" y="-60%" width="220%" height="220%">'
      '<feGaussianBlur stdDeviation="7"/></filter>')
    A('<filter id="glow" x="-70%" y="-70%" width="240%" height="240%">'
      '<feGaussianBlur stdDeviation="3.2" result="b"/>'
      '<feMerge><feMergeNode in="b"/><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>'
      '</filter>')
    A('<filter id="glowS" x="-70%" y="-70%" width="240%" height="240%">'
      '<feGaussianBlur stdDeviation="1.6" result="b"/>'
      '<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>')
    A('<filter id="drop" x="-20%" y="-20%" width="140%" height="140%">'
      '<feDropShadow dx="0" dy="18" stdDeviation="22" flood-color="#000000" '
      'flood-opacity="{:.2f}"/></filter>'.format(c["shadow"]))
    A('<filter id="noise" x="0" y="0" width="100%" height="100%">'
      '<feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="3" stitchTiles="stitch">'
      '<animate attributeName="baseFrequency" values="0.9;0.82;0.9" dur="8s" repeatCount="indefinite"/>'
      '</feTurbulence><feColorMatrix type="saturate" values="0"/></filter>')
    # clips
    A('<clipPath id="card"><rect x="0" y="0" width="{}" height="{}" rx="26"/></clipPath>'.format(W, H))
    A('<clipPath id="clipL"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}"/></clipPath>'.format(**LP))
    A('<clipPath id="clipR"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}"/></clipPath>'.format(**RP))
    # per-line ascii typing clips
    for i in range(len(ASCII)):
        y = ATOP + i * ALH
        A('<clipPath id="al{i}"><rect x="{x:.1f}" y="{y:.1f}" width="0" height="{h:.1f}">'
          '<animate attributeName="width" values="0;0;{w:.1f};{w:.1f};{w:.1f}" '
          'keyTimes="0;{k0:.4f};{k1:.4f};0.93;1" dur="16s" repeatCount="indefinite"/>'
          '</rect></clipPath>'.format(
              i=i, x=AX - 2, y=y - AFS * 0.92, h=ALH, w=AW + 6,
              k0=(0.25 + i * 0.11) / 16, k1=(0.25 + i * 0.11 + 0.34) / 16))
    # role typing clips + cursor tracks
    total = 4.0 * len(ROLES)
    rx = CX + 26
    for i, ph in enumerate(ROLES):
        pts = typing_points(len(ph), i * 4.0, total)
        # Pad the clip past the last glyph. At exactly n*12 the final character sits on
        # the clip boundary and hinting shaves its right edge off ("Builde|r"). The pad
        # is narrower than the cursor block that sits at the same spot, so it never
        # reveals a sliver of the next character.
        wv, wk = keyed([(t, n * 12.0 + 9.0 if n else 0.0) for t, n in pts], total)
        A('<clipPath id="rc{i}"><rect x="{x}" y="196" width="0" height="34">'
          '<animate attributeName="width" values="{v}" keyTimes="{k}" dur="{d}s" '
          'calcMode="discrete" repeatCount="indefinite"/></rect></clipPath>'.format(
              i=i, x=rx, v=wv, k=wk, d=total))
    A('</defs>')

    # ---------------- style (hover, only when SVG is opened directly) ----------------
    A('<style>'
      '.pill{transform-box:fill-box;transform-origin:center;transition:transform .25s cubic-bezier(.2,.8,.2,1),filter .25s ease}'
      '.pill:hover{transform:scale(1.07);filter:brightness(1.3) saturate(1.2)}'
      '.soc{transform-box:fill-box;transform-origin:center;transition:transform .25s cubic-bezier(.2,.8,.2,1),filter .25s ease;cursor:pointer}'
      '.soc:hover{transform:scale(1.12);filter:brightness(1.35)}'
      '@media (prefers-reduced-motion:reduce){*{animation:none}}'
      '</style>')

    # ---------------- background ----------------
    A('<g clip-path="url(#card)">')
    A('<rect width="{}" height="{}" fill="{}"/>'.format(W, H, c["bg"]))
    # blobs
    A('<g filter="url(#soft)">')
    A('<ellipse cx="210" cy="140" rx="300" ry="230" fill="url(#b1)">'
      '<animateTransform attributeName="transform" type="translate" '
      'values="0 0;40 -26;-24 18;0 0" dur="18s" repeatCount="indefinite"/></ellipse>')
    A('<ellipse cx="980" cy="520" rx="330" ry="240" fill="url(#b2)">'
      '<animateTransform attributeName="transform" type="translate" '
      'values="0 0;-38 -22;26 20;0 0" dur="22s" repeatCount="indefinite"/></ellipse>')
    A('<ellipse cx="620" cy="60" rx="280" ry="180" fill="url(#b3)">'
      '<animateTransform attributeName="transform" type="translate" '
      'values="0 0;24 30;-30 -12;0 0" dur="26s" repeatCount="indefinite"/></ellipse>')
    A('</g>')
    # faint grid
    A('<g stroke="{}" stroke-opacity="{}" stroke-width="1">'.format(c["text"], c["grid"]))
    for gx in range(0, W + 1, 40):
        A('<line x1="{0}" y1="0" x2="{0}" y2="{1}"/>'.format(gx, H))
    for gy in range(0, H + 1, 40):
        A('<line x1="0" y1="{0}" x2="{1}" y2="{0}"/>'.format(gy, W))
    A('</g>')
    # particles
    for i in range(18):
        px = random.uniform(20, W - 20)
        py = random.uniform(40, H - 40)
        r = random.uniform(0.9, 2.0)
        dur = random.uniform(9, 20)
        col = [c["a1"], c["a2"], c["a3"]][i % 3]
        A('<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.2f}" fill="{col}" opacity="0">'
          '<animate attributeName="opacity" values="0;.75;0" dur="{d:.1f}s" '
          'begin="{b:.1f}s" repeatCount="indefinite"/>'
          '<animate attributeName="cy" values="{y:.1f};{y2:.1f}" dur="{d:.1f}s" '
          'begin="{b:.1f}s" repeatCount="indefinite"/></circle>'.format(
              x=px, y=py, y2=py - random.uniform(60, 150), r=r, col=col,
              d=dur, b=random.uniform(0, 8)))
    # full-card scanline
    A('<rect x="0" y="-70" width="{}" height="70" fill="url(#scanG)" opacity=".5">'
      '<animate attributeName="y" values="-70;{}" dur="6s" repeatCount="indefinite"/>'
      '</rect>'.format(W, H))
    # noise
    A('<rect width="{}" height="{}" filter="url(#noise)" opacity="{}" '
      'style="mix-blend-mode:overlay"/>'.format(W, H, c["noise"]))
    A('</g>')

    # card border + shimmer
    A('<rect x="1" y="1" width="{}" height="{}" rx="25" fill="none" stroke="{}" '
      'stroke-width="1.5"/>'.format(W - 2, H - 2, c["border2"]))
    A('<rect x="1" y="1" width="{}" height="{}" rx="25" fill="none" stroke="url(#shim)" '
      'stroke-width="1.5" opacity=".85"/>'.format(W - 2, H - 2))

    # =============== LEFT PANEL ===============
    A('<g filter="url(#drop)"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" '
      'fill="url(#pnl)" fill-opacity="{o}"/></g>'.format(o=0.92, **LP))
    A('<g clip-path="url(#clipL)">')
    A('<rect x="{x}" y="{y}" width="{w}" height="180" fill="url(#glass)"/>'.format(**LP))
    # panel titlebar
    for j, col in enumerate(["#FF5F57", "#FEBC2E", "#28C840"]):
        A('<circle cx="{}" cy="50" r="5" fill="{}" opacity=".9"/>'.format(56 + j * 18, col))
    A('<text x="{}" y="54" font-family="{}" font-size="11.5" fill="{}" '
      'letter-spacing="1.2">portrait.asc</text>'.format(LP["x"] + 96, MONO, c["dim"]))
    A('<line x1="{}" y1="72" x2="{}" y2="72" stroke="{}" stroke-width="1"/>'.format(
        LP["x"], LP["x"] + LP["w"], c["border"]))

    # ascii art (floating group)
    A('<g>')
    A('<animateTransform attributeName="transform" type="translate" '
      'values="0 0;0 -7;0 0" dur="7s" repeatCount="indefinite" calcMode="spline" '
      'keyTimes="0;0.5;1" keySplines=".45 0 .55 1;.45 0 .55 1"/>')
    A('<g font-family="{}" font-size="{:.2f}" fill="url(#asc)" xml:space="preserve" '
      'filter="url(#glowS)">'.format(MONO, AFS))
    for i, line in enumerate(ASCII):
        # The clip does the character-level typing; the opacity animation repeats the
        # same schedule at line level. Renderers that ignore clip-path on <text>
        # (WebKit, SVG-as-image) still get a correct line-by-line reveal instead of
        # the whole portrait appearing at once.
        k0 = (0.25 + i * 0.11) / 16
        k1 = (0.25 + i * 0.11 + 0.34) / 16
        A('<text clip-path="url(#al{i})" opacity="1" x="{x:.1f}" y="{y:.1f}" '
          'letter-spacing="0">{t}'
          '<animate attributeName="opacity" values="0;0;1;1;1" '
          'keyTimes="0;{k0:.4f};{k1:.4f};0.93;1" dur="16s" repeatCount="indefinite"/>'
          '</text>'.format(
              i=i, x=AX, y=ATOP + i * ALH, t=esc(line.ljust(MAXLEN)), k0=k0, k1=k1))
    A('</g></g>')

    # ascii scanline
    A('<rect x="{x}" y="{y}" width="{w}" height="54" fill="url(#scanG)">'
      '<animate attributeName="y" values="{y};{y2}" dur="4.5s" repeatCount="indefinite"/>'
      '</rect>'.format(x=LP["x"], y=LP["y"] + 44, w=LP["w"], y2=LP["y"] + LP["h"]))

    # caption + cursor
    cy = ATOP + len(ASCII) * ALH + 42
    A('<text x="{x}" y="{y:.0f}" font-family="{m}" font-size="12" fill="{d}" '
      'letter-spacing="2.4">RENDER COMPLETE</text>'.format(x=AX, y=cy, m=MONO, d=c["dim"]))
    A('<rect x="{x:.0f}" y="{y:.0f}" width="9" height="15" fill="{a}">'
      '<animate attributeName="opacity" values="1;1;0;0" dur="1.1s" repeatCount="indefinite"/>'
      '</rect>'.format(x=AX + 122, y=cy - 12, a=c["a2"]))
    A('<line x1="{}" y1="{}" x2="{}" y2="{}" stroke="url(#acc)" stroke-width="2" '
      'opacity=".7"/>'.format(AX, cy + 22, AX + AW, cy + 22))
    A('</g>')
    A('<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="none" stroke="{b}" '
      'stroke-width="1"/>'.format(b=c["border"], **LP))

    # =============== RIGHT PANEL ===============
    A('<g filter="url(#drop)"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" '
      'fill="url(#pnl)" fill-opacity="{o}"/></g>'.format(o=0.92, **RP))
    A('<g clip-path="url(#clipR)">')
    A('<rect x="{x}" y="{y}" width="{w}" height="200" fill="url(#glass)"/>'.format(**RP))
    for j, col in enumerate(["#FF5F57", "#FEBC2E", "#28C840"]):
        A('<circle cx="{}" cy="50" r="5" fill="{}" opacity=".9"/>'.format(472 + j * 18, col))
    A('<text x="{}" y="54" font-family="{}" font-size="11.5" fill="{}" text-anchor="middle" '
      'letter-spacing="1.1">{}@dev — zsh — 96×32</text>'.format(
          RP["x"] + RP["w"] / 2, MONO, c["dim"], NAME.lower()))
    A('<line x1="{}" y1="72" x2="{}" y2="72" stroke="{}" stroke-width="1"/>'.format(
        RP["x"], RP["x"] + RP["w"], c["border"]))
    # sheen sweep over the terminal glass
    A('<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="url(#sheen)"/>'.format(**RP))

    def reveal(begin, dx=-14):
        return ('<animate attributeName="opacity" values="0;1" dur=".55s" begin="{b:.2f}s" '
                'fill="freeze"/><animateTransform attributeName="transform" type="translate" '
                'values="{dx} 0;0 0" dur=".55s" begin="{b:.2f}s" fill="freeze" '
                'calcMode="spline" keyTimes="0;1" keySplines=".2 .8 .2 1"/>'.format(b=begin, dx=dx))

    # greeting
    A('<g opacity="0">{r}<text x="{x}" y="118" font-size="17" fill="{m}" '
      'letter-spacing="3.4">HI THERE 👋</text></g>'.format(r=reveal(0.3), x=CX, m=c["muted"]))
    # name
    A('<g opacity="0">{r}<text x="{x}" y="172" font-size="46" font-weight="700" '
      'fill="url(#acc)" letter-spacing="-1.2" filter="url(#glow)">I&apos;m {n}</text></g>'.format(
          r=reveal(0.55), x=CX, n=NAME))

    # role typing line
    A('<g opacity="0">{r}'.format(r=reveal(1.1)))
    A('<text x="{x}" y="222" font-family="{m}" font-size="20" fill="{a}">&gt;</text>'.format(
        x=CX, m=MONO, a=c["a3"]))
    for i, ph in enumerate(ROLES):
        # Without this the phrases only stay separated by their clips — and a renderer
        # that drops clip-path paints all five on top of each other. The opacity window
        # keeps exactly one phrase on screen no matter what happens to the clipping.
        pv, pk = keyed([(0.0, 1.0 if i == 0 else 0.0),
                        (i * 4.0, 1.0),
                        (i * 4.0 + 4.0, 0.0)], total)
        # Third, independent guard. The clip can be dropped and the opacity animation
        # can be dropped; a phrase parked at x -6000 is outside the viewBox and the
        # outermost <svg> clips that away in every renderer. Worst case one phrase
        # shows instead of five stacked on top of each other.
        tv, tk = keyed_pairs([(0.0, i == 0), (i * 4.0, True), (i * 4.0 + 4.0, False)], total)
        A('<g transform="translate({t0})">'
          '<animateTransform attributeName="transform" type="translate" values="{tv}" '
          'keyTimes="{tk}" dur="{d}s" calcMode="discrete" repeatCount="indefinite"/>'.format(
              t0="0 0" if i == 0 else "-6000 0", tv=tv, tk=tk, d=total))
        A('<text clip-path="url(#rc{i})" opacity="1" x="{x}" y="222" font-family="{m}" '
          'font-size="20" fill="{t}" letter-spacing="0">{p}'
          '<animate attributeName="opacity" values="{pv}" keyTimes="{pk}" dur="{d}s" '
          'calcMode="discrete" repeatCount="indefinite"/>'
          '</text>'.format(
              i=i, x=rx, m=MONO, t=c["text"], p=esc(ph), pv=pv, pk=pk, d=total))
        A('</g>')
        pts = typing_points(len(ph), i * 4.0, total)
        xv, xk = keyed([(t, rx + n * 12.0) for t, n in pts], total)
        ov, ok = keyed([(t, 1 if (i * 4.0 - 0.02) <= t <= (i * 4.0 + 4.0) else 0) for t, _ in pts], total)
        A('<rect y="207" width="10" height="20" fill="{a}" opacity="0" x="{x}">'
          '<animate attributeName="x" values="{xv}" keyTimes="{xk}" dur="{d}s" '
          'calcMode="discrete" repeatCount="indefinite"/>'
          '<animate attributeName="opacity" values="{ov}" keyTimes="{ok}" dur="{d}s" '
          'calcMode="discrete" repeatCount="indefinite"/>'
          '<animate attributeName="fill-opacity" values="1;1;.15;.15" dur="1s" '
          'repeatCount="indefinite"/></rect>'.format(
              a=c["a2"], x=rx, xv=xv, xk=xk, ov=ov, ok=ok, d=total))
    A('</g>')

    A('<line x1="{x}" y1="252" x2="{x2}" y2="252" stroke="{b}" stroke-width="1" opacity="0">'
      '<animate attributeName="opacity" values="0;1" dur=".6s" begin="1.5s" fill="freeze"/>'
      '</line>'.format(x=CX, x2=CX + CW, b=c["border"]))

    # info rows — the block always occupies the 282..414 band so the gap down to
    # STACK stays constant no matter how many rows INFO has.
    nrow = len(INFO)
    rstep = min(38.0, 132.0 / (nrow - 1)) if nrow > 1 else 0.0
    rtop = 282 + (132.0 - rstep * (nrow - 1)) / 2
    for i, (icon, label, val) in enumerate(INFO):
        y = rtop + i * rstep
        A('<g opacity="0">{r}'.format(r=reveal(1.8 + i * 0.18)))
        A('<g transform="translate({ix},{iy})" fill="none" stroke="{a}" stroke-width="1.5" '
          'stroke-linecap="round" stroke-linejoin="round">{p}</g>'.format(
              ix=CX + 9, iy=round(y - 5, 1), a=c["a2"], p=ICONS[icon]))
        A('<text x="{x}" y="{y}" font-family="{m}" font-size="12" fill="{d}" '
          'letter-spacing="1.6">{l}</text>'.format(x=CX + 30, y=round(y, 1), m=MONO, d=c["dim"],
                                                   l=label.upper()))
        A('<text x="{x}" y="{y}" font-size="15.5" fill="{t}">{v}</text>'.format(
            x=CX + 148, y=round(y, 1), t=c["text"], v=esc(val)))
        A('</g>')

    # skills
    A('<text x="{x}" y="450" font-family="{m}" font-size="12" fill="{d}" letter-spacing="2.6" '
      'opacity="0">STACK<animate attributeName="opacity" values="0;1" dur=".5s" begin="2.9s" '
      'fill="freeze"/></text>'.format(x=CX, m=MONO, d=c["dim"]))
    rows, cur, curw = [], [], 0.0
    for sk in SKILLS:
        wpill = len(sk) * 7.0 + 28
        if curw + wpill > CW and cur:
            rows.append(cur); cur, curw = [], 0.0
        cur.append((sk, wpill)); curw += wpill + 10
    if cur:
        rows.append(cur)
    idx = 0
    for ri, row in enumerate(rows[:2]):
        px = CX
        py = 460 + ri * 36
        for sk, wpill in row:
            A('<g class="pill" opacity="0">'
              '<animate attributeName="opacity" values="0;1" dur=".45s" begin="{b:.2f}s" fill="freeze"/>'
              '<rect x="{x:.1f}" y="{y}" width="{w:.1f}" height="28" rx="14" fill="{pb}" '
              'fill-opacity="{po}" stroke="{a}" stroke-opacity=".45" stroke-width="1">'
              '<animate attributeName="stroke-opacity" values=".25;.75;.25" dur="{d:.1f}s" '
              'begin="{b2:.2f}s" repeatCount="indefinite"/></rect>'
              '<text x="{tx:.1f}" y="{ty}" font-size="12.5" fill="{t}" text-anchor="middle" '
              'letter-spacing=".2">{s}</text></g>'.format(
                  b=3.05 + idx * 0.07, b2=idx * 0.3, d=3.4 + (idx % 3) * 0.7,
                  x=px, y=py, w=wpill, pb=c["pillbg"], po=c["pillop"],
                  a=[c["a1"], c["a2"], c["a3"]][idx % 3],
                  tx=px + wpill / 2, ty=py + 18.5, t=c["text"], s=esc(sk)))
            px += wpill + 10
            idx += 1

    # socials
    socials = [
        ("github", "https://github.com/Eshwar1502"),
        ("linkedin", "https://www.linkedin.com/in/eshwar-prasad-24343a245/"),
    ]
    marks = {
        "github": '<circle cx="-4.5" cy="-4" r="2.6"/><circle cx="-4.5" cy="5" r="2.6"/>'
                  '<circle cx="5" cy="-4" r="2.6"/><path d="M-4.5 -1.4v3.8"/>'
                  '<path d="M5 -1.4v1.2c0 2.2-2 3-4.4 3.2"/>',
        "linkedin": '<path d="M-6 -1.5v7"/><circle cx="-6" cy="-5.4" r="1.1"/>'
                    '<path d="M-1 5.5v-7"/><path d="M-1 1.2c0-2.2 1.4-3 2.9-3S6 -.9 6 1.4v4.1"/>',
        "x": '<path d="M-6 -6 6 6"/><path d="M6 -6 -6 6"/>',
        "globe": '<circle cx="0" cy="0" r="6.6"/><path d="M-6.6 0h13.2"/>'
                 '<path d="M0 -6.6c3.3 3.5 3.3 9.7 0 13.2c-3.3-3.5-3.3-9.7 0-13.2Z"/>',
    }
    for i, (key, href) in enumerate(socials):
        cxp = CX + 20 + i * 48
        A('<a xlink:href="{h}" target="_blank"><g class="soc" opacity="0">'
          '<animate attributeName="opacity" values="0;1" dur=".5s" begin="{b:.2f}s" fill="freeze"/>'
          '<circle cx="{cx}" cy="556" r="16" fill="{pb}" fill-opacity="{po}" stroke="{bd}" '
          'stroke-width="1"/>'
          '<circle cx="{cx}" cy="556" r="16" fill="none" stroke="{a}" stroke-width="1" opacity=".5">'
          '<animate attributeName="opacity" values=".18;.7;.18" dur="3.6s" begin="{b2:.1f}s" '
          'repeatCount="indefinite"/></circle>'
          '<g transform="translate({cx},556)" fill="none" stroke="{a}" stroke-width="1.6" '
          'stroke-linecap="round" stroke-linejoin="round" filter="url(#glowS)">{m}</g>'
          '</g></a>'.format(h=href, b=3.7 + i * 0.12, b2=i * 0.5, cx=cxp,
                            pb=c["pillbg"], po=c["pillop"], bd=c["border2"],
                            a=[c["a2"], c["a1"], c["a3"], c["a2"]][i], m=marks[key]))

    A('<text x="{x}" y="561" font-size="13" fill="{d}" text-anchor="end" opacity="0">'
      'Thanks for stopping by.'
      '<animate attributeName="opacity" values="0;1" dur=".8s" begin="4.3s" fill="freeze"/>'
      '</text>'.format(x=CX + CW, d=c["dim"]))
    A('</g>')
    A('<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="none" stroke="{b}" '
      'stroke-width="1"/>'.format(b=c["border"], **RP))

    A('</svg>')
    return "\n".join(s)


for theme in ("dark", "light"):
    out = build(theme)
    path = os.path.join(OUT_DIR, "{}-{}.svg".format(theme, VERSION))
    with open(path, "w", encoding="utf-8") as f:
        f.write(out)
    ET.fromstring(out.encode("utf-8"))  # well-formedness check
    print(os.path.basename(path), "ok", len(out), "bytes")
