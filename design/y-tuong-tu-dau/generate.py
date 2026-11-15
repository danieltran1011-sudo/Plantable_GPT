#!/usr/bin/env python3
"""Generate the "Ý tưởng từ đầu" artboards (K0–K5): four new partis for the Tam Quan villa,
started again from the site and the CHỐT brief rather than from the La Rotonda B plans.

Boards use the canvas artboard format, so tools/build.py turns them into pages like the others.
Plan coordinates are centimetres on the same site grid as RB0: sea (east) at the top, road
ĐT639 (west) at the bottom, north to the left. New lot x −190..2010, y −400..3600; old house
to the north. Section coordinates: horizontal = plan y, vertical = −level.

Usage: python3 design/y-tuong-tu-dau/generate.py   (then run tools/build.py)
"""
import json
from html import escape
from pathlib import Path

HERE = Path(__file__).resolve().parent

INK, MUTED, ACC, RULE = '#15263B', '#4A5868', '#7A5620', '#C5CAC5'
OLD, OLD_LINE, TERR, PAVE = '#ECEBE4', '#8E918C', '#E6E8E2', '#E3DCC8'
WATER, WATER_LINE, TEAL, RUST = '#BFDDE0', '#5A9AA0', '#1F7A80', '#B0502C'
GREEN, GREEN_LINE, EARTH, SLATE, GARAGE = '#DCE5D3', '#6C8F54', '#E2DCCD', '#8794A3', '#D8C9A0'
FONTS = ('<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:'
         'wght@500;600&amp;family=Be+Vietnam+Pro:wght@400;500;600&amp;display=swap">')

AXIS = 910                              # centre line of the new lot
PLAN_VIEW = (-1100, -760, 3250, 4600)   # shown at 640 × 906 px
PLAN_K = PLAN_VIEW[2] / 640
SEC_VIEW = (-800, -1720, 5040, 2100)    # shown at 744 × 310 px
SEC_K = SEC_VIEW[2] / 744
PARTI_VIEW = (-1100, -500, 3250, 4200)


# ---------- SVG helpers ----------

def rect(x, y, w, h, fill, stroke=None, sw=2.5, extra=''):
    s = f' stroke="{stroke}" stroke-width="{sw}"' if stroke else ''
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}"{s}{extra}></rect>'


def path(d, stroke, sw, fill='none', extra=''):
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{extra}></path>'


def circle(cx, cy, r, fill, stroke=None, sw=2.5):
    s = f' stroke="{stroke}" stroke-width="{sw}"' if stroke else ''
    return f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}"{s}></circle>'


def label(x, y, text, px, k, fill=INK, weight=600, anchor='middle', halo='#FFFFFF', rot=None):
    size = round(px * k, 1)
    tr = f' transform="rotate({rot} {x} {y})"' if rot is not None else ''
    st = (f' stroke="{halo}" stroke-width="{round(size * 0.3, 1)}" paint-order="stroke" stroke-linejoin="round"'
          if halo else '')
    return (f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" fill="{fill}" '
            f'text-anchor="{anchor}"{st}{tr}>{escape(text, quote=False)}</text>')


def arrow(d, color, x, y, angle, k, dashed=True, w=1.8):
    sw = round(w * k, 1)
    dash = f' stroke-dasharray="{round(6 * k)} {round(3.2 * k)}"' if dashed else ''
    s = round(k / 4.2, 2)
    return (path(d, color, sw, extra=f'{dash} stroke-linecap="round" stroke-linejoin="round"')
            + f'<path d="M-20 -16 L18 0 L-20 16 z" fill="{color}" '
              f'transform="translate({x} {y}) rotate({angle}) scale({s})"></path>')


def svg(view, w, h, aria, body):
    vb = ' '.join(str(v) for v in view)
    return (f'<svg viewBox="{vb}" role="img" aria-label="{escape(aria)}" '
            f'style="width: {w}px; height: {h}px; display: block; flex: none">\n{body}\n</svg>')


def m2(w, h):
    return round(w * h / 10000)


def room(x, y, w, h, name, fill='#FFFFFF', px=9, area=True, rot=None, k=PLAN_K):
    """A room: filled rectangle, thin walls, name and area (m²) at its centre."""
    cx, cy = x + w / 2, y + h / 2
    o = [rect(x, y, w, h, fill, INK, 7)]
    if rot is None:
        o.append(label(cx, cy - (0.2 * px * k if area else -0.35 * px * k), name, px, k, INK, 600, 'middle', fill))
        if area:
            o.append(label(cx, cy + 1.1 * px * k, f'{m2(w, h)} m²', px - 1, k, MUTED, 400, 'middle', fill))
    else:
        o.append(label(cx + 0.35 * px * k, cy, name + (f' · {m2(w, h)} m²' if area else ''), px, k, INK, 600,
                       'middle', fill, rot))
    return '\n'.join(o)


# ---------- Site (plan) ----------

OLD_HOUSE = 'M-1038 -742 H-190 V-220 H-320 V1250 H-720 V1130 H-1038 Z'


def site(k, garden_to, front_y, show_forecourt=True):
    """Lot, old house, rear garden (−2.50) down to the house, forecourt, garage, road."""
    o = [rect(-1038, -760, 848, 4360, '#EAEAE5'),
         rect(-190, -400, 2200, 4000, '#EFEDE4'),
         rect(-190, -400, 2200, garden_to + 400, GREEN),
         path(OLD_HOUSE, OLD_LINE, 22, OLD),
         rect(-1100, 3600, 3250, 260, '#C6C7C1'),
         path('M-190 -400 V3600 H760 M1060 3600 H2010 V-400 H-190', ACC, 5, extra=' stroke-dasharray="30 18"'),
         label(-680, 300, 'NHÀ CŨ', 12, k, rot=-90), label(-680, 1480, '±0.00', 9, k, MUTED, 400),
         label(-600, 2400, 'SÂN NHÀ CŨ', 9, k, MUTED, 400, rot=-90),
         label(AXIS, 3770, 'ĐƯỜNG ĐT639 · TÂY', 11, k), label(AXIS, -640, 'BIỂN · ĐÔNG', 11, k, ACC),
         label(1950, -330, 'vườn sau −2.50', 9, k, GREEN_LINE, 600, 'end')]
    if show_forecourt:
        if front_y < 2900:
            o.append(rect(260, front_y, 1300, 2900 - front_y, PAVE))
        o += [rect(760, 2900, 300, 700, PAVE),
              rect(1110, 3000, 900, 560, GARAGE, ACC, 4),
              label(1560, 3270, 'NHÀ XE 3 Ô', 9, k), label(1560, 3330 + 9 * k, 'và bảo vệ', 8, k, MUTED, 400),
              label(AXIS, max(front_y + 230, 2740), 'sân danh dự ±0.00', 9, k, MUTED, 400, 'middle', PAVE)]
    # north arrow and scale bar
    o += [path('M1700 -640 H1980', INK, 6), path('M1700 -640 l50 -22 v44 z', INK, 0, INK),
          label(2030, -620, 'B', 11, k, INK, 600, 'middle', None),
          path('M-1000 3480 h500 M-1000 3468 v24 M-500 3468 v24 M-900 3474 v12 M-800 3474 v12 M-700 3474 v12 M-600 3474 v12', INK, 3),
          label(-1000, 3450, '0', 8, k, INK, 400, 'middle', None), label(-500, 3450, '5 m', 8, k, INK, 400, 'middle', None)]
    return '\n'.join(o)


def link(x, y, w, h, k):
    return rect(x, y, w, h, '#DCE9E6', INK, 4) + label(x + w / 2, y - 40, 'nối nhà cũ', 8, k, TEAL)


# ---------- Section frame ----------

def sec_frame(k, east, west):
    """Ground: garden −2.50 east of the house, forecourt ±0.00 west of it, road, level marks."""
    o = [rect(-800, 250, 5040, 140, EARTH), rect(west, 0, 3800 - west, 250, EARTH),
         path(f'M-800 250 H{east}', GREEN_LINE, 8), path(f'M{west} 0 H3600', INK, 5),
         rect(3600, 0, 200, 24, '#8E918C')]
    for z, t in ((-250, '−2.50'), (0, '±0.00'), (90, '+0.90'), (560, '+5.60'), (1030, '+10.30'), (1500, '+15.00')):
        o += [path(f'M3880 {-z} H3960', ACC, 5), label(3975, -z + round(3.2 * k), t, 9, k, ACC, 600, 'start', None)]
    o += [label(-760, -1500, '← BIỂN', 10, k, ACC, 600, 'start'), label(3560, -1500, 'ĐƯỜNG →', 10, k, ACC, 600, 'end'),
          label(-400, 225, 'vườn −2.50', 8, k, GREEN_LINE, 400)]
    return o


def slab(s1, s2, z):
    return rect(s1, -z, s2 - s1, 30, INK)


# ---------- HTML helpers ----------

def row(name, value, text):
    return ('<div style="display: flex; flex-direction: column; gap: 3px; padding: 8px 0; border-top: 1px solid #C5CAC5">\n'
            '<div style="display: flex; justify-content: space-between; gap: 12px; font-size: 14px; font-weight: 600">'
            f'<span>{escape(name)}</span><span style="flex: none">{escape(value)}</span></div>\n'
            f'<div style="font-size: 12.5px; line-height: 1.5; color: #4A5868">{escape(text)}</div>\n</div>')


def header(code, title, note):
    return ('<div style="height: 60px; box-sizing: border-box; padding-bottom: 10px; border-bottom: 2px solid #15263B; '
            'display: flex; justify-content: space-between; align-items: flex-end">\n'
            '<div style="display: flex; align-items: baseline; gap: 16px">\n'
            f'<span style="font-size: 13px; font-weight: 600; letter-spacing: 2px; color: #7A5620">{code}</span>\n'
            "<h1 style=\"margin: 0; font-family: 'Cormorant Garamond', serif; font-weight: 600; font-size: 42px; line-height: 1\">"
            f'{escape(title)}</h1>\n</div>\n'
            f'<div style="font-size: 13px; color: #4A5868">{escape(note)}</div>\n</div>')


def caption(text):
    return f'<div style="font-size: 11px; font-weight: 600; letter-spacing: 1.6px; color: #7A5620">{escape(text)}</div>'


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


def scheme_board(code, title, note, plan_svg, idea, section_svg, rows):
    half = (len(rows) + 1) // 2
    cols = ''.join('<div style="display: flex; flex-direction: column">\n' + '\n'.join(row(*r) for r in part) + '\n</div>\n'
                   for part in (rows[:half], rows[half:]))
    right = ('<div style="flex: 1; min-width: 0; display: flex; flex-direction: column; gap: 14px">\n'
             f'<div style="font-size: 16px; line-height: 1.55">{escape(idea)}</div>\n'
             '<div style="display: flex; flex-direction: column; gap: 6px">\n'
             + caption('MẶT CẮT DỌC TRỤC · BIỂN BÊN TRÁI, ĐƯỜNG BÊN PHẢI') + '\n' + section_svg + '\n</div>\n'
             '<div style="display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 0 28px">\n'
             + cols + '</div>\n</div>')
    left = ('<div style="width: 640px; flex: none; display: flex; flex-direction: column; gap: 6px">\n'
            + caption('TẦNG 1 · CỐT +0.90 TRÊN KHU ĐẤT') + '\n' + plan_svg + '\n</div>')
    return header(code, title, note) + '\n<div style="display: flex; gap: 32px">\n' + left + '\n' + right + '\n</div>'


# ---------- Mini parti diagrams ----------

def parti(kind, w=140):
    o = [rect(-190, -400, 2200, 4000, '#EFEDE4', MUTED, 25), rect(-190, -400, 2200, 600, GREEN),
         path(OLD_HOUSE, 'none', 0, '#CFCFCA'), rect(1110, 3000, 900, 560, GARAGE)]
    if kind == 'K1':
        o += [rect(10, 300, 1800, 1600, INK), rect(10, 1450, 1800, 450, ACC), rect(300, -300, 1200, 400, WATER)]
    elif kind == 'K2':
        o += [rect(-40, 100, 1900, 2400, SLATE), rect(210, 350, 1400, 1900, INK), rect(710, 1000, 400, 500, ACC),
              rect(310, -300, 1200, 350, WATER)]
    elif kind == 'K3':
        o += [rect(10, 0, 1800, 2300, '#B9C0C9'), rect(10, 500, 1800, 1800, SLATE), rect(10, 1000, 1800, 1300, MUTED),
              rect(10, 1500, 1800, 800, INK), rect(210, 60, 1400, 380, WATER)]
    elif kind == 'K4':
        o += [rect(-190, 400, 840, 1800, INK), rect(1170, 400, 640, 1800, INK), rect(650, 700, 520, 600, ACC),
              rect(710, -350, 400, 700, WATER), path(f'M{AXIS} -400 V3600', ACC, 20, extra=' stroke-dasharray="60 40"')]
    h = round(w * PARTI_VIEW[3] / PARTI_VIEW[2])
    return svg(PARTI_VIEW, w, h, f'Sơ đồ khối phương án {kind}', '\n'.join(o))


# ---------- K1 · Tường phía tây ----------

def k1():
    k = PLAN_K
    o = [site(k, 50, 1900)]
    o.append(rect(300, -300, 1200, 400, WATER, WATER_LINE, 4))
    o.append(label(900, -90, 'HỒ BƠI 12 × 4 m · −2.50', 9, k, INK, 600, 'middle', WATER))
    o.append(path(' '.join(f'M760 {y} H1060' for y in range(-10, 51, 20)), INK, 3))
    o += [room(10, 50, 1800, 250, 'LOGGIA BIỂN · sâu 2,5 m', TERR, 8, False),
          room(10, 300, 750, 1150, 'SALON'), room(760, 300, 300, 1150, 'SẢNH DÀI', rot=-90),
          room(1060, 300, 390, 1150, 'PHÒNG ĂN'), room(1450, 300, 360, 1150, 'BẾP'),
          room(10, 1450, 390, 450, 'POWDER', SLATE, 8), room(400, 1450, 360, 450, 'THANG', SLATE, 8, False),
          room(760, 1450, 300, 450, 'VÀO', SLATE, 8, False), room(1060, 1450, 200, 450, 'TM', SLATE, 8, False),
          room(1260, 1450, 550, 450, 'BẾP PHỤ', SLATE, 8),
          rect(10, 300, 1800, 1600, 'none', INK, 20), rect(10, 1450, 1800, 450, 'none', INK, 20),
          link(-320, 1100, 330, 250, k),
          label(AXIS, 2000 + 9 * k, 'TƯỜNG TÂY dày 4,5 m', 10, k, ACC, 600, 'middle', PAVE),
          path(f'M{AXIS} -400 V3600', ACC, 4, extra=' stroke-dasharray="40 24"')]
    plan_svg = svg(PLAN_VIEW, 640, 906,
                   'Phương án K1, mặt bằng tầng 1: nhà 18 × 16 m đặt giữa lô, dải tường dày 4,5 m phía đường chứa thang, '
                   'thang máy, powder, bếp phụ; phía biển là salon, sảnh dài trên trục, phòng ăn và bếp, tất cả mở ra '
                   'loggia 2,5 m; hồ bơi 12 × 4 m ở vườn sau', '\n'.join(o))
    s = sec_frame(SEC_K, 50, 1900)
    s += [rect(300, -1500, 1600, 1750, '#FFFFFF'), rect(1450, -1620, 450, 1870, SLATE),
          rect(-300, 250, 400, 120, WATER, WATER_LINE, 3)]
    s += [slab(300, 1900, -250), slab(50, 1900, 90), slab(50, 1900, 560), slab(50, 1900, 1030), slab(50, 1900, 1500)]
    s += [rect(50, -1500, 26, 1590, INK), path('M300 -90 V-1500', '#5A9AA0', 10), rect(1870, -1620, 30, 1870, INK)]
    s += [arrow('M3300 -1450 L1980 -950', RUST, 1960, -942, 158, SEC_K),
          label(3560, -1380, 'nắng chiều bị chặn', 9, SEC_K, RUST, 600, 'end'),
          arrow('M-700 -330 H1380', TEAL, 1400, -330, 0, SEC_K), label(-700, -380, 'gió biển', 9, SEC_K, TEAL, 600, 'start'),
          label(875, -300, 'SALON · ĂN · BẾP', 9, SEC_K), label(875, -770, 'PHÒNG NGỦ', 9, SEC_K),
          label(875, -1240, 'CHỦ NHÀ', 9, SEC_K), label(875, 160, 'POOL LOUNGE · SPA', 9, SEC_K),
          label(1675, -700, 'TƯỜNG TÂY', 9, SEC_K, '#FFFFFF', 600, 'middle', None, -90)]
    section_svg = svg(SEC_VIEW, 744, 310,
                      'Mặt cắt K1: dải tường tây cao hơn mái chặn nắng chiều; phía đông ba tầng phòng lớn có loggia, '
                      'gió biển đi xuyên; tầng dưới mở ra vườn và hồ bơi', '\n'.join(s))
    rows = [
        ('−2.50', '288 m²', 'Pool lounge, spa, phòng tập mở ra vườn và hồ bơi 12 × 4 m. Trong dải tường: phòng nhân viên, giặt ủi, kho, kỹ thuật.'),
        ('+0.90', '288 m²', 'Salon 86 m², sảnh dài trên trục, phòng ăn 45 m², bếp 41 m², cả bốn nhìn biển qua loggia 2,5 m.'),
        ('+5.60', '288 m²', 'Phòng gia đình trên trục và ba phòng ngủ ra ban công biển; tắm và tủ nằm trong dải tường.'),
        ('+10.30', '288 m²', 'Căn hộ chủ: phòng ngủ trên trục, cánh ông và cánh bà hai bên, thư phòng, phòng ngủ phụ.'),
        ('Mạnh', 'đơn giản, nhìn biển', 'Một khung kết cấu đều, dễ thi công. Mọi phòng chính nhìn biển; mặt tây kín nên chiều mát và yên.'),
        ('Yếu', 'mặt biển toàn kính', 'Mặt đông hứng thẳng gió bão: cần cửa chớp chống bão suốt mặt. Từ cổng vào không thấy biển.'),
        ('Nối nhà cũ', 'cầu kính tầng 1', 'Hành lang kính ngắn sang nhà cũ; chênh 0,9 m giải bằng bậc và thang nâng.'),
        ('Tổng', 'khoảng 864 m² + 288 m²', 'Nhà 18 × 16 m, ba tầng trên mặt đất và một tầng dưới; nhà xe 3 ô ở sân trước.'),
    ]
    return scheme_board('K1', 'Tường phía tây', 'Gom phần kín vào một dải dày dọc mặt đường · mở hết ra biển',
                        plan_svg,
                        'Mọi thứ cần kín — thang, thang máy, tắm, kho, bếp phụ — gom vào một dải dày 4,5 m dọc mặt đường. '
                        'Phần còn lại sâu 11,5 m là những phòng lớn mở hết ra biển. Dải tường che nắng chiều và tiếng '
                        'đường; phía biển chỉ còn kính và loggia.', section_svg, rows)


# ---------- K2 · Một mái, bốn hiên ----------

def k2():
    k = PLAN_K
    o = [site(k, 100, 2500)]
    o.append(rect(310, -300, 1200, 350, WATER, WATER_LINE, 4))
    o.append(label(910, -100, 'HỒ BƠI 12 × 3,5 m', 9, k, INK, 600, 'middle', WATER))
    o.append(rect(-40, 100, 1900, 2400, TERR, INK, 6))
    o += [circle(x, y, 26, INK) for x in range(-15, 1860, 375) for y in (125, 2475)]
    o += [circle(x, y, 26, INK) for x in (-15, 1835) for y in range(500, 2400, 400)]
    o += [room(210, 350, 1400, 650, 'GRAND SALON'), room(210, 1000, 450, 700, 'PHÒNG ĂN'),
          room(660, 1000, 500, 700, 'SẢNH GIỮA'), room(1160, 1000, 450, 700, 'BẾP'),
          room(210, 1700, 450, 550, 'THƯ VIỆN', px=8), room(660, 1700, 500, 550, 'TIỀN SẢNH', px=8),
          room(1160, 1700, 450, 550, 'THANG · TM', px=8),
          rect(210, 350, 1400, 1900, 'none', INK, 20),
          rect(760, 1100, 300, 500, 'none', ACC, 6, ' stroke-dasharray="20 14"'),
          label(910, 1640, 'lồng đèn mái', 8, k, ACC),
          label(910, 230, 'HIÊN SÂU 2,5 m · hai tầng', 9, k, INK, 600, 'middle', TERR),
          label(85, 1300, 'HIÊN', 9, k, INK, 600, 'middle', TERR, -90), label(1735, 1300, 'HIÊN', 9, k, INK, 600, 'middle', TERR, -90),
          link(-320, 1000, 280, 200, k),
          path(f'M{AXIS} -400 V3600', ACC, 4, extra=' stroke-dasharray="40 24"')]
    plan_svg = svg(PLAN_VIEW, 640, 906,
                   'Phương án K2, mặt bằng tầng 1: lõi nhà 14 × 19 m có hiên 2,5 m bao bốn phía; Grand Salon suốt mặt biển, '
                   'giữa nhà là sảnh thông tầng dưới lồng đèn mái, hai bên là phòng ăn và bếp, phía đường là thư viện, '
                   'tiền sảnh và thang', '\n'.join(o))
    s = sec_frame(SEC_K, 100, 2500)
    s += [rect(350, -1030, 1900, 1280, '#FFFFFF'), rect(-300, 250, 400, 100, WATER, WATER_LINE, 3)]
    s += [slab(350, 2250, -250), slab(100, 2500, 90), slab(100, 1000, 560), slab(1700, 2500, 560), slab(700, 1000, 1030),
          slab(1700, 1900, 1030), rect(350, -900, 26, 1150, INK), rect(2224, -900, 26, 1150, INK),
          rect(100, -930, 26, 1020, INK), rect(2474, -930, 26, 1020, INK)]
    s += [path('M-60 -900 L1300 -1480 L2660 -900', INK, 30), rect(1150, -1640, 300, 170, '#FFFFFF', INK, 8),
          path('M1120 -1640 L1300 -1720 L1480 -1640', INK, 12)]
    s += [arrow('M1350 -150 V-1660', TEAL, 1350, -1690, -90, SEC_K, dashed=False),
          arrow('M-700 -330 H1100', TEAL, 1120, -330, 0, SEC_K), label(-700, -380, 'gió biển', 9, SEC_K, TEAL, 600, 'start'),
          arrow('M3300 -1450 L2700 -980', RUST, 2680, -965, 142, SEC_K),
          label(3560, -1380, 'nắng dừng ở mái hiên', 9, SEC_K, RUST, 600, 'end'),
          label(675, -300, 'SALON', 9, SEC_K), label(1350, -300, 'SẢNH GIỮA', 9, SEC_K),
          label(1975, -300, 'TIỀN SẢNH', 9, SEC_K), label(675, -770, 'GIA ĐÌNH', 9, SEC_K),
          label(1300, -1150, 'CHỦ NHÀ TRONG MÁI', 9, SEC_K), label(1300, 160, 'POOL LOUNGE · SPA', 9, SEC_K)]
    section_svg = svg(SEC_VIEW, 744, 310,
                      'Mặt cắt K2: một mái dốc lớn phủ cả nhà và hiên hai tầng; sảnh giữa thông tầng có lồng đèn mái hút '
                      'khí nóng; nắng dừng ở mép mái hiên', '\n'.join(s))
    rows = [
        ('−2.50', '266 m²', 'Pool lounge, spa, bếp phụ, phòng nhân viên dưới lõi nhà; hồ bơi 12 × 3,5 m ngay dưới hiên biển.'),
        ('+0.90', '266 m² + hiên', 'Grand Salon 91 m² suốt mặt biển, sảnh giữa thông tầng, phòng ăn 32 m², bếp 32 m², thư viện, tiền sảnh.'),
        ('+5.60', 'khoảng 230 m²', 'Ba phòng ngủ và phòng học ở bốn góc mở ra hiên tầng 2; phòng gia đình phía biển.'),
        ('Trong mái', 'khoảng 170 m²', 'Căn hộ chủ dưới mái, cửa sổ mái nhìn biển, lồng đèn ngay trên sảnh giữa.'),
        ('Mạnh', 'mát nhất', 'Tường không bị nắng chiếu thẳng; hiên là chỗ sống ngoài trời. Dáng biệt thự Đông Dương, đối xứng như villa Palladio.'),
        ('Yếu', 'ít sàn, mái lớn', 'Chỉ khoảng 666 m² sàn kín; phòng ăn, bếp nhỏ hơn đề bài. Mái lớn và hiên rộng dễ bị bão lật: phải neo rất kỹ.'),
        ('Nối nhà cũ', 'lối có mái', 'Nhà đứng riêng, cách nhà cũ một lối đi có mái ở phía bắc.'),
        ('Tổng', 'lõi 14 × 19 m', 'Hiên 19 × 24 m, cách ranh hai bên 1,5 m; khoảng 340 m² hiên có mái mỗi hai tầng.'),
    ]
    return scheme_board('K2', 'Một mái, bốn hiên', 'Một khối vuông dưới mái lớn · hiên sâu bốn phía · sảnh giữa có lồng đèn',
                        plan_svg,
                        'Một khối vuông vức dưới một mái dốc lớn; quanh bốn mặt là hiên sâu 2,5 m ở cả hai tầng nên tường '
                        'không bao giờ bị nắng chiếu thẳng. Giữa nhà là sảnh thông tầng, trên có lồng đèn mái hút hơi nóng '
                        'ra ngoài.', section_svg, rows)


# ---------- K3 · Bậc thang ra biển ----------

def k3():
    k = PLAN_K
    o = [site(k, 0, 2300)]
    o += [room(10, 0, 1800, 500, '', TERR, area=False),
          rect(210, 60, 1400, 380, WATER, WATER_LINE, 4),
          label(910, 230, 'HỒ TRÀN 14 × 3,8 m · trên mái tầng dưới', 9, k, INK, 600, 'middle', WATER),
          room(10, 500, 1000, 700, 'SALON'), room(1010, 500, 800, 700, 'PHÒNG ĂN'),
          room(10, 1200, 600, 700, 'KHÁCH NHỎ'), room(610, 1200, 600, 700, 'SẢNH THANG', area=False),
          room(1210, 1200, 600, 700, 'BẾP'),
          room(10, 1900, 600, 400, 'POWDER · TM', px=8), room(610, 1900, 600, 400, 'TIỀN SẢNH', px=8),
          room(1210, 1900, 600, 400, 'BẾP PHỤ', px=8),
          rect(710, 1350, 400, 400, 'none', TEAL, 6, ' stroke-dasharray="18 12"'),
          label(910, 1640, 'giếng trời 4 × 4 m', 8, k, TEAL, 600, 'middle'),
          rect(10, 500, 1800, 1800, 'none', INK, 20)]
    for y, t in ((1000, 'mép tầng 2 · lùi 5 m'), (1500, 'mép tầng 3 · lùi 10 m')):
        o += [path(f'M-60 {y} H1880', RUST, 6, extra=' stroke-dasharray="26 16"'),
              label(-80, y + 30, t, 8, k, RUST, 600, 'end')]
    o += [label(2000, 250, '+0.90', 8, k, MUTED, 400, 'end'), link(-320, 1200, 330, 250, k),
          path(f'M{AXIS} -400 V3600', ACC, 4, extra=' stroke-dasharray="40 24"')]
    plan_svg = svg(PLAN_VIEW, 640, 906,
                   'Phương án K3, mặt bằng tầng 1: nhà 18 m rộng, mặt đường thẳng; phía biển là sân thượng sâu 5 m với hồ '
                   'tràn 14 m; salon và phòng ăn mở ra sân; giữa nhà là sảnh thang có giếng trời; nét đứt đỏ là mép tầng 2 '
                   'và tầng 3 lùi dần về phía đường', '\n'.join(o))
    s = sec_frame(SEC_K, 0, 2300)
    s += [rect(0, -90, 2300, 340, '#FFFFFF'), rect(500, -560, 1800, 470, '#FFFFFF'),
          rect(1000, -1030, 1300, 470, '#FFFFFF'), rect(1500, -1500, 800, 470, '#FFFFFF')]
    s += [slab(0, 2300, -250), slab(0, 2300, 90), slab(500, 2300, 560), slab(1000, 2300, 1030), slab(1500, 2300, 1500),
          rect(2270, -1620, 30, 1870, INK), rect(0, -90, 26, 340, INK)]
    for x, z1, z2 in ((500, 90, 560), (1000, 560, 1030), (1500, 1030, 1500)):
        s.append(path(f'M{x} {-z1} V{-z2}', '#5A9AA0', 10))
        s.append(rect(x - 70, -z1 - 70, 60, 70, GREEN, GREEN_LINE, 3))
    s += [rect(50, -200, 400, 110, WATER, WATER_LINE, 3), path('M0 -190 V-90', INK, 6),
          rect(1700, -1500, 400, 1410, 'none', TEAL, 6, ' stroke-dasharray="18 12"'),
          arrow('M-700 -330 H-60', TEAL, -40, -330, 0, SEC_K), arrow('M-700 -800 H440', TEAL, 460, -800, 0, SEC_K),
          arrow('M-700 -1270 H940', TEAL, 960, -1270, 0, SEC_K),
          label(-700, -1320, 'mỗi tầng một sân nhìn biển', 9, SEC_K, TEAL, 600, 'start'),
          label(250, -230, 'HỒ TRÀN', 8, SEC_K, INK, 600, 'middle', WATER), label(1150, 160, 'TẦNG DƯỚI SÂU 23 m', 9, SEC_K),
          label(1150, -300, 'SALON', 9, SEC_K), label(1650, -770, 'PHÒNG NGỦ', 9, SEC_K),
          label(1900, -1240, 'CHỦ NHÀ', 9, SEC_K), label(1900, -1580, 'giếng trời', 8, SEC_K, TEAL)]
    section_svg = svg(SEC_VIEW, 744, 310,
                      'Mặt cắt K3: nhà lùi 5 m mỗi tầng về phía đường, tạo ba sân thượng chồng lên nhau nhìn biển; hồ tràn '
                      'trên mái tầng dưới; mặt đường thẳng ba tầng; giếng trời xuyên các tầng', '\n'.join(s))
    rows = [
        ('−2.50', '414 m²', 'Sâu 23 m dưới cả nhà: pool lounge và spa mở ra vườn, phòng giải trí, phòng tập, hầm rượu, nhân viên, giặt ủi.'),
        ('+0.90', '324 m²', 'Salon 70 m² và phòng ăn 56 m² mở ra sân có hồ tràn 14 m; bếp 42 m²; sảnh thang có giếng trời.'),
        ('+5.60', '234 m²', 'Lùi 5 m. Phòng gia đình và ba phòng ngủ mở ra sân trồng cây trên mái salon.'),
        ('+10.30', '144 m²', 'Lùi thêm 5 m. Căn hộ chủ với cánh ông, cánh bà, mở ra sân thượng trên cùng.'),
        ('Mạnh', 'mỗi tầng một sân', 'Tầng nào cũng có sân 90 m² nhìn biển. Khối thấp dần về phía biển nên ít mặt đứng cao hứng gió bão. Hai bộ mặt: palazzo phía đường, vườn treo phía biển.'),
        ('Yếu', 'chống thấm', 'Sân chồng lên phòng, hồ tràn nằm trên mái: chống thấm là rủi ro lớn nhất. Sân hướng đông nắng trưa, cần giàn che. Sàn trên mặt đất chỉ khoảng 702 m².'),
        ('Nối nhà cũ', 'hành lang tầng 1', 'Hành lang kính sang nhà cũ ở giữa cạnh bắc.'),
        ('Tổng', 'khoảng 702 m² + 414 m²', 'Mặt đường rộng 18 m, cao ba tầng; tầng dưới lớn nhất bù cho các tầng trên nhỏ dần.'),
    ]
    return scheme_board('K3', 'Bậc thang ra biển', 'Mặt đường là palazzo · mặt biển lùi dần thành ba sân thượng',
                        plan_svg,
                        'Mặt đường là một palazzo phẳng ba tầng; mặt biển lùi dần mỗi tầng 5 m thành ba sân thượng chồng '
                        'lên nhau, như nhà bậc thang ở Amalfi. Tầng nào cũng có một sân rộng nhìn biển, và hồ tràn nằm '
                        'ngay trên mái tầng dưới.', section_svg, rows)


# ---------- K4 · Cổng nhìn ra biển ----------

def k4():
    k = PLAN_K
    o = [site(k, 400, 2200)]
    o.append(rect(710, -350, 400, 700, WATER, WATER_LINE, 4))
    o.append(label(910, 0, 'HỒ BƠI', 9, k, INK, 600, 'middle', WATER))
    o.append(label(910, 0 + 11 * k, '4 × 7 m', 8, k, MUTED, 400, 'middle', WATER))
    o += [room(650, 1300, 520, 900, '', PAVE, area=False),
          rect(650, 400, 520, 300, '#FFFFFF', INK, 7),
          path(' '.join(f'M650 {y} H1170' for y in range(430, 700, 30)), INK, 3),
          room(650, 700, 520, 600, 'LOGGIA', TERR),
          rect(650, 700, 520, 600, 'none', ACC, 8, ' stroke-dasharray="24 14"'),
          label(910, 1260, 'cầu tầng 2–3 ở trên', 8, k, ACC, 600, 'middle', TERR),
          label(910, 1750, 'CỔNG TRÊN TRỤC', 9, k, INK, 600, 'middle', PAVE),
          label(910, 1750 + 11 * k, 'rộng 5,2 m', 8, k, MUTED, 400, 'middle', PAVE),
          label(910, 560, 'BẬC XUỐNG VƯỜN', 8, k)]
    o += [room(-190, 400, 840, 600, 'PHÒNG ĂN'), room(-190, 1000, 840, 500, 'SẢNH · THANG · TM', px=8),
          room(-190, 1500, 840, 700, 'SALON'),
          room(1170, 400, 640, 700, 'BẾP'), room(1170, 1100, 640, 400, 'BẾP PHỤ', px=8),
          room(1170, 1500, 640, 700, 'PHỤC VỤ', px=8),
          rect(-190, 400, 840, 1800, 'none', INK, 20), rect(1170, 400, 640, 1800, 'none', INK, 20),
          rect(640, 1150, 20, 200, '#FFFFFF'), label(910, 1420, '← cửa chính', 8, k, ACC, 600, 'middle', PAVE),
          link(-320, 1000, 130, 300, k),
          label(-120, 2380, 'KHỐI BẮC', 9, k, ACC, 600, 'start', PAVE), label(1490, 2380, 'KHỐI NAM', 9, k, ACC, 600, 'middle', PAVE),
          path(f'M{AXIS} -400 V3600', ACC, 4, extra=' stroke-dasharray="40 24"')]
    o.append(arrow(f'M{AXIS} 3450 V-300', TEAL, AXIS, -330, -90, k, w=1.4))
    plan_svg = svg(PLAN_VIEW, 640, 906,
                   'Phương án K4, mặt bằng tầng 1: hai khối dọc lô đất, khối bắc 8,4 m có phòng ăn, sảnh thang và salon, '
                   'khối nam 6,4 m có bếp, bếp phụ và sảnh phục vụ; giữa là cổng 5,2 m trên trục, từ đường nhìn thẳng ra '
                   'biển; dưới cầu là loggia ăn ngoài trời; bậc xuống vườn và hồ bơi trên trục', '\n'.join(o))
    s = sec_frame(SEC_K, 400, 2200)
    s += [rect(400, -1500, 1800, 1410, '#E4E6E1', OLD_LINE, 4),
          label(1750, -1150, 'mặt bên khối bắc', 8, SEC_K, MUTED, 400, 'middle', '#E4E6E1'),
          rect(400, -60, 1800, 310, '#FFFFFF'), rect(700, -1500, 600, 940, '#FFFFFF')]
    s += [slab(400, 2200, -250), slab(700, 2200, 90), slab(700, 1300, 560), slab(700, 1300, 1030), slab(700, 1300, 1500),
          path('M700 -90 L400 250', INK, 12), path(' '.join(f'M{700 - i * 30} {-90 + i * 34} h-30' for i in range(10)), INK, 5),
          path('M700 -560 V-1500 M1300 -560 V-1500', '#5A9AA0', 10), rect(-350, 250, 700, 110, WATER, WATER_LINE, 3)]
    s += [arrow('M3200 -160 H-650', TEAL, -680, -160, 180, SEC_K, w=1.4),
          label(3200, -210, 'từ cổng nhìn thẳng ra biển', 9, SEC_K, TEAL, 600, 'end'),
          label(1000, -300, 'LOGGIA', 9, SEC_K, INK, 600, 'middle', TERR), label(1750, -300, 'CỔNG', 9, SEC_K),
          label(1000, -770, 'GIA ĐÌNH · CẦU', 9, SEC_K), label(1000, -1240, 'PHÒNG TRÀ', 9, SEC_K),
          label(1300, 160, 'POOL LOUNGE DƯỚI CỔNG', 9, SEC_K), label(560, -180, 'bậc', 8, SEC_K)]
    section_svg = svg(SEC_VIEW, 744, 310,
                      'Mặt cắt K4 dọc cổng: sàn cổng ở cốt +0.90 thông từ sân trước ra bậc xuống vườn; cầu hai tầng bắc '
                      'ngang cổng; từ cổng nhìn thẳng ra biển; pool lounge nằm dưới cổng', '\n'.join(s))
    rows = [
        ('−2.50', 'khoảng 340 m²', 'Dưới hai khối và dưới cổng: pool lounge mở ra hồ bơi trên trục, spa, phòng giải trí, nhân viên, giặt ủi.'),
        ('+0.90', '266 m²', 'Khối bắc: phòng ăn 50 m² nhìn biển, sảnh thang, salon 59 m². Khối nam: bếp 45 m² nhìn biển, bếp phụ, sảnh phục vụ.'),
        ('+5.60', '297 m²', 'Phòng gia đình trên cầu nhìn cả biển lẫn sân trước; hai phòng ngủ khối bắc; phòng khách và phòng học khối nam.'),
        ('+10.30', '297 m²', 'Căn hộ chủ chiếm cả khối bắc, cánh ông và cánh bà; phòng trà trên cầu; khối nam phòng ngủ phụ và phòng tập.'),
        ('Mạnh', 'đến là thấy biển', 'Vừa qua cổng chính đã thấy biển xuyên qua nhà. Hai khối hẹp 6–8 m nên phòng nào cũng thông gió hai mặt. Loggia dưới cầu là phòng ăn ngoài trời.'),
        ('Yếu', 'hai lõi, ống gió', 'Hai lõi thang; từ bếp sang phòng ăn đi qua loggia có mái nhưng hở. Khi bão cổng thành ống gió: cần cửa cổng cao đóng được ở đầu phía biển.'),
        ('Nối nhà cũ', 'khối bắc sát nhà cũ', 'Khối bắc cách nhà cũ 1,3 m, nối bằng một cửa ở sảnh thang.'),
        ('Tổng', 'khoảng 860 m² + 340 m²', 'Khối bắc 8,4 × 18 m, khối nam 6,4 × 18 m, cầu 5,2 × 6 m. Khác Nhà Sân Nước (S0): khoảng giữa là cổng hẹp có cầu, không phải sân.'),
    ]
    return scheme_board('K4', 'Cổng nhìn ra biển', 'Hai khối, một cổng trên trục, một cầu hai tầng',
                        plan_svg,
                        'Nhà tách làm hai khối dọc lô đất, chừa giữa một cổng rộng 5,2 m trên trục: vừa qua cổng chính là '
                        'thấy biển xuyên qua nhà. Hai khối nối bằng một cầu hai tầng; dưới cầu là loggia ăn ngoài trời giữa '
                        'phòng ăn và bếp.', section_svg, rows)


# ---------- K0 · Khu đất và đề bài ----------

def k0():
    k = PLAN_K
    o = [site(k, 3600, 3600, show_forecourt=False)]
    o += [rect(-190, -400, 2200, 4000, '#EFEDE4'), rect(-190, -400, 2200, 1200, GREEN),
          path('M-190 800 H2010', GREEN_LINE, 6, extra=' stroke-dasharray="20 14"'),
          label(1700, 760, 'dốc 2,5 m', 9, k, GREEN_LINE, 600, 'middle', GREEN),
          label(500, 300, 'vườn −2.50', 10, k, GREEN_LINE, 600, 'middle', GREEN),
          label(500, 2200, 'sân ±0.00', 10, k, MUTED, 600, 'middle', '#EFEDE4'),
          path('M-190 -400 V3600 H760 M1060 3600 H2010 V-400 H-190', ACC, 5, extra=' stroke-dasharray="30 18"'),
          path('M-190 -470 H2010 M-190 -490 v40 M2010 -490 v40', INK, 4), label(1500, -500, '22 m', 9, k, INK, 600),
          path('M2080 -400 V3600 M2060 -400 h40 M2060 3600 h40', INK, 4), label(2060, 1600, '40 m · 880 m²', 9, k, INK, 600, 'middle', '#F3F4F1', -90)]
    o += [arrow(f'M{x} -700 V-430', TEAL, x, -410, 90, k) for x in (250, 1450)]
    o += [label(910, 120, 'gió biển ban ngày · tầm nhìn đẹp nhất', 9, k, TEAL, 600, 'middle', GREEN),
          arrow('M-900 -700 L-560 -360', TEAL, -545, -345, 45, k, w=1.4),
          label(-560, -240, 'gió mùa đông bắc · mùa mưa', 8, k, TEAL, 600, 'middle'),
          arrow('M2100 -720 L1650 -330', RUST, 1630, -312, 139, k, w=2.4),
          label(1400, -180, 'bão đến từ biển', 9, k, RUST, 600, 'middle', GREEN),
          arrow(f'M{AXIS} 3880 V3300', RUST, AXIS, 3280, -90, k, w=2.4),
          label(AXIS, 3200, 'nắng chiều · gió tây khô nóng · tiếng ồn', 9, k, RUST, 600, 'middle', '#EFEDE4'),
          path('M2120 -300 A4000 4000 0 0 0 2120 3400', ACC, 8, extra=' stroke-dasharray="30 22"')]
    o += [circle(x, y, 50, '#E9C46A', ACC, 4) for x, y in ((1866, 300), (1666, 1550), (1866, 2800))]
    o += [label(1580, 1540, 'mặt trời', 9, k, ACC, 600, 'end', '#EFEDE4'), label(1580, 1540 + 11 * k, 'chủ yếu phía nam', 8, k, ACC, 400, 'end', '#EFEDE4'),
          label(-500, 300, 'giữ lại · khoảng 438 m² sàn', 8, k, MUTED, 400, rot=-90)]
    plan_svg = svg(PLAN_VIEW, 640, 906,
                   'Phân tích khu đất: lô 22 × 40 m, 880 m²; biển phía đông với gió biển và bão; đường ĐT639 phía tây với '
                   'nắng chiều, gió tây và tiếng ồn; mặt trời chủ yếu phía nam; nhà cũ giữ lại ở phía bắc; đất dốc 2,5 m '
                   'về phía biển', '\n'.join(o))
    site_rows = [
        ('Lô đất', '22 × 40 m · 880 m²', 'Lô mới hợp với thửa nhà cũ phía bắc. Nhà cũ giữ kết cấu, khoảng 438 m² sàn.'),
        ('Biển', 'phía đông', 'Tầm nhìn đẹp nhất và gió mát ban ngày đều từ phía đông; bão cũng đến từ phía này.'),
        ('Đường', 'phía tây', 'ĐT639 ồn, nắng chiều gắt; mùa hè có ngày gió tây khô nóng. Mặt này nên kín.'),
        ('Dốc', '2,5 m về phía biển', 'Sân trước ±0.00, vườn sau −2.50: tầng dưới mở thẳng ra vườn, không phải đào sâu.'),
        ('Nắng', 'chủ yếu phía nam', 'Ở vĩ độ Tam Quan, cạnh nam của lô nhận nắng nhiều hơn cạnh bắc.'),
        ('Nhà cũ', 'phía bắc, ±0.00', 'Thấp hơn tầng 1 mới 0,9 m. Phương án nào cũng phải nối được với nhà cũ.'),
    ]
    brief = [('Tiếp khách', 'salon, phòng ăn ~48 m², bếp chính ~40 m² và bếp phụ, powder, áo khoác'),
             ('Gia đình', 'phòng gia đình ~40 m², thư viện, phòng học'),
             ('Ngủ', 'sáu phòng, ba ở nhà cũ; phòng chủ ~40 m² với cánh ông, cánh bà'),
             ('Giải trí', 'hồ bơi, spa, pool lounge, phòng giải trí, phòng tập'),
             ('Phục vụ', 'hai phòng nhân viên, nhập hàng, giặt ủi; nhà xe 3 ô và bảo vệ'),
             ('Thờ', 'phòng thờ giữ ở nhà cũ')]
    brief_html = '\n'.join(
        '<div style="display: flex; gap: 12px; padding: 6px 0; border-top: 1px solid #C5CAC5; font-size: 13px; line-height: 1.45">'
        f'<span style="width: 84px; flex: none; font-weight: 600">{escape(a)}</span><span style="color: #4A5868">{escape(b)}</span></div>'
        for a, b in brief)
    names = [('K1', 'Tường phía tây'), ('K2', 'Một mái, bốn hiên'), ('K3', 'Bậc thang ra biển'), ('K4', 'Cổng nhìn ra biển')]
    partis = '\n'.join(
        '<div style="display: flex; flex-direction: column; gap: 6px; align-items: flex-start">' + parti(c, 132)
        + f'<div style="font-size: 13px; line-height: 1.3"><span style="font-weight: 600; letter-spacing: 2px; color: #7A5620">{c}</span> '
          f'{escape(n)}</div></div>' for c, n in names)
    half = len(site_rows) // 2
    right = ('<div style="flex: 1; min-width: 0; display: flex; flex-direction: column; gap: 16px">\n'
             '<div style="font-size: 16px; line-height: 1.55">Bỏ mặt bằng cũ, đọc lại khu đất và giữ nguyên đề bài của bộ '
             'CHỐT. Bốn phương án bên dưới mỗi cái bắt đầu từ một đặc điểm của khu đất: nắng tây, khí hậu nóng ẩm, '
             'dốc ra biển, và trục nhìn ra biển.</div>\n'
             '<div style="display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 0 28px">\n'
             + ''.join('<div style="display: flex; flex-direction: column">' + '\n'.join(row(*r) for r in part) + '</div>\n'
                       for part in (site_rows[:half], site_rows[half:]))
             + '</div>\n<div style="display: flex; flex-direction: column">' + caption('ĐỀ BÀI · GIỮ NHƯ BỘ CHỐT') + '\n'
             '<div style="height: 6px"></div>' + brief_html + '</div>\n'
             '<div style="display: flex; flex-direction: column; gap: 8px">' + caption('BỐN CÁCH BẮT ĐẦU') + '\n'
             '<div style="display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 16px">\n' + partis + '\n</div></div>\n</div>')
    left = ('<div style="width: 640px; flex: none; display: flex; flex-direction: column; gap: 6px">\n'
            + caption('KHU ĐẤT · BIỂN Ở TRÊN, ĐƯỜNG Ở DƯỚI, BẮC BÊN TRÁI') + '\n' + plan_svg + '\n</div>')
    return (header('K0', 'Làm lại từ khu đất', 'Đọc lại khu đất · đề bài giữ nguyên · bốn hướng mới')
            + '\n<div style="display: flex; gap: 32px">\n' + left + '\n' + right + '\n</div>')


# ---------- K5 · So sánh ----------

SCORES = [
    ('Nhìn biển', (3, 2, 3, 2), ('mọi phòng chính', 'chủ yếu salon', 'mỗi tầng một sân', 'ăn, bếp, cầu')),
    ('Mát, che nắng', (3, 3, 1, 2), ('tường tây chặn nắng', 'hiên bốn phía', 'sân phơi nắng', 'khối hẹp, gió hai mặt')),
    ('Chịu bão', (2, 1, 2, 1), ('cần cửa chớp mặt đông', 'mái lớn dễ lật', 'khối thấp dần', 'cổng thành ống gió')),
    ('Đủ sàn theo đề bài', (3, 1, 2, 3), ('khoảng 864 m²', 'khoảng 666 m²', 'khoảng 702 m²', 'khoảng 860 m²')),
    ('Dễ thi công', (3, 2, 1, 2), ('khung đều', 'mái phức tạp', 'sân và hồ trên mái', 'hai lõi thang')),
    ('Nối nhà cũ', (2, 1, 2, 3), ('cầu kính', 'lối có mái', 'hành lang kính', 'sát khối bắc')),
    ('Ấn tượng khi đến', (2, 2, 2, 3), ('mặt tây kín', 'mái và hiên', 'palazzo phía đường', 'thấy biển qua cổng')),
]


def dots(n):
    return ('<span style="letter-spacing: 3px"><span style="color: #7A5620">' + '●' * n + '</span>'
            '<span style="color: #C5CAC5">' + '●' * (3 - n) + '</span></span>')


def k5():
    names = [('K1', 'Tường phía tây'), ('K2', 'Một mái, bốn hiên'), ('K3', 'Bậc thang ra biển'), ('K4', 'Cổng nhìn ra biển')]
    th = 'padding: 0 16px 10px 0; vertical-align: bottom; text-align: left; border-bottom: 2px solid #15263B'
    td = 'padding: 13px 16px 13px 0; border-bottom: 1px solid #C5CAC5; vertical-align: top'
    head = (f'<th style="{th}; width: 190px; font-size: 12px; font-weight: 600; letter-spacing: 1.2px; color: #4A5868">TIÊU CHÍ</th>'
            + ''.join(f'<th style="{th}"><div style="display: flex; flex-direction: column; gap: 6px">{parti(c, 104)}'
                      f'<div style="font-size: 14px; font-weight: 600"><span style="letter-spacing: 2px; color: #7A5620">{c}</span> '
                      f'{escape(n)}</div></div></th>' for c, n in names))
    body = []
    for crit, sc, notes in SCORES:
        cells = ''.join(f'<td style="{td}"><div style="font-size: 15px">{dots(s)}</div>'
                        f'<div style="font-size: 12.5px; color: #4A5868; margin-top: 2px">{escape(t)}</div></td>'
                        for s, t in zip(sc, notes))
        body.append(f'<tr><td style="{td}; font-size: 14px; font-weight: 600">{escape(crit)}</td>{cells}</tr>')
    totals = [sum(sc[i] for _, sc, _ in SCORES) for i in range(4)]
    body.append(f'<tr><td style="{td}; font-size: 14px; font-weight: 600; border-bottom: 2px solid #15263B">Cộng</td>'
                + ''.join(f'<td style="{td}; border-bottom: 2px solid #15263B; font-family: \'Cormorant Garamond\', serif; '
                          f'font-size: 30px; font-weight: 600; line-height: 1">{t}<span style="font-size: 16px; color: #4A5868"> / 21</span></td>'
                          for t in totals) + '</tr>')
    table = (f'<table style="width: 100%; border-collapse: collapse">\n<thead><tr>{head}</tr></thead>\n<tbody>\n'
             + '\n'.join(body) + '\n</tbody>\n</table>')
    rec = [('Đề xuất', 'K4, mượn tường tây của K1',
            'K4 là hướng mới nhất: trục và đối xứng vẫn còn, nhưng lần này trục mở ra biển ngay từ cổng. Lấy từ K1 '
            'nguyên tắc tường tây: hai đầu khối phía đường gom thang, tắm, kho, để mặt đường kín và mát. Đầu cổng '
            'phía biển có cửa cổng cao đóng được khi bão.'),
           ('Phương án an toàn', 'K1',
            'Điểm cao nhất, rẻ và dễ làm nhất. Chọn K1 nếu ưu tiên chi phí và vận hành hơn ấn tượng khi đến.'),
           ('Giữ lại một ý', 'sân của K3',
            'Dù chọn phương án nào, tầng 3 có thể lùi lại để có một sân thượng nhìn biển cho căn hộ chủ, như K3.')]
    rec_html = ('<div style="display: grid; grid-template-columns: 1.4fr 1fr 1fr; gap: 28px">\n' + '\n'.join(
        '<div style="display: flex; flex-direction: column; gap: 4px; padding-top: 10px; border-top: 2px solid #15263B">'
        f"<div style=\"font-family: 'Cormorant Garamond', serif; font-size: 24px; font-weight: 600; line-height: 1.1\">{escape(a)}</div>"
        f'<div style="font-size: 13px; font-weight: 600; letter-spacing: 1.5px; color: #7A5620">{escape(b)}</div>'
        f'<div style="font-size: 13.5px; line-height: 1.5; color: #4A5868">{escape(c)}</div></div>' for a, b, c in rec) + '\n</div>')
    return (header('K5', 'So sánh bốn hướng', 'Đánh giá sơ bộ của tôi · ba chấm là tốt nhất')
            + '\n' + table + '\n' + rec_html)


BOARDS = [
    ('K0', 'k0-khu-dat-de-bai', 'K0KhuDat.dc.html', 'Làm lại từ khu đất – đọc khu đất, đề bài, bốn hướng mới', k0),
    ('K1', 'k1-tuong-phia-tay', 'K1TuongTay.dc.html', 'Tường phía tây – dải kín dọc mặt đường, phòng lớn mở ra biển', k1),
    ('K2', 'k2-mot-mai-bon-hien', 'K2MotMai.dc.html', 'Một mái, bốn hiên – khối vuông, hiên sâu, sảnh giữa có lồng đèn', k2),
    ('K3', 'k3-bac-thang-ra-bien', 'K3BacThang.dc.html', 'Bậc thang ra biển – mỗi tầng lùi 5 m thành một sân thượng', k3),
    ('K4', 'k4-cong-nhin-ra-bien', 'K4Cong.dc.html', 'Cổng nhìn ra biển – hai khối, một cổng trên trục, cầu hai tầng', k4),
    ('K5', 'k5-so-sanh', 'K5SoSanh.dc.html', 'So sánh bốn hướng và đề xuất', k5),
]


def main():
    for code, slug, file, title, fn in BOARDS:
        (HERE / file).write_text(page(f'{code} · {title}', fn()), encoding='utf-8')
        print(file)
    manifest = {
        'order': 2,
        'project': 'Biệt thự Tam Quan',
        'set': 'Ý tưởng từ đầu',
        'eyebrow': 'Làm lại từ khu đất · chưa có trên canvas',
        'heading': 'Bốn hướng mới cho biệt thự',
        'summary': 'Không theo mặt bằng La Rotonda B. Cùng khu đất, cùng đề bài của bộ CHỐT, bốn cách đặt nhà khác hẳn nhau. '
                   'Xem K0 trước, K5 để so sánh.',
        'generator': 'design/y-tuong-tu-dau/generate.py',
        'boards': [{'code': c, 'slug': s, 'file': f, 'w': 1480, 'h': 1060, 'title': t} for c, s, f, t, _ in BOARDS],
    }
    (HERE / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
