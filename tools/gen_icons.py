#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成 tabbar 线形图标（普通态/选中态）"""
from PIL import Image, ImageDraw
import math, os

S = 324          # 画布
LW = 20          # 线宽
OUT = os.path.join(os.path.dirname(__file__), '..', 'static', 'tabbar')
os.makedirs(OUT, exist_ok=True)

def canvas():
    img = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    return img, ImageDraw.Draw(img)

def line(d, pts, color, w=LW):
    d.line([tuple(p) for p in pts], fill=color, width=w, joint='curve')
    for p in (pts[0], pts[-1]):
        r = w / 2 - 1
        d.ellipse([p[0]-r, p[1]-r, p[0]+r, p[1]+r], fill=color)

def arc(d, box, a0, a1, color, w=LW):
    d.arc(box, a0, a1, fill=color, width=w)

def dot(d, x, y, r, color):
    d.ellipse([x-r, y-r, x+r, y+r], fill=color)

def save(img, name):
    img.resize((81, 81), Image.LANCZOS).save(os.path.join(OUT, name + '.png'))
    print('✓', name)

def icon_home(d, c):
    # 房子
    line(d, [(52, 172), (162, 74), (272, 172)], c)
    line(d, [(86, 158), (86, 258), (238, 258), (238, 158)], c)
    line(d, [(132, 258), (132, 196), (192, 196), (192, 258)], c)

def icon_book(d, c):
    # 打开的书
    arc(d, [52, 60, 200, 300], 200, 340, c)
    arc(d, [124, 60, 272, 300], 200, 340, c)
    line(d, [(162, 112), (162, 268)], c)
    for i, y in enumerate((150, 190, 230)):
        line(d, [(100 - i*6, y), (140 - i*4, y + 6)], c, 12)
        line(d, [(186 + i*4, y + 6), (226 + i*6, y)], c, 12)

def icon_yinyang(d, c):
    cx, cy, r = 162, 162, 108
    arc(d, [cx-r, cy-r, cx+r, cy+r], 0, 360, c)
    arc(d, [cx-r, cy-r, cx, cy+r], 270, 90, c)
    arc(d, [cx, cy-r, cx+r, cy+r], 90, 270, c)
    dot(d, cx, cy - 54, 16, c)
    dot(d, cx, cy + 54, 16, c)

def icon_ai(d, c):
    # 对话气泡 + 星
    arc(d, [52, 60, 272, 244], 180, 360, c)
    line(d, [(52, 152), (52, 196)], c)
    line(d, [(52, 196), (102, 246)], c)
    line(d, [(102, 246), (118, 262)], c)
    line(d, [(272, 152), (272, 196)], c)
    line(d, [(272, 196), (222, 246)], c)
    # 中心星形
    pts = []
    for i in range(8):
        ang = math.pi / 4 * i - math.pi / 2
        rr = 46 if i % 2 == 0 else 18
        pts.append((162 + rr * math.cos(ang), 150 + rr * math.sin(ang)))
    d.polygon(pts, fill=c)

def icon_user(d, c):
    dot(d, 162, 108, 52, None) if False else None
    arc(d, [110, 52, 214, 156], 0, 360, c)
    arc(d, [66, 178, 258, 350], 180, 360, c)
    line(d, [(66, 264), (66, 266)], c)

ICONS = {'home': icon_home, 'book': icon_book, 'yinyang': icon_yinyang, 'ai': icon_ai, 'user': icon_user}
for name, fn in ICONS.items():
    for suffix, color in [('', (138, 129, 114, 255)), ('-on', (154, 46, 31, 255))]:
        img, d = canvas()
        fn(d, color)
        save(img, name + suffix)

# logo: 从源图生成正方形 logo
src = os.path.join(os.path.dirname(__file__), '..', 'tools', 'logo_src.jpg')
dst = os.path.join(os.path.dirname(__file__), '..', 'static', 'logo.png')
if os.path.exists(src):
    im = Image.open(src).convert('RGB')
    w, h = im.size
    s = min(w, h)
    im = im.crop(((w-s)//2, (h-s)//2, (w+s)//2, (h+s)//2)).resize((240, 240), Image.LANCZOS)
    im.save(dst, quality=90)
    print('✓ logo.png')
