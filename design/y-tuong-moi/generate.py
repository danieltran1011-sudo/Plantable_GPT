#!/usr/bin/env python3
"""Generate the "Ý tưởng mới" artboards (YT0–YT7) for La Rotonda B.

The boards use the same format and visual language as the canvas artboards in design/rotonda-b,
so tools/build.py turns them into pages the same way. Geometry is in centimetres, taken from the
RB plans: main axis x = 331, sea (east) at the top, new building y 0..2000, porte-cochère y 2000..2440.

Usage: python3 design/y-tuong-moi/generate.py   (then run tools/build.py)
"""
import json
from html import escape
from pathlib import Path

HERE = Path(__file__).resolve().parent

INK, MUTED, ACC, PAPER, RULE = '#15263B', '#4A5868', '#7A5620', '#F3F4F1', '#C5CAC5'
OLD, OLD_LINE, TERR, PC = '#ECEBE4', '#8E918C', '#E6E8E2', '#E4DCC6'
WATER, WATER_LINE, TEAL, RUST, BLUE = '#BFDDE0', '#5A9AA0', '#1F7A80', '#B0502C', '#3B5BA5'
GREEN, GREEN_LINE, PAVE, EARTH = '#DCE5D3', '#6C8F54', '#D9CFB6', '#E2DCCD'
FONTS = ('<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:'
         'wght@500;600&amp;family=Be+Vietnam+Pro:wght@400;500;600&amp;display=swap">')


# ---------- SVG helpers ----------

def rect(x, y, w, h, fill, stroke=None, sw=2.5, extra=''):
    s = f' stroke="{stroke}" stroke-width="{sw}"' if stroke else ''
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}"{s}{extra}></rect>'


def path(d, stroke, sw, fill='none', extra=''):
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{extra}></path>'


def circle(cx, cy, r, fill, stroke=None, sw=2.5, extra=''):
    s = f' stroke="{stroke}" stroke-width="{sw}"' if stroke else ''
    return f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}"{s}{extra}></circle>'


def label(x, y, text, px, k, fill=INK, weight=600, anchor='middle', halo='#FFFFFF', rot=None):
    """Text sized in screen px; k = viewBox units per screen px."""
    size = round(px * k, 1)
    tr = f' transform="rotate({rot} {x} {y})"' if rot is not None else ''
    st = (f' stroke="{halo}" stroke-width="{round(size * 0.32, 1)}" paint-order="stroke" stroke-linejoin="round"'
          if halo else '')
    return (f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" fill="{fill}" '
            f'text-anchor="{anchor}"{st}{tr}>{escape(text, quote=False)}</text>')


def arrow(d, color, x, y, angle, k, dashed=True, w=1.8):
    sw = round(w * k, 1)
    dash = f' stroke-dasharray="{round(6 * k)} {round(3.2 * k)}"' if dashed else ''
    s = round(k / 3.8, 2)
    return (path(d, color, sw, extra=f'{dash} stroke-linecap="round" stroke-linejoin="round"')
            + f'<path d="M-20 -16 L18 0 L-20 16 z" fill="{color}" '
              f'transform="translate({x} {y}) rotate({angle}) scale({s})"></path>')


def marker(n, x, y, k, fill=ACC):
    r = round(11 * k)
    return circle(x, y, r, fill, '#FFFFFF', round(1.5 * k, 1)) + label(x, y + round(4.3 * k), str(n), 12, k, '#FFFFFF', halo=None)


# ---------- Plan base (simplified from RB2 / RB3) ----------

PLAN_VIEW = (-1150, -850, 3100, 3478)


def plan(level, k, porte_label=True):
    """level: 't1' (cốt +0.90), 't2' (cốt +5.60) or 'mai' (roof)."""
    o = []
    old = 'M-1038 -742 H-190 V-220 H-320 V1250 H-720 V1130 H-1038 Z'
    body = 'M-320 0 H1700 V1630 A170 170 0 0 1 1530 1800 H982 V2000 H-320 Z'
    o.append(path(old, OLD_LINE, 22, OLD))
    if level == 'mai':
        o.append(rect(-129, -200, 920, 200, TERR, OLD_LINE, 2.5, ' stroke-dasharray="14 10"'))
        o.append(path(body, INK, 16, '#FFFFFF'))
        o.append(path('M-280 40 H1660 V1630 A130 130 0 0 1 1530 1760 H942 V1960 H-280 Z', MUTED, 3, extra=' stroke-dasharray="18 12"'))
        o.append(path('M982 0 V1800', INK, 8))
        o.append(rect(-19, 2000, 700, 440, TERR, INK))
        o.append(circle(331, 1150, 110, '#BFD9DE', INK, 4))
        o.append(circle(1530, 1630, 170, '#D8CFB8', INK, 5))
        o.append(circle(-520, 880, 170, '#D8CFB8', INK, 5))
        o.append(path('M331 -700 V2600', ACC, 5, extra=' stroke-dasharray="40 24"'))
        o += [label(331, 520, 'MÁI THÂN GIỮA', 13, k), label(331, 1330, 'giếng trời Ø 2,2 m', 11, k, MUTED, 400),
              label(-680, 300, 'NHÀ CŨ', 14, k, rot=-90), label(-520, 1110, 'vòm cũ', 11, k, MUTED, 400),
              label(1530, 1880, 'chóp vòm tháp', 11, k, MUTED, 400),
              label(331, -60, 'sân thượng +10.30 bên dưới', 10, k, MUTED, 400),
              label(331, 2250, 'MÁI PORTE-COCHÈRE', 11, k)]
    else:
        if level == 't1':
            o.append(rect(-320, -200, 2020, 200, TERR, INK))
            o.append(rect(-129, -200, 920, 200, '#DDE2D6', INK))
            o += [rect(x, -200, 56, 56, INK) for x in (-132, 42, 216, 390, 564, 738)]
        else:
            o.append(rect(-129, -200, 920, 200, TERR, INK))
            o += [circle(-104 + 174 * i, -172, 24, INK) for i in range(6)]
        o.append(path(body, 'none', 0, '#FFFFFF'))
        pc_fill = PC if level == 't1' else TERR
        o.append(rect(-19, 2000, 700, 440, pc_fill, INK))
        o += [circle(x, 2415, 22, INK) for x in (6, 222, 440, 656)]
        o.append(rect(-100, 700, 862, 900, INK))
        o.append(circle(331, 1150, 410, '#FFFFFF' if level == 't1' else '#E4EEEC'))
        walls = [(-320, 0, 2020, 30), (-320, 0, 20, 2000), (1670, 0, 30, 1630), (982, 1770, 548, 30),
                 (952, 1800, 30, 200), (-320, 1970, 1302, 30), (972, 30, 20, 1770),
                 (-300, 700, 200, 20), (762, 700, 210, 20), (-300, 1580, 200, 20), (762, 1580, 210, 20),
                 (-29, 1600, 20, 370), (671, 1600, 20, 370)]
        walls += ([(992, 760, 678, 20), (992, 1000, 678, 20)] if level == 't1' else
                  [(992, 500, 678, 20), (992, 760, 678, 20), (992, 1250, 678, 20), (-300, 520, 1272, 20)])
        o += [rect(*w, INK) for w in walls]
        gaps = [(231, 690, 200, 72), (251, 1540, 160, 70), (-108, 965, 70, 90), (700, 965, 70, 90), (972, 300, 20, 140)]
        gaps += [(251, 1966, 160, 36)] if level == 't1' else [(251, 515, 160, 30)]
        o += [rect(*g, '#FFFFFF') for g in gaps]
        o += [rect(x, 0, 120, 30, '#FFFFFF', INK) for x in (-272, -77, 97, 271, 445, 619, 814)]
        o.append(rect(-320, 770, 20, 120, '#FFFFFF'))
        o.append(path('M1685 1630 A155 155 0 0 1 1530 1785', INK, 30))
        o.append(rect(774, 730, 170, 180, '#FFFFFF', INK, 3))
        o.append(path('M774 730 L944 910 M944 730 L774 910', INK, 1.5))
        o.append(path(' '.join(f'M764 {y} H966' for y in range(1268, 1581, 26)) + ' M865 1242 V1580', '#6F5A3A', 2.2))
        if level == 't1':
            o.append(circle(331, 1150, 250, 'none', ACC, 2))
            o.append(circle(331, 1150, 120, 'none', ACC, 2))
        o.append(path('M331 -700 V2600', ACC, 4, extra=' stroke-dasharray="40 24"'))
        if level == 't1':
            o += [label(331, 400, 'GRAND SALON', 13, k), label(331, 1250, 'LA ROTONDA', 12, k),
                  label(331, 1800, 'TIỀN SẢNH', 11, k), label(1331, 400, 'PHÒNG ĂN', 12, k),
                  label(1331, 890, 'SOẠN', 10, k), label(1331, 1450, 'BẾP ÂU', 12, k),
                  label(331, -90, 'HÀNG VÒM BIỂN', 10, k), label(1240, -90, 'SÂN THƯỢNG BIỂN', 10, k),
                  label(-200, 1150, 'HÀNH LANG TRANH', 9, k, rot=-90)]
            if porte_label:
                o.append(label(331, 2250, 'PORTE-COCHÈRE', 11, k))
        else:
            o += [label(331, 330, 'PHÒNG GIA ĐÌNH', 13, k), label(331, 630, 'GALLERIA', 10, k),
                  label(331, 1170, 'KHOẢNG THÔNG', 11, k), label(331, 1800, 'PHÒNG ĐỌC', 11, k),
                  label(1331, 280, 'SUITE KHÁCH', 12, k), label(1331, 1500, 'SUITE 2', 12, k),
                  label(331, -90, 'LOGGIA BIỂN', 10, k)]
        o += [label(859, 830, 'TM', 10, k), label(-680, 300, 'NHÀ CŨ', 14, k, rot=-90),
              label(331, -330, 'VƯỜN SAU · cốt −2.50', 11, k, MUTED, 400)]
    o.append(label(1330, -640, 'HƯỚNG BIỂN · ĐÔNG', 12, k, ACC))
    o.append(path('M1180 -520 h500 M1180 -532 v24 M1280 -526 v12 M1380 -526 v12 M1480 -526 v12 M1580 -526 v12 M1680 -532 v24', INK, 3))
    o += [label(1180, -548, '0', 10, k, INK, 400, halo=None), label(1680, -548, '5 m', 10, k, INK, 400, halo=None)]
    return '\n'.join(o)


def site(k):
    """Forecourt, drive, garage and road in front of the house (from RB0)."""
    o = [rect(-1150, 2440, 3100, 1160, '#EFEDE4'),
         rect(-1038, 1250, 848, 2350, '#EAEAE5'),
         path('M331 3580 V3140 Q331 2790 681 2790 H900 Q1260 2790 1260 2560 Q1260 2270 860 2270 H-19 '
              'Q-359 2270 -359 2600 V2800 Q-359 3120 -710 3120 V3590', PAVE, 330),
         rect(20, 2470, 780, 130, GREEN, GREEN_LINE, 3, ' rx="60"'),
         rect(-190, 2980, 250, 560, GREEN, GREEN_LINE, 3),
         rect(581, 2960, 1119, 600, '#D8C9A0', ACC, 4),
         rect(1700, 900, 310, 2700, '#D6D4CC'),
         rect(-1150, 3600, 3100, 250, '#C6C7C1'),
         path('M-190 -400 V3600 H2010 V-400 Z', ACC, 4, extra=' stroke-dasharray="30 18"'),
         label(1340, 2420, 'SÂN DANH DỰ', 12, k), label(1140, 3270, 'NHÀ XE', 12, k),
         label(1855, 2500, 'DỐC PHỤC VỤ 12 %', 10, k, rot=-90),
         label(331, 3760, 'ĐƯỜNG ĐT639', 13, k), label(331, 3690, 'cổng chính', 10, k, MUTED, 400),
         label(-760, 2500, 'SÂN NHÀ CŨ', 11, k, rot=-90)]
    return '\n'.join(o)


# ---------- Longitudinal section along the main axis (east left, west right) ----------

SECTION_VIEW = (-1300, -1720, 5560, 2200)


def section(k, labels=True):
    """Schematic section along x = 331. Horizontal = plan y (cm), vertical = -level (cm)."""
    o = [rect(-1300, 250, 5560, 230, EARTH), rect(2460, 0, 1800, 250, EARTH),
         path('M-1300 250 H0', GREEN_LINE, 6),
         rect(0, -1500, 2000, 1750, '#FFFFFF'), rect(2000, -75, 460, 325, '#FFFFFF'),
         rect(-310, 250, 950, 150, WATER, WATER_LINE, 3),
         rect(640, 250, 1820, 30, INK)]
    for z, s1, s2 in ((90, -200, 2000), (560, -200, 740), (560, 1560, 2000), (1030, -200, 2000),
                      (1500, 0, 2000), (75, 2000, 2460), (560, 2000, 2440)):
        o.append(rect(s1, -z, s2 - s1, 30, INK))
    o += [rect(-200, -560, 56, 810, INK), rect(-200, -1030, 40, 470, INK),
          path('M-200 -1130 H0', INK, 4), path('M-190 -1130 V-1030 M-100 -1130 V-1030 M-10 -1130 V-1030', INK, 3),
          rect(0, -1600, 30, 100, INK), rect(1970, -1600, 30, 100, INK)]
    for s, w in ((0, 30), (1970, 30)):
        o += [rect(s, -560, w, 170, INK), rect(s, -1030, w, 170, INK), rect(s, -1500, w, 170, INK)]
    for s in (700, 1560):
        o += [rect(s, -560, 40, 170, INK), rect(s, -1030, 40, 330, INK), rect(s, -60, 40, 110, INK)]
    o += [rect(0, -60, 30, 110, INK), rect(2430, -60, 30, 310, INK)]
    o += [rect(740, -560, 110, 30, INK), rect(1450, -560, 110, 30, INK),
          path('M850 -560 V-660 M1450 -560 V-660', INK, 4)]
    o.append(path('M740 -700 A410 290 0 0 1 1560 -700', INK, 12))
    o.append(path('M740 -560 V-700 M1560 -560 V-700', INK, 6))
    o.append(rect(2400, -560, 30, 485, INK))
    o += [path('M2460 0 H3880', INK, 5), rect(3600, 0, 200, 22, '#8E918C')]
    o.append(path('M1150 -1690 V420', ACC, 4, extra=' stroke-dasharray="30 18"'))
    o.append(label(1150, -1640, 'trục sảnh tròn', 9, k, ACC, 400))
    for z, t in ((-250, '−2.50'), (0, '±0.00'), (90, '+0.90'), (560, '+5.60'), (1030, '+10.30'), (1500, '+15.00')):
        o += [path(f'M3900 {-z} H3990', ACC, 4), label(4010, -z + round(4 * k), t, 11, k, ACC, 600, 'start', None)]
    if not labels:
        return '\n'.join(o)
    o += [label(350, -300, 'GRAND SALON', 11, k), label(1150, -300, 'LA ROTONDA', 11, k),
          label(1785, -300, 'TIỀN SẢNH', 10, k), label(2220, -300, 'PORTE-COCHÈRE', 10, k),
          label(350, -760, 'PHÒNG GIA ĐÌNH', 10, k), label(1785, -760, 'PHÒNG ĐỌC', 10, k),
          label(350, -1230, 'PHÒNG NGỦ CHỦ', 10, k), label(1150, -1230, 'PHÒNG KHÁCH TRÒN', 10, k),
          label(1785, -1230, 'THƯ PHÒNG', 10, k), label(165, 340, 'HỒ BƠI', 10, k),
          label(1150, 120, 'POOL LOUNGE', 10, k), label(1785, 120, 'HẦM RƯỢU', 10, k),
          label(2230, 120, 'RẠP PHIM', 10, k), label(-100, -1150, 'SÂN THƯỢNG', 9, k),
          label(-700, 320, 'VƯỜN SAU −2.50', 10, k, MUTED, 400), label(3000, -40, 'SÂN DANH DỰ ±0.00', 10, k, MUTED, 400),
          label(3700, -40, 'ĐƯỜNG', 10, k, MUTED, 400),
          label(-850, -1450, '← BIỂN · ĐÔNG', 12, k, ACC), label(3450, -1450, 'TÂY · ĐƯỜNG ĐT639 →', 12, k, ACC)]
    return '\n'.join(o)


def svg(view, w, h, aria, body):
    vb = ' '.join(str(v) for v in view)
    return (f'<svg viewBox="{vb}" role="img" aria-label="{escape(aria)}" '
            f'style="width: {w}px; height: {h}px; display: block; flex: none">\n{body}\n</svg>')


# ---------- HTML helpers (same markup as the RB boards) ----------

def row(name, value, text):
    return ('<div style="display: flex; flex-direction: column; gap: 3px; padding: 9px 0; border-bottom: 1px solid #C5CAC5">\n'
            '<div style="display: flex; justify-content: space-between; gap: 12px; font-size: 15px; font-weight: 600">'
            f'<span>{escape(name)}</span><span style="flex: none">{escape(value)}</span></div>\n'
            f'<div style="font-size: 13px; line-height: 1.5; color: #4A5868">{escape(text)}</div>\n</div>')


def card(name, value, text):
    return ('<div style="display: flex; flex-direction: column; gap: 3px; padding-top: 10px; border-top: 1px solid #C5CAC5">\n'
            '<div style="display: flex; justify-content: space-between; gap: 12px; font-size: 15px; font-weight: 600">'
            f'<span>{escape(name)}</span><span style="flex: none">{escape(value)}</span></div>\n'
            f'<div style="font-size: 13px; line-height: 1.5; color: #4A5868">{escape(text)}</div>\n</div>')


def legend(items):
    cells = []
    for kind, color, text in items:
        if kind == 'line':
            sw = f'<div style="width: 26px; height: 0; flex: none; border-top: 4px dashed {color}"></div>'
        elif kind == 'dot':
            sw = f'<div style="width: 16px; height: 16px; flex: none; border-radius: 50%; background: {color}"></div>'
        else:
            sw = f'<div style="width: 26px; height: 12px; flex: none; background: {color}; border: 1px solid #8E918C; box-sizing: border-box"></div>'
        cells.append(f'<div style="display: flex; align-items: center; gap: 8px">{sw}<span>{escape(text)}</span></div>')
    return ('<div style="display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 8px 16px; padding-top: 12px; '
            'font-size: 12px; color: #4A5868">\n' + '\n'.join(cells) + '\n</div>')


def header(code, title, note):
    return ('<div style="height: 60px; box-sizing: border-box; padding-bottom: 10px; border-bottom: 2px solid #15263B; '
            'display: flex; justify-content: space-between; align-items: flex-end">\n'
            '<div style="display: flex; align-items: baseline; gap: 16px">\n'
            f'<span style="font-size: 13px; font-weight: 600; letter-spacing: 2px; color: #7A5620">{code}</span>\n'
            "<h1 style=\"margin: 0; font-family: 'Cormorant Garamond', serif; font-weight: 600; font-size: 42px; line-height: 1\">"
            f'{escape(title)}</h1>\n</div>\n'
            f'<div style="font-size: 13px; color: #4A5868">{escape(note)}</div>\n</div>')


def page(title, inner):
    return f"""<!doctype html>
<html lang="vi">
<head>
<meta charset="utf-8">
<title>{escape(title)}</title>
<script src="./support.js"></script>
</head>
<body>
<x-dc>
<helmet>
{FONTS}
<style>
body{{margin:0}}
</style>
</helmet>
<div style="width: 1480px; height: 1060px; box-sizing: border-box; padding: 32px; background: #F3F4F1; color: #15263B; font-family: 'Be Vietnam Pro', sans-serif; display: flex; flex-direction: column; gap: 16px">
{inner}
</div>
</x-dc>
<script type="text/x-dc" data-dc-script data-props='{{"$preview":{{"width":1480,"height":1060}}}}'>
class Component extends DCLogic {{
renderVals() {{
return {{}};
}}
}}
</script>
</body>
</html>
"""


def plan_board(code, title, note, drawing, side_title, rows, leg):
    side = ('<div style="flex: 1; min-width: 0; display: flex; flex-direction: column">\n'
            "<div style=\"font-family: 'Cormorant Garamond', serif; font-weight: 600; font-size: 28px; line-height: 1.15; "
            f'padding-bottom: 8px; border-bottom: 2px solid #15263B">{escape(side_title)}</div>\n'
            + '\n'.join(row(*r) for r in rows) + '\n' + legend(leg) + '\n</div>')
    return (header(code, title, note) + '\n<div style="display: flex; gap: 32px">\n'
            '<div style="width: 820px; height: 920px; flex: none; display: flex; justify-content: center">\n'
            + drawing + '\n</div>\n' + side + '\n</div>')


def section_board(code, title, note, drawing, cards):
    grid = ('<div style="display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 14px 32px">\n'
            + '\n'.join(card(*c) for c in cards) + '\n</div>')
    return header(code, title, note) + '\n' + drawing + '\n' + grid


# ---------- The ideas ----------

def yt1():
    k = SECTION_VIEW[2] / 1416
    o = [section(k)]
    o.append(arrow('M-1150 -240 H2900', TEAL, 2915, -240, 0, k))
    o.append(arrow('M-1150 -650 H2700', TEAL, 2715, -650, 0, k))
    o.append(arrow('M1060 -150 C1060 -420 1120 -600 1300 -700', TEAL, 1315, -706, -25, k, dashed=False, w=1.4))
    o.append(arrow('M1240 -150 C1240 -380 1280 -560 1420 -660', TEAL, 1433, -668, -35, k, dashed=False, w=1.4))
    for s, w in ((0, 30), (700, 40), (1560, 40), (1970, 30)):
        o.append(rect(s, -470, w, 70, ACC))
    o.append(label(1150, -860, 'khí nóng thoát qua tầng 2', 10, k, TEAL))
    o.append(label(-700, -280, 'gió biển ban ngày', 11, k, TEAL))
    o.append(label(-700, -690, 'vào loggia tầng 2', 10, k, TEAL, 400))
    o.append(label(-450, -445, 'ô thoáng trên mọi cửa trên trục', 10, k, ACC, 600, 'end'))
    o.append(path('M-420 -440 H-10', ACC, 4))
    for s, z in ((350, 520), (350, 990)):
        o.append(path(f'M{s} {-z} V{-z + 40} M{s - 120} {-z + 40} H{s + 120}', INK, 6))
    o.append(label(560, -425, 'quạt trần', 9, k, MUTED, 400))
    drawing = svg(SECTION_VIEW, 1416, 560,
                  'Mặt cắt dọc trục chính La Rotonda B: gió biển vào từ phía đông qua hàng vòm và năm cửa Grand Salon, '
                  'đi thẳng qua sảnh tròn, tiền sảnh, ra porte-cochère phía tây; ở tầng 2 gió vào loggia, qua phòng gia đình '
                  'và khoảng thông, ra cửa phòng đọc; khí nóng trong sảnh tròn bốc lên và thoát qua tầng 2; mọi cửa trên trục '
                  'có ô thoáng phía trên', '\n'.join(o))
    cards = [
        ('Một đường gió', 'dài khoảng 26 m',
         'Gió biển vào qua hàng vòm và năm cửa Grand Salon, đi thẳng qua sảnh tròn, tiền sảnh rồi ra porte-cochère. '
         'Trục chính không có vách ngang nào chắn.'),
        ('Ô thoáng trên cửa', 'khóa cửa vẫn có gió',
         'Mọi cửa trên trục có ô thoáng chớp lật phía trên cánh cửa. Ban đêm khóa cửa đi mà vẫn xả được hơi nóng '
         'tích trong tường đá.'),
        ('Sảnh tròn làm ống khói', 'cao 9 m',
         'Khí nóng dồn lên dưới trần vòm. Mở cửa phòng đọc và loggia tầng 2 để khí nóng thoát ra; '
         'kỹ sư cơ điện cần tính diện tích mở cho đủ.'),
        ('Quạt trần', 'cho ngày lặng gió',
         'Hai quạt cánh lớn quay chậm ở Grand Salon và phòng gia đình. Có gió thì ít phải bật máy lạnh ở hai phòng lớn nhất.'),
        ('Điều kiện', 'cửa phải thẳng hàng',
         'Năm cửa salon, cửa sảnh tròn và cửa chính phải mở được cùng lúc. Nếu sau này đặt vách kính cố định '
         'ở tiền sảnh thì mất đường gió.'),
        ('Yếu', 'mưa tạt và muối',
         'Mùa bão phải đóng hết. Ô thoáng cần lưới chống côn trùng và chớp chống mưa tạt; '
         'bản lề, then cài dùng inox 316 hoặc đồng vì gió biển mang muối.'),
    ]
    return section_board('YT1', 'Gió biển xuyên trục chính', 'Mặt cắt sơ đồ dọc trục chính · dựng từ các mặt bằng RB1–RB4',
                         drawing, cards)


def yt2():
    view = (480, -1170, 1340, 1503)
    k = view[2] / 820
    o = [section(k, labels=False),
         label(1150, -1080, 'PHÒNG KHÁCH TRÒN · +10.30', 11, k), label(1150, 140, 'POOL LOUNGE · −2.50', 11, k),
         label(600, -300, 'GRAND SALON', 10, k), label(1700, -300, 'TIỀN SẢNH', 10, k),
         label(600, -760, 'GALLERIA', 10, k), label(1700, -760, 'PHÒNG ĐỌC', 10, k)]
    o.append(path('M760 -700 A390 270 0 0 1 1540 -700', TEAL, 9, extra=' stroke-dasharray="16 10"'))
    src, focus = (1150, -250), (1150, -470)
    for px, py in ((880, -918), (1020, -975), (1280, -975), (1420, -918)):
        o.append(path(f'M{src[0]} {src[1]} L{px} {py}', MUTED, 2.5))
        o.append(path(f'M{px} {py} L{focus[0]} {focus[1]}', RUST, 3, extra=' stroke-dasharray="10 7"'))
    o += [circle(src[0], src[1], 14, INK), circle(focus[0], focus[1], 20, 'none', RUST, 5),
          label(1150, -205, 'người nói', 10, k, INK, 400), label(1150, -505, 'điểm dội tụ', 10, k, RUST)]
    o.append(rect(950, -98, 400, 10, ACC))
    o.append(label(1150, -118, 'thảm tròn Ø khoảng 4 m', 10, k, ACC))
    for s in (720, 1580):
        o.append(path(f'M{s} -100 ' + ' '.join(f'l{12 if i % 2 else -12} -25' for i in range(11)), ACC, 4))
    o.append(label(1150, -1010, 'vòm thạch cao hút âm', 11, k, TEAL))
    o.append(arrow('M1380 -640 C1420 -660 1450 -680 1470 -700', RUST, 1478, -708, -45, k, dashed=False, w=1.4))
    o.append(label(1330, -610, 'vang lên tầng 2', 10, k, RUST))
    drawing = svg(view, 820, 920,
                  'Mặt cắt qua sảnh tròn La Rotonda B: tiếng nói từ giữa sàn phản xạ trên trần vòm và hội tụ về một điểm '
                  'phía trên đầu người nói; đề xuất lớp thạch cao hút âm dưới vòm, thảm tròn giữa sàn và rèm ở hai cửa',
                  '\n'.join(o))
    rows = [
        ('Vấn đề', 'tường tròn, trần vòm',
         'Tường cong và vòm lõm gom tiếng về một điểm: đứng giữa sảnh nói sẽ nghe tiếng mình dội lại, tiếng giày trên '
         'sàn đá vang lâu. Sảnh thông lên tầng 2 nên tiếng ồn tiệc lan tới phòng gia đình.'),
        ('Trần vòm', 'hút âm, nhìn vẫn trơn',
         'Làm vòm bằng thạch cao đục lỗ li ti hoặc vữa hút âm phun mịn, sơn như vòm thường. Đây là việc quan trọng '
         'nhất vì chính vòm gây hội tụ.'),
        ('Sàn', 'thảm tròn giữa phòng',
         'Thảm tròn khoảng Ø 4 m dưới đèn chùm, chừa viền đá quanh chân hai vế thang. Nếu làm sàn đá la bàn (NC3) '
         'thì bỏ thảm, bù bằng rèm và ghế bọc nệm.'),
        ('Cửa và hốc', 'rèm dày',
         'Rèm nhung ở cửa sang Grand Salon và tiền sảnh; hốc tượng trong tường phá bớt mặt cong.'),
        ('Kiểm tra', 'đo khi xây thô',
         'Đo thời gian vang khi xây thô xong, trước khi làm trần vòm, để chọn đúng lượng vật liệu hút âm thay vì đoán.'),
        ('Được', 'chỗ chơi nhạc nhỏ',
         'Khi tiếng vang đã kiểm soát, sảnh tròn dùng được cho piano hoặc nhóm nhạc nhỏ trong tiệc, khách đứng ở '
         'ban công tầng 2 nghe xuống.'),
    ]
    leg = [('line', TEAL, 'Lớp hút âm dưới vòm'), ('line', RUST, 'Tiếng dội hội tụ'),
           ('box', ACC, 'Thảm, rèm')]
    return plan_board('YT2', 'Âm học cho La Rotonda', 'Mặt cắt qua sảnh tròn · Ø 8,2 m, cao khoảng 9 m, trần vòm thạch cao',
                      drawing, 'Sảnh tròn đẹp nhưng vang', rows, leg)


def yt3():
    k = PLAN_VIEW[2] / 820
    o = [plan('t2', k)]
    o.append(path('M-19 2000 V2440 H681 V2000', INK, 12))
    o += [path(f'M{x} 2030 V2410', ACC, 6) for x in range(30, 681, 80)]
    o.append(path('M-5 2060 H667 M-5 2380 H667', ACC, 8))
    o.append(rect(0, 2395, 662, 30, GREEN, GREEN_LINE, 3))
    o.append(rect(10, 2040, 40, 330, '#FFFFFF', '#5E6B7A'))
    o.append(circle(331, 2200, 60, '#FFFFFF', '#5E6B7A'))
    o += [circle(331 + dx, 2200 + dy, 18, '#FFFFFF', '#5E6B7A') for dx, dy in ((-95, 0), (95, 0), (0, -95), (0, 95))]
    o.append(rect(251, 1966, 160, 38, '#FFFFFF'))
    o.append(path('M251 2000 L251 2080 A80 80 0 0 0 331 2000 M411 2000 L411 2080 A80 80 0 0 1 331 2000', INK, 3))
    o.append(label(730, 2200, 'BAN CÔNG HOÀNG HÔN', 11, k, INK, 600, 'start'))
    o.append(label(730, 2255, '+5.60 · khoảng 28 m²', 10, k, MUTED, 400, 'start'))
    o.append(label(331, 1920, 'cửa đôi mới', 10, k, ACC))
    o.append(arrow('M331 2450 V2590', ACC, 331, 2600, 90, k))
    o.append(label(390, 2570, 'nhìn sân danh dự · hướng tây', 10, k, ACC, 600, 'start'))
    drawing = svg(PLAN_VIEW, 820, 920,
                  'Mặt bằng tầng 2 La Rotonda B: mái porte-cochère 7 × 4,4 m trước phòng đọc trở thành ban công có lan can, '
                  'giàn che, bồn cây dọc mép và bàn ghế; cửa sổ giữa của phòng đọc đổi thành cửa đôi; ban công nhìn về phía '
                  'tây, xuống sân danh dự', '\n'.join(o))
    rows = [
        ('Ý chính', 'mái thành ban công',
         'Mái porte-cochère 7 × 4,4 m hiện chỉ là mái. Làm thành ban công cho phòng đọc tầng 2; cửa sổ giữa của '
         'phòng đọc đổi thành cửa đôi trên trục.'),
        ('Hướng', 'tây, nhìn sân danh dự',
         'Đây sẽ là chỗ ngồi ngoài trời duy nhất phía đường. Chiều nắng gắt, nhưng lúc hoàng hôn là chỗ đẹp nhất, '
         'nhìn xuống sân và xe khách đến.'),
        ('Giàn che', 'hoa giấy hoặc nhài',
         'Giàn pergola thấp bằng gỗ hoặc thép sơn, phủ cây leo, che nắng chiều. Giàn thấp hơn lan can tầng 3 để mặt '
         'tiền không đổi dáng.'),
        ('Kết cấu', 'tải ban công, không phải tải mái',
         'Sàn phải tính cho người và bồn cây; bốn cột porte-cochère có thể phải to hơn. Chống thấm hai lớp vì ngay '
         'dưới là chỗ đón khách.'),
        ('Mặt tiền', 'giữ đối xứng',
         'Lan can cùng kiểu lan can loggia biển; bồn cây đặt đối xứng hai bên trục.'),
        ('Yếu', 'nhìn ra đường',
         'Ban công lộ ra đường ĐT639 nên kém riêng tư; hàng cây trong bồn dọc mép che bớt tầm nhìn từ ngoài vào.'),
    ]
    leg = [('box', TERR, 'Ban công, loggia'), ('line', ACC, 'Giàn che'),
           ('box', GREEN, 'Bồn cây'), ('line', INK, 'Lan can')]
    return plan_board('YT3', 'Ban công hoàng hôn trên porte-cochère', 'Tầng 2 · cốt +5.60 · cửa từ phòng đọc',
                      drawing, 'Một chỗ ngồi ngoài trời phía tây', rows, leg)


def yt4():
    k = PLAN_VIEW[2] / 820
    o = [plan('t1', k)]
    o.append(arrow('M331 2600 V1500 C331 1250 520 1010 735 1010 H859 V930', BLUE, 859, 918, -90, k, w=2.2))
    o.append(arrow('M290 1330 C180 1220 0 1010 -150 1010 H-250 V830 H-470', BLUE, -482, 830, 180, k, w=2.2))
    o.append(path('M-470 830 H-600 V-380 H-873 V-430', BLUE, round(1.6 * k, 1), extra=f' stroke-dasharray="{round(4 * k)} {round(3 * k)}"'))
    o.append(rect(-460, 780, 100, 100, '#F2ECDD', ACC, 4))
    o.append(rect(251, 1990, 160, 60, '#F2ECDD', ACC, 3))
    o += [marker(1, 470, 2020, k), marker(2, 859, 640, k), marker(3, -410, 700, k), marker(4, -873, -560, k)]
    o += [label(-873, -470, 'SUITE ÔNG BÀ', 11, k), label(-873, -420, '±0.00', 10, k, MUTED, 400),
          label(-475, 915, 'thang nâng', 10, k, ACC, 600, 'end'), label(520, 2330, '+0.75', 10, k, BLUE),
          label(520, 1880, '+0.90', 10, k, BLUE), label(-600, 1000, '±0.00', 10, k, BLUE)]
    drawing = svg(PLAN_VIEW, 820, 920,
                  'Mặt bằng tầng 1 La Rotonda B với lối đi không bậc: từ sân qua porte-cochère, dốc nhẹ thay bậc ở cửa chính, '
                  'qua tiền sảnh và sảnh tròn tới thang máy; nhánh thứ hai theo hành lang tranh tới cửa sang nhà cũ, nơi đặt '
                  'thang nâng 0,9 m, rồi tới suite ông bà ở nhà cũ', '\n'.join(o))
    rows = [
        ('Bốn cao độ', '±0.00 · +0.75 · +0.90 · −2.50',
         'Sân và nhà cũ ở ±0.00, porte-cochère +0.75, tầng 1 mới +0.90, tầng dưới −2.50. Mỗi chỗ lệch là một chỗ '
         'người già hoặc xe lăn phải dừng.'),
        ('① Cửa chính', 'dốc thay bậc 15 cm',
         'Bậc từ porte-cochère vào tiền sảnh làm thành dốc 1:12 dài khoảng 1,8 m, lát cùng loại đá, nhìn gần như phẳng.'),
        ('② Thang máy', 'từ −2.50 đến +10.30',
         'Thang máy đã có và tới mọi tầng mới. Chọn cabin đủ cho xe lăn và một người đi kèm, cửa rộng khoảng 90 cm.'),
        ('③ Sang nhà cũ', 'thang nâng 0,9 m',
         'Sàn nhà cũ thấp hơn tầng 1 mới 0,9 m. Dốc cho chênh lệch này dài gần 11 m, nên đặt một thang nâng nhỏ '
         'cạnh bậc ở cửa nối hành lang tranh với nhà cũ.'),
        ('④ Suite ông bà', 'cùng cốt sân xe cũ',
         'Suite tầng trệt nhà cũ đã ở ±0.00 nên ông bà vào thẳng từ cổng cũ. Thang nâng nối suite với phần nhà mới '
         'và thang máy.'),
        ('Chốt sớm', 'hố thang nâng',
         'Thang nâng cần hố và nguồn điện riêng, phải có trong bản vẽ kết cấu trước khi đổ sàn. Thêm tay vịn hai bên '
         'thang xoắn và sàn đá nhám quanh hồ bơi.'),
    ]
    leg = [('line', BLUE, 'Lối không bậc'), ('box', '#F2ECDD', 'Dốc, thang nâng'),
           ('dot', ACC, 'Điểm can thiệp')]
    return plan_board('YT4', 'Một lối không bậc cho ông bà', 'Tầng 1 · cốt +0.90 · nối porte-cochère, thang máy và nhà cũ',
                      drawing, 'Đi khắp nhà không gặp bậc', rows, leg)


def yt5():
    view = (-1150, -850, 3100, 4700)
    k = view[3] / 920
    o = [site(k), plan('t1', k, porte_label=False)]
    o.append(rect(1000, 2280, 600, 250, WATER, TEAL, 5, ' stroke-dasharray="20 12"'))
    o.append(label(1300, 2395, 'BỂ NGẦM 30 m³', 11, k, TEAL))
    o.append(label(1300, 2450, '6 × 2,5 × 2 m', 9, k, MUTED, 400))
    pipe = f' stroke-dasharray="{round(4 * k)} {round(2.5 * k)}"'
    o.append(path('M-300 2000 V2120 H1300 V2280 M1690 1500 H1760 V2120 H1300 M972 2000 V2120', TEAL, round(1.6 * k, 1), extra=pipe))
    o += [circle(x, y, 26, TEAL) for x, y in ((-300, 1990), (972, 1990), (1690, 1500), (681, 2000), (-19, 2000))]
    o.append(arrow('M1000 2500 H-65 V3150', TEAL, -65, 3160, 90, k))
    o.append(circle(-65, 3260, 90, 'none', TEAL, 6))
    o.append(label(110, 3420, 'giếng thấm', 10, k, TEAL, 600, 'start'))
    o += [circle(1200, 2900, 40, TEAL), label(1260, 2920, 'vòi rửa xe', 10, k, TEAL, 600, 'start'),
          circle(40, 2640, 40, TEAL), label(100, 2660, 'tưới vườn', 10, k, TEAL, 600, 'start')]
    drawing = svg(view, 607, 920,
                  'Mặt bằng tầng 1 và sân trước La Rotonda B: ống thoát mái ở mặt tiền và cánh phải gom về một bể ngầm 30 m³ '
                  'dưới sân danh dự; nước tràn chảy vào giếng thấm trong dải cây bên trái; vòi lấy nước ở nhà xe và vườn',
                  '\n'.join(o))
    rows = [
        ('Ý chính', 'giữ nước mưa trên đất',
         'Mái nhà mới chiếm khoảng 390 m². Gom toàn bộ ống thoát mái về một bể ngầm dưới sân danh dự thay vì xả ra cống.'),
        ('Dung tích', 'khoảng 30 m³',
         'Bể 6 × 2,5 × 2 m. Một trận mưa 80 mm trên 390 m² mái cho khoảng 31 m³, vừa đầy bể.'),
        ('Dùng vào', 'tưới, rửa xe, rửa sân',
         'Tưới vườn mùa khô, rửa xe ngay cạnh nhà xe, rửa sân và lối đi; có thể bù nước bay hơi cho hồ bơi sau khi lọc.'),
        ('Tràn', 'vào giếng thấm',
         'Bể đầy thì nước tràn vào giếng thấm trong dải cây bên trái, không chảy ra đường hay xuống tầng dưới.'),
        ('Kết cấu', 'dưới làn xe',
         'Bể nằm dưới sân có xe chạy nên nắp và đáy phải chịu tải xe, và đặt tách khỏi móng nhà.'),
        ('Nước giếng', 'thử trước khi dùng',
         'Gần biển, nước ngầm có thể nhiễm mặn. Nếu muốn khoan thêm giếng thì lấy mẫu thử trước, chưa trộn vào bể nước mưa.'),
        ('Chốt sớm', 'cùng lúc san nền sân',
         'Bể và ống gom phải làm cùng lúc san nền sân danh dự; làm sau là phải đào lại sân và đường xe.'),
    ]
    leg = [('box', WATER, 'Bể ngầm'), ('line', TEAL, 'Ống gom, ống tràn'), ('dot', TEAL, 'Ống đứng, vòi lấy nước')]
    return plan_board('YT5', 'Bể nước mưa dưới sân danh dự', 'Tổng mặt bằng phía trước · mái nhà mới khoảng 390 m²',
                      drawing, 'Nước mưa ở lại trong lô đất', rows, leg)


def yt6():
    k = PLAN_VIEW[2] / 820
    o = [plan('mai', k)]
    for c in range(5):
        for r in range(6):
            o.append(rect(1090 + c * 100, 120 + r * 200, 96, 194, '#2C425C', '#FFFFFF', 3))
    o.append(path('M1090 60 H1590 M1610 120 V1320', ACC, 4))
    o.append(label(1340, 40, 'lùi 1 m khỏi lan can', 9, k, ACC))
    o.append(path('M1100 1320 V1420 H865 V1470', ACC, round(1.4 * k, 1), extra=f' stroke-dasharray="{round(4 * k)} {round(2.5 * k)}"'))
    o.append(rect(835, 1470, 60, 60, ACC))
    o.append(label(865, 1590, 'cáp xuống kho tầng 1', 9, k, ACC))
    o.append(label(1655, 720, 'MÁI CÁNH PHẢI · +15.00', 11, k, rot=-90))
    drawing = svg(PLAN_VIEW, 820, 920,
                  'Mặt bằng mái La Rotonda B: khoảng 30 tấm pin mặt trời xếp năm cột sáu hàng trên mái bằng cánh phải, '
                  'lùi một mét khỏi lan can; cáp đi theo hộp kỹ thuật cạnh thang phụ xuống kho tầng 1; mái thân giữa, '
                  'vòm tháp và nhà cũ giữ nguyên', '\n'.join(o))
    rows = [
        ('Ý chính', 'giấu sau lan can',
         'Mái cánh phải 7,2 × 18 m là mái bằng có lan can bao quanh. Tấm pin đặt gần như nằm phẳng, thấp hơn lan can, '
         'nên đứng dưới sân không thấy.'),
        ('Quy mô', 'khoảng 30 tấm',
         'Năm cột, sáu hàng tấm cỡ 1 × 2 m, khoảng 12 kWp nếu dùng tấm 400–450 Wp. Sản lượng thực phải do đơn vị lắp '
         'đặt tính theo nắng tại chỗ.'),
        ('Bão', 'nghiêng thấp, bắt vào dầm',
         'Tấm nghiêng dưới 10°, khung bắt vào dầm mái chứ không chỉ đè đối trọng. Lùi khỏi mép mái vì gió giật mạnh '
         'nhất ở mép và góc.'),
        ('Biến tần, pin', 'ở tầng 1, không ở tầng dưới',
         'Đặt trong kho tầng 1 cạnh thang phụ. Tầng dưới có nguy cơ ngập khi bão (xem YT7) nên không để thiết bị điện ở đó.'),
        ('Khi mất điện', 'giữ phần thiết yếu',
         'Pin nuôi bơm thoát nước tầng dưới, đèn, tủ lạnh và mạng. Đây là lý do chính để làm pin lưu trữ ở nơi hay có bão.'),
        ('Chốt sớm', 'ống chờ và tải mái',
         'Hộp kỹ thuật từ mái xuống kho và tải trọng mái phải có trong thiết kế; lắp tấm có thể làm sau.'),
    ]
    leg = [('box', '#2C425C', 'Tấm pin'), ('line', ACC, 'Đường cáp'), ('box', '#D8CFB8', 'Chóp vòm')]
    return plan_board('YT6', 'Điện mặt trời sau lan can mái', 'Mặt bằng mái · cánh phải cốt +15.00',
                      drawing, 'Mái cánh phải làm việc', rows, leg)


def yt7():
    k = SECTION_VIEW[2] / 1416
    o = [section(k)]
    o.append(path('M-1300 170 H-60', RUST, round(1.4 * k, 1), extra=f' stroke-dasharray="{round(5 * k)} {round(3 * k)}"'))
    o.append(label(-1250, 150, 'mực nước bão: chưa có số liệu, cần khảo sát', 10, k, RUST, 600, 'start'))
    o.append(arrow('M-1000 215 H-90', RUST, -78, 215, 0, k))
    o.append(rect(-60, 215, 60, 35, ACC))
    o.append(rect(-20, 110, 18, 140, ACC))
    o.append(rect(700, 280, 140, 110, WATER, RUST, 4))
    o.append(circle(770, 335, 26, '#FFFFFF', INK, 4))
    o.append(rect(1820, -250, 90, 140, ACC))
    o.append(path('M900 430 H-250', RUST, 4))
    o.append(path('M-190 415 L-150 445 L-150 415 L-190 445 Z', RUST, 3, '#FFFFFF'))
    o += [marker(1, -130, 120, k), marker(2, 90, 120, k), marker(3, 900, 340, k), marker(4, 1720, -150, k),
          marker(5, -170, 350, k)]
    drawing = svg(SECTION_VIEW, 1416, 560,
                  'Mặt cắt dọc trục chính La Rotonda B nhấn vào tầng dưới cốt −2.50 mở ra vườn sau phía biển: nước dâng từ '
                  'phía biển có thể tràn vào qua cửa ra vườn; năm biện pháp gồm ngưỡng cửa cao, tấm chắn tháo lắp, hố thu '
                  'có hai bơm, tủ điện đặt ở tầng 1 và van một chiều trên ống thoát', '\n'.join(o))
    cards = [
        ('Vì sao lo', 'tầng dưới quay ra biển',
         'Tầng dưới ở −2.50, thấp hơn sân trước 2,5 m và mở thẳng ra vườn sau phía biển. Hồ bơi, pool lounge, '
         'hầm rượu, rạp phim, phòng giúp việc đều ở đây.'),
        ('Việc đầu tiên', 'đo cao độ',
         'Khảo sát cao độ vườn sau so với mực triều cao nhất và hỏi vết nước bão cũ trong vùng. Chiều cao ngưỡng '
         'và tấm chắn chỉ chốt được khi có số liệu này.'),
        ('① ② Chặn ở cửa', 'ngưỡng và tấm chắn',
         'Cửa ra vườn có ngưỡng cao hơn sân vườn. Hai bên cửa chừa rãnh ray để gài tấm chắn nhôm khi có tin bão, '
         'cất trong kho ngay cạnh.'),
        ('③ Hố thu, bơm', 'hai bơm luân phiên',
         'Hố thu ở điểm thấp nhất, hai bơm chìm có phao: một chạy, một dự phòng. Bơm nối vào nguồn pin (YT6) để '
         'chạy được khi mất điện.'),
        ('④ Thiết bị', 'để ở tầng 1',
         'Tủ điện chính, biến tần, thiết bị mạng đặt ở kho tầng 1. Tầng dưới chỉ đi dây từ trên xuống, ổ cắm đặt cao.'),
        ('⑤ Ống và dốc', 'không cho nước chảy ngược',
         'Ống thoát sàn và hồ bơi có van một chiều. Đầu dốc phục vụ 12 % ở cổng phụ cần gờ chặn và rãnh thu ngang '
         'để nước mưa ngoài đường không chảy xuống sân phục vụ.'),
    ]
    return section_board('YT7', 'Giữ tầng dưới khô khi bão', 'Mặt cắt sơ đồ dọc trục chính · tầng dưới cốt −2.50',
                         drawing, cards)


SUMMARY = [
    ('YT1', 'Gió biển xuyên trục chính', 'trục chính, tầng 1–2', 'ô thoáng trên cửa, quạt trần', 'cùng hồ sơ cửa'),
    ('YT2', 'Âm học cho La Rotonda', 'sảnh tròn', 'vòm hút âm, thảm, rèm', 'trước khi làm trần'),
    ('YT3', 'Ban công trên porte-cochère', 'tầng 2, mặt tiền', 'mái thành ban công, giàn che', 'trước thiết kế kết cấu'),
    ('YT4', 'Một lối không bậc', 'cửa chính, nối nhà cũ', 'dốc thay bậc, thang nâng 0,9 m', 'trước khi đổ sàn'),
    ('YT5', 'Bể nước mưa', 'dưới sân danh dự', 'bể 30 m³, giếng thấm', 'cùng lúc san nền sân'),
    ('YT6', 'Điện mặt trời', 'mái cánh phải', 'khoảng 30 tấm, pin ở tầng 1', 'ống chờ trong thiết kế'),
    ('YT7', 'Tầng dưới khô khi bão', 'tầng dưới −2.50', 'khảo sát, ngưỡng, bơm, van', 'trước thiết kế móng'),
]


def yt0():
    th = 'padding: 8px 12px 8px 0; text-align: left; font-size: 12px; font-weight: 600; letter-spacing: 1.2px; color: #4A5868; border-bottom: 2px solid #15263B'
    td = 'padding: 17px 12px 17px 0; font-size: 16px; line-height: 1.4; border-bottom: 1px solid #C5CAC5; vertical-align: baseline'
    head = ''.join(f'<th style="{th}">{h}</th>' for h in ('MÃ', 'Ý TƯỞNG', 'Ở ĐÂU', 'LÀM GÌ', 'PHẢI CHỐT'))
    body = '\n'.join(
        f'<tr><td style="{td}; font-size: 13px; font-weight: 600; letter-spacing: 2px; color: #7A5620">{c}</td>'
        f'<td style="{td}; font-weight: 600">{escape(n)}</td><td style="{td}; color: #4A5868">{escape(w)}</td>'
        f'<td style="{td}; color: #4A5868">{escape(d)}</td><td style="{td}">{escape(t)}</td></tr>'
        for c, n, w, d, t in SUMMARY)
    table = (f'<table style="width: 100%; border-collapse: collapse">\n<thead><tr>{head}</tr></thead>\n'
             f'<tbody>\n{body}\n</tbody>\n</table>')
    groups = [
        ('Chốt trước móng và kết cấu', 'YT7 · YT4 · YT3',
         'Khảo sát cao độ chống ngập, hố thang nâng, tải ban công trên porte-cochère. Làm sau là phải đục bê tông.'),
        ('Chốt cùng hồ sơ cơ điện', 'YT5 · YT6 · YT1',
         'Bể và ống gom nước mưa, hộp kỹ thuật cho pin mặt trời, ô thoáng trong bản vẽ cửa. Lắp đặt có thể làm sau.'),
        ('Để tới phần hoàn thiện', 'YT2',
         'Hút âm cho sảnh tròn chỉ cần quyết trước khi làm trần vòm, sau khi đo tiếng vang lúc xây thô.'),
    ]
    cols = '\n'.join(
        '<div style="display: flex; flex-direction: column; gap: 6px; padding-top: 12px; border-top: 2px solid #15263B">'
        f"<div style=\"font-family: 'Cormorant Garamond', serif; font-weight: 600; font-size: 26px; line-height: 1.1\">{escape(a)}</div>"
        f'<div style="font-size: 13px; font-weight: 600; letter-spacing: 2px; color: #7A5620">{escape(b)}</div>'
        f'<div style="font-size: 15px; line-height: 1.55; color: #4A5868">{escape(c)}</div></div>'
        for a, b, c in groups)
    return ('<div style="display: flex; flex-direction: column; gap: 8px">\n'
            '<div style="font-size: 12px; font-weight: 600; letter-spacing: 2.4px; color: #7A5620">'
            'Ý TƯỞNG MỚI · ĐỀ XUẤT THÊM CHO LA ROTONDA B</div>\n'
            "<h1 style=\"margin: 0; font-family: 'Cormorant Garamond', serif; font-weight: 600; font-size: 88px; line-height: 1\">"
            'Bảy ý tưởng thêm</h1>\n'
            '<div style="max-width: 980px; font-size: 17px; line-height: 1.5; color: #4A5868">Không đổi mặt bằng đã chọn. Mỗi ý '
            'tưởng sửa một chỗ nhỏ để nhà mát hơn, êm hơn, dễ đi lại cho người già và chịu được bão ở bờ biển Tam Quan. '
            'Không trùng các nâng cấp NC1–NC10 và mặt tiền MT1–MT10 đã có trên canvas. Các con số ghi “khoảng” là ước tính, cần kỹ sư kiểm lại.</div>\n</div>\n'
            + table + '\n'
            '<div style="display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 32px; margin-top: 28px">\n'
            + cols + '\n</div>')


BOARDS = [
    ('YT0', 'yt0-tong-hop', 'YT0TongHop.dc.html', 'Tổng hợp – bảy ý tưởng và thứ tự phải chốt', yt0),
    ('YT1', 'yt1-gio-bien', 'YT1GioBien.dc.html', 'Gió biển xuyên trục chính – ô thoáng, sảnh tròn làm ống khói', yt1),
    ('YT2', 'yt2-am-hoc-rotonda', 'YT2AmHoc.dc.html', 'Âm học cho La Rotonda – trần vòm hút âm, thảm, rèm', yt2),
    ('YT3', 'yt3-ban-cong-porte-cochere', 'YT3BanCong.dc.html', 'Ban công hoàng hôn trên mái porte-cochère (cốt +5.60)', yt3),
    ('YT4', 'yt4-loi-khong-bac', 'YT4KhongBac.dc.html', 'Một lối không bậc cho ông bà – dốc, thang máy, thang nâng sang nhà cũ', yt4),
    ('YT5', 'yt5-nuoc-mua', 'YT5NuocMua.dc.html', 'Bể nước mưa 30 m³ dưới sân danh dự', yt5),
    ('YT6', 'yt6-dien-mat-troi', 'YT6MatTroi.dc.html', 'Điện mặt trời giấu sau lan can mái cánh phải', yt6),
    ('YT7', 'yt7-tang-duoi-kho', 'YT7ChongNgap.dc.html', 'Giữ tầng dưới khô khi bão – khảo sát, ngưỡng, bơm, van', yt7),
]


def main():
    for code, slug, file, title, fn in BOARDS:
        (HERE / file).write_text(page(f'{code} · {title}', fn()), encoding='utf-8')
        print(file)
    manifest = {
        'order': 2,
        'project': 'Biệt thự Tam Quan',
        'set': 'Ý tưởng mới',
        'eyebrow': 'Đề xuất thêm · chưa có trên canvas',
        'heading': 'Bảy ý tưởng thêm cho La Rotonda B',
        'summary': 'Gió biển, âm học sảnh tròn, ban công trên porte-cochère, lối không bậc cho ông bà, nước mưa, '
                   'điện mặt trời và chống ngập tầng dưới. Mỗi ý tưởng một bản; xem YT0 trước.',
        'generator': 'design/y-tuong-moi/generate.py',
        'boards': [{'code': c, 'slug': s, 'file': f, 'w': 1480, 'h': 1060, 'title': t} for c, s, f, t, _ in BOARDS],
    }
    (HERE / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
