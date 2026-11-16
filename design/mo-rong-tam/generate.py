#!/usr/bin/env python3
"""Generate the "Mở rộng tạm · chữ U" boards (U0–U2): a single-storey (cấp 4) temporary extension
for about five years, drawn from the owner's sketch: a U in the road half of the new lot, its sea wing
touching the side of the old house, its road wing along the street with a passage through it, and the
open side facing the old house's front yard; a two-post gate on the street next to the road wing.

Reuses the drawing helpers of design/dinh-thu/generate.py. Plan coordinates are the same site grid:
sea (east) at the top, road (west) at the bottom, north to the left; new lot x −190..2010,
y −400..3600; old house to the north.

Usage: python3 design/mo-rong-tam/generate.py   (then run tools/build.py)
"""
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location('dinh_thu', HERE.parent / 'dinh-thu' / 'generate.py')
dt = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(dt)

rect, path, circle, label, arrow, svg, Y, room, gap, treads = (dt.rect, dt.path, dt.circle, dt.label, dt.arrow, dt.svg,
                                                                dt.Y, dt.room, dt.gap, dt.treads)
INK, MUTED, ACC, TERR, PAVE, GREEN, GREEN_LINE = dt.INK, dt.MUTED, dt.ACC, dt.TERR, dt.PAVE, dt.GREEN, dt.GREEN_LINE
OLD, OLD_LINE, WATER, WATER_LINE, TEAL, GARAGE = dt.OLD, dt.OLD_LINE, dt.WATER, dt.WATER_LINE, dt.TEAL, dt.GARAGE
WALL, RUSTIC, TRIM, LINE, EARTH, IRON = dt.WALL, dt.RUSTIC, dt.TRIM, dt.LINE, dt.EARTH, dt.IRON

# ----- geometry, read from the sketch and rounded -----
EAST = (-190, 600, 1450, 450)          # cánh biển: rooms y 600..1050, x −190..1260
SOUTH = (810, 1050, 450, 1950)         # cánh nam: rooms x 810..1260, y 1050..3000
ROAD = (-190, 3000, 1450, 600)         # cánh đường: rooms y 3000..3600, x −190..1260
COURT = (-190, 1200, 850, 1650)        # sân trong x −190..660, y 1200..2850 (opens north onto the old yard)
VERANDAS = ((-190, 1050, 1000, 150), (660, 1050, 150, 1950), (-190, 2850, 1000, 150))
LINK = (-320, 600, 130, 450)           # piece that closes the 1.3 m strip up to the old house wall

EAST_ROOMS = [(-190, 590, 'PHÒNG ĂN'), (400, 460, 'BẾP'), (860, 400, 'GIẶT · KHO')]
# (start y, length, name, note, doors, windows): openings sit midway between the 3 m veranda columns
SOUTH_ROOMS = [(1050, 800, 'PHÒNG KHÁCH', None, (1350, 1650), ()), (1850, 500, 'PHÒNG TẬP', None, (2250,), (1950,)),
               (2350, 650, 'KHÁCH NGỦ', 'ngủ + tắm', (2550,), (2775,))]
COLS_SOUTH = [1200, 1500, 1800, 2100, 2400, 2700, 2850]
ROAD_ROOMS = [(-190, 340, 'BẢO VỆ', None, '#FFFFFF'), (150, 270, 'GIÀY · WC', None, '#FFFFFF'),
              (420, 300, 'LỐI VÀO', 'xuyên qua', PAVE), (720, 540, 'NHÀ XE 2 Ô', None, GARAGE)]
GATE = (-600, -190)                    # two-post gate on the street, next to the road wing

PLAN_VIEW = (-1100, -820, 3250, 4720)


def site(k):
    return [rect(-1100, -820, 3250, 4720, '#F3F4F1'), rect(-1038, -820, 848, 4420, '#EAEAE5'),
            rect(-190, -400, 2200, 4000, '#EFEDE4'), rect(-1100, 3600, 3250, 260, '#C6C7C1'),
            path(dt.OLD_HOUSE, OLD_LINE, 22, OLD),
            label(-680, 300, 'NHÀ CŨ', 11, k, INK, 600, 'middle', OLD, -90), label(-680, 900, '+0.90', 8, k, MUTED, 400, 'middle', OLD),
            label(910, 3790, 'ĐƯỜNG ĐT639 · TÂY', 10, k, INK, 600, 'middle', '#C6C7C1'),
            label(910, -560, 'BIỂN · ĐÔNG', 10, k, ACC, 600, 'middle', None)]


def gate(k):
    a, b = GATE
    return [path(f'M{a} 3600 H{b}', IRON, 8, extra=' stroke-dasharray="26 14"'), circle(a, 3600, 45, TRIM, INK, 5),
            circle(b, 3600, 45, TRIM, INK, 5), label((a + b) / 2, 3700, 'cổng hai trụ', 8, k, INK, 600, 'middle', '#C6C7C1'),
            path('M-1038 3600 H-640 M1260 3600 H2010', INK, 8)]


def plan_u(k):
    o = [rect(-190, -400, 2200, 1000, GREEN), rect(1260, 600, 750, 3000, '#E7EDE0'),
         label(910, 100, 'VƯỜN TẠM PHÍA BIỂN', 10, k, GREEN_LINE, 600, 'middle', GREEN),
         label(910, 140, 'nửa lô phía biển để trống · xem các ý V1–V6', 8, k, GREEN_LINE, 400, 'middle', GREEN),
         label(1640, 2000, 'VƯỜN BÊN · lối phục vụ', 8, k, GREEN_LINE, 600, 'middle', '#E7EDE0', -90)]
    o += [rect(*COURT, GREEN), rect(-1038, 1250, 848, 2350, '#E9EBDF'),
          path('M-760 2050 H660', PAVE, 120), circle(240, 2050, 170, PAVE), circle(240, 2050, 95, WATER, WATER_LINE, 4)]
    o += [circle(x, y, 55, '#B8CBA8', GREEN_LINE, 3) for x, y in ((-80, 1330), (540, 1330), (-80, 2720), (540, 2720))]
    for v in VERANDAS:
        o.append(rect(*v, TERR))
    cols = [(x, 1200) for x in (-40, 260, 560)] + [(660, y) for y in COLS_SOUTH] + [(x, 2850) for x in (-40, 260, 560)]
    o += [circle(x, y, 15, INK) for x, y in cols]
    for x, w, n in EAST_ROOMS:
        o += room(x, 600, w, 450, n, k, px=8)
        o += [gap(x + w / 2 - 60, 1035, 120, 30), rect(x + w / 2 - 70, 580, 140, 40, '#FFFFFF', INK, 2)]
    for y, h, n, sub, doors, wins in SOUTH_ROOMS:
        o += room(810, y, 450, h, n, k, px=8, sub=(f'{sub} · {dt.m2(450, h)} m²' if sub else None))
        o += [gap(795, d - 65, 30, 130) for d in doors] + [rect(790, w - 45, 40, 90, '#FFFFFF', INK, 2) for w in wins]
        o += [rect(1240, y + h / 2 - 60, 40, 120, '#FFFFFF', INK, 2)]
    for x, w, n, sub, fill in ROAD_ROOMS:
        o += room(x, 3000, w, 600, n, k, fill, px=7.5, sub=sub)
        if n not in ('LỐI VÀO', 'NHÀ XE 2 Ô'):
            o += [gap(x + w / 2 - 55, 2985, 110, 30)]
    o += [gap(420, 2985, 300, 30), gap(430, 3585, 280, 30), path('M430 3600 H710', IRON, 8, extra=' stroke-dasharray="18 10"'),
          gap(740, 3585, 500, 30), path('M740 3600 H1240', INK, 4, extra=' stroke-dasharray="30 12"'), gap(740, 2985, 160, 30)]
    o += [path('M420 3020 A280 300 0 0 1 720 3020', ACC, 5), path('M420 3580 A280 300 0 0 0 720 3580', ACC, 5)]
    o += [rect(*LINK, '#FFFFFF', INK, 14), gap(-335, 770, 30, 120), gap(-205, 780, 30, 100)]
    o += [path('M-320 600 H1260 V3600 H-190 V3000 M-320 1050 H810 V3000 H-190 V3000', INK, 24)]
    o += dt.flush_late()
    o += [label(240, 1700, 'SÂN TRONG', 10, k, INK, 600, 'middle', GREEN),
          label(240, 1740, 'mở ra sân nhà cũ', 8, k, MUTED, 400, 'middle', GREEN),
          label(-610, 1700, 'SÂN NHÀ CŨ', 10, k, MUTED, 600, 'middle', '#E9EBDF'),
          label(-610, 1740, 'gộp với sân trong', 8, k, MUTED, 400, 'middle', '#E9EBDF'),
          label(240, 2050, 'giếng', 7, k, INK, 600, 'middle', WATER),
          label(320, 1140, 'HIÊN', 7, k, INK, 600, 'middle', TERR), label(735, 2400, 'HIÊN', 7, k, INK, 600, 'middle', TERR, -90),
          label(320, 2940, 'HIÊN', 7, k, INK, 600, 'middle', TERR),
          label(-480, 830, 'cửa sẵn có', 7, k, ACC, 600, 'end', OLD)]
    return o


def compass(k):
    return [path('M1700 -640 H1980', INK, 6), path('M1700 -640 l50 -22 v44 z', INK, 0, INK),
            label(2040, -620, 'B', 10, k, INK, 600, 'middle', None)]


def u0():
    k = PLAN_VIEW[2] / 620
    plan = svg(PLAN_VIEW, 620, 900, 'Mặt bằng mở rộng tạm hình chữ U theo phác thảo: chữ U ở nửa phía đường của lô mới, mở về '
               'phía bắc ra sân trước nhà cũ. Cánh phía biển chạm hông nhà cũ qua lỗ cửa sẵn có, gồm phòng ăn, bếp, giặt kho. '
               'Cánh nam gồm phòng khách, phòng tập, phòng khách ngủ có tắm. Cánh phía đường gồm bảo vệ, giày và WC, lối vào '
               'xuyên qua, nhà xe hai ô. Cổng hai trụ trên mặt đường cạnh cánh đường. Nửa lô phía biển để làm vườn tạm.',
               '\n'.join(site(k) + plan_u(k) + gate(k) + compass(k)))
    rows = [
        ('Theo phác thảo', 'chữ U ở nửa phía đường',
         'Chữ U chiếm nửa lô mới phía đường, mở về phía bắc ra sân nhà cũ. Nửa phía biển để trống làm vườn tạm. Kích thước tôi làm tròn từ hình vẽ tay.'),
        ('Cánh biển', 'chạm hông nhà cũ',
         'Phòng ăn 27 m², bếp 21 m², giặt kho 18 m². Đầu phía bắc nối vào nhà cũ qua lỗ cửa sẵn có ở tường hông, chỗ sau này là khối nối của dinh thự.'),
        ('Cánh nam', 'khách · tập · khách ngủ',
         'Phòng khách 36 m² hai cửa ra hiên, phòng tập 23 m², phòng khách ngủ có tắm 29 m². Phía nam còn dải vườn bên 7,5 m làm lối phục vụ.'),
        ('Cánh đường', 'lối vào xuyên qua',
         'Lối vào có mái xuyên qua cánh đường ra sân trong; hai bên là bảo vệ, giày dép và WC, nhà xe 2 ô mở ra đường. Cổng hai trụ ở mặt đường cho xe vào sân.'),
        ('Sân chung', 'khoảng 17 × 16 m',
         'Sân trong 8,5 × 16,5 m gộp với sân trước nhà cũ thành một sân. Hiên 1,5 m có cột chạy quanh ba cạnh.'),
        ('Cốt và diện tích', '+0.90 · khoảng 240 m²',
         'Mọi phòng ở +0.90 như nhà cũ; lối vào, nhà xe ở ±0.00. Khoảng 222 m² phòng, 18 m² lối vào, 55 m² hiên.'),
    ]
    right = dt.side_title('Chữ U theo phác thảo') + '\n' + '\n'.join(dt.row(*r) for r in rows)
    left = dt.caption('MẶT BẰNG · BIỂN Ở TRÊN, BẮC BÊN TRÁI · CỐT SÀN +0.90') + '\n' + plan
    return dt.header('U0', 'Mở rộng tạm · chữ U', 'Theo phác thảo · một tầng, khoảng 5 năm') + '\n' + dt.two_col(left, right, 620)


def u1():
    # elevation of the south-wing veranda seen from the court (sea on the left)
    ev = (800, -640, 2540, 680)
    ke = ev[2] / 1416
    e = [rect(800, Y(0), 2540, 60, '#E7EADF'), path(f'M800 {Y(0)} H3340', GREEN_LINE, 5),
         rect(1050, Y(560), 1950, 470, WALL, LINE, 3)]
    for y, h, n, sub, doors, wins in SOUTH_ROOMS:
        for d in doors:
            e += dt.window(d, 90, 130, 250, panes=4)
        for w in wins:
            e += dt.window(w, 200, 90, 140, panes=2)
    e += [rect(1050, Y(90), 1950, 90, RUSTIC, LINE, 2)]
    for yy in COLS_SOUTH:
        e += dt.column(yy, 90, 420, 26, 'tuscan')
    e += [rect(1040, Y(480), 1970, 60, TRIM, LINE, 2.5), rect(1030, Y(500), 1990, 20, TRIM, LINE, 2),
          rect(1040, Y(570), 1970, 70, WALL, LINE, 2), rect(1030, Y(585), 1990, 15, TRIM, LINE, 2)]
    for yy in (1650, 2550):
        e += [rect(yy - 90 - i * 25, Y(90 - i * 30), 180 + i * 50, 30, TRIM, LINE, 1.2) for i in range(3)]
    e += [label(1030, Y(300), 'cánh biển ←', 9, ke, ACC, 600, 'end', None), label(3020, Y(300), '→ cánh đường', 9, ke, ACC, 600, 'start', None),
          label(2100, Y(-40), 'bậc xuống sân theo cốt đất', 8, ke, MUTED, 400, 'middle', None)]
    elev = svg(ev, 1416, 379, 'Mặt đứng hiên cánh nam nhìn từ sân trong: nền đá thấp 0,9 m, hàng cột Tuscan mảnh nhịp 3 m đỡ dầm '
               'có phào, tường chắn mái che mái tôn; phía sau là hai cửa phòng khách, cửa và cửa sổ phòng tập, phòng khách ngủ; '
               'hai chỗ có bậc xuống sân', '\n'.join(e))
    # cross section north–south through the court at y ≈ 2000
    sv = (-1150, -1950, 3450, 2250)
    ks = sv[2] / 700
    s = [rect(-1150, Y(0), 3450, 200, EARTH), path(f'M-1150 {Y(0)} H2300', LINE, 4)]
    s += [rect(-1038, Y(1500), 718, 1500, OLD, OLD_LINE, 4), rect(-700, Y(1640), 360, 140, OLD, OLD_LINE, 4),
          path(f'M-690 {Y(1640)} A170 180 0 0 1 -350 {Y(1640)} Z', OLD_LINE, 4, '#D8CFB8'),
          label(-679, Y(800), 'nhà cũ phía sau', 9, ks, MUTED, 600, 'middle', OLD)]
    s += [rect(660, Y(90), 600, 90, RUSTIC, LINE, 2), rect(810, Y(410), 450, 320, '#FFFFFF'),
          rect(810, Y(90), 450, 20, INK), rect(810, Y(410), 20, 320, INK), rect(1240, Y(560), 20, 470, INK),
          path(f'M630 {Y(430)} L1260 {Y(520)}', INK, 14), rect(610, Y(450), 50, 30, IRON),
          rect(665, Y(420), 22, 330, TRIM, LINE, 2), rect(1225, Y(580), 50, 20, TRIM, LINE, 2),
          rect(2000, Y(200), 20, 200, INK)]
    L = lambda x, z, t, px=9, c=INK, w=600, bg='#FFFFFF': label(x, Y(z), t, px, ks, c, w, 'middle', bg)
    s += [L(235, 60, 'SÂN TRONG', 9, GREEN_LINE, 600, '#F3F4F1'), L(1035, 250, 'PHÒNG', 9), L(735, 250, 'HIÊN', 8, INK, 600, '#F3F4F1'),
          L(-600, 60, 'SÂN NHÀ CŨ', 8, MUTED, 400, '#F3F4F1'), L(1630, 60, 'VƯỜN BÊN', 8, GREEN_LINE, 600, '#F3F4F1'),
          L(1000, 680, 'mái tôn dốc 10°, giấu sau tường', 8, ACC, 600, '#F3F4F1'), L(2010, 250, 'ranh', 7, MUTED, 400, '#F3F4F1')]
    s += dt.level_marks(2120, ks, ((0, '±0.00'), (90, '+0.90'), (580, '+5.80')))
    sect = svg(sv, 700, 456, 'Mặt cắt bắc nam qua sân trong: nhà cũ cao ở phía sau bên trái; sân nhà cũ và sân trong liền nhau; '
               'cánh nam một tầng sàn +0.90 với hiên có cột và mái tôn dốc về phía sân; dải vườn bên đến tường ranh',
               '\n'.join(s))
    rows = [
        ('Khung', 'thép hộp mạ kẽm', 'Cột, dầm, xà gồ thép bắt bu-lông trên móng đơn bê tông nông: sau 5 năm tháo ra, phần lớn thép và tôn dùng lại được.'),
        ('Tường', 'gạch nhẹ trát vữa vôi', 'Gạch bê tông khí chưng áp, trát và sơn màu ngà như dinh thự; vách trong bằng panel nhẹ.'),
        ('Mái', 'tôn cách nhiệt, chống bão', 'Tôn ba lớp dốc 10° về phía sân, vít có đệm, đai giằng chống tốc mái; tường chắn mái có phào che kín mái tôn.'),
        ('Hiên', 'cột Tuscan mảnh', 'Cột ống thép bọc vữa Ø 26 cm, nhịp 3 m, dầm có phào: kiểu barchessa của villa Ý, rẻ mà cùng ngôn ngữ dinh thự.'),
        ('Lối vào xuyên', 'vòm ở cánh đường', 'Lối vào có mái xuyên qua cánh đường, hai đầu viền vòm; cửa sắt ở phía đường, mở thẳng vào sân trong.'),
        ('Nhà cũ vẫn là chính', 'cao 4,8–5,8 m', 'Nhà tạm một tầng, thấp, không che tháp vòm và mặt tiền nhà cũ nhìn từ sân.'),
    ]
    grid = ('<div style="display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 0 24px">'
            + ''.join('<div style="display: flex; flex-direction: column">' + '\n'.join(dt.row(*r) for r in part) + '</div>'
                      for part in (rows[:3], rows[3:])) + '</div>')
    bottom = ('<div style="display: flex; gap: 32px">'
              '<div style="width: 700px; flex: none; display: flex; flex-direction: column; gap: 6px">'
              + dt.caption('MẶT CẮT BẮC – NAM QUA SÂN TRONG') + sect + '</div>'
              '<div style="flex: 1; min-width: 0">' + grid + '</div></div>')
    top = '<div style="display: flex; flex-direction: column; gap: 6px">' + dt.caption('MẶT ĐỨNG HIÊN CÁNH NAM · NHÌN TỪ SÂN TRONG') + elev + '</div>'
    return dt.header('U1', 'Hiên, mặt cắt, cách làm', 'Cấp 4 khung thép · dùng 5 năm · dễ tháo') + '\n' + top + '\n' + bottom


def u2():
    k = PLAN_VIEW[2] / 620
    o = site(k) + [rect(*COURT, '#E7EDE0'), rect(-190, -400, 2200, 1000, '#EEF2E8')]
    for r in (EAST, SOUTH, LINK):
        o.append(rect(*r, '#F6D9CC', '#B0502C', 6, ' stroke-dasharray="20 12"'))
    for v in VERANDAS:
        o.append(rect(*v, '#FBEDE6', '#B0502C', 3, ' stroke-dasharray="12 10"'))
    o += [rect(*ROAD, GARAGE, ACC, 8)] + gate(k)
    o += [rect(dt.X0, dt.Y0, dt.X1 - dt.X0, dt.Y1 - dt.Y0, 'none', INK, 14, ' stroke-dasharray="40 20"'),
          rect(dt.C0, dt.Y1, dt.C1 - dt.C0, 250, 'none', INK, 8, ' stroke-dasharray="24 14"'),
          rect(dt.LX0, dt.LY0, dt.LX1 - dt.LX0, dt.LY1 - dt.LY0, 'none', INK, 8, ' stroke-dasharray="24 14"'),
          circle(dt.RX, dt.RY, dt.R_OUT, 'none', INK, 6),
          rect(-190, 3000, 900, 600, 'none', INK, 6, ' stroke-dasharray="16 10"'), rect(1110, 3000, 900, 600, 'none', INK, 6, ' stroke-dasharray="16 10"')]
    L = lambda x, y, t, px=9, c=INK, w=600, bg='#FFFFFF': label(x, y, t, px, k, c, w, 'middle', bg)
    o += [L(1450, 1200, 'DINH THỰ SAU NÀY', 9, INK, 600, '#EFEDE4'), L(1450, 1240, 'nét đứt', 8, MUTED, 400, '#EFEDE4'),
          L(540, 830, 'CÁNH BIỂN · tháo', 8, '#B0502C', 600, '#F6D9CC'), L(1035, 2400, 'CÁNH NAM · tháo', 7, '#B0502C', 600, '#F6D9CC', ),
          L(535, 3300, 'CÁNH ĐƯỜNG', 8, INK, 600, GARAGE), L(535, 3340, 'giữ nếu dời lối vào', 7, INK, 400, GARAGE),
          L(1560, 3300, 'nhà cổng dinh thự', 7, MUTED, 400, '#EFEDE4')]
    o += compass(k)
    plan = svg(PLAN_VIEW, 620, 900, 'Chồng mặt bằng: chữ U tạm theo phác thảo và dinh thự sau này. Cánh biển, cánh nam và phần nối '
               'vào nhà cũ nằm trong vùng dinh thự và sẽ tháo; cánh đường nằm trên dải nhà xe và nhà cổng của dinh thự, giữ lại '
               'được nếu lối vào dời về trục dinh thự; dinh thự, khối nối, porch và hai nhà cổng vẽ nét đứt', '\n'.join(o))
    steps = [
        ('Năm 0', 'xây chữ U', 'Khoảng 3–5 tháng cho khung thép và hoàn thiện. Nhà cũ ở bình thường trong lúc làm.'),
        ('Năm 1–5', 'ở nhà cũ + chữ U', 'Trong thời gian này làm khảo sát (cốt sàn, móng nhà cũ, nước ngầm), thiết kế kỹ thuật và xin phép dinh thự.'),
        ('Năm 5', 'tháo cánh biển và cánh nam', 'Hai cánh này và phần nối nằm đúng chỗ dinh thự. Thép, tôn, cửa nhôm tháo ra bán lại hoặc làm kho, chòi vườn.'),
        ('Cánh đường', 'có thể giữ', 'Nằm đúng dải nhà xe và nhà cổng của dinh thự (DT1). Muốn giữ thì dời lối vào xuyên (nay cách ranh bắc khoảng 7,6 m) sang trục dinh thự, cách ranh bắc 11 m, và đổi nhà xe sang phía bắc.'),
        ('Mối nối với nhà cũ', 'dùng lại chỗ cũ', 'Lỗ cửa nhà cũ dùng cho chữ U cũng là chỗ khối nối của dinh thự (DT8); không cần đục thêm tường cũ.'),
        ('Đừng làm', 'trong vùng nét đứt', 'Không đổ móng sâu, không trồng cây lớn xuống đất, không chôn bể nước trong vùng dinh thự; cây trồng chậu, điện nước đi nổi.'),
    ]
    right = dt.side_title('Năm năm, rồi dinh thự') + '\n' + '\n'.join(dt.row(*r) for r in steps)
    left = dt.caption('CHỒNG MẶT BẰNG · CHỮ U TẠM VÀ DINH THỰ SAU NÀY') + '\n' + plan
    return dt.header('U2', 'Lộ trình 5 năm', 'Cái gì tháo, cái gì giữ khi xây dinh thự') + '\n' + dt.two_col(left, right, 620)


BOARDS = [
    ('U0', 'u0-mo-rong-chu-u', 'U0MatBang.dc.html', 'Mở rộng tạm chữ U theo phác thảo – mặt bằng', u0),
    ('U1', 'u1-hien-mat-cat', 'U1HienMatCat.dc.html', 'Hiên cánh nam, mặt cắt qua sân, cách làm cấp 4', u1),
    ('U2', 'u2-lo-trinh-5-nam', 'U2LoTrinh.dc.html', 'Lộ trình 5 năm – tháo gì, giữ gì khi xây dinh thự', u2),
]


def main():
    for code, slug, file, title, fn in BOARDS:
        (HERE / file).write_text(dt.page(f'{code} · {title}', fn()), encoding='utf-8')
        print(file)
    manifest = {
        'order': 3,
        'project': 'Biệt thự Tam Quan',
        'set': 'Mở rộng tạm',
        'eyebrow': 'Giai đoạn 1 · công trình tạm khoảng 5 năm',
        'heading': 'Mở rộng tạm hình chữ U',
        'summary': 'Theo phác thảo: nhà một tầng cấp 4 hình chữ U ở nửa lô mới phía đường, cánh biển chạm hông nhà cũ, '
                   'mở ra sân nhà cũ thành một sân chung; lối vào xuyên qua cánh đường, cổng hai trụ trên mặt đường.',
        'generator': 'design/mo-rong-tam/generate.py',
        'boards': [{'code': c, 'slug': s, 'file': f, 'w': 1480, 'h': 1060, 'title': t} for c, s, f, t, _ in BOARDS],
    }
    (HERE / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
