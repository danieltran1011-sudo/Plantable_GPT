#!/usr/bin/env python3
"""Generate the "Mở rộng tạm · chữ U" boards (U0–U2): a single-storey (cấp 4) temporary extension
for about five years, a U around the new lot that opens north onto the old house's front yard.

Reuses the drawing helpers of design/dinh-thu/generate.py. Plan coordinates are the same site grid:
sea (east) at the top, road (west) at the bottom, north to the left; new lot x −190..2010,
y −400..3600; old house to the north.

Usage: python3 design/mo-rong-tam/generate.py   (then run tools/build.py)
"""
import importlib.util
import json
from html import escape
from pathlib import Path

HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location('dinh_thu', HERE.parent / 'dinh-thu' / 'generate.py')
dt = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(dt)

rect, path, circle, label, arrow, svg, Y, room, gap, treads = (dt.rect, dt.path, dt.circle, dt.label, dt.arrow, dt.svg,
                                                                dt.Y, dt.room, dt.gap, dt.treads)
INK, MUTED, ACC, TERR, PAVE, GREEN, GREEN_LINE = dt.INK, dt.MUTED, dt.ACC, dt.TERR, dt.PAVE, dt.GREEN, dt.GREEN_LINE
OLD, OLD_LINE, WATER, WATER_LINE, TEAL, GARAGE = dt.OLD, dt.OLD_LINE, dt.WATER, dt.WATER_LINE, dt.TEAL, dt.GARAGE
WALL, RUSTIC, TRIM, LINE, GLASS, EARTH, IRON = dt.WALL, dt.RUSTIC, dt.TRIM, dt.LINE, dt.GLASS, dt.EARTH, dt.IRON

# the U: room bands 4.2 m deep (6 m on the road side), verandas 1.8 m on the court side
SEA = (-190, -400, 2200, 420)          # dãy biển, rooms y −400..20
SOUTH = (1590, 20, 420, 2980)          # dãy nam, rooms x 1590..2010, y 20..3000
ROAD = (-190, 3000, 2200, 600)         # dãy đường, rooms y 3000..3600
COURT = (-190, 200, 1600, 2620)        # sân trong x −190..1410, y 200..2820
VERANDAS = ((-190, 20, 1780, 180), (1410, 20, 180, 2980), (-190, 2820, 1780, 180))

SEA_ROOMS = [(-190, 900, 'PHÒNG KHÁCH', 'nhìn biển'), (710, 600, 'PHÒNG ĂN', None), (1310, 700, 'BẾP', None)]
# (start, length, name, note, door, windows): doors and windows sit midway between the 3 m veranda columns
SOUTH_ROOMS = [(20, 400, 'GIẶT · KHO', None, 350, ()), (420, 400, 'NHÂN VIÊN', None, 650, ()),
               (820, 580, 'PHÒNG TẬP', None, 1250, (950,)), (1400, 800, 'KHÁCH 1', 'ngủ + tắm', 1850, (1550, 2150)),
               (2200, 800, 'KHÁCH 2', 'ngủ + tắm', 2450, (2750,))]
VERANDA_COLS = list(range(200, 2821, 300)) + [2820]
ROAD_ROOMS = [(-190, 900, 'NHÀ XE 3 Ô', None, GARAGE), (710, 400, 'LỐI VÀO', '±0.00 · 5 bậc lên', PAVE),
              (1110, 450, 'BẢO VỆ', None, '#FFFFFF'), (1560, 450, 'GIÀY · POWDER', None, '#FFFFFF')]

PLAN_VIEW = (-1100, -820, 3250, 4720)


def base(k, ghost=False):
    """Site, old house, old yard, road, and the U drawn in full (or faint for the overlay board)."""
    o = [rect(-1100, -820, 3250, 4720, '#F3F4F1'), rect(-1038, -820, 848, 4420, '#EAEAE5'),
         rect(-190, -400, 2200, 4000, '#EFEDE4'), rect(-1100, 3600, 3250, 260, '#C6C7C1'),
         path(dt.OLD_HOUSE, OLD_LINE, 22, OLD),
         path('M-1038 3600 H-900 M-520 3600 H-190', INK, 10), path('M710 3600 V3600', INK, 1),
         label(-680, 300, 'NHÀ CŨ', 11, k, INK, 600, 'middle', OLD, -90), label(-680, 900, '+0.90', 8, k, MUTED, 400, 'middle', OLD),
         label(-610, 2300, 'SÂN NHÀ CŨ', 10, k, MUTED, 600, 'middle', '#EAEAE5'),
         label(-710, 3700, 'cổng cũ', 8, k, MUTED, 400, 'middle', '#C6C7C1'),
         label(910, 3790, 'ĐƯỜNG ĐT639 · TÂY', 10, k, INK, 600, 'middle', '#C6C7C1'),
         label(910, -560, 'BIỂN · ĐÔNG', 10, k, ACC, 600, 'middle', None)]
    if ghost:
        return o
    o += [rect(*COURT, GREEN), path('M-190 1510 H1410 M610 200 V2820', PAVE, 120),
          circle(610, 1510, 210, PAVE), circle(610, 1510, 120, WATER, WATER_LINE, 4)]
    o += [circle(x, y, 60, '#B8CBA8', GREEN_LINE, 3) for x, y in ((40, 430), (1180, 430), (40, 2590), (1180, 2590), (40, 1150), (1180, 1870))]
    o += [rect(100, 560, 1000, 380, 'none', WATER_LINE, 5, ' stroke-dasharray="22 14"'),
          label(600, 760, 'hồ bơi lắp ghép · tùy chọn', 8, k, WATER_LINE, 600, 'middle', GREEN)]
    for v in VERANDAS:
        o.append(rect(*v, TERR))
    cols = [(x, 200) for x in range(-40, 1411, 300)] + [(1410, y) for y in VERANDA_COLS] + [(x, 2820) for x in range(-40, 1411, 300)]
    o += [circle(x, y, 16, INK) for x, y in cols]
    for x, w, n, sub in SEA_ROOMS:
        o += room(x, -400, w, 420, n, k, sub=(f'{sub} · {dt.m2(w, 420)} m²' if sub else None))
        o += [gap(x + w / 2 - 70, 5, 140, 30)]
        o += [rect(cx - 60, -420, 120, 40, '#FFFFFF', INK, 2) for cx in range(int(x + 150), int(x + w - 100), 300)]
    for y, h, n, sub, door, wins in SOUTH_ROOMS:
        o += room(1590, y, 420, h, n, k, px=8, sub=(f'{sub} · {dt.m2(420, h)} m²' if sub else None))
        o += [gap(1575, door - 65, 30, 130)] + [rect(1570, w - 45, 40, 90, '#FFFFFF', INK, 2) for w in wins]
    for x, w, n, sub, fill in ROAD_ROOMS:
        o += room(x, 3000, w, 600, n, k, fill, px=8, sub=(f'{sub}' if sub else None))
        if n != 'LỐI VÀO':
            o += [gap(x + w / 2 - 60, 2985, 120, 30)]
    o += [gap(710, 2985, 400, 30), gap(730, 3585, 360, 30), path('M730 3600 H1090', IRON, 8, extra=' stroke-dasharray="20 10"'),
          gap(-150, 3585, 820, 30), path('M-150 3600 H670', INK, 4, extra=' stroke-dasharray="30 12"')]
    o += treads(710, 3010, 400, 150, 5)
    o += [path('M-190 20 V-400 H2010 V3600 H-190 V3000', INK, 28), path('M-190 20 H1590 V3000 H-190', INK, 18)]
    o += [gap(-205, -380, 30, 140), label(-215, -440, 'nối salon biển', 7, k, ACC, 600, 'end', '#F3F4F1')]
    o += dt.flush_late()
    o += [label(610, 1300, 'SÂN TRONG', 11, k, INK, 600, 'middle', GREEN),
          label(610, 1340, 'khoảng 420 m² · cốt đất hiện trạng', 8, k, MUTED, 400, 'middle', GREEN),
          label(610, 1510, 'giếng nước', 7, k, INK, 600, 'middle', WATER),
          label(470, 110, 'HIÊN 1,8 m', 8, k, INK, 600, 'middle', TERR), label(1500, 1150, 'HIÊN', 8, k, INK, 600, 'middle', TERR, -90),
          label(470, 2920, 'HIÊN', 8, k, INK, 600, 'middle', TERR),
          arrow('M300 2150 H-560', TEAL, -585, 2150, 180, k, w=1.6),
          label(-200, 2110, 'chữ U mở ra sân nhà cũ', 8, k, TEAL, 600, 'middle', '#EFEDE4')]
    return o


def compass(k):
    return [path('M1700 -640 H1980', INK, 6), path('M1700 -640 l50 -22 v44 z', INK, 0, INK),
            label(2040, -620, 'B', 10, k, INK, 600, 'middle', None)]


def u0():
    k = PLAN_VIEW[2] / 620
    plan = svg(PLAN_VIEW, 620, 900, 'Mặt bằng mở rộng tạm hình chữ U một tầng quanh lô mới, mở về phía bắc ra sân nhà cũ: '
               'dãy phía biển có phòng khách nhìn biển nối vào salon biển nhà cũ, phòng ăn và bếp; dãy dọc ranh nam có giặt '
               'kho, phòng nhân viên, phòng tập và hai phòng khách ngủ; dãy phía đường có nhà xe ba ô, lối vào có cổng, bảo '
               'vệ, giày và powder; hiên 1,8 m chạy quanh sân trong khoảng 420 mét vuông có lối đá chữ thập, giếng nước và '
               'hồ bơi lắp ghép tùy chọn', '\n'.join(base(k) + compass(k)))
    rows = [
        ('Ý chính', 'một sân chung với nhà cũ',
         'Ba dãy nhà một tầng ôm ba cạnh lô mới; cạnh bắc để trống, nên sân trong và sân trước nhà cũ thành một sân lớn khoảng 25 × 26 m.'),
        ('Dãy biển', 'khách · ăn · bếp',
         'Phòng khách 38 m² nhìn biển nối thẳng vào salon biển nhà cũ; phòng ăn 25 m², bếp 29 m². Cửa sổ quay ra biển, cửa đi ra hiên.'),
        ('Dãy nam', 'phục vụ · tập · khách ngủ',
         'Giặt kho và phòng nhân viên sát bếp; phòng tập 24 m²; hai phòng khách ngủ có tắm, 34 m² mỗi phòng. Lưng tựa ranh nam, lấy sáng từ hiên.'),
        ('Dãy đường', 'nhà xe · cổng · bảo vệ',
         'Nhà xe 3 ô mở ra đường; lối vào có cổng sắt, 5 bậc lên hiên như hiên nhà cũ; bảo vệ, giày dép, powder.'),
        ('Cốt sàn', '+0.90 như nhà cũ',
         'Mọi phòng ở +0.90, nối nhà cũ không thêm bậc. Nhà xe và lối vào ở ±0.00 theo đường. Sân trong giữ đất hiện trạng; cần đo cốt.'),
        ('Diện tích', 'khoảng 350 m² phòng',
         'Phòng 92 + 125 + 132 m², hiên khoảng 120 m². Nếu thấy lớn, bỏ một phòng khách ngủ hoặc thu dãy nam ngắn lại.'),
    ]
    right = dt.side_title('Chữ U quanh một sân') + '\n' + '\n'.join(dt.row(*r) for r in rows)
    left = dt.caption('MẶT BẰNG · BIỂN Ở TRÊN, BẮC BÊN TRÁI · CỐT SÀN +0.90') + '\n' + plan
    return dt.header('U0', 'Mở rộng tạm · chữ U', 'Một tầng, khoảng 5 năm · mở ra sân nhà cũ') + '\n' + dt.two_col(left, right, 620)


def u1():
    # elevation of the south-wing veranda seen from the court (sea on the left)
    ev = (-150, -640, 3300, 700)
    ke = ev[2] / 1416
    e = [rect(-150, Y(0), 3300, 60, '#E7EADF'), path(f'M-150 {Y(0)} H3150', GREEN_LINE, 5)]
    e += [rect(20, Y(560), 2980, 470, WALL, LINE, 3)]
    for y, h, n, sub, door, wins in SOUTH_ROOMS:
        e += dt.window(door, 90, 130, 250, panes=4)
        for w in wins:
            e += dt.window(w, 200, 90, 140, panes=2)
    e += [rect(20, Y(90), 2980, 90, RUSTIC, LINE, 2)]
    for yy in VERANDA_COLS:
        e += dt.column(yy, 90, 420, 26, 'tuscan')
    e += [rect(10, Y(480), 3000, 60, TRIM, LINE, 2.5), rect(0, Y(500), 3020, 20, TRIM, LINE, 2),
          rect(10, Y(570), 3000, 70, WALL, LINE, 2), rect(0, Y(585), 3020, 15, TRIM, LINE, 2)]
    for yy in (650, 1550, 2450):
        e += [rect(yy - 90, Y(90), 180, 90, TRIM, LINE, 1.5)] + [rect(yy - 90 - i * 25, Y(90 - (i + 1) * 30), 180 + i * 50, 30, TRIM, LINE, 1.2) for i in range(3)]
    e += [label(-120, Y(300), '← dãy biển', 9, ke, ACC, 600, 'start', None), label(3120, Y(300), 'dãy đường →', 9, ke, ACC, 600, 'end', None)]
    e += [label(1510, Y(-40), 'bậc xuống sân theo cốt đất', 8, ke, MUTED, 400, 'middle', None)]
    elev = svg(ev, 1416, 300, 'Mặt đứng hiên dãy nam nhìn từ sân trong: nền đá thấp cao 0,9 m, hàng cột Tuscan mảnh nhịp '
               '3 m đỡ dầm có phào, tường chắn mái che mái tôn; phía sau là cửa đi kính và cửa sổ của các phòng; ba chỗ có '
               'bậc xuống sân', '\n'.join(e))
    # cross section north–south through the court: old house beyond, court, south wing
    sv = (-1150, -1950, 3450, 2250)
    ks = sv[2] / 700
    s = [rect(-1150, Y(0), 3300, 200, EARTH), path(f'M-1150 {Y(0)} H2150', LINE, 4)]
    s += [rect(-1038, Y(1500), 718, 1500, OLD, OLD_LINE, 4), rect(-700, Y(1640), 360, 140, OLD, OLD_LINE, 4),
          path(f'M-690 {Y(1640)} A170 180 0 0 1 -350 {Y(1640)} Z', OLD_LINE, 4, '#D8CFB8'),
          label(-679, Y(800), 'nhà cũ phía sau', 9, ks, MUTED, 600, 'middle', OLD)]
    s += [rect(1410, Y(90), 600, 90, RUSTIC, LINE, 2), rect(1590, Y(410), 420, 320, '#FFFFFF'),
          rect(1590, Y(90), 420, 20, INK), rect(1590, Y(410), 20, 320, INK), rect(1990, Y(560), 20, 470, INK),
          path(f'M1380 {Y(430)} L2010 {Y(520)}', INK, 14), rect(1360, Y(450), 50, 30, IRON),
          rect(1415, Y(420), 22, 330, TRIM, LINE, 2), rect(1975, Y(580), 50, 20, TRIM, LINE, 2)]
    s += [path(f'M-190 {Y(0)} V{Y(-40)} M1410 {Y(0)} V{Y(90)}', LINE, 3)]
    L = lambda x, z, t, px=9, c=INK, w=600, bg='#FFFFFF': label(x, Y(z), t, px, ks, c, w, 'middle', bg)
    s += [L(610, 60, 'SÂN TRONG · đất hiện trạng', 9, GREEN_LINE, 600, '#F3F4F1'), L(1800, 250, 'PHÒNG', 9),
          L(1500, 250, 'HIÊN', 8, INK, 600, '#F3F4F1'), L(-600, 60, 'SÂN NHÀ CŨ ±0.00', 8, MUTED, 400, '#F3F4F1'),
          L(1700, 650, 'mái tôn dốc 10°, giấu sau tường', 8, ACC, 600, '#F3F4F1')]
    s += dt.level_marks(2030, ks, ((0, '±0.00'), (90, '+0.90'), (580, '+5.80')))
    sect = svg(sv, 700, 456, 'Mặt cắt bắc nam qua sân trong: nhà cũ cao khoảng 18,9 m ở phía sau bên trái; sân trong ở cốt đất '
               'hiện trạng; dãy nam bên phải một tầng sàn +0.90, hiên có cột, mái tôn dốc về phía sân, tường chắn mái cao '
               'khoảng 5,8 m', '\n'.join(s))
    rows = [
        ('Khung', 'thép hộp mạ kẽm', 'Cột, dầm, xà gồ thép bắt bu-lông trên móng đơn bê tông nông: sau 5 năm tháo ra, phần lớn thép và tôn dùng lại được.'),
        ('Tường', 'gạch nhẹ trát vữa vôi', 'Gạch bê tông khí chưng áp, trát và sơn màu ngà như dinh thự; vách trong bằng panel nhẹ.'),
        ('Mái', 'tôn cách nhiệt, chống bão', 'Tôn ba lớp dốc 10° về phía sân, vít có đệm, đai giằng chống tốc mái; tường chắn mái có phào che kín mái tôn.'),
        ('Hiên', 'cột Tuscan mảnh', 'Cột ống thép bọc vữa Ø 26 cm, nhịp 3 m, dầm có phào: kiểu barchessa của villa Ý, rẻ mà cùng ngôn ngữ dinh thự.'),
        ('Cửa', 'nhôm kính, cửa chớp', 'Cửa đi kính ra hiên; dãy biển có cửa chớp nhôm giả gỗ đóng được khi bão.'),
        ('Nhà cũ vẫn là nhân vật chính', 'cao 4,8–5,8 m', 'Nhà tạm thấp, chỉ một tầng, không che tháp vòm và mặt tiền nhà cũ nhìn từ sân.'),
    ]
    grid = ('<div style="display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 0 24px">'
            + ''.join('<div style="display: flex; flex-direction: column">' + '\n'.join(dt.row(*r) for r in part) + '</div>'
                      for part in (rows[:3], rows[3:])) + '</div>')
    bottom = ('<div style="display: flex; gap: 32px">'
              '<div style="width: 700px; flex: none; display: flex; flex-direction: column; gap: 6px">'
              + dt.caption('MẶT CẮT BẮC – NAM QUA SÂN TRONG') + sect + '</div>'
              '<div style="flex: 1; min-width: 0">' + grid + '</div></div>')
    top = '<div style="display: flex; flex-direction: column; gap: 6px">' + dt.caption('MẶT ĐỨNG HIÊN DÃY NAM · NHÌN TỪ SÂN TRONG') + elev + '</div>'
    return dt.header('U1', 'Hiên, mặt cắt, cách làm', 'Cấp 4 khung thép · dùng 5 năm · dễ tháo') + '\n' + top + '\n' + bottom


def u2():
    k = PLAN_VIEW[2] / 620
    o = base(k, ghost=True)
    o += [rect(*COURT, '#E7EDE0')]
    for r in (SEA, SOUTH):
        o.append(rect(*r, '#F6D9CC', '#B0502C', 6, ' stroke-dasharray="20 12"'))
    for v in VERANDAS:
        o.append(rect(*v, '#FBEDE6', '#B0502C', 3, ' stroke-dasharray="12 10"'))
    o += [rect(*ROAD, GARAGE, ACC, 10)]
    o += [rect(dt.X0, dt.Y0, dt.X1 - dt.X0, dt.Y1 - dt.Y0, 'none', INK, 14, ' stroke-dasharray="40 20"'),
          rect(dt.C0, dt.Y1, dt.C1 - dt.C0, 250, 'none', INK, 8, ' stroke-dasharray="24 14"'),
          rect(dt.LX0, dt.LY0, dt.LX1 - dt.LX0, dt.LY1 - dt.LY0, 'none', INK, 8, ' stroke-dasharray="24 14"'),
          circle(dt.RX, dt.RY, dt.R_OUT, 'none', INK, 6)]
    L = lambda x, y, t, px=9, c=INK, w=600, bg='#FFFFFF': label(x, y, t, px, k, c, w, 'middle', bg)
    o += [L(910, 1150, 'DINH THỰ SAU NÀY', 10, INK, 600, '#E7EDE0'), L(910, 1190, 'nét đứt', 8, MUTED, 400, '#E7EDE0'),
          L(910, -200, 'DÃY BIỂN · tháo, dùng lại thép, tôn, cửa', 8, '#B0502C', 600, '#F6D9CC'),
          L(1800, 1500, 'DÃY NAM · tháo', 7, '#B0502C', 600, '#F6D9CC', ),
          L(910, 3300, 'DÃY ĐƯỜNG · giữ lại làm nhà xe và nhà cổng', 8, INK, 600, GARAGE)]
    o += compass(k)
    plan = svg(PLAN_VIEW, 620, 900, 'Chồng mặt bằng: chữ U tạm và dinh thự sau này. Dãy biển và dãy nam nằm trong vùng xây dinh '
               'thự và sẽ tháo; dãy đường trùng vị trí nhà xe và nhà cổng của dinh thự nên có thể làm kiên cố ngay và giữ lại; '
               'dinh thự, khối nối và porch vẽ nét đứt', '\n'.join(o))
    steps = [
        ('Năm 0', 'xây chữ U', 'Khoảng 4–6 tháng cho khung thép và hoàn thiện. Nhà cũ ở bình thường trong lúc làm, sân nhà cũ vẫn là lối chính.'),
        ('Năm 1–5', 'ở nhà cũ + chữ U', 'Dùng song song với nhà cũ. Trong thời gian này làm khảo sát (cốt sàn, móng nhà cũ, nước ngầm), thiết kế kỹ thuật và xin phép dinh thự.'),
        ('Năm 5', 'tháo dãy biển và dãy nam', 'Hai dãy này nằm đúng chỗ dinh thự và tầng dưới −2.50. Thép, tôn, cửa nhôm tháo ra bán lại hoặc dùng cho kho, chòi vườn.'),
        ('Giữ lại', 'dãy đường', 'Dãy đường trùng vị trí nhà xe 3 ô và nhà cổng của dinh thự (DT1). Nên làm phần này kiên cố ngay từ đầu, cùng đá và phào, rồi giữ luôn.'),
        ('Đừng làm', 'trong vùng nét đứt', 'Không đổ móng sâu, không trồng cây lớn xuống đất, không chôn bể nước trong vùng dinh thự: cây trồng chậu, đường điện nước đi nổi dễ tháo.'),
        ('Pháp lý', 'cần hỏi', 'Công trình tạm có thời hạn phải được phép theo quy định địa phương; nên hỏi trước khi làm, nhất là phần sát ranh nam.'),
    ]
    right = dt.side_title('Năm năm, rồi dinh thự') + '\n' + '\n'.join(dt.row(*r) for r in steps)
    left = dt.caption('CHỒNG MẶT BẰNG · CHỮ U TẠM VÀ DINH THỰ SAU NÀY') + '\n' + plan
    return dt.header('U2', 'Lộ trình 5 năm', 'Cái gì tháo, cái gì giữ khi xây dinh thự') + '\n' + dt.two_col(left, right, 620)


BOARDS = [
    ('U0', 'u0-mo-rong-chu-u', 'U0MatBang.dc.html', 'Mở rộng tạm chữ U – mặt bằng, mở ra sân nhà cũ', u0),
    ('U1', 'u1-hien-mat-cat', 'U1HienMatCat.dc.html', 'Hiên dãy nam, mặt cắt qua sân, cách làm cấp 4', u1),
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
        'summary': 'Nhà một tầng cấp 4 ôm ba cạnh lô mới, mở ra sân nhà cũ thành một sân chung. Cùng cốt +0.90 với nhà cũ, '
                   'khung thép dễ tháo; dãy phía đường có thể giữ lại làm nhà xe và nhà cổng của dinh thự.',
        'generator': 'design/mo-rong-tam/generate.py',
        'boards': [{'code': c, 'slug': s, 'file': f, 'w': 1480, 'h': 1060, 'title': t} for c, s, f, t, _ in BOARDS],
    }
    (HERE / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
