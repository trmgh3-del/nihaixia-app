#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成 1024×1024 App 图标（朱砂底 + 经方印章）"""
from PIL import Image, ImageDraw, ImageFont
import math, os

S = 2048  # 2x 超采样
OUT = os.path.join(os.path.dirname(__file__), '..', 'static')

# 配色
BG_TOP = (154, 46, 31)     # 朱砂红
BG_BOT = (100, 26, 16)     # 深朱砂  
SEAL_COL = (253, 248, 238)  # 米白
GOLD = (246, 231, 201)     # 鎏金
DARK = (60, 15, 8)

img = Image.new('RGB', (S, S), BG_TOP)
d = ImageDraw.Draw(img)

# ===== 背景：对角渐变 =====
for y in range(S):
    t = y / S
    r = int(BG_TOP[0] + (BG_BOT[0] - BG_TOP[0]) * t)
    g = int(BG_TOP[1] + (BG_BOT[1] - BG_TOP[1]) * t)
    b = int(BG_TOP[2] + (BG_BOT[2] - BG_TOP[2]) * t)
    d.line([(0, y), (S, y)], fill=(r, g, b))

# ===== 装饰：太极圆弧（右上角） =====
d2 = ImageDraw.Draw(img, 'RGBA')
cx, cy, r = int(S * 0.82), int(S * 0.18), int(S * 0.28)
d2.ellipse([cx-r, cy-r, cx+r, cy+r], outline=(246, 231, 201, 25), width=12)
d2.arc([cx-r+60, cy-r+60, cx+r-60, cy+r-60], 0, 180, fill=(246, 231, 201, 18), width=10)

# ===== 装饰：本草纹样（左下角圆点阵） =====
for i in range(5):
    for j in range(3):
        x = int(S * 0.08) + i * 70
        y = int(S * 0.82) + j * 70
        r2 = 12 if (i + j) % 2 == 0 else 8
        d2.ellipse([x-r2, y-r2, x+r2, y+r2], fill=(246, 231, 201, 20))

# ===== 中央印章：「經方」二字 =====
# 字体尝试列表
font_paths = [
    '/usr/share/fonts/truetype/noto/NotoSansCJK-Bold.ttc',
    '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
    '/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc',
    '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc',
    '/System/Library/Fonts/PingFang.ttc',
    '/System/Library/Fonts/STHeiti Medium.ttc',
    'C:/Windows/Fonts/msyhbd.ttc',
]

font = None
for fp in font_paths:
    if os.path.exists(fp):
        try:
            font = ImageFont.truetype(fp, int(S * 0.36))
            break
        except:
            continue

if font is None:
    # 无字体时用纯图形：太极图案
    cx, cy, r = S // 2, S // 2, S // 3
    # 大圆
    d.ellipse([cx-r, cy-r, cx+r, cy+r], fill=SEAL_COL)
    # S曲线
    d.pieslice([cx-r, cy-r, cx+r, cy], 180, 360, fill=DARK)
    d.pieslice([cx-r, cy, cx+r, cy+r], 0, 180, fill=SEAL_COL)
    # 两个小圆
    r2 = r // 4
    d.ellipse([cx-r2, cy-r-r2, cx+r2, cy-r+r2], fill=DARK)
    d.ellipse([cx-r2, cy-r2, cx+r2, cy+r2], fill=SEAL_COL)
    r3 = r // 8
    d.ellipse([cx-r3, cy-r-r3, cx+r3, cy-r+r3], fill=SEAL_COL)
    d.ellipse([cx-r3, cy-r3, cx+r3, cy+r3], fill=DARK)
else:
    # 印章方框
    box_size = int(S * 0.62)
    bx = (S - box_size) // 2
    by = (S - box_size) // 2
    # 外框
    border_w = int(S * 0.02)
    d.rounded_rectangle([bx, by, bx + box_size, by + box_size], radius=int(S * 0.06),
                        outline=SEAL_COL, width=border_w)
    # 内框（细线）
    inset = border_w + int(S * 0.015)
    d.rounded_rectangle([bx + inset, by + inset, bx + box_size - inset, by + box_size - inset],
                        radius=int(S * 0.045), outline=(246, 231, 201, 100), width=max(3, int(S * 0.004)))

    # 「經方」竖排两字
    chars = ['經', '方']
    char_size = int(S * 0.26)
    char_spacing = int(S * 0.32)
    start_y = S // 2 - char_spacing // 2 - char_size // 3
    for i, ch in enumerate(chars):
        bbox = d.textbbox((0, 0), ch, font=font)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        x = S // 2 - tw // 2
        y = start_y + i * char_spacing
        d.text((x, y), ch, fill=SEAL_COL, font=font)

# ===== 底部装饰：金线 =====
line_y = int(S * 0.92)
d.line([(int(S * 0.2), line_y), (int(S * 0.8), line_y)], fill=GOLD, width=6)
# 中央小菱形
d_size = 14
d_x = S // 2
d.polygon([(d_x, line_y - d_size), (d_x + d_size, line_y), (d_x, line_y + d_size), (d_x - d_size, line_y)], fill=GOLD)

# ===== 圆角裁切（iOS风格） =====
mask = Image.new('L', (S, S), 0)
md = ImageDraw.Draw(mask)
# iOS 圆角约为边长的22.5%
corner = int(S * 0.225)
md.rounded_rectangle([0, 0, S, S], radius=corner, fill=255)
img.putalpha(mask)

# ===== 输出多种尺寸 =====
# 1024×1024（App Store / 高清）
img_1024 = img.resize((1024, 1024), Image.LANCZOS)
img_1024.save(os.path.join(OUT, 'icon-1024.png'))
print('✓ icon-1024.png (1024×1024)')

# 144×144（Android xxxhdpi）
img_144 = img.resize((144, 144), Image.LANCZOS)
img_144.save(os.path.join(OUT, 'icon-144.png'))
print('✓ icon-144.png (144×144)')

# 96×96（Android xxhdpi）  
img_96 = img.resize((96, 96), Image.LANCZOS)
img_96.save(os.path.join(OUT, 'icon-96.png'))
print('✓ icon-96.png (96×96)')

# 72×72（Android xhdpi）
img_72 = img.resize((72, 72), Image.LANCZOS)
img_72.save(os.path.join(OUT, 'icon-72.png'))
print('✓ icon-72.png (72×72)')

# 48×48（Android hdpi）
img_48 = img.resize((48, 48), Image.LANCZOS)
img_48.save(os.path.join(OUT, 'icon-48.png'))
print('✓ icon-48.png (48×48)')

# 预览图
img_preview = img.resize((300, 300), Image.LANCZOS)
img_preview.save('/tmp/icon-preview.png')
print('✓ preview saved')
print('\n全尺寸图标生成完成')
