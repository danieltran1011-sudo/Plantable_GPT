#!/usr/bin/env python3
"""Generate the "Dinh thự Tam Quan" design set (DT0–DT7): one French–Italian neoclassical mansion
for the Tam Quan site, drawn as a full set — concept, site plan, three floor-plan boards,
two elevations and a long section.

Boards use the canvas artboard format, so tools/build.py turns them into pages like the others.
Plans: centimetres on the RB0 site grid, sea (east) at the top, road (west) at the bottom,
north to the left. The house is x −40..1860 (19 m), y 300..2000 (17 m), axis x = 910.
Elevations and sections: x (or plan y) horizontal, svg y = −level in cm.

Usage: python3 design/dinh-thu/generate.py   (then run tools/build.py)
"""
import json
import math
from html import escape
from pathlib import Path

HERE = Path(__file__).resolve().parent

INK, MUTED, ACC, RULE = '#15263B', '#4A5868', '#7A5620', '#C5CAC5'
OLD, OLD_LINE, TERR, PAVE = '#ECEBE4', '#8E918C', '#E6E8E2', '#E3DCC8'
WATER, WATER_LINE, TEAL, RUST = '#BFDDE0', '#5A9AA0', '#1F7A80', '#B0502C'
GREEN, GREEN_LINE, EARTH, GARAGE = '#DCE5D3', '#6C8F54', '#E2DCCD', '#D8C9A0'
# elevation palette (same family as the CHỐT elevations)
WALL, RUSTIC, TRIM, LINE = '#EFE8D8', '#E2D9C3', '#F8F4EA', '#3A3A36'
GLASS, WOOD, COPPER, IRON, JOINT = '#8FA7B0', '#A99C82', '#9AB0A4', '#2B2F33', '#B9AE95'
FONTS = ('<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:'
         'wght@500;600&amp;family=Be+Vietnam+Pro:wght@400;500;600&amp;display=swap">')

AXIS = 910
X0, X1, Y0, Y1 = -40, 1860, 300, 2000      # house footprint
C0, C1 = 510, 1310                          # central bay
BAYS = (97, 372, 676, 910, 1143, 1447, 1722)
COLS = (560, 793, 1027, 1260)               # giant columns / porch columns


# ---------- generic SVG helpers ----------

def f(v):
    return f'{v:.1f}'.rstrip('0').rstrip('.') if isinstance(v, float) else str(v)


def rect(x, y, w, h, fill, stroke=None, sw=2.5, extra=''):
    s = f' stroke="{stroke}" stroke-width="{f(sw)}"' if stroke else ''
    return f'<rect x="{f(x)}" y="{f(y)}" width="{f(w)}" height="{f(h)}" fill="{fill}"{s}{extra}></rect>'


def path(d, stroke, sw, fill='none', extra=''):
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{f(sw)}"{extra}></path>'


def circle(cx, cy, r, fill, stroke=None, sw=2.5):
    s = f' stroke="{stroke}" stroke-width="{f(sw)}"' if stroke else ''
    return f'<circle cx="{f(cx)}" cy="{f(cy)}" r="{f(r)}" fill="{fill}"{s}></circle>'


def ellipse(cx, cy, rx, ry, fill, stroke=None, sw=2):
    s = f' stroke="{stroke}" stroke-width="{f(sw)}"' if stroke else ''
    return f'<ellipse cx="{f(cx)}" cy="{f(cy)}" rx="{f(rx)}" ry="{f(ry)}" fill="{fill}"{s}></ellipse>'


def label(x, y, text, px, k, fill=INK, weight=600, anchor='middle', halo='#FFFFFF', rot=None):
    size = round(px * k, 1)
    tr = f' transform="rotate({rot} {f(x)} {f(y)})"' if rot is not None else ''
    st = (f' stroke="{halo}" stroke-width="{round(size * 0.3, 1)}" paint-order="stroke" stroke-linejoin="round"'
          if halo else '')
    return (f'<text x="{f(x)}" y="{f(y)}" font-size="{size}" font-weight="{weight}" fill="{fill}" '
            f'text-anchor="{anchor}"{st}{tr}>{escape(text, quote=False)}</text>')


def arrow(d, color, x, y, angle, k, dashed=True, w=1.8):
    sw = round(w * k, 1)
    dash = f' stroke-dasharray="{round(6 * k)} {round(3.2 * k)}"' if dashed else ''
    s = round(k / 4.2, 2)
    return (path(d, color, sw, extra=f'{dash} stroke-linecap="round" stroke-linejoin="round"')
            + f'<path d="M-20 -16 L18 0 L-20 16 z" fill="{color}" '
              f'transform="translate({f(x)} {f(y)}) rotate({angle}) scale({s})"></path>')


def marker(n, x, y, k, fill=ACC):
    r = round(9 * k)
    return circle(x, y, r, fill, '#FFFFFF', round(1.2 * k, 1)) + label(x, y + round(3.4 * k), str(n), 10, k, '#FFFFFF', halo=None)


def svg(view, w, h, aria, body):
    vb = ' '.join(f(v) for v in view)
    return (f'<svg viewBox="{vb}" role="img" aria-label="{escape(aria)}" '
            f'style="width: {w}px; height: {h}px; display: block; flex: none">\n{body}\n</svg>')


def Y(z):
    return -z


def m2(w, h):
    return round(w * h / 10000)


# ---------- classical elements (elevation, cm) ----------

def rustication(x1, x2, z1, z2, course=45):
    o = [rect(x1, Y(z2), x2 - x1, z2 - z1, RUSTIC)]
    z = z1 + course
    while z < z2 - 5:
        o.append(path(f'M{f(x1)} {f(Y(z))} H{f(x2)}', JOINT, 4))
        z += course
    return o


def balustrade(x1, x2, z0, h=100, pitch=24, piers=()):
    o = [rect(x1, Y(z0 + 16), x2 - x1, 16, TRIM, LINE, 2)]
    n = int((x2 - x1) // pitch)
    start = x1 + ((x2 - x1) - n * pitch) / 2 + pitch / 2
    for i in range(n):
        cx = start + i * pitch
        if any(abs(cx - p) < 30 for p in piers):
            continue
        o.append(rect(cx - 3.5, Y(z0 + h - 16), 7, h - 32, TRIM, LINE, 1.2))
        o.append(ellipse(cx, Y(z0 + 16 + (h - 32) * 0.32), 7.5, (h - 32) * 0.26, TRIM, LINE, 1.2))
    o.append(rect(x1, Y(z0 + h), x2 - x1, 16, TRIM, LINE, 2))
    for p in piers:
        o.append(rect(p - 22, Y(z0 + h), 44, h, TRIM, LINE, 2))
    return o


def urn(cx, z0, s=1.0):
    return [rect(cx - 16 * s, Y(z0 + 14 * s), 32 * s, 14 * s, TRIM, LINE, 1.5),
            rect(cx - 7 * s, Y(z0 + 26 * s), 14 * s, 12 * s, TRIM, LINE, 1.5),
            ellipse(cx, Y(z0 + 48 * s), 22 * s, 22 * s, TRIM, LINE, 1.5),
            rect(cx - 18 * s, Y(z0 + 72 * s), 36 * s, 6 * s, TRIM, LINE, 1.5),
            ellipse(cx, Y(z0 + 82 * s), 8 * s, 10 * s, TRIM, LINE, 1.5)]


def column(cx, z0, z1, d, order='corinthian', flutes=True):
    """Column from z0 (bottom of base) to z1 (top of capital); d = lower diameter."""
    o = []
    bh = 0.5 * d
    caph = {'tuscan': 0.5 * d, 'ionic': 0.55 * d, 'corinthian': 1.1 * d}[order]
    o.append(rect(cx - 0.68 * d, Y(z0 + 0.22 * d), 1.36 * d, 0.22 * d, TRIM, LINE, 2))
    o.append(rect(cx - 0.6 * d, Y(z0 + 0.38 * d), 1.2 * d, 0.16 * d, TRIM, LINE, 2))
    o.append(rect(cx - 0.54 * d, Y(z0 + bh), 1.08 * d, 0.12 * d, TRIM, LINE, 1.5))
    sb, st = z0 + bh, z1 - caph
    top = 0.42 * d
    o.append(path(f'M{f(cx - d / 2)} {f(Y(sb))} L{f(cx - top)} {f(Y(st))} H{f(cx + top)} L{f(cx + d / 2)} {f(Y(sb))} Z',
                  LINE, 2, TRIM))
    if flutes and order != 'tuscan':
        for fx in (-0.25, 0, 0.25):
            o.append(path(f'M{f(cx + fx * d)} {f(Y(sb + 0.2 * d))} L{f(cx + fx * d * 0.85)} {f(Y(st - 0.2 * d))}', JOINT, 2))
    if order == 'tuscan':
        o += [rect(cx - 0.5 * d, Y(st + 0.12 * d), d, 0.12 * d, TRIM, LINE, 1.5),
              path(f'M{f(cx - 0.5 * d)} {f(Y(st + 0.12 * d))} L{f(cx - 0.62 * d)} {f(Y(st + 0.3 * d))} '
                   f'H{f(cx + 0.62 * d)} L{f(cx + 0.5 * d)} {f(Y(st + 0.12 * d))} Z', LINE, 1.5, TRIM),
              rect(cx - 0.66 * d, Y(z1), 1.32 * d, 0.2 * d, TRIM, LINE, 2)]
    elif order == 'ionic':
        o += [rect(cx - 0.55 * d, Y(st + 0.2 * d), 1.1 * d, 0.2 * d, TRIM, LINE, 1.5)]
        for sx in (-1, 1):
            vx = cx + sx * 0.55 * d
            o += [circle(vx, Y(st + 0.25 * d), 0.2 * d, TRIM, LINE, 1.5), circle(vx, Y(st + 0.25 * d), 0.07 * d, LINE)]
        o.append(rect(cx - 0.7 * d, Y(z1), 1.4 * d, 0.12 * d, TRIM, LINE, 2))
    else:  # corinthian
        bell_top = z1 - 0.16 * d
        o.append(path(f'M{f(cx - 0.44 * d)} {f(Y(st))} L{f(cx - 0.62 * d)} {f(Y(bell_top))} '
                      f'H{f(cx + 0.62 * d)} L{f(cx + 0.44 * d)} {f(Y(st))} Z', LINE, 1.5, TRIM))
        for row, (zf, span) in enumerate(((0.36, 0.48), (0.7, 0.56))):
            zl = st + zf * (bell_top - st)
            for i in range(-1, 2):
                lx = cx + i * span * d * 0.75
                w = 0.26 * d
                o.append(path(f'M{f(lx - w)} {f(Y(zl - 0.3 * d))} Q{f(lx - w)} {f(Y(zl))} {f(lx)} {f(Y(zl + 0.08 * d))} '
                              f'Q{f(lx + w)} {f(Y(zl))} {f(lx + w)} {f(Y(zl - 0.3 * d))}', LINE, 1.5))
        for sx in (-1, 1):
            o.append(circle(cx + sx * 0.6 * d, Y(bell_top - 0.08 * d), 0.08 * d, TRIM, LINE, 1.5))
        o.append(path(f'M{f(cx - 0.72 * d)} {f(Y(z1))} Q{f(cx)} {f(Y(z1 - 0.08 * d))} {f(cx + 0.72 * d)} {f(Y(z1))} '
                      f'V{f(Y(bell_top))} H{f(cx - 0.72 * d)} Z', LINE, 1.5, TRIM))
        o.append(circle(cx, Y(bell_top - 0.05 * d), 0.07 * d, TRIM, LINE, 1.2))
    return o


def pilaster(cx, z0, z1, w):
    return [rect(cx - w / 2 - 8, Y(z0 + 30), w + 16, 30, TRIM, LINE, 2),
            rect(cx - w / 2, Y(z1 - 60), w, (z1 - 60) - (z0 + 30), TRIM, LINE, 2),
            path(f'M{f(cx - w / 4)} {f(Y(z0 + 50))} V{f(Y(z1 - 80))} M{f(cx + w / 4)} {f(Y(z0 + 50))} V{f(Y(z1 - 80))}', JOINT, 2),
            rect(cx - w / 2 - 6, Y(z1 - 20), w + 12, 40, TRIM, LINE, 2),
            path(f'M{f(cx - w / 2)} {f(Y(z1 - 40))} q{f(w / 4)} -12 {f(w / 2)} 0 q{f(w / 4)} 12 {f(w / 2)} 0', LINE, 1.5),
            rect(cx - w / 2 - 12, Y(z1), w + 24, 20, TRIM, LINE, 2)]


def entablature(x1, x2, z0, proj=28, dentils=True):
    """Architrave 30, frieze 40, cornice 50: z0..z0+120."""
    o = [rect(x1, Y(z0 + 30), x2 - x1, 30, TRIM, LINE, 2),
         path(f'M{f(x1)} {f(Y(z0 + 12))} H{f(x2)}', JOINT, 2),
         rect(x1, Y(z0 + 70), x2 - x1, 40, WALL, LINE, 2),
         rect(x1 - 8, Y(z0 + 80), x2 - x1 + 16, 10, TRIM, LINE, 2),
         rect(x1 - proj, Y(z0 + 110), x2 - x1 + 2 * proj, 30, TRIM, LINE, 2.5),
         rect(x1 - proj - 6, Y(z0 + 120), x2 - x1 + 2 * proj + 12, 10, TRIM, LINE, 2)]
    if dentils:
        x = x1 - 4
        while x < x2:
            o.append(rect(x, Y(z0 + 88), 8, 8, TRIM, LINE, 1))
            x += 16
    return o


def pediment(x1, x2, z0, pitch=0.25, oculus=True):
    xm, half = (x1 + x2) / 2, (x2 - x1) / 2
    H = half * pitch
    o = [path(f'M{f(x1)} {f(Y(z0))} L{f(xm)} {f(Y(z0 + H))} L{f(x2)} {f(Y(z0))} Z', LINE, 2.5, TRIM)]
    i = 40
    o.append(path(f'M{f(x1 + i / pitch * 0.9)} {f(Y(z0 + 8))} L{f(xm)} {f(Y(z0 + H - i))} '
                  f'L{f(x2 - i / pitch * 0.9)} {f(Y(z0 + 8))} Z', LINE, 2, WALL))
    if oculus:
        o += [circle(xm, Y(z0 + H * 0.4), H * 0.22, TRIM, LINE, 2), circle(xm, Y(z0 + H * 0.4), H * 0.15, GLASS, LINE, 2)]
        for sx in (-1, 1):
            o.append(path(f'M{f(xm + sx * H * 0.25)} {f(Y(z0 + H * 0.4))} q{f(sx * H * 0.5)} {f(H * 0.25)} '
                          f'{f(sx * H * 1.1)} {f(-H * 0.05)}', LINE, 2))
    return o, z0 + H


def window(cx, z0, w, h, kind='rect', frame=14, ped=None, balcony=False, panes=4, door=False, keystone=False):
    o = []
    x1, x2 = cx - w / 2, cx + w / 2
    if kind == 'arch':
        r = w / 2
        zs = z0 + h - r
        fr = r + frame
        o.append(path(f'M{f(x1 - frame)} {f(Y(z0))} V{f(Y(zs))} A{f(fr)} {f(fr)} 0 0 1 {f(x2 + frame)} {f(Y(zs))} '
                      f'V{f(Y(z0))} Z', LINE, 2, TRIM))
        o.append(path(f'M{f(x1)} {f(Y(z0))} V{f(Y(zs))} A{f(r)} {f(r)} 0 0 1 {f(x2)} {f(Y(zs))} V{f(Y(z0))} Z',
                      LINE, 2, WOOD if door else GLASS))
        if not door:
            o.append(path(f'M{f(cx)} {f(Y(z0))} V{f(Y(z0 + h))} ' + ' '.join(
                f'M{f(x1)} {f(Y(z0 + (zs - z0) * t / panes))} H{f(x2)}' for t in range(1, panes)), TRIM, 3))
            o.append(path(f'M{f(x1)} {f(Y(zs))} H{f(x2)}', TRIM, 3))
        else:
            o.append(path(f'M{f(cx)} {f(Y(z0))} V{f(Y(zs))}', LINE, 2))
            o += [rect(x1 + 15, Y(z0 + (zs - z0) * 0.9), w / 2 - 30, (zs - z0) * 0.35, 'none', LINE, 1.5),
                  rect(cx + 15, Y(z0 + (zs - z0) * 0.9), w / 2 - 30, (zs - z0) * 0.35, 'none', LINE, 1.5),
                  rect(x1 + 15, Y(z0 + (zs - z0) * 0.45), w / 2 - 30, (zs - z0) * 0.35, 'none', LINE, 1.5),
                  rect(cx + 15, Y(z0 + (zs - z0) * 0.45), w / 2 - 30, (zs - z0) * 0.35, 'none', LINE, 1.5)]
        if keystone:
            o.append(path(f'M{f(cx - 12)} {f(Y(z0 + h + frame + 6))} L{f(cx - 8)} {f(Y(z0 + h - 6))} '
                          f'H{f(cx + 8)} L{f(cx + 12)} {f(Y(z0 + h + frame + 6))} Z', LINE, 1.5, TRIM))
    else:
        o.append(rect(x1 - frame, Y(z0 + h + frame), w + 2 * frame, h + frame, TRIM, LINE, 2))
        o.append(rect(x1, Y(z0 + h), w, h, GLASS, LINE, 2))
        o.append(path(f'M{f(cx)} {f(Y(z0))} V{f(Y(z0 + h))} ' + ' '.join(
            f'M{f(x1)} {f(Y(z0 + h * t / panes))} H{f(x2)}' for t in range(1, panes)), TRIM, 3))
        if ped:
            cz = z0 + h + frame
            o += [rect(x1 - frame - 8, Y(cz + 16), 10, 16, TRIM, LINE, 1.5), rect(x2 + frame - 2, Y(cz + 16), 10, 16, TRIM, LINE, 1.5),
                  rect(x1 - frame - 14, Y(cz + 28), w + 2 * frame + 28, 12, TRIM, LINE, 2)]
            if ped == 'tri':
                o.append(path(f'M{f(x1 - frame - 14)} {f(Y(cz + 28))} L{f(cx)} {f(Y(cz + 28 + (w / 2 + frame + 14) * 0.32))} '
                              f'L{f(x2 + frame + 14)} {f(Y(cz + 28))} Z', LINE, 2, TRIM))
            elif ped == 'seg':
                rr = (w / 2 + frame + 14)
                o.append(path(f'M{f(x1 - frame - 14)} {f(Y(cz + 28))} A{f(rr * 1.6)} {f(rr * 1.6)} 0 0 1 {f(x2 + frame + 14)} '
                              f'{f(Y(cz + 28))} Z', LINE, 2, TRIM))
            elif ped == 'flat':
                pass
    o.append(rect(x1 - frame - 10, Y(z0), w + 2 * frame + 20, 12, TRIM, LINE, 2))
    if balcony:
        bw = w + 2 * frame + 40
        o += [rect(cx - bw / 2 - 6, Y(z0 - 2), bw + 12, 14, TRIM, LINE, 2)]
        o += [rect(cx + sx * (bw / 2 - 20) - 8, Y(z0 - 16), 16, 22, TRIM, LINE, 1.5) for sx in (-1, 1)]
        o += balustrade(cx - bw / 2, cx + bw / 2, z0, 80, 20)
    return o


def lantern(cx, z0):
    """Octagonal drum (seen flat) with three arched lights, copper dome; dome top at z0 + 290."""
    o = [rect(cx - 125, Y(z0 + 195), 250, 195, WALL, LINE, 2.5)]
    for dx in (-72, 0, 72):
        o += window(cx + dx, z0 + 40, 36, 115, 'arch', 8, panes=2)
    o += [rect(cx - 125, Y(z0 + 195), 16, 195, TRIM, LINE, 1.5), rect(cx + 109, Y(z0 + 195), 16, 195, TRIM, LINE, 1.5),
          rect(cx - 138, Y(z0 + 215), 276, 20, TRIM, LINE, 2)]
    o.append(path(f'M{f(cx - 130)} {f(Y(z0 + 215))} A130 75 0 0 1 {f(cx + 130)} {f(Y(z0 + 215))} Z', LINE, 2.5, COPPER))
    for dx in (-75, 0, 75):
        o.append(path(f'M{f(cx + dx * 0.95)} {f(Y(z0 + 215))} Q{f(cx + dx * 0.55)} {f(Y(z0 + 270))} {f(cx)} {f(Y(z0 + 290))}', LINE, 1.5))
    o += [circle(cx, Y(z0 + 300), 10, COPPER, LINE, 1.5), path(f'M{f(cx)} {f(Y(z0 + 310))} V{f(Y(z0 + 345))}', LINE, 4)]
    return o


def chimney(cx, z0, z1):
    return [rect(cx - 35, Y(z1), 70, z1 - z0, WALL, LINE, 2), rect(cx - 45, Y(z1 + 14), 90, 14, TRIM, LINE, 2),
            path(f'M{f(cx - 35)} {f(Y(z1 - 25))} H{f(cx + 35)}', JOINT, 2)]


# ---------- the facade (both fronts share the upper body) ----------

def upper_body(front=True):
    """Everything from the band course (+5.40) up: giant order, windows, entablature, balustrade,
    pediment, roof furniture. Front uses engaged columns, the sea side flat pilasters."""
    o = []
    o += [rect(X0, Y(1380), X1 - X0, 1380 - 590, WALL, LINE, 3)]
    o += [rect(X0 - 10, Y(590), X1 - X0 + 20, 50, TRIM, LINE, 2.5), path(f'M{X0 - 10} {Y(565)} H{X1 + 10}', JOINT, 2)]
    o += [rect(C0, Y(1380), C1 - C0, 790, '#F3EDDF', LINE, 2)]                # avant-corps
    for i, cx in enumerate(BAYS):
        central = C0 < cx < C1
        ped = 'tri' if cx == AXIS else ('seg' if central else ('seg' if i in (0, 6) else 'tri'))
        o += window(cx, 660, 130, 290, ped=ped, balcony=not central or not front, panes=4)
        o += window(cx, 1090, 130, 190, panes=3)
    for px in (X0 + 40, X1 - 40):
        o += pilaster(px, 590, 1380, 80)
    for cx in COLS:
        o += column(cx, 590, 1380, 80, 'corinthian') if front else pilaster(cx, 590, 1380, 70)
    o += entablature(X0 - 10, X1 + 10, 1380)
    o += [label(AXIS, Y(1428), 'MDCCCXXVI' if False else '', 1, 1, halo=None)]
    piers = (X0 + 22, 300, C0 - 40, C1 + 40, 1520, X1 - 22)
    o += balustrade(X0, C0 - 40, 1500, 100, 24, piers=(X0 + 22, 245, C0 - 62))
    o += balustrade(C1 + 40, X1, 1500, 100, 24, piers=(C1 + 62, 1575, X1 - 22))
    for p in (X0 + 22, 245, C1 + 62 - 0, 1575, X1 - 22, C0 - 62):
        o += urn(p, 1600, 1.0)
    ped, apex = pediment(C0 - 40, C1 + 40, 1500, 0.24)
    o += ped
    o += urn(AXIS, apex - 4, 1.1) + urn(C0 - 30, 1500, 0.9) + urn(C1 + 30, 1500, 0.9)
    return o


def roof_furniture():
    o = []
    o += chimney(150, 1500, 1790) + chimney(1670, 1500, 1790)
    o += lantern(AXIS, 1600)
    return o


def front_facade():
    o = []
    o += roof_furniture()
    o += rustication(X0, X1, 90, 590)
    o += [rect(X0 - 15, Y(90), X1 - X0 + 30, 90, RUSTIC, LINE, 2), path(f'M{X0 - 15} {Y(60)} H{X1 + 15}', JOINT, 3)]
    o += [rect(X0, Y(590), X1 - X0, 500, 'none', LINE, 3)]
    for cx in BAYS:
        if cx == AXIS:
            o += window(cx, 90, 180, 400, 'arch', 18, door=True, keystone=True)
        else:
            o += window(cx, 170, 120, 300, 'arch', 16, panes=3, keystone=True)
    o += upper_body(front=True)
    # porch: four Tuscan columns carrying the balcony of the piano nobile
    o += [rect(C0 - 10, Y(560), C1 - C0 + 20, 90, TRIM, LINE, 2.5), path(f'M{C0 - 10} {Y(530)} H{C1 + 10}', JOINT, 2)]
    for cx in COLS:
        o += column(cx, 90, 470, 50, 'tuscan')
    o += balustrade(C0 - 10, C1 + 10, 560, 95, 22, piers=(C0 + 12, AXIS - 140, AXIS + 140, C1 - 12))
    # perron
    for i in range(5):
        w = (C1 - C0) + 100 + i * 40
        o.append(rect(AXIS - w / 2, Y(90 - i * 18), w, 18, TRIM, LINE, 1.5))
    # area railings in front of the side bays (light wells to the lower floor)
    for a, b in ((X0, C0 - 50), (C1 + 50, X1)):
        o.append(path(f'M{a} {Y(100)} H{b} M{a} {Y(10)} H{b} ' + ' '.join(f'M{x} {Y(10)} V{Y(100)}' for x in range(a + 10, b, 18)),
                      IRON, 2.5))
    o.append(path(f'M-1100 0 H1960', LINE, 5))
    return o


def sea_facade():
    o = []
    o += roof_furniture()
    o += rustication(X0, X1, -250, 590)
    o += [rect(X0, Y(590), X1 - X0, 840, 'none', LINE, 3)]
    # lower floor: three-arched grotto under the terrace
    for cx in (676, AXIS, 1143):
        o += window(cx, -250, 200, 300, 'arch', 22, door=False, panes=3, keystone=True)
    for cx in BAYS:
        if not C0 < cx < C1:
            o += window(cx, -170, 110, 150, 'rect', 12, panes=2)
    # piano nobile on the sea side is the ground floor: tall arched French doors
    for cx in BAYS:
        central = C0 < cx < C1
        o += window(cx, 110 if central else 170, 150 if central else 120, 380 if central else 300, 'arch', 16,
                    panes=4, keystone=True)
    o += [rect(C0 - 30, Y(90), C1 - C0 + 60, 26, TRIM, LINE, 2)]
    o += balustrade(C0 - 30, C1 + 30, 90, 100, 24, piers=(C0 - 8, AXIS - 120, AXIS + 120, C1 + 8))
    # horseshoe stair: two flights curving down to the garden
    for sx in (-1, 1):
        xa = C0 - 30 if sx < 0 else C1 + 30
        xb = xa + sx * 360
        o.append(path(f'M{xa} {Y(90)} Q{xa + sx * 120} {Y(90)} {xb} {Y(-250)} H{xb + sx * 60} '
                      f'Q{xa + sx * 200} {Y(116)} {xa} {Y(116)} Z', LINE, 2.5, TRIM))
        o.append(path(f'M{xa} {Y(190)} Q{xa + sx * 150} {Y(190)} {xb + sx * 50} {Y(-150)}', LINE, 3))
        o.append(rect(xb + sx * 30 - 25, Y(-150), 50, 100, TRIM, LINE, 2))
        o += urn(xb + sx * 30, -150, 0.8)
    o += upper_body(front=False)
    o.append(rect(670, Y(-250), 480, 8, WATER, WATER_LINE, 2))
    o.append(path('M-1100 250 H3000', GREEN_LINE, 6))
    return o


def old_house(fill=OLD):
    """Old house front, simplified (from the CHỐT elevation), x −1038..−320."""
    o = [rect(-1038, -1500, 718, 1500, fill, LINE, 5), rect(-700, -1640, 360, 140, fill, LINE, 5),
         path('M-690 -1640 A170 180 0 0 1 -350 -1640 Z', LINE, 5, '#D8CFB8'), path('M-520 -1820 V-1890', LINE, 6),
         path('M-1038 -560 h718 M-1038 -1030 h718', LINE, 3)]
    for x in (-928, -570):
        o += [rect(x, -900, 100, 240, GLASS, LINE, 3), rect(x, -1350, 100, 220, GLASS, LINE, 3)]
    o += [rect(-928, -430, 100, 250, GLASS, LINE, 3), path('M-600 0 V-380 A80 80 0 0 1 -440 -380 V0 Z', LINE, 3, WOOD)]
    return o


def level_marks(x, k, levels):
    o = []
    for z, t in levels:
        o += [path(f'M{x} {Y(z)} H{x + 70}', ACC, 4), label(x + 85, Y(z) + 3.4 * k, t, 9, k, ACC, 600, 'start', None)]
    return o


# ---------- plan helpers ----------

FLOOR_VIEW = (-420, -480, 2660, 3000)
LATE = []   # room labels, drawn after furniture so nothing covers them


def flush_late():
    out = list(LATE)
    LATE.clear()
    return out


def room(x, y, w, h, name, k, fill='#FFFFFF', px=9, area=True, rot=None, sub=None):
    cx, cy = x + w / 2, y + h / 2
    out = [rect(x, y, w, h, fill, INK, 18)]
    o = LATE
    if rot is None:
        dy = -0.25 * px * k if (area or sub) else 0.35 * px * k
        o.append(label(cx, cy + dy, name, px, k, INK, 600, 'middle', fill))
        extra = sub or (f'{m2(w, h)} m²' if area else None)
        if extra:
            o.append(label(cx, cy + dy + 1.25 * px * k, extra, px - 1.5, k, MUTED, 400, 'middle', fill))
    else:
        o.append(label(cx + 0.35 * px * k, cy, name + (f' · {m2(w, h)} m²' if area else ''), px, k, INK, 600, 'middle', fill, rot))
    return out


def gap(x, y, w, h):
    return rect(x, y, w, h, '#FFFFFF')


def windows_plan(skip=()):
    o = []
    for cx in BAYS:
        for wy in (Y0, Y1):
            if (cx, wy) in skip:
                continue
            o += [rect(cx - 65, wy - 20, 130, 40, '#FFFFFF', INK, 2), path(f'M{cx - 65} {wy} H{cx + 65}', INK, 2)]
    for wx in (X0, X1):
        for cy in (560, 900, 1300, 1750):
            if (wx, cy) in skip:
                continue
            o += [rect(wx - 20, cy - 60, 40, 120, '#FFFFFF', INK, 2), path(f'M{wx} {cy - 60} V{cy + 60}', INK, 2)]
    return o


def treads(x, y, w, h, n, vertical=True, color=INK):
    if vertical:
        return [rect(x, y, w, h, '#FFFFFF', color, 3), path(' '.join(f'M{x} {y + h * i / n:.0f} H{x + w}' for i in range(1, n)), color, 2)]
    return [rect(x, y, w, h, '#FFFFFF', color, 3), path(' '.join(f'M{x + w * i / n:.0f} {y} V{y + h}' for i in range(1, n)), color, 2)]


def checker(x, y, w, h, s=50):
    o = [rect(x, y, w, h, '#F4F1EA')]
    for i in range(int(w // s)):
        for j in range(int(h // s)):
            if (i + j) % 2 == 0:
                o.append(rect(x + i * s, y + j * s, s, s, '#D9D3C4'))
    return o


def fireplace(x, y, horizontal=True):
    if horizontal:
        return [rect(x - 90, y, 180, 35, TRIM, INK, 3), rect(x - 50, y + 5, 100, 22, '#8E8676')]
    return [rect(x, y - 90, 35, 180, TRIM, INK, 3), rect(x + 5, y - 50, 22, 100, '#8E8676')]


def outline():
    return [rect(X0, Y0, X1 - X0, Y1 - Y0, 'none', INK, 40)]


def compass(k, x=2050, y=-380):
    return [path(f'M{x - 140} {y} H{x + 60}', INK, 6), path(f'M{x - 140} {y} l40 -18 v36 z', INK, 0, INK),
            label(x + 100, y + 14, 'B', 10, k, INK, 600, 'middle', None),
            label(x - 40, y - 60, 'BIỂN ↑', 9, k, ACC, 600, 'middle', None)]


def scalebar(k, x=-380, y=2440):
    return [path(f'M{x} {y} h500 M{x} {y - 12} v24 M{x + 500} {y - 12} v24 ' + ' '.join(f'M{x + 100 * i} {y - 6} v12' for i in range(1, 5)), INK, 3),
            label(x, y - 24, '0', 8, k, INK, 400, 'middle', None), label(x + 500, y - 24, '5 m', 8, k, INK, 400, 'middle', None)]



# ---------- La Rotonda: round hall with two curved stairs ----------

RX, RY, R_OUT, R_IN = AXIS, 1350, 370, 250       # centre, wall radius, inner edge of the stairs
CELL = (C0, 950, C1 - C0, 800)                   # the square cell the round hall sits in
FLIGHTS = ((65, -75), (115, 255))                # start and end angle of each flight (degrees, y down)


def _pt(r, a):
    return RX + r * math.cos(math.radians(a)), RY + r * math.sin(math.radians(a))


def rotunda_cell(fill='#FFFFFF'):
    """Poché of the square cell with the round hall cut out of it."""
    return [rect(*CELL, INK), circle(RX, RY, R_OUT, fill)]


def curved_stairs(k, seen=False, n=26):
    c = OLD_LINE if seen else INK
    o = []
    for a0, a1 in FLIGHTS:
        sweep = 1 if a1 > a0 else 0
        (x0, y0), (x1, y1) = _pt(R_OUT, a0), _pt(R_OUT, a1)
        (x2, y2), (x3, y3) = _pt(R_IN, a1), _pt(R_IN, a0)
        d = (f'M{x0:.1f} {y0:.1f} A{R_OUT} {R_OUT} 0 0 {sweep} {x1:.1f} {y1:.1f} L{x2:.1f} {y2:.1f} '
             f'A{R_IN} {R_IN} 0 0 {1 - sweep} {x3:.1f} {y3:.1f} Z')
        o.append(path(d, c, 3, '#FFFFFF' if not seen else 'none'))
        treads_ = []
        for i in range(1, n):
            a = a0 + (a1 - a0) * i / n
            (xa, ya), (xb, yb) = _pt(R_IN, a), _pt(R_OUT, a)
            treads_.append(f'M{xa:.1f} {ya:.1f} L{xb:.1f} {yb:.1f}')
        o.append(path(' '.join(treads_), c, 1.8))
        if not seen:
            rm = (R_IN + R_OUT) / 2
            pts = [_pt(rm, a0 + (a1 - a0) * t / 12) for t in range(1, 12)]
            dd = 'M' + ' L'.join(f'{x:.1f} {y:.1f}' for x, y in pts)
            (xe, ye), (xp, yp) = pts[-1], pts[-2]
            ang = math.degrees(math.atan2(ye - yp, xe - xp))
            o.append(arrow(dd, INK, xe, ye, round(ang), k, dashed=False, w=1))
    return o


def rotunda_landing(level):
    """Upper floors: arrival landing on the sea side (and a ring gallery on tầng 3)."""
    o = []
    if level == 2:
        (x0, y0), (x1, y1) = _pt(R_OUT, -105), _pt(R_OUT, -75)
        (x2, y2), (x3, y3) = _pt(R_IN, -75), _pt(R_IN, -105)
        o.append(path(f'M{x0:.1f} {y0:.1f} A{R_OUT} {R_OUT} 0 0 1 {x1:.1f} {y1:.1f} L{x2:.1f} {y2:.1f} '
                      f'A{R_IN} {R_IN} 0 0 0 {x3:.1f} {y3:.1f} Z', INK, 3, TRIM))
    else:
        o.append(circle(RX, RY, (R_IN + R_OUT) / 2, 'none', '#FFFFFF', R_OUT - R_IN))
    o.append(circle(RX, RY, R_IN, 'none', IRON, 6))
    return o


# ---------- HTML helpers ----------

def row(name, value, text):
    return ('<div style="display: flex; flex-direction: column; gap: 3px; padding: 8px 0; border-top: 1px solid #C5CAC5">\n'
            '<div style="display: flex; justify-content: space-between; gap: 12px; font-size: 14px; font-weight: 600">'
            f'<span>{escape(name)}</span><span style="flex: none">{escape(value)}</span></div>\n'
            f'<div style="font-size: 12.5px; line-height: 1.5; color: #4A5868">{escape(text)}</div>\n</div>')


def callouts(items):
    return '\n'.join(
        '<div style="display: flex; gap: 10px; padding: 8px 0; border-top: 1px solid #C5CAC5">'
        f'<span style="flex: none; width: 22px; height: 22px; border-radius: 50%; background: #7A5620; color: #FFFFFF; '
        f'font-size: 12px; font-weight: 600; display: flex; align-items: center; justify-content: center">{n}</span>'
        f'<div style="display: flex; flex-direction: column; gap: 2px"><span style="font-size: 14px; font-weight: 600">{escape(a)}</span>'
        f'<span style="font-size: 12.5px; line-height: 1.5; color: #4A5868">{escape(b)}</span></div></div>'
        for n, a, b in items)


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


def side_title(text):
    return ("<div style=\"font-family: 'Cormorant Garamond', serif; font-weight: 600; font-size: 28px; line-height: 1.15; "
            f'padding-bottom: 8px; border-bottom: 2px solid #15263B">{escape(text)}</div>')


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


def two_col(left_html, right_html, left_w):
    return (f'<div style="display: flex; gap: 32px">\n<div style="width: {left_w}px; flex: none; display: flex; '
            f'flex-direction: column; gap: 6px">\n{left_html}\n</div>\n<div style="flex: 1; min-width: 0; display: flex; '
            f'flex-direction: column; gap: 12px">\n{right_html}\n</div>\n</div>')


# ---------- DT5 · Mặt đứng chính ----------

FRONT_VIEW = (-1100, -2000, 3400, 2160)


def front_drawing(w, h, marks=True):
    k = FRONT_VIEW[2] / w
    o = old_and_link()
    o += front_facade()
    if marks:
        o += level_marks(1980, k, ((0, '±0.00 sân'), (90, '+0.90'), (560, '+5.60'), (1030, '+10.30'), (1500, '+15.00'),
                                   (1890, '+18.90 lồng đèn')))
        o += [path('M-1038 1240 V1300 M-320 1240 V1300 M-40 1240 V1300 M1860 1240 V1300', LINE, 2)]
        for n, x, z in ((1, AXIS, 1555), (2, 793, 1060), (3, 120, 1440), (4, 245, 1660), (5, 372, 1010),
                        (6, 97, 330), (7, AXIS, 520), (8, AXIS, 1960), (9, -680, 1720)):
            o.append(marker(n, x + (0 if n in (1, 7, 8) else 0), Y(z), k))
        o += [label(-679, 70 + 10 * k, 'nhà cũ ốp lại · mặt lùi 7,5 m', 9, k, MUTED, 400, 'middle', None),
              label(910, 70 + 10 * k, 'mặt tiền 19 m · bảy nhịp', 10, k, INK, 600, 'middle', None)]
    return svg(FRONT_VIEW, w, h,
               'Mặt đứng chính dinh thự nhìn từ đường: nền đá rusticated tầng 1 với cửa vòm, porch bốn cột Tuscan đỡ ban '
               'công; tầng 2 và 3 gom bằng bốn cột Corinth khổng lồ ở ba nhịp giữa và trụ áp ở hai góc; cửa sổ tầng 2 '
               'có trán tam giác và trán cung xen kẽ; entablature có răng cưa; lan can con tiện với bình đá; trán tường '
               'tam giác có cửa sổ tròn; phía sau là lồng đèn mái vòm đồng và hai ống khói; bên trái là nhà cũ có tháp vòm',
               '\n'.join(o))


def detail_row():
    """Three enlarged details under the front elevation."""
    a = [rect(-170, Y(1520), 340, 340, WALL)] + column(0, 590, 1380, 80, 'corinthian') + entablature(-170, 170, 1380, proj=28)
    a = svg((-170, -1525, 340, 345), 190, 193, 'Chi tiết đầu cột Corinth và entablature: lá ô-rô hai tầng, '
            'cuộn góc, đầu cột cong, dầm đầu cột hai lớp, diềm và phào răng cưa', '\n'.join(a))
    b = [rect(-140, Y(1080), 610, 520, WALL)] + window(0, 660, 130, 290, ped='tri', balcony=True) \
        + window(330, 660, 130, 290, ped='seg', balcony=True)
    b = svg((-150, -1090, 630, 560), 214, 190, 'Chi tiết hai cửa sổ tầng 2: khung đá, ô kính nhỏ, trán tam giác '
            'và trán cung trên công-xôn, ban công lan can nhỏ', '\n'.join(b))
    c = [rect(-40, Y(1720), 500, 340, WALL)] + entablature(-40, 460, 1380, proj=20) \
        + balustrade(0, 420, 1500, 100, 24, piers=(22, 398)) + urn(22, 1600) + urn(398, 1600)
    c = svg((-40, -1720, 500, 360), 264, 190, 'Chi tiết lan can con tiện trên phào mái, trụ đá và bình đá', '\n'.join(c))
    cell = lambda cap, s: ('<div style="display: flex; flex-direction: column; gap: 6px; align-items: flex-start">'
                           + caption(cap) + s + '</div>')
    return ('<div style="display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 16px; margin-top: 6px">'
            + cell('CHI TIẾT · ĐẦU CỘT CORINTH', a) + cell('CHI TIẾT · CỬA SỔ TẦNG 2', b)
            + cell('CHI TIẾT · LAN CAN VÀ BÌNH ĐÁ', c) + '</div>')


def dt5():
    draw = front_drawing(1040, 661)
    items = [
        (1, 'Trán tường tam giác', 'Phủ ba nhịp giữa, dốc khoảng 13°, cửa sổ tròn và vòng hoa đá; bình đá ở đỉnh và hai đầu.'),
        (2, 'Thức Corinth khổng lồ', 'Bốn cột áp tường Ø 80 cm cao gần 8 m, gom tầng 2 và tầng 3 làm một, tỷ lệ 1 : 10.'),
        (3, 'Entablature', 'Cao 1,2 m: dầm đầu cột hai lớp, diềm trơn, phào răng cưa; chạy liền quanh cả bốn mặt.'),
        (4, 'Lan can con tiện', 'Che mái bằng phía sau; trụ ở mỗi trục cột, bình đá trên trụ.'),
        (5, 'Cửa sổ tầng 2', 'Cao 2,9 m, trán tam giác và trán cung xen kẽ, ban công lan can nhỏ.'),
        (6, 'Nền rusticated', 'Tầng 1 bằng đá xẻ rãnh ngang mỗi 45 cm; cửa vòm có đá khóa.'),
        (7, 'Porch bốn cột', 'Cột Tuscan đỡ ban công phòng học tầng 2; năm bậc từ sân lên +0.90.'),
        (8, 'Lồng đèn', 'Vòm đồng trên La Rotonda, đỉnh +18.90, cùng cao độ chóp vòm nhà cũ.'),
        (9, 'Nhà cũ nối liền', 'Cùng cốt sàn +0.90, cùng 5 bậc từ sân; ốp lại cùng nền đá, phào, lan can +15.00. Xem DT8.'),
    ]
    right = side_title('Đọc mặt đứng') + '\n' + callouts(items)
    left = (caption('MẶT ĐỨNG CHÍNH · NHÌN TỪ ĐƯỜNG ĐT639 · KHÔNG VẼ HAI NHÀ CỔNG ĐỂ THẤY RÕ MẶT NHÀ') + '\n' + draw
            + '\n' + detail_row())
    return header('DT5', 'Mặt đứng chính', 'Hướng tây · nền đá, thức khổng lồ, trán tường') + '\n' + two_col(left, right, 1040)


# ---------- DT6 · Mặt đứng biển ----------

SEA_VIEW = (-600, -2010, 3800, 2330)


def dt6():
    w, h = 1200, 736
    k = SEA_VIEW[2] / w
    o = ['<g transform="translate(1820 0) scale(-1 1)">'] + old_and_link(sea=True) + ['</g>']
    o += sea_facade()
    o += level_marks(2960, k, ((-250, '−2.50 vườn'), (90, '+0.90'), (560, '+5.60'), (1030, '+10.30'), (1500, '+15.00'),
                               (1890, '+18.90')))
    for n, x, z in ((1, AXIS, -90), (2, 330, -60), (3, AXIS, 140), (4, 1143, 330), (5, 1260, 1000), (6, AXIS, 1555)):
        o.append(marker(n, x, Y(z), k))
    o += [label(2499, 300, 'nhà cũ', 9, k, MUTED, 400, 'middle', None)]
    draw = svg(SEA_VIEW, w, h,
               'Mặt đứng phía biển: tầng dưới cốt −2.50 là nền đá với ba vòm mở vào hang hồ bơi; trên đó sân thượng có lan '
               'can và hai vế thang móng ngựa xuống vườn; tầng 1 có cửa vòm cao của Grand Salon; tầng 2 và 3 có trụ áp '
               'Corinth khổng lồ; trán tường tam giác và lồng đèn như mặt chính; nhà cũ ở bên phải', '\n'.join(o))
    items = [
        (1, 'Hang vòm hồ bơi', 'Đất dốc 2,5 m nên tầng dưới lộ hẳn ra: ba vòm đá mở vào ninfeo, hồ bơi chạy từ vườn vào dưới Grand Salon.'),
        (2, 'Thang móng ngựa', 'Hai vế cong ôm lấy ba vòm, từ sân thượng +0.90 xuống vườn −2.50; trụ và bình đá ở chân thang.'),
        (3, 'Sân thượng', 'Rộng 8 m, sâu 3 m, lan can con tiện; nối Grand Salon với vườn.'),
        (4, 'Cửa vòm Grand Salon', 'Ba cửa vòm cao 3,8 m mở ra sân thượng; hai bên là thư viện và phòng ăn.'),
        (5, 'Trụ áp thay cột', 'Mặt sau dùng trụ áp phẳng cùng thức Corinth: phẳng hơn mặt chính, đúng thứ bậc cổ điển.'),
        (6, 'Cùng đường mái', 'Entablature, lan can, trán tường giống mặt chính; từ biển nhìn vào vẫn là một dinh thự.'),
    ]
    half = (len(items) + 2) // 3
    cols = ''.join('<div style="display: flex; flex-direction: column">' + callouts(items[i:i + 2]) + '</div>'
                   for i in range(0, len(items), 2))
    grid = f'<div style="display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 0 28px">{cols}</div>'
    body = ('<div style="display: flex; flex-direction: column; gap: 6px; align-items: center">\n'
            '<div style="align-self: flex-start">' + caption('MẶT ĐỨNG PHÍA BIỂN · NHÌN TỪ VƯỜN SAU · NHÀ CŨ BÊN PHẢI') + '</div>\n'
            + draw + '\n</div>\n' + grid)
    return header('DT6', 'Mặt đứng phía biển', 'Hướng đông · hang vòm, thang móng ngựa, sân thượng') + '\n' + body


# ---------- DT7 · Mặt cắt ----------

SECT_VIEW = (-500, -2000, 3500, 2480)


def dt7():
    w, h = 1066, 755
    k = SECT_VIEW[2] / w
    o = [rect(-500, 250, 3500, 240, EARTH), rect(2460, 0, 540, 250, EARTH), rect(2280, 90, 180, 160, EARTH),
         path('M-500 250 H0', GREEN_LINE, 8), path('M2400 0 H3000', LINE, 5),
         rect(-410, Y(-150), 20, 100, TRIM, LINE, 2)]
    # interiors: lower floor runs out to the arcade at s 0, upper floors stop at the sea wall s 300
    o += [rect(0, Y(90), 2250, 340, '#FFFFFF'), rect(300, Y(1500), 1700, 1410, '#FFFFFF')]
    o += [rect(-300, 260, 1150, 140, WATER, WATER_LINE, 3)]
    # balustrade along the side facade, seen beyond the cut
    o += balustrade(300, 2000, 1500, 100, 24, piers=(322, 650, 1000, 1600, 1978))
    for s1, s2, z in ((850, 2250, -250), (0, 2000, 90), (300, 950, 560), (1750, 2000, 560), (980, 1100, 560), (1600, 1720, 560),
                      (300, 950, 1030), (1750, 2000, 1030), (980, 1100, 1030), (1600, 1720, 1030),
                      (300, 1230, 1500), (1470, 2000, 1500), (2000, 2250, 90), (2000, 2250, 560)):
        o.append(rect(s1, Y(z), s2 - s1, 30, INK))
    for sw in (300, 1960):
        o += [rect(sw, Y(660), 40, 180, INK), rect(sw, Y(1090), 40, 140, INK), rect(sw, Y(1500), 40, 220, INK)]
        o += [rect(sw - 30, Y(1500), 100, 120, TRIM, LINE, 2), rect(sw - 50, Y(1505), 140, 30, TRIM, LINE, 2)]
    o += [rect(0, Y(90), 40, 30, INK), rect(2250, Y(90), 30, 340, INK)]
    o += [rect(-10, Y(190), 20, 100, TRIM, LINE, 2), path(f'M-10 {Y(190)} H300', LINE, 4)]
    # ninfeo: columns and shallow vaults seen beyond
    o += [rect(235, Y(60), 30, 310, TRIM, LINE, 2), rect(585, Y(60), 30, 310, TRIM, LINE, 2),
          path(f'M40 {Y(40)} Q137 {Y(85)} 235 {Y(40)} M265 {Y(40)} Q425 {Y(85)} 585 {Y(40)} M615 {Y(40)} Q800 {Y(85)} 985 {Y(40)}', LINE, 3)]
    # Grand Salon: coffered ceiling, cove, chandelier
    o += [rect(340, Y(530), 610, 22, TRIM, LINE, 2)]
    o += [rect(x, Y(508), 70, 18, '#E9E1CE', LINE, 1.5) for x in range(380, 900, 100)]
    o += [path(f'M340 {Y(450)} Q380 {Y(450)} 380 {Y(508)} M950 {Y(450)} Q910 {Y(450)} 910 {Y(508)}', LINE, 3),
          path(f'M650 {Y(508)} V{Y(440)}', LINE, 2), ellipse(650, Y(420), 60, 22, '#E9C46A', LINE, 2)]
    # La Rotonda: drum walls with openings, ring galleries, the curved flights seen on the far wall
    o += [rect(950, Y(1500), 30, 1750, INK), rect(1720, Y(1500), 30, 1750, INK)]
    for zb, zt in ((90, 420), (560, 820), (1030, 1290), (-250, -30)):
        o += [rect(950, Y(zt), 30, zt - zb, '#FFFFFF'), rect(1720, Y(zt), 30, zt - zb, '#FFFFFF')]
    band_o, band_i, steps_ = [], [], []
    for t in range(0, 27):
        a = 65 - 140 * t / 26
        z = 90 + 470 * t / 26
        band_o.append((RY + R_OUT * math.sin(math.radians(a)), z))
        band_i.append((RY + R_IN * math.sin(math.radians(a)), z))
    d = 'M' + ' L'.join(f'{x:.0f} {Y(z):.0f}' for x, z in band_o) + ' L' + ' L'.join(f'{x:.0f} {Y(z - 18):.0f}' for x, z in reversed(band_o)) + ' Z'
    o += [path(d, LINE, 2.5, TRIM)]
    o += [path(' '.join(f'M{x:.0f} {Y(z):.0f} v18' for x, z in band_o[1:]), LINE, 1.5)]
    o += [path('M' + ' L'.join(f'{x:.0f} {Y(z + 90):.0f}' for x, z in band_o), OLD_LINE, 3)]
    for z in (560, 1030):
        o += [path(f'M1100 {Y(z + 90)} V{Y(z)} M1600 {Y(z + 90)} V{Y(z)} M980 {Y(z + 90)} H1100 M1600 {Y(z + 90)} H1720', IRON, 4)]
    # racks of the round cellar
    o += [path(' '.join(f'M{x} {Y(-230)} V{Y(40)}' for x in range(1010, 1720, 70)), '#8B7B5E', 6)]
    # lantern and its chandelier, centred on the rotunda
    o += [rect(1230, Y(1700), 240, 200, WALL, LINE, 3), path(f'M1220 {Y(1700)} A130 120 0 0 1 1480 {Y(1700)}', LINE, 4, COPPER),
          path(f'M1350 {Y(1820)} V{Y(1880)}', LINE, 5), path(f'M1350 {Y(1500)} V{Y(980)}', LINE, 2),
          ellipse(1350, Y(950), 90, 34, '#E9C46A', LINE, 2)]
    o += [path(f'M{x} {Y(1560)} L{x2} {Y(300)}', '#E9C46A', 6, extra=' stroke-dasharray="8 16" opacity="0.8"')
          for x, x2 in ((1280, 1170), (1420, 1530))]
    o += [arrow(f'M1520 {Y(450)} V{Y(1600)}', TEAL, 1520, Y(1640), -90, k, dashed=False, w=1.4)]
    # porch and perron
    o += [rect(2210, Y(470), 26, 380, TRIM, LINE, 2), rect(2195, Y(495), 56, 25, TRIM, LINE, 2)]
    o += balustrade(2000, 2250, 590, 90, 22)
    o += [path(' '.join(f'M{2250 + i * 30} {-90 + i * 18} h30 v18' for i in range(5)), LINE, 3)]
    L = lambda x, z, t, px=9, c=INK, wgt=600: label(x, Y(z), t, px, k, c, wgt, 'middle', '#FFFFFF')
    o += [L(650, 300, 'GRAND SALON'), L(650, 250, 'cao 4,4 m · trần ô cờ', 8, MUTED, 400),
          L(1350, 780, 'LA ROTONDA'), L(1350, 730, 'Ø 7,4 m · thông ba tầng tới lồng đèn', 8, MUTED, 400),
          L(1855, 300, 'TIỀN SẢNH', 8), L(2125, 300, 'PORCH', 8),
          L(650, 780, 'PHÒNG GIA ĐÌNH'), L(1860, 780, 'PHÒNG HỌC', 8), L(650, 1250, 'PHÒNG NGỦ CHỦ'),
          L(1860, 1250, 'KHÁCH RIÊNG', 8), L(420, -110, 'NINFEO · HỒ BƠI', 9), L(1350, -110, 'HẦM RƯỢU TRÒN'),
          L(2000, -110, 'CHIẾU PHIM', 8), L(-250, -170, 'VƯỜN −2.50', 8, GREEN_LINE), L(150, 140, 'SÂN THƯỢNG', 8),
          L(2700, 40, 'SÂN DANH DỰ ±0.00', 8, MUTED, 400), L(1350, 1960, 'LỒNG ĐÈN', 8, ACC),
          label(-450, 455, '← BIỂN', 10, k, ACC, 600, 'start', EARTH), label(2950, 455, 'ĐƯỜNG →', 10, k, ACC, 600, 'end', EARTH)]
    o += level_marks(2760, k, ((-250, '−2.50'), (90, '+0.90'), (560, '+5.60'), (1030, '+10.30'), (1500, '+15.00'), (1890, '+18.90')))
    draw = svg(SECT_VIEW, w, h,
               'Mặt cắt dọc trục chính: từ vườn biển qua hồ bơi chạy vào hang dưới Grand Salon; Grand Salon cao 4,4 m '
               'trần ô cờ có đèn chùm; sảnh tròn La Rotonda Ø 7,4 m với hai vế thang cong ôm tường, '
               'thông ba tầng tới lồng đèn mái vòm ở cốt +18.90; hầm rượu tròn bên dưới; tiền sảnh, porch và bậc xuống sân danh dự',
               '\n'.join(o))
    items = [
        ('Hồ bơi đi vào nhà', 'dài 11,5 m',
         'Hồ bơi bắt đầu ngoài vườn, chui qua vòm đá vào ninfeo dưới Grand Salon. Bơi từ trong hang ra ánh sáng phía biển.'),
        ('Grand Salon', '+0.90 · cao 4,4 m',
         'Trần ô cờ thạch cao, phào cổ ngỗng, đèn chùm; ba cửa vòm cao ra sân thượng.'),
        ('La Rotonda', 'hai vế thang cong',
         'Sảnh tròn Ø 7,4 m. Hai vế 26 bậc rộng 1,2 m ôm tường, bắt đầu hai bên cửa từ tiền sảnh, gặp nhau ở chiếu tới phía biển tầng 2, như La Rotonda B.'),
        ('Lồng đèn', 'đỉnh +18.90',
         'La Rotonda thông ba tầng tới vòm. Sáng trời rơi thẳng xuống giữa hai vế thang; ô thoáng ở thân lồng đèn mở ra cho hơi nóng thoát.'),
        ('Hầm rượu tròn', 'ngay dưới La Rotonda',
         'Cùng vòng tròn ở tầng dưới, giá rượu quanh tường như ý NC2. Phòng chiếu phim chuyển xuống dưới porch, 40 m².'),
    ]
    right = side_title('Một chuỗi không gian') + '\n' + '\n'.join(row(*r) for r in items)
    left = caption('MẶT CẮT DỌC TRỤC CHÍNH · BIỂN BÊN TRÁI, ĐƯỜNG BÊN PHẢI') + '\n' + draw
    return header('DT7', 'Mặt cắt dọc trục', 'Hồ bơi, Grand Salon, La Rotonda, lồng đèn') + '\n' + two_col(left, right, 1066)


# ---------- DT3 · Tầng 1 ----------

def horseshoe(k):
    o = []
    for sx in (-1, 1):
        xa = C0 + 30 if sx < 0 else C1 - 30
        xb = xa + sx * 290
        d = f'M{xa} 40 Q{xb} 40 {xb} -280'
        o += [path(d, INK, 150), path(d, TRIM, 130), path(d, INK, 130, extra=' stroke-dasharray="2.5 24"')]
    return o


def dt3():
    k = FLOOR_VIEW[2] / 798
    o = [rect(-420, -480, 2660, 3000, '#F3F4F1'), rect(-420, -480, 2660, 480, GREEN), rect(-420, 2150, 2660, 370, PAVE)]
    o += [rect(685, -300, 450, 300, WATER, WATER_LINE, 4), rect(685, 0, 450, 850, 'none', WATER_LINE, 4, ' stroke-dasharray="16 10"')]
    o += horseshoe(k)
    o += [rect(C0, 0, C1 - C0, 300, TERR, INK, 6)]
    o += balustrade_plan(C0, C1, 0)
    o += room(C0, Y0, C1 - C0, 650, 'GRAND SALON', k, px=11)
    o += rotunda_cell()
    o += checker(C0 + 10, 1760, C1 - C0 - 20, 230)
    o += room(C0, 1750, C1 - C0, 250, '', k, 'none', area=False)
    o += room(X0, Y0, C0 - X0, 850, 'THƯ VIỆN', k, sub='salon nhỏ · 47 m²')
    o += room(X0, 1150, C0 - X0, 350, 'POWDER · ÁO KHOÁC', k, px=8)
    o += room(X0, 1500, C0 - X0, 500, '', k, area=False)
    o += room(C1, Y0, X1 - C1, 850, 'PHÒNG ĂN', k, sub='18 chỗ · 47 m²')
    o += room(C1, 1150, X1 - C1, 300, 'SOẠN · TỦ RƯỢU', k, px=8)
    o += room(C1, 1450, X1 - C1, 550, 'BẾP ÂU', k, sub='30 m²')
    o += outline()
    o += windows_plan(skip={(X0, 1750), (X0, 560), (X0, 900)})
    # openings
    for g in ((810, 935, 200, 70), (830, 1700, 160, 65), (820, 1985, 180, 30), (500, 770, 25, 120), (1300, 770, 25, 120),
              (495, 1300, 60, 100), (1265, 1300, 60, 100), (500, 1800, 25, 120), (130, 1140, 120, 25), (130, 1490, 120, 25),
              (1540, 1140, 120, 25), (1540, 1440, 120, 25), (X0 - 25, 1650, 30, 200)):
        o.append(gap(*g))
    for cx in (676, AXIS, 1143):
        o += [rect(cx - 75, Y0 - 25, 150, 50, '#FFFFFF'), path(f'M{cx - 75} {Y0} H{cx + 75}', INK, 2)]
    o += curved_stairs(k) + [circle(RX, RY, 60, '#F4F1EA', ACC, 3)]
    o += fireplace(235, 1100) + fireplace(1825, 830, horizontal=False)
    o += [rect(1460, 470, 250, 520, '#FFFFFF', '#5E6B7A', 3, ' rx="40"')]
    o += [circle(1440, y, 16, '#FFFFFF', '#5E6B7A', 2.5) for y in range(520, 960, 72)]
    o += [circle(1730, y, 16, '#FFFFFF', '#5E6B7A', 2.5) for y in range(520, 960, 72)]
    o += [rect(640, 410, 540, 60, '#FFFFFF', '#5E6B7A', 3, ' rx="16"'), rect(640, 670, 540, 60, '#FFFFFF', '#5E6B7A', 3, ' rx="16"'),
          rect(810, 490, 200, 80, '#FFFFFF', '#5E6B7A', 3)]
    o += [path('M0 380 V740 M0 920 V1080 M0 380 H460', '#8B7B5E', 26)]
    o += treads(-10, 1530, 280, 440, 15) + [rect(310, 1540, 170, 170, '#FFFFFF', INK, 3), path('M310 1540 L480 1710 M480 1540 L310 1710', INK, 1.5),
                                         label(395, 1760, 'TM', 8, k)]
    o += [rect(1340, 1480, 500, 70, '#FFFFFF', '#5E6B7A', 3), rect(1360, 1830, 220, 100, '#FFFFFF', '#5E6B7A', 3)]
    o += treads(1700, 1760, 140, 220, 8)
    # porch, perron, gallery to the old house
    o += [rect(C0, Y1, C1 - C0, 250, TERR, INK, 6)] + [circle(cx, 2220, 25, INK) for cx in COLS]
    o += [rect(C0 - 50 - i * 20, 2250 + i * 30, C1 - C0 + 100 + i * 40, 30, '#FFFFFF', INK, 2) for i in range(5)]
    o += link_plan(k, 1)
    o += [rect(X0, Y1, C0 - 60 - X0, 150, '#FFFFFF', IRON, 3, ' stroke-dasharray="10 8"'),
          rect(C1 + 60, Y1, X1 - C1 - 60, 150, '#FFFFFF', IRON, 3, ' stroke-dasharray="10 8"')]
    o += [label(AXIS, 1210, 'LA ROTONDA', 10, k, INK, 600, 'middle', '#FFFFFF'), label(AXIS, 1245, 'Ø 7,4 m · 43 m²', 8, k, MUTED, 400, 'middle', '#FFFFFF'),
          label(AXIS, 1490, 'hai vế thang cong', 8, k, ACC, 600, 'middle', '#FFFFFF'),
          label(AXIS, 1870, 'TIỀN SẢNH', 9, k, INK, 600, 'middle', '#F4F1EA'), label(AXIS, 1905, '20 m²', 8, k, MUTED, 400, 'middle', '#F4F1EA'),
          label(235, 1490 + 0, '', 8, k), label(140, 1620, 'SẢNH PHỤ', 8, k, INK, 600, 'middle', '#FFFFFF'),
          label(AXIS, 160, 'SÂN THƯỢNG +0.90', 9, k, INK, 600, 'middle', TERR), label(AXIS, -150, 'HỒ BƠI', 9, k, INK, 600, 'middle', WATER),
          label(AXIS, 2140, 'PORCH', 9, k, INK, 600, 'middle', TERR), label(AXIS, 2470, 'SÂN DANH DỰ ±0.00', 9, k, MUTED, 400, 'middle', PAVE),
          label(200, -360, 'thang móng ngựa', 8, k, INK, 600, 'middle', GREEN), label(1620, -360, 'xuống vườn −2.50', 8, k, INK, 600, 'middle', GREEN),
          label(250, 2080, 'hào sáng', 8, k, IRON, 400, 'middle', '#FFFFFF'), label(1590, 2080, 'hào sáng', 8, k, IRON, 400, 'middle', '#FFFFFF'),
          path(f'M-420 830 H{X1}', ACC, 4, extra=' stroke-dasharray="30 18"'), label(X1 + 60, 810, 'enfilade', 8, k, ACC, 600, 'start', None),
          path(f'M{AXIS} -460 V2500', ACC, 3, extra=' stroke-dasharray="40 24" opacity="0.7"')]
    o += flush_late() + compass(k, 2120, -400) + scalebar(k, -380, 2440)
    draw = svg(FLOOR_VIEW, 798, 900,
               'Mặt bằng tầng 1: trên trục từ đường vào là porch bốn cột, tiền sảnh lát đá bàn cờ, sảnh tròn '
               'La Rotonda Ø 7,4 m với hai vế thang cong đối xứng ôm tường, Grand Salon 52 mét vuông mở ba cửa ra sân thượng, thang móng '
               'ngựa xuống vườn và hồ bơi; bên bắc là thư viện, powder, sảnh phụ với thang và thang máy, khối nối liền nhà '
               'cũ; bên nam là phòng ăn 18 chỗ, soạn, bếp Âu; thư viện, salon và phòng ăn nối bằng một đường cửa', '\n'.join(o))
    rows = [
        ('Trục danh dự', 'porch → salon',
         'Porch bốn cột, tiền sảnh bàn cờ, La Rotonda, Grand Salon, sân thượng: năm không gian nối thẳng, hẹp, tròn, rộng, rồi mở ra biển.'),
        ('Enfilade', '29 m qua hai nhà',
         'Phòng ăn, Grand Salon, thư viện, rồi qua khối nối vào sảnh trước nhà cũ: một đường cửa thẳng hàng, không một bậc.'),
        ('Grand Salon', '52 m² · cao 4,4 m',
         'Ba cửa vòm ra sân thượng 24 m², thang móng ngựa xuống vườn. Đây là phòng tiếp khách chính, nhìn biển.'),
        ('Phục vụ', 'tách khỏi khách',
         'Bếp Âu và soạn ở cánh nam, có thang phục vụ riêng xuống bếp Á và nhập hàng ở tầng dưới. Người phục vụ không đi qua trục.'),
        ('Nhà cũ', 'cùng +0.90, không bậc',
         'Nhà cũ có 5 bậc từ sân lên, sàn khoảng +0.90 như tầng 1 mới: enfilade đi phẳng qua khối nối vào sảnh trước nhà cũ. Chi tiết ở DT8.'),
        ('Diện tích', '323 m² + porch, sân thượng',
         'Khối nhà 19 × 17 m; porch 20 m², sân thượng 24 m².'),
    ]
    right = side_title('Tầng tiếp khách') + '\n' + '\n'.join(row(*r) for r in rows)
    left = caption('TẦNG 1 · CỐT +0.90 · BIỂN Ở TRÊN') + '\n' + draw
    return header('DT3', 'Tầng 1 · tiếp khách', 'Cốt +0.90 · trục danh dự, enfilade, La Rotonda') + '\n' + two_col(left, right, 798)


def balustrade_plan(x1, x2, y):
    return [rect(x1, y - 12, x2 - x1, 24, TRIM, INK, 3)] + [rect(x, y - 18, 30, 36, TRIM, INK, 3) for x in (x1, (x1 + x2) / 2 - 15, x2 - 30)]


# ---------- DT2 · Tầng dưới ----------

def dt2():
    k = FLOOR_VIEW[2] / 798
    o = [rect(-420, -480, 2660, 3000, '#F3F4F1'), rect(-420, -480, 2660, 480, GREEN), rect(-420, 2150, 2660, 370, EARTH)]
    o += horseshoe(k)
    o += room(C0, 0, C1 - C0, 950, '', k, '#EEF3F1', area=False)
    o += [rect(685, -300, 450, 1150, WATER, WATER_LINE, 4)]
    o += rotunda_cell()
    o += room(C0, 1750, C1 - C0, 500, 'PHÒNG CHIẾU PHIM', k, px=8, sub='dưới porch · 40 m²')
    o += room(X0, Y0, C0 - X0, 800, 'PHÒNG TẬP', k)
    o += room(X0, 1100, C0 - X0, 400, 'SPA · XÔNG', k, px=8)
    o += room(X0, 1500, C0 - X0, 500, '', k, area=False)
    o += room(C1, Y0, X1 - C1, 800, 'BẾP Á', k, sub='hút mùi ra vườn · 44 m²')
    o += room(C1, 1100, X1 - C1, 400, 'GIẶT ỦI · KHO', k, px=8)
    o += room(C1, 1500, X1 - C1, 500, '', k, area=False)
    o += [path(f'M{X0} {Y0} V{Y1} H{C0} V2250 H{C1} V{Y1} H{X1} V{Y0} H{C1} V0 H{C0} V{Y0} Z', INK, 40)]
    for cx in (676, AXIS, 1143):
        o += [rect(cx - 100, -20, 200, 40, '#EEF3F1'), path(f'M{cx - 100} 0 H{cx + 100}', WATER_LINE, 3)]
    for cx in (97, 372, 1447, 1722):
        o += [rect(cx - 55, Y0 - 20, 110, 40, '#FFFFFF', INK, 2), path(f'M{cx - 55} {Y0} H{cx + 55}', INK, 2)]
    for cx in (97, 372, 1447, 1722):
        o += [rect(cx - 55, Y1 - 20, 110, 40, '#FFFFFF', INK, 2), path(f'M{cx - 55} {Y1} H{cx + 55}', INK, 2)]
    for g in ((500, 600, 25, 120), (1300, 600, 25, 120), (860, 935, 100, 70), (860, 1700, 100, 65), (500, 1760, 25, 120),
              (130, 1090, 120, 25), (130, 1490, 120, 25), (1540, 1090, 120, 25), (1540, 1490, 120, 25)):
        o.append(gap(*g))
    o += [circle(x, y, 30, '#FFFFFF', INK, 4) for x in (590, 1230) for y in (250, 600)]
    o += [rect(1340, 330, 500, 70, '#FFFFFF', '#5E6B7A', 3), rect(1500, 560, 200, 100, '#FFFFFF', '#5E6B7A', 3)]
    o += treads(-10, 1530, 280, 440, 15) + [rect(310, 1540, 170, 170, '#FFFFFF', INK, 3), path('M310 1540 L480 1710 M480 1540 L310 1710', INK, 1.5)]
    o += treads(1700, 1760, 140, 220, 8)
    o += [rect(X0, Y1, C0 - 60 - X0, 150, '#FFFFFF', IRON, 3, ' stroke-dasharray="10 8"'),
          rect(C1 + 60, Y1, X1 - C1 - 60, 150, '#FFFFFF', IRON, 3, ' stroke-dasharray="10 8"')]
    o += treads(1600, 2015, 240, 130, 8, vertical=False)
    o += [rect(560 + i * 90, 1960, 70, 230, '#FFFFFF', '#5E6B7A', 2.5, ' rx="12"') for i in range(8)]
    o += [path(' '.join('M{:.0f} {:.0f} L{:.0f} {:.0f}'.format(*_pt(R_OUT - 15, a), *_pt(R_OUT - 110, a)) for a in range(0, 360, 20)
                        if not (60 < a < 120 or 240 < a < 300)), '#8B7B5E', 12),
          circle(RX, RY, 80, '#FFFFFF', '#5E6B7A', 3), label(RX, RY + 150, 'HẦM RƯỢU TRÒN', 8, k, INK, 600, 'middle', '#FFFFFF'),
          label(RX, RY + 182, 'Ø 7,4 m · 43 m²', 7, k, MUTED, 400, 'middle', '#FFFFFF')]
    o += [label(AXIS, 160, 'NINFEO', 11, k, INK, 600, 'middle', '#EEF3F1'),
          label(AXIS, 200, 'hồ bơi trong hang vòm', 8, k, MUTED, 400, 'middle', '#EEF3F1'),
          label(AXIS, 700, 'HỒ BƠI 4,5 × 11,5 m', 9, k, INK, 600, 'middle', WATER),
          label(AXIS, -200, 'ba vòm đá', 8, k, INK, 600, 'middle', WATER),
          label(140, 1620, 'THANG · TM', 8, k, INK, 600, 'middle', '#FFFFFF'),
          label(1580, 1600, 'THANG PHỤC VỤ', 8, k, INK, 600, 'middle', '#FFFFFF'),
          label(1580, 1640, 'nhập hàng', 7, k, MUTED, 400, 'middle', '#FFFFFF'),
          label(1720, 2190, 'bậc từ sân xuống hào sáng', 8, k, IRON, 400, 'end', EARTH),
          label(AXIS, 2300, 'đất dưới sân danh dự', 8, k, MUTED, 400, 'middle', EARTH),
          label(200, -380, 'VƯỜN −2.50', 9, k, GREEN_LINE, 600, 'middle', GREEN),
          path(f'M{AXIS} -460 V2500', ACC, 3, extra=' stroke-dasharray="40 24" opacity="0.7"')]
    o += flush_late() + compass(k, 2120, -400) + scalebar(k, -380, 2440)
    draw = svg(FLOOR_VIEW, 798, 900,
               'Mặt bằng tầng dưới cốt −2.50: ở giữa là ninfeo, một phòng hang có hồ bơi 4,5 × 11,5 m chạy từ vườn qua ba '
               'vòm đá vào trong nhà; sau đó là hầm rượu tròn dưới La Rotonda và phòng chiếu phim dưới porch; bên bắc là phòng tập, spa, thang và thang '
               'máy; bên nam là bếp Á, giặt ủi, thang phục vụ và nhập hàng qua hào sáng', '\n'.join(o))
    rows = [
        ('Ninfeo', 'hang có hồ bơi',
         'Kiểu hang nước trong vườn villa Ý: vòm đá, tường rusticated, hồ bơi chạy từ vườn qua ba vòm vào trong. Bốn cột đỡ sàn Grand Salon phía trên.'),
        ('Hầm rượu tròn', 'Ø 7,4 m · 43 m²', 'Ngay dưới La Rotonda, cùng vòng tròn: giá rượu quanh tường, bàn nếm ở giữa, như ý NC2 trên canvas.'),
        ('Giải trí', 'chiếu phim, tập, spa', 'Phòng chiếu 40 m² dưới tiền sảnh và porch; phòng tập nhìn vườn; spa và xông hơi cạnh hồ.'),
        ('Bếp Á, phục vụ', 'cánh nam', 'Bếp Á 44 m² mở ra vườn để thoát mùi; giặt ủi, kho; thang phục vụ lên bếp Âu.'),
        ('Nhập hàng', 'qua hào sáng', 'Bậc từ sân danh dự xuống hào sáng phía nam, vào thẳng thang phục vụ; không qua cửa chính.'),
        ('Hai phòng nhân viên', 'ở nhà cổng nam', 'Tầng dưới dành cho gia đình và phục vụ; nhân viên ở nhà cổng phía nam (xem DT1).'),
    ]
    right = side_title('Tầng vườn') + '\n' + '\n'.join(row(*r) for r in rows)
    left = caption('TẦNG DƯỚI · CỐT −2.50 · MỞ RA VƯỜN BIỂN') + '\n' + draw
    return header('DT2', 'Tầng dưới · ninfeo', 'Cốt −2.50 · hồ bơi trong hang vòm, hầm rượu, giải trí') + '\n' + two_col(left, right, 798)


# ---------- DT4 · Tầng 2 và tầng 3 ----------

UPPER_VIEW = (-350, 120, 2400, 2300)


def upper_plan(level, k):
    o = [rect(-250, 120, 2300, 2300, '#F3F4F1')]
    if level == 2:
        o += room(C0, Y0, C1 - C0, 650, 'PHÒNG GIA ĐÌNH', k, px=10)
        o += rotunda_cell('#E4EEEC')
        o += room(C0, 1750, C1 - C0, 250, 'PHÒNG HỌC', k, px=8)
        o += room(X0, Y0, C0 - X0, 600, 'PHÒNG NGỦ 1', k) + room(X0, 900, C0 - X0, 250, 'TẮM', k, px=8)
        o += room(X0, 1150, C0 - X0, 350, 'SẢNH NỐI', k, px=8) + room(X0, 1500, C0 - X0, 500, '', k, area=False)
        o += room(C1, Y0, X1 - C1, 600, 'PHÒNG NGỦ 2', k) + room(C1, 900, X1 - C1, 250, 'TẮM', k, px=8)
        o += room(C1, 1150, X1 - C1, 250, 'TẮM', k, px=8) + room(C1, 1400, X1 - C1, 600, 'PHÒNG NGỦ 3', k)
        o += [rect(C0, Y1, C1 - C0, 250, TERR, INK, 6)] + balustrade_plan(C0, C1, Y1 + 250)
        o += [label(AXIS, 2150, 'BAN CÔNG TRÊN PORCH', 8, k, INK, 600, 'middle', TERR)]
        gaps = ((810, 935, 200, 70), (830, 1700, 160, 65), (495, 1300, 60, 100), (1265, 1300, 60, 100),
                (500, 600, 25, 100), (1300, 600, 25, 100), (130, 890, 120, 25), (1540, 890, 120, 25), (1540, 1390, 120, 25),
                (500, 1820, 25, 100), (1300, 1820, 25, 100))
        tag, sub = 'KHOẢNG THÔNG', 'chiếu tới phía biển'
    else:
        o += room(C0, Y0, C1 - C0, 650, 'PHÒNG NGỦ CHỦ', k, px=10)
        o += rotunda_cell('#E4EEEC')
        o += room(C0, 1750, C1 - C0, 250, 'KHÁCH RIÊNG', k, px=8)
        o += room(X0, Y0, C0 - X0, 450, 'TẮM ÔNG', k, px=9) + room(X0, 750, C0 - X0, 400, 'THAY ĐỒ ÔNG', k, px=8)
        o += room(X0, 1150, C0 - X0, 350, 'SẢNH NỐI', k, px=8) + room(X0, 1500, C0 - X0, 500, '', k, area=False)
        o += room(C1, Y0, X1 - C1, 450, 'TẮM BÀ', k, px=9) + room(C1, 750, X1 - C1, 400, 'THAY ĐỒ BÀ', k, px=8)
        o += room(C1, 1150, X1 - C1, 850, 'PHÒNG NGỦ PHỤ', k)
        gaps = ((810, 935, 200, 70), (830, 1700, 160, 65), (495, 1300, 60, 100), (500, 450, 25, 100), (1300, 450, 25, 100), (500, 850, 25, 100),
                (1300, 850, 25, 100), (130, 740, 120, 25), (1540, 740, 120, 25), (500, 1250, 25, 100), (1300, 1500, 25, 100))
        tag, sub = 'BAN CÔNG TRÒN', 'dưới lồng đèn'
        o += [rect(760, 520, 300, 260, '#FFFFFF', '#5E6B7A', 3), rect(740, 500, 340, 40, '#FFFFFF', '#5E6B7A', 3)]
        o += [rect(-10, 380, 250, 110, '#FFFFFF', '#5E6B7A', 3, ' rx="40"'), rect(1580, 380, 250, 110, '#FFFFFF', '#5E6B7A', 3, ' rx="40"')]
    o += outline() + windows_plan(skip={(X0, 560), (X0, 900)}) + link_plan(k, 2)
    gaps = gaps + ((130, 1490, 120, 25),)
    for g in gaps:
        o.append(gap(*g))
    if level == 2:
        o += curved_stairs(k, seen=True)
    o += rotunda_landing(level)
    if level == 3:
        o += [circle(RX, RY, 120, 'none', ACC, 5), label(RX, RY + 10, 'lồng đèn ở trên', 7, k, ACC, 600, 'middle', '#E4EEEC')]
    o += [label(AXIS, 1250 if level == 2 else 1185, tag, 8, k, INK, 600, 'middle', '#E4EEEC'),
          label(AXIS, 1280 if level == 2 else 1215, sub, 7, k, MUTED, 400, 'middle', '#E4EEEC')]
    o += treads(-10, 1530, 280, 440, 15) + [rect(310, 1540, 170, 170, '#FFFFFF', INK, 3), path('M310 1540 L480 1710 M480 1540 L310 1710', INK, 1.5),
                                         label(140, 1620, 'THANG · TM', 7, k, INK, 600, 'middle', '#FFFFFF')]
    o += fireplace(AXIS, Y1 - 50) if level == 2 else fireplace(AXIS, 912)
    o += [path(f'M{AXIS} 140 V2400', ACC, 3, extra=' stroke-dasharray="40 24" opacity="0.6"')]
    return o + flush_late()


def dt4():
    k = UPPER_VIEW[2] / 690
    p2 = svg(UPPER_VIEW, 690, 661,
             'Mặt bằng tầng 2 cốt +5.60: phòng gia đình ở giữa phía biển, chiếu tới và ban công quanh La Rotonda, phòng '
             'học trên porch có ban công; hai phòng ngủ bên nam, một phòng ngủ bên bắc, mỗi phòng có tắm; thang và thang '
             'máy ở góc tây bắc', '\n'.join(upper_plan(2, k) + compass(k, 1840, 200)))
    p3 = svg(UPPER_VIEW, 690, 661,
             'Mặt bằng tầng 3 cốt +10.30: phòng ngủ chủ ở giữa phía biển; cánh ông bên bắc với tắm và thay đồ; cánh bà bên '
             'nam với tắm và thay đồ; khoảng thông dưới lồng đèn; phòng khách riêng phía đường; phòng ngủ phụ ở góc tây nam',
             '\n'.join(upper_plan(3, k) + compass(k, 1840, 200)))
    plans = ('<div style="display: grid; grid-template-columns: 690px 690px; gap: 36px">\n'
             '<div style="display: flex; flex-direction: column; gap: 6px">' + caption('TẦNG 2 · CỐT +5.60 · GIA ĐÌNH') + p2 + '</div>\n'
             '<div style="display: flex; flex-direction: column; gap: 6px">' + caption('TẦNG 3 · CỐT +10.30 · CĂN HỘ CHỦ') + p3 + '</div>\n</div>')
    rows = [
        ('Tầng 2', 'phòng gia đình 52 m²', 'Ba phòng ngủ có tắm, cùng ba suite nhà cũ là sáu; sảnh nối sang thẳng tầng suite nhà cũ. Phòng học 20 m² trên porch.'),
        ('La Rotonda', 'chiếu tới phía biển', 'Hai vế thang cong gặp nhau ở chiếu tới trước phòng gia đình; lan can sắt rèn vòng quanh khoảng thông.'),
        ('Tầng 3', 'căn hộ chủ đối xứng', 'Phòng ngủ chủ 52 m² trên trục nhìn biển; cánh ông bên bắc, cánh bà bên nam. Sảnh nối sang phòng thờ nhà cũ.'),
        ('Phòng ngủ phụ', '47 m²', 'Góc tây nam tầng 3, cho con nhỏ hoặc người giúp việc riêng; khách riêng 20 m² phía đường.'),
    ]
    notes = ('<div style="display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 0 28px">\n'
             + '\n'.join(row(*r) for r in rows) + '\n</div>')
    return header('DT4', 'Tầng 2 và tầng 3', 'Cốt +5.60 và +10.30 · cùng một lưới bảy nhịp') + '\n' + plans + '\n' + notes


# ---------- DT1 · Tổng mặt bằng ----------

SITE_VIEW = (-1100, -620, 3250, 4500)


def dt1():
    k = SITE_VIEW[2] / 640
    o = [rect(-1100, -620, 3250, 4500, '#F3F4F1'), rect(-1038, -620, 848, 4220, '#EAEAE5'),
         rect(-190, -400, 2200, 4000, '#EFEDE4'), rect(-190, -400, 2200, 700, GREEN),
         path('M-1038 -742 H-190 V-220 H-320 V1250 H-720 V1130 H-1038 Z', OLD_LINE, 22, OLD),
         rect(-1100, 3600, 3250, 260, '#C6C7C1')]
    # garden: hedges, pool, horseshoe stair, sea balustrade
    o += [rect(-150, -370, 700, 60, '#B8CBA8', GREEN_LINE, 3), rect(1270, -370, 700, 60, '#B8CBA8', GREEN_LINE, 3),
          rect(-150, 0, 450, 240, '#C9D9BC', GREEN_LINE, 3), rect(1520, 0, 450, 240, '#C9D9BC', GREEN_LINE, 3)]
    o += [circle(x, y, 40, '#7FA06A') for x in (-100, 250, 1570, 1920) for y in (120,)]
    o += [rect(685, -300, 450, 300, WATER, WATER_LINE, 4)] + horseshoe(k) + [rect(C0, 0, C1 - C0, 300, TERR, INK, 6)]
    o += [rect(-190, -415, 2200, 30, TRIM, INK, 4)] + [rect(x - 25, -425, 50, 50, TRIM, INK, 4) for x in (-170, 360, AXIS, 1460, 1990)]
    # house roof plan
    o += [rect(X0, Y0, X1 - X0, Y1 - Y0, '#D9DDE0', INK, 16), rect(X0 + 40, Y0 + 40, X1 - X0 - 80, Y1 - Y0 - 80, 'none', TRIM, 18),
          circle(AXIS, RY, 130, COPPER, INK, 6), circle(AXIS, RY, 40, TRIM, INK, 4),
          rect(115, 1050, 70, 120, WALL, INK, 4), rect(1635, 1050, 70, 120, WALL, INK, 4),
          path(f'M{C0 - 40} {Y0} L{AXIS} {Y0 + 110} L{C1 + 40} {Y0} M{C0 - 40} {Y1} L{AXIS} {Y1 - 110} L{C1 + 40} {Y1}', INK, 6)]
    o += [rect(C0, Y1, C1 - C0, 250, TERR, INK, 6)] + [rect(C0 - 50 - i * 20, 2250 + i * 30, C1 - C0 + 100 + i * 40, 30, '#FFFFFF', INK, 2) for i in range(5)]
    o += [rect(LX0, LY0, LX1 - LX0, LY1 - LY0, '#D9DDE0', INK, 12), rect(LX0 + 30, LY0 + 30, LX1 - LX0 - 60, LY1 - LY0 - 60, 'none', TRIM, 14)]
    # court, gate, pavilions, drive
    o += [rect(-190, 2400, 2200, 600, PAVE), path(f'M-190 {2400} H2010', INK, 3)]
    o += [rect(-190, 3000, 900, 600, GARAGE, ACC, 5), rect(1110, 3000, 900, 600, GARAGE, ACC, 5)]
    o += [path(f'M-190 3000 L260 3300 L710 3000 M-190 3600 L260 3300 L710 3600', ACC, 3),
          path(f'M1110 3000 L1560 3300 L2010 3000 M1110 3600 L1560 3300 L2010 3600', ACC, 3)]
    o += [rect(680, 3540, 60, 80, TRIM, INK, 4), rect(1080, 3540, 60, 80, TRIM, INK, 4), path('M740 3580 H1080', IRON, 8)]
    o += [arrow('M910 3700 V2700 H-150 Q-500 2700 -500 3000 V3700', INK, -500, 3720, 90, k)]
    o += [path('M-190 -400 V2400 M-190 3000 V3600 M2010 -400 V3600', ACC, 5, extra=' stroke-dasharray="30 18"')]
    L = lambda x, y, t, px=9, c=INK, wgt=600, bg='#FFFFFF', anc='middle', rot=None: label(x, y, t, px, k, c, wgt, anc, bg, rot)
    o += [L(AXIS, 900, 'DINH THỰ', 11, INK, 600, '#D9DDE0'), L(AXIS, 900 + 13 * k, '19 × 17 m', 8, MUTED, 400, '#D9DDE0'),
          L(AXIS, 1570, 'lồng đèn', 8, INK, 600, '#D9DDE0'), L(260, 3330, 'NHÀ XE 3 Ô', 9, INK, 600, GARAGE),
          L(1560, 3300, 'NHÀ CỔNG', 9, INK, 600, GARAGE), L(1560, 3300 + 12 * k, 'bảo vệ, 2 nhân viên', 7, MUTED, 400, GARAGE),
          L(AXIS, 2830, 'SÂN DANH DỰ ±0.00', 9, INK, 600, PAVE), L(AXIS, 3790, 'ĐƯỜNG ĐT639 · TÂY', 10),
          L(AXIS, -500, 'BIỂN · ĐÔNG', 10, ACC, 600, '#F3F4F1'), L(-680, 300, 'NHÀ CŨ', 11, INK, 600, OLD, 'middle', -90),
          L(-600, 2600, 'SÂN NHÀ CŨ · lối xe ra', 8, MUTED, 400, '#EAEAE5', 'middle', -90),
          L(AXIS, -180, 'HỒ BƠI', 8, INK, 600, WATER), L(AXIS, 160, 'sân thượng', 8, INK, 600, TERR),
          L(-150, -470, 'lan can nhìn biển', 8, INK, 400, '#F3F4F1', 'start'), L(AXIS, 2130, 'porch', 8, INK, 600, TERR)]
    o += [path(f'M{AXIS} -400 V3600', ACC, 4, extra=' stroke-dasharray="40 24"')]
    o += compass(k, 1880, -500)
    draw = svg(SITE_VIEW, 640, 886,
               'Tổng mặt bằng: dinh thự 19 × 17 m giữa lô, trên trục chính từ cổng ra biển; phía đường là hai nhà cổng đối '
               'xứng, bắc là nhà xe 3 ô, nam là nhà cổng cho bảo vệ và nhân viên; giữa là cổng sắt; sân danh dự trước '
               'porch; xe vào cổng giữa, dừng ở bậc, ra qua sân nhà cũ; phía biển là sân thượng, thang móng ngựa, hồ bơi '
               'trên trục, hàng rào cây cắt tỉa và lan can nhìn biển', '\n'.join(o))
    rows = [
        ('Trục chính', 'khoảng 40 m', 'Cổng sắt giữa hai nhà cổng, sân danh dự, porch, dinh thự, sân thượng, hồ bơi, lan can nhìn biển: tất cả trên một đường.'),
        ('Hai nhà cổng', 'đối xứng, 9 × 6 m', 'Bắc là nhà xe 3 ô; nam là nhà cổng cho bảo vệ và hai phòng nhân viên. Trán tường thấp, cùng đá với nhà chính.'),
        ('Sân danh dự', 'sâu 6 m', 'Lát đá, xe vào cổng giữa, dừng trước bậc porch rồi ra qua sân nhà cũ phía bắc như lối cũ.'),
        ('Vườn biển', 'sâu 7 m, thấp 2,5 m', 'Sân thượng, thang móng ngựa, hồ bơi trên trục; hàng cây cắt tỉa hai bên; lan can đá ở mép lô nhìn ra biển.'),
        ('Mật độ', 'cần kiểm', 'Nhà chính 323 m², khối nối 27 m², porch 20 m², hai nhà cổng 108 m²: khoảng 54% lô 880 m². Phải đối chiếu quy định địa phương.'),
        ('Nhà cũ', 'nối liền', 'Khối nối 2,8 m lấp khe giữa hai nhà, cùng mái +15.00; nhà cũ ốp lại cùng ngôn ngữ. Xem DT8.'),
    ]
    right = side_title('Dinh thự trên một trục') + '\n' + '\n'.join(row(*r) for r in rows)
    left = caption('TỔNG MẶT BẰNG · BIỂN Ở TRÊN, BẮC BÊN TRÁI') + '\n' + draw
    return header('DT1', 'Tổng mặt bằng', 'Hai nhà cổng, sân danh dự, dinh thự, vườn biển') + '\n' + two_col(left, right, 640)


# ---------- DT0 · Ý tưởng ----------

def dt0():
    hero = front_drawing(900, 572, marks=False)
    principles = [
        ('Trục', 'một đường 40 m từ cổng ra biển',
         'Cổng, sân danh dự, porch, tiền sảnh, La Rotonda, Grand Salon, sân thượng, thang móng ngựa, hồ bơi, biển.'),
        ('Tỷ lệ', 'nền · thân · đầu như một cây cột',
         'Tầng 1 nền đá rusticated; tầng 2–3 gom bằng thức Corinth khổng lồ cao 8 m; trên cùng là entablature, lan can, trán tường.'),
        ('Enfilade', 'một đường cửa 29 m', 'Phòng ăn, Grand Salon, thư viện, khối nối, sảnh trước nhà cũ: hai nhà nối liền trên một đường cửa.'),
        ('La Rotonda', 'sảnh tròn, thang cong', 'Sảnh tròn Ø 7,4 m, hai vế thang cong ôm tường, thông ba tầng tới lồng đèn +18.90, cùng cao độ chóp vòm nhà cũ.'),
        ('Khí hậu', 'cổ điển nhưng chịu bão', 'Mái bằng sau lan can thay mái mansard; cửa chớp gỗ giấu trong ô tường; porch và sân thượng che mưa nắng.'),
    ]
    swatches = [('#E2D9C3', 'Đá vôi rusticated', 'nền tầng 1, tầng dưới'), ('#EFE8D8', 'Vữa vôi màu ngà', 'tường tầng 2–3'),
                ('#F8F4EA', 'Đá trắng', 'cột, phào, lan can'), ('#9AB0A4', 'Đồng xanh', 'vòm lồng đèn'),
                ('#2B2F33', 'Sắt rèn', 'cổng, lan can hào sáng'), ('#8FA7B0', 'Kính ô nhỏ', 'cửa sổ, cửa vòm')]
    sw = ('<div style="display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 10px 16px">' + ''.join(
        f'<div style="display: flex; gap: 8px; align-items: center"><div style="width: 30px; height: 30px; flex: none; '
        f'background: {c}; border: 1px solid #8E918C"></div><div style="display: flex; flex-direction: column">'
        f'<span style="font-size: 12.5px; font-weight: 600">{escape(a)}</span><span style="font-size: 11.5px; color: #4A5868">{escape(b)}</span></div></div>'
        for c, a, b in swatches) + '</div>')
    seq = ['Cổng', 'Sân danh dự', 'Porch', 'Tiền sảnh', 'La Rotonda', 'Grand Salon', 'Sân thượng', 'Thang móng ngựa', 'Hồ bơi', 'Biển']
    seq_html = ('<div style="display: flex; flex-wrap: wrap; align-items: center; gap: 6px 8px; font-size: 13px">' + ''.join(
        (f'<span style="padding: 5px 10px; border: 1px solid #C5CAC5; background: #FFFFFF">{escape(s)}</span>'
         + ('<span style="color: #7A5620">→</span>' if i < len(seq) - 1 else '')) for i, s in enumerate(seq)) + '</div>')
    left = ('<div style="display: flex; flex-direction: column; gap: 8px">'
            '<div style="font-size: 12px; font-weight: 600; letter-spacing: 2.4px; color: #7A5620">DINH THỰ TAM QUAN · TÂN CỔ ĐIỂN PHÁP – Ý</div>'
            "<div style=\"font-family: 'Cormorant Garamond', serif; font-weight: 600; font-size: 64px; line-height: 1\">Một dinh thự trên trục ra biển</div>"
            '<div style="font-size: 16px; line-height: 1.55; color: #4A5868; max-width: 880px">Thiết kế lại từ đầu theo lối dinh thự '
            'châu Âu thế kỷ 18: đối xứng tuyệt đối, thức cột khổng lồ, chuỗi phòng nối thẳng trục, và một lồng đèn mái vòm '
            'nói cùng ngôn ngữ với tháp vòm nhà cũ. Nhà cũ được nối liền, cùng cốt sàn +0.90, và ốp lại để hai nhà thành một dinh thự. Giữ đề bài của bộ CHỐT, cùng cao độ các tầng.</div></div>\n'
            + caption('MẶT ĐỨNG CHÍNH') + '\n' + hero + '\n' + caption('CHUỖI KHÔNG GIAN TRÊN TRỤC') + '\n' + seq_html)
    right = (side_title('Năm nguyên tắc') + '\n' + '\n'.join(row(*r) for r in principles) + '\n'
             + caption('VẬT LIỆU') + '\n' + sw)
    return header('DT0', 'Dinh thự Tam Quan', 'Ý tưởng · phong cách · nguyên tắc') + '\n' + two_col(left, right, 900)


OLD_HOUSE = 'M-1038 -742 H-190 V-220 H-320 V1250 H-720 V1130 H-1038 Z'


# ---------- Nối liền với nhà cũ ----------

LX0, LX1, LY0, LY1 = -320, -40, 300, 1250      # the link block between the old house and the new house


def old_house_reclad():
    """Old house front re-clad in the language of the new house: rusticated base to the band course,
    quoins, framed windows, the same entablature and balustrade at +15.00, copper dome."""
    x1, x2 = -1038, -320
    o = [rect(-700, Y(1660), 360, 160, WALL, LINE, 3), rect(-700, Y(1660), 26, 160, TRIM, LINE, 1.5),
         rect(-366, Y(1660), 26, 160, TRIM, LINE, 1.5)]
    o += window(-600, 1530, 44, 100, 'arch', 8, panes=2) + window(-440, 1530, 44, 100, 'arch', 8, panes=2)
    o += [rect(-714, Y(1680), 388, 20, TRIM, LINE, 2),
          path(f'M-690 {Y(1680)} A170 140 0 0 1 -350 {Y(1680)} Z', LINE, 3, COPPER),
          path(f'M-600 {Y(1680)} Q-575 {Y(1780)} -520 {Y(1820)} M-440 {Y(1680)} Q-465 {Y(1780)} -520 {Y(1820)}', LINE, 1.5),
          circle(-520, Y(1830), 10, COPPER, LINE, 1.5), path(f'M-520 {Y(1840)} V{Y(1890)}', LINE, 4)]
    o += rustication(x1, x2, 0, 590)
    o += [rect(x1, Y(1380), x2 - x1, 790, WALL, LINE, 3), rect(x1 - 10, Y(590), x2 - x1 + 20, 50, TRIM, LINE, 2.5)]
    for i, z in enumerate(range(640, 1380, 62)):
        w = 70 if i % 2 == 0 else 46
        o += [rect(x1, Y(z + 56), w, 56, TRIM, LINE, 1.5), rect(x2 - w, Y(z + 56), w, 56, TRIM, LINE, 1.5)]
    o += window(-878, 190, 100, 270, 'arch', 14, panes=3, keystone=True)
    o += window(-520, 90, 160, 400, 'arch', 18, door=True, keystone=True)
    o += [rect(-520 - (220 + i * 30) / 2, Y(90 - i * 18), 220 + i * 30, 18, TRIM, LINE, 1.5) for i in range(5)]
    for cx in (-878, -520):
        o += window(cx, 680, 100, 250, ped='tri', balcony=True, panes=4)
        o += window(cx, 1110, 100, 190, panes=3)
    o += entablature(x1 - 10, x2 + 10, 1380)
    o += balustrade(x1, x2, 1500, 100, 24, piers=(x1 + 22, -679, x2 - 22))
    for p in (x1 + 22, -679, x2 - 22):
        o += urn(p, 1600)
    return o


def link_elev():
    """The link block seen from the front: recessed, plain, with the family door."""
    o = rustication(LX0, LX1, 0, 590)
    o += [rect(LX0, Y(1380), LX1 - LX0, 790, '#E9E1CE', LINE, 3), rect(LX0, Y(590), LX1 - LX0, 50, TRIM, LINE, 2)]
    o += window(-180, 90, 120, 330, 'arch', 16, door=True, keystone=True)
    o += [rect(-180 - (160 + i * 24) / 2, Y(90 - i * 18), 160 + i * 24, 18, TRIM, LINE, 1.5) for i in range(5)]
    o += window(-180, 680, 100, 250, ped='seg', panes=4) + window(-180, 1110, 100, 190, panes=3)
    o += entablature(LX0, LX1, 1380, proj=10)
    o += balustrade(LX0, LX1, 1500, 100, 24, piers=(LX0 + 22, LX1 - 22))
    return o


def old_and_link(sea=False):
    """Old house and link for an elevation; on the sea side they stand on a stone plinth down to the garden."""
    o = []
    if sea:
        o += rustication(-1038, -40, -250, 0) + [path(f'M-1038 {Y(0)} H-40', LINE, 3)]
    return o + link_elev() + old_house_reclad()


def link_plan(k, level, show_old=True):
    """The link block in plan. level 1: +0.90, level with the old front hall (five steps above the yard)
    and the new ground floor, entered from the old yard up five steps.
    Upper levels: a short corridor with steps, to be fixed after the old floors are surveyed."""
    o = []
    if show_old:
        o.append(rect(-420 if level == 1 else -350, -480 if level == 1 else 120, 100 if level == 1 else 30,
                      1730 if level == 1 else 1130, OLD))
    o.append(rect(LX0, LY0, LX1 - LX0, LY1 - LY0, '#FFFFFF', INK, 18))
    if level == 1:
        o += treads(-250, LY1 + 12, 140, 150, 5)
        o += [rect(-250, LY0 - 20, 140, 40, '#FFFFFF', INK, 2), path(f'M-250 {LY0} H-110', INK, 2)]
        for g in ((LX1 - 25, 770, 30, 120), (LX0 - 30, 770, 30, 120), (-250, LY1 - 12, 140, 30)):
            o.append(gap(*g))
        o += [label(-180, 450, 'KHỐI NỐI', 8, k, INK, 600, 'middle', '#FFFFFF'),
              label(-180, 490, '+0.90', 7, k, MUTED, 400, 'middle', '#FFFFFF'),
              label(-180, 1010, 'không bậc', 7, k, ACC, 600, 'middle', '#FFFFFF'),
              label(-180, 1470, '5 bậc', 7, k, INK, 600, 'middle', '#F3F4F1')]
    else:
        o += treads(-300, 1100, 240, 120, 4, vertical=True)
        for g in ((LX1 - 25, 1160, 30, 80), (LX0 - 30, 500, 30, 120), (LX0 - 30, 900, 30, 120)):
            o.append(gap(*g))
        o.append(label(-170, 700, 'HÀNH LANG NỐI', 7, k, INK, 600, 'middle', '#FFFFFF', -90))
        o.append(label(-180, 1070, 'bậc · đo sau', 6, k, MUTED, 400, 'middle', '#FFFFFF'))
    return o


def dt8():
    # plan of the junction, old house in full
    pv = (-1100, -800, 1800, 2950)
    k = pv[2] / 537
    o = [rect(*pv, '#F3F4F1'), rect(-1038, -800, 848, 2950, '#EAEAE5'), rect(-190, -400, 900, 700, GREEN)]
    o.append(path(OLD_HOUSE, OLD_LINE, 22, OLD))
    o += [rect(-1016, 154, 674, 22, OLD_LINE), gap(-860, 150, 160, 30), rect(-342, -220, 22, 1470, OLD_LINE),
          path('M-1016 730 H-744 M-696 730 H-342', OLD_LINE, 3, extra=' stroke-dasharray="10 8"'),
          path('M-700 196 H-535 A190 190 0 0 1 -535 576 M-700 291 H-535 A95 95 0 0 1 -535 481 M-700 196 V291 M-535 481 V576',
               '#6F5A3A', 3)]
    o += room(X0, Y0, C0 - X0, 850, 'THƯ VIỆN', k, sub='+0.90 · 47 m²')
    o += room(X0, 1150, C0 - X0, 350, 'POWDER', k, px=8)
    o += room(X0, 1500, C0 - X0, 500, 'SẢNH PHỤ', k, px=8, sub='thang · TM')
    o += room(C0, Y0, 900, 650, '', k, area=False) + [rect(C0, 950, 900, 800, INK), circle(RX, RY, R_OUT, '#FFFFFF')]
    o += room(C0, 1750, 900, 250, '', k, area=False)
    o += [label(615, 625, 'GRAND SALON', 7, k, INK, 600, 'middle', '#FFFFFF', -90), label(615, 1350, 'LA ROTONDA', 7, k, INK, 600, 'middle', '#FFFFFF', -90),
          label(615, 1875, 'TIỀN SẢNH', 6, k, INK, 600, 'middle', '#FFFFFF', -90)]
    o += [rect(X0, Y0, 900, Y1 - Y0, 'none', INK, 40), rect(C0, 0, 300, 300, TERR, INK, 6)]
    o += link_plan(k, 1, show_old=False)
    o += [gap(500, 770, 25, 120), gap(X0 - 25, 760, 30, 140)]
    o += flush_late()
    o += [path('M-1016 830 H700', ACC, 5, extra=' stroke-dasharray="30 18"'),
          label(-680, -300, 'SALON BIỂN', 9, k, INK, 600, 'middle', OLD), label(-680, -255, 'nhà cũ', 7, k, MUTED, 400, 'middle', OLD),
          label(-880, 640, 'SẢNH SAU', 8, k, INK, 600, 'middle', OLD), label(-880, 680, 'thang · cao hơn 2 bậc', 7, k, MUTED, 400, 'middle', OLD),
          label(-680, 960, 'SẢNH TRƯỚC', 8, k, INK, 600, 'middle', OLD), label(-680, 1000, '+0.90 · sau 5 bậc', 7, k, MUTED, 400, 'middle', OLD), path('M-1016 730 H-744', OLD_LINE, 0), label(-880, 760, '2 bậc', 7, k, ACC, 600, 'middle', OLD),
          label(-520, 1400, 'HIÊN · 5 bậc', 8, k, INK, 600, 'middle', '#EAEAE5'),
          label(-640, 1800, 'SÂN NHÀ CŨ', 9, k, MUTED, 600, 'middle', '#EAEAE5'),
          label(-640, 1840, 'lối gia đình hằng ngày', 7, k, MUTED, 400, 'middle', '#EAEAE5'),
          label(-150, 810, 'enfilade 29 m', 8, k, ACC, 600, 'middle', '#FFFFFF'),
          arrow('M-180 1900 V1290', TEAL, -180, 1270, -90, k, w=1.4),
          
          label(600, -150, 'vườn −2.50', 7, k, GREEN_LINE, 600, 'middle', GREEN)]
    o += compass(k, 520, -650)
    plan = svg(pv, 537, 880,
               'Mặt bằng mối nối tầng 1: nhà cũ bên trái với salon biển, sảnh thang và phòng khách gia đình; khối nối 2,8 m '
               'ở giữa ở cốt +0.90, bằng sảnh trước nhà cũ và thư viện nhà mới, không bậc; cửa sổ nhìn vườn biển và cửa vào từ sân nhà '
               'cũ ở hai đầu; một đường enfilade 29 m chạy từ nhà cũ qua khối nối, thư viện, Grand Salon', '\n'.join(o))
    # front elevation of the junction
    ev = (-1100, -1950, 1800, 2050)
    ke = ev[2] / 395
    e = old_and_link() + front_facade()
    e += [path(f'M-1100 {Y(1500)} H700', ACC, 5, extra=' stroke-dasharray="24 14"'),
          label(-1080, Y(1760), 'đường mái +15.00 chạy suốt', 8, ke, ACC, 600, 'start', '#F3F4F1')]
    elev = svg(ev, 395, 450, 'Mặt đứng mối nối: nhà cũ ốp lại cùng nền đá, góc đá so le, khung cửa có trán, entablature '
               'và lan can như nhà mới, vòm tháp lợp đồng; khối nối lùi vào với cửa vòm gia đình; nhà mới bên phải', '\n'.join(e))
    # cross section through the link (north left)
    sv = (-1100, -1950, 1800, 2250)
    ks = sv[2] / 360
    s = [rect(-1100, Y(0), 1060, 300, EARTH), rect(-40, Y(-250), 740, 50, EARTH),
         rect(-1038, Y(1500), 718, 1500, OLD), rect(LX0, Y(1500), 280, 1500, '#FFFFFF'), rect(-40, Y(1500), 740, 1750, '#FFFFFF')]
    s += [rect(-1038, Y(1500), 22, 1500, OLD_LINE), rect(-342, Y(1500), 22, 1500, OLD_LINE), gap(-342, Y(330), 22, 240),
          rect(-1038, Y(90), 718, 90, EARTH), rect(-1038, Y(90), 718, 25, OLD_LINE), rect(-1038, Y(1500), 718, 25, OLD_LINE)]
    s += [path(f'M-1016 {Y(z)} H-342', OLD_LINE, 6, extra=' stroke-dasharray="20 14"') for z in (480, 950)]
    s += [rect(-700, Y(1660), 360, 160, WALL, LINE, 2), path(f'M-690 {Y(1680)} A170 140 0 0 1 -350 {Y(1680)} Z', LINE, 2.5, COPPER),
          path(f'M-520 {Y(1820)} V{Y(1890)}', LINE, 4)]
    s += [rect(-60, Y(1500), 40, 1750, INK), gap(-60, Y(390), 40, 300), gap(-60, Y(800), 40, 240), gap(-60, Y(1270), 40, 240)]
    for z in (-250, 90, 560, 1030, 1500):
        s.append(rect(-20, Y(z), 720, 30, INK))
    s += [rect(LX0, Y(90), 280, 90, EARTH), rect(LX0, Y(90), 280, 30, INK), rect(LX0, Y(560), 280, 30, INK), rect(LX0, Y(1030), 280, 30, INK), rect(LX0, Y(1500), 280, 30, INK)]
    s += [rect(-1038, Y(1500), 1738, 26, INK)] + balustrade(-1038, 700, 1500, 100, 24, piers=(-1016, -679, -320, -40, 300, 678))
    L = lambda x, z, t, px=8, c=INK, w=600, bg='#FFFFFF': label(x, Y(z), t, px, ks, c, w, 'middle', bg)
    s += [L(-679, 700, 'NHÀ CŨ', 9, INK, 600, OLD), L(-679, 640, 'sảnh trước +0.90', 7, MUTED, 400, OLD), L(-679, 590, 'tầng trên: đo tại chỗ', 7, MUTED, 400, OLD),
          L(-180, 760, 'NỐI', 8), L(330, 760, 'NHÀ MỚI', 9), L(330, 300, 'thư viện +0.90', 7, MUTED, 400),
          L(330, -110, 'phòng tập −2.50', 7, MUTED, 400), L(-180, 200, '+0.90', 7, ACC, 600),
          L(-120, 1700, '+15.00 chung', 7, ACC, 600, '#F3F4F1')]
    sect = svg(sv, 360, 450, 'Mặt cắt ngang qua khối nối: nhà cũ bên trái, sàn sảnh trước ở +0.90 sau năm bậc từ sân, cao độ các sàn trên cần đo; khối nối '
               'ở giữa cùng cốt +0.90 với sảnh trước nhà cũ và tầng 1 nhà mới, không bậc; nhà mới bên phải có tầng dưới −2.50; một entablature và một lan can chạy '
               'liền trên cả ba phần ở cốt +15.00', '\n'.join(s))
    rows = [
        ('Nối liền ở đâu', 'khối 2,8 × 9,5 m',
         'Lấp khe giữa tường đông nhà cũ và tường bắc nhà mới, suốt ba tầng, cùng mái. Hai nhà thành một khối, không còn khe hở.'),
        ('Một enfilade', 'dài 29 m',
         'Phòng ăn, Grand Salon, thư viện, khối nối, sảnh trước nhà cũ trên một đường cửa, không một bậc. Theo RB2, tường nhà cũ đã có lỗ cửa ở đây; cần kiểm tại chỗ.'),
        ('Cùng cốt +0.90', 'không bậc giữa hai nhà',
         'Nhà cũ có 5 bậc từ sân lên, tức sàn sảnh trước khoảng +0.90, bằng tầng 1 mới. Hai bậc lên sảnh sau trong nhà cũ giữ nguyên. Tầng 2, 3 chốt sau khi đo.'),
        ('Cửa gia đình', '5 bậc như hiên nhà cũ',
         'Đầu phía đường của khối nối là cửa vào hằng ngày từ sân nhà cũ và nhà xe, không qua tiền sảnh danh dự. Đầu phía biển là cửa sổ cao nhìn vườn.'),
        ('Một mặt tiền', 'cùng nền, phào, mái',
         'Nhà cũ ốp lại: nền rusticated tới +5.60, góc đá so le, cửa có khung và trán, entablature và lan can +15.00. Vòm tháp lợp đồng xanh.'),
        ('Kết cấu', 'khe lún ẩn',
         'Nhà mới móng sâu (có tầng dưới), nhà cũ móng nông: hai kết cấu đứng riêng, khe lún giấu sau ốp đá. Phải khảo sát móng nhà cũ trước.'),
    ]
    grid = ('<div style="display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 0 28px">'
            + ''.join('<div style="display: flex; flex-direction: column">' + '\n'.join(row(*r) for r in part) + '</div>'
                      for part in (rows[:3], rows[3:])) + '</div>')
    right = ('<div style="display: flex; gap: 24px">'
             '<div style="display: flex; flex-direction: column; gap: 6px">' + caption('MẶT ĐỨNG MỐI NỐI') + elev + '</div>'
             '<div style="display: flex; flex-direction: column; gap: 6px">' + caption('MẶT CẮT QUA KHỐI NỐI') + sect + '</div></div>\n'
             + grid)
    left = caption('TẦNG 1 · NHÀ CŨ, KHỐI NỐI, NHÀ MỚI') + '\n' + plan
    return header('DT8', 'Nối liền với nhà cũ', 'Một khối nối, một enfilade, một đường mái') + '\n' + two_col(left, right, 537)


BOARDS = [
    ('DT0', 'dt0-y-tuong', 'DT0YTuong.dc.html', 'Dinh thự Tam Quan – ý tưởng, phong cách, năm nguyên tắc', dt0),
    ('DT1', 'dt1-tong-mat-bang', 'DT1TongMatBang.dc.html', 'Tổng mặt bằng – hai nhà cổng, sân danh dự, vườn biển', dt1),
    ('DT2', 'dt2-tang-duoi', 'DT2TangDuoi.dc.html', 'Tầng dưới – ninfeo có hồ bơi trong hang vòm (cốt −2.50)', dt2),
    ('DT3', 'dt3-tang-1', 'DT3Tang1.dc.html', 'Tầng 1 – trục danh dự, enfilade, La Rotonda thang cong (cốt +0.90)', dt3),
    ('DT4', 'dt4-tang-2-3', 'DT4Tang23.dc.html', 'Tầng 2 và tầng 3 – gia đình và căn hộ chủ (cốt +5.60, +10.30)', dt4),
    ('DT5', 'dt5-mat-dung-chinh', 'DT5MatDungChinh.dc.html', 'Mặt đứng chính – nền đá, thức Corinth khổng lồ, trán tường', dt5),
    ('DT6', 'dt6-mat-dung-bien', 'DT6MatDungBien.dc.html', 'Mặt đứng phía biển – hang vòm, thang móng ngựa, sân thượng', dt6),
    ('DT7', 'dt7-mat-cat', 'DT7MatCat.dc.html', 'Mặt cắt dọc trục – hồ bơi, Grand Salon, La Rotonda, lồng đèn', dt7),
    ('DT8', 'dt8-noi-nha-cu', 'DT8NoiNhaCu.dc.html', 'Nối liền với nhà cũ – khối nối, enfilade 29 m, một đường mái', dt8),
]


def main():
    for code, slug, file, title, fn in BOARDS:
        (HERE / file).write_text(page(f'{code} · {title}', fn()), encoding='utf-8')
        print(file)
    manifest = {
        'order': 2,
        'project': 'Biệt thự Tam Quan',
        'set': 'Dinh thự Tam Quan',
        'eyebrow': 'Thiết kế mới · tân cổ điển Pháp – Ý',
        'heading': 'Dinh thự Tam Quan',
        'summary': 'Một dinh thự châu Âu trên trục từ cổng ra biển: nền đá rusticated, thức Corinth khổng lồ, La Rotonda thang cong, '
                   'Grand Salon nhìn biển, hồ bơi trong hang vòm. Nhà cũ nối liền thành một khối. Trọn bộ chín bản, từ ý tưởng tới mối nối.',
        'generator': 'design/dinh-thu/generate.py',
        'boards': [{'code': c, 'slug': s, 'file': fl, 'w': 1480, 'h': 1060, 'title': t} for c, s, fl, t, _ in BOARDS],
    }
    (HERE / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
