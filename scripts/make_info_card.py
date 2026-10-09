#!/usr/bin/env python3
"""
Generate a clean, animated Neofetch-style info card SVG
matching darshan-ascii.svg canvas size (840 x 880).

Lines fade and slide in on a staggered timing curve like terminal output.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "info-card.svg")

W, H = 840, 880
PAD = 24
TITLEBAR_H = 30

BG = "#0d1117"
BG2 = "#111722"
FRAME = "#30363d"
MUTED = "#7d8590"
TEXT = "#e6edf3"
CYAN = "#22d3ee"
GREEN = "#39d353"
YELLOW = "#f2cc60"
PURPLE = "#bc8cff"
BLUE = "#58a6ff"
RED = "#ff7b72"

# Neofetch items for Darshan
INFO = [
    ("Title", "Darshan", CYAN, True),
    ("Divider", "-----------------------", MUTED, False),
    ("OS", "GitHub Core / Dev Edition x86_64", TEXT, False),
    ("Host", "Full Stack Developer · AI Builder", TEXT, False),
    ("Kernel", "Python · JavaScript · HTML/CSS", TEXT, False),
    ("Uptime", "Since Nov 2023 (Active Builder)", TEXT, False),
    ("Projects", "RAG, bhoomi-setu, Monthly-todo-tracker", TEXT, False),
    ("Focus", "Generative AI · Retrieval Augmented Gen · Web Apps", TEXT, False),
    ("Shell", "zsh 5.9 (x86_64-darshan)", TEXT, False),
    ("Terminal", "antigravity-term", TEXT, False),
    ("Activity", "218 Contributions in the last year", GREEN, False),
    ("Status", "Open to collaborate & innovate", YELLOW, False),
]

PALETTE_COLORS = [
    "#484f58", "#ff7b72", "#3fb950", "#d29922", "#58a6ff", "#bc8cff", "#39c5cf", "#b1bac4",
    "#6e7681", "#ffa198", "#56d364", "#e3b341", "#79c0ff", "#d2a8ff", "#56d4dd", "#f0f6fc"
]

STAGGER = 0.12
FADE_DUR = 0.45

css = f"""
@keyframes lineIn {{
  0%   {{ opacity: 0; transform: translateX(-12px); }}
  100% {{ opacity: 1; transform: translateX(0); }}
}}
.line {{ opacity: 0; animation: lineIn {FADE_DUR}s cubic-bezier(0.16, 1, 0.3, 1) both; }}
@media (prefers-reduced-motion: reduce) {{ .line {{ opacity: 1 !important; transform: none !important; animation: none !important; }} }}
""".strip()

parts = [
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
    f'font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">',
    f'<style>{css}</style>',
    '<defs>'
    f'<linearGradient id="ibg" x1="0" y1="0" x2="0" y2="1">'
    f'<stop offset="0" stop-color="{BG2}"/><stop offset="1" stop-color="{BG}"/></linearGradient>'
    '</defs>',
    f'<rect width="{W}" height="{H}" rx="12" fill="url(#ibg)"/>',
    f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="12" fill="none" stroke="{FRAME}" stroke-width="1"/>',
    f'<line x1="0" y1="{TITLEBAR_H}" x2="{W}" y2="{TITLEBAR_H}" stroke="{FRAME}"/>',
]
for i, dot in enumerate(["#ff5f56", "#ffbd2e", "#27c93f"]):
    parts.append(f'<circle cx="{PAD + i*16}" cy="{TITLEBAR_H/2}" r="5" fill="{dot}"/>')
parts.append(f'<text x="{W/2}" y="{TITLEBAR_H/2 + 4}" fill="{MUTED}" font-size="12" text-anchor="middle">darshan@github: ~$ neofetch</text>')

start_y = TITLEBAR_H + 50
line_height = 42

for i, (key, val, col, is_title) in enumerate(INFO):
    y = start_y + i * line_height
    delay = i * STAGGER
    parts.append(f'<g class="line" style="animation-delay: {delay:.2f}s">')
    if is_title:
        parts.append(f'<text x="{PAD + 16}" y="{y}" font-size="28" font-weight="700" fill="{col}">{val}</text>')
        parts.append(f'<text x="{PAD + 16 + 130}" y="{y}" font-size="22" font-weight="400" fill="{MUTED}">@github</text>')
    elif key == "Divider":
        parts.append(f'<text x="{PAD + 16}" y="{y}" font-size="20" fill="{col}">{val}</text>')
    else:
        parts.append(f'<text x="{PAD + 16}" y="{y}" font-size="20" font-weight="700" fill="{CYAN}">{key}:</text>')
        parts.append(f'<text x="{PAD + 160}" y="{y}" font-size="20" fill="{col}">{val}</text>')
    parts.append('</g>')

# Color blocks row at bottom
color_y = start_y + len(INFO) * line_height + 40
delay_colors = len(INFO) * STAGGER
parts.append(f'<g class="line" style="animation-delay: {delay_colors:.2f}s">')
block_w = 40
block_h = 24
for row in range(2):
    for col in range(8):
        c_idx = row * 8 + col
        bx = PAD + 16 + col * (block_w + 6)
        by = color_y + row * (block_h + 6)
        parts.append(f'<rect x="{bx}" y="{by}" width="{block_w}" height="{block_h}" rx="4" fill="{PALETTE_COLORS[c_idx]}"/>')
parts.append('</g>')

parts.append('</svg>')
svg = "".join(parts)
with open(OUT, "w", encoding="utf-8") as f:
    f.write(svg)
print(f"wrote {OUT}: {W} x {H}, {len(svg)//1024} KB")
