#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""界面功能图标 v1：与 tabbar v2 同设计语言（等线宽/圆头端点），多色版适配不同底色"""
from PIL import Image, ImageDraw
import math, os

S = 288          # 画布（4x 输出72px）
LW = 17
OUT = os.path.join(os.path.dirname(__file__), '..', 'static', 'icons')
os.makedirs(OUT, exist_ok=True)

GRAY = (138, 129, 114, 255)    # 暖灰（浅底）
LIGHT = (253, 248, 238, 255)   # 米白（深底）
BRAND = (154, 46, 31, 255)     # 朱砂
GOLD = (200, 164, 92, 255)     # 鎏金

class Pen:
    def __init__(self, d, color, w=LW):
        self.d, self.c, self.w = d, color, w
    def line(self, pts):
        self.d.line([tuple(p) for p in pts], fill=self.c, width=self.w, joint='curve')
        r = self.w / 2
        for p in (pts[0], pts[-1]):
            self.d.ellipse([p[0]-r, p[1]-r, p[0]+r, p[1]+r], fill=self.c)
    def arc(self, box, a0, a1, seg=42):
        cx, cy = (box[0]+box[2])/2, (box[1]+box[3])/2
        rx, ry = (box[2]-box[0])/2, (box[3]-box[1])/2
        pts = [(cx + rx*math.cos(math.radians(a0+(a1-a0)*i/seg)),
                cy + ry*math.sin(math.radians(a0+(a1-a0)*i/seg))) for i in range(seg+1)]
        self.line(pts)
    def dot(self, x, y, r):
        self.d.ellipse([x-r, y-r, x+r, y+r], fill=self.c)
    def rrect(self, box, r, outline=True):
        x0, y0, x1, y1 = box
        if outline:
            self.arc([x0, y0, x0+2*r, y0+2*r], 180, 270)
            self.arc([x1-2*r, y0, x1, y0+2*r], 270, 360)
            self.arc([x1-2*r, y1-2*r, x1, y1], 0, 90)
            self.arc([x0, y1-2*r, x0+2*r, y1], 90, 180)
            self.line([(x0+r, y0), (x1-r, y0)])
            self.line([(x1, y0+r), (x1, y1-r)])
            self.line([(x1-r, y1), (x0+r, y1)])
            self.line([(x0, y1-r), (x0, y0+r)])

def icon_search(d, c):
    p = Pen(d, c)
    p.arc([56, 56, 196, 196], 30, 360)
    p.line([(178, 178), (236, 236)])

def icon_settings(d, c):
    p = Pen(d, c)
    # 齿轮：8齿
    cx, cy, r1, r2 = 144, 144, 92, 66
    pts = []
    for i in range(16):
        a = math.pi/8*i
        r = r1 if i % 2 == 0 else r2
        pts.append((cx + r*math.cos(a), cy + r*math.sin(a)))
    d.polygon(pts, fill=c)
    # 中心镂空（画透明圆）
    d.ellipse([cx-34, cy-34, cx+34, cy+34], fill=(0,0,0,0))

def icon_trash(d, c):
    p = Pen(d, c)
    p.line([(88, 84), (200, 84)])
    p.line([(118, 84), (128, 56), (160, 56), (170, 84)])
    p.rrect([92, 84, 196, 236], 14)
    p2 = Pen(d, c, LW-6)
    p2.line([(126, 116), (126, 204)])
    p2.line([(162, 116), (162, 204)])

def icon_share(d, c):
    p = Pen(d, c)
    # 上箭头 + 托盘
    p.line([(144, 52), (144, 176)])
    p.line([(102, 94), (144, 52), (186, 94)])
    p.line([(64, 150), (64, 226), (224, 226), (224, 150)])

def icon_copy(d, c):
    p = Pen(d, c)
    p.rrect([76, 76, 196, 212], 16)     # 后卡
    p.rrect([96, 56, 216, 192], 16)     # 前卡（右上）

def icon_dice(d, c):
    p = Pen(d, c)
    p.rrect([52, 52, 236, 236], 34)
    r = 15
    p.dot(98, 98, r); p.dot(190, 98, r); p.dot(144, 144, r); p.dot(98, 190, r); p.dot(190, 190, r)

def icon_book(d, c):
    p = Pen(d, c)
    p.arc([48, 54, 144, 240], 205, 335)
    p.arc([144, 54, 240, 240], 205, 335)
    p.line([(144, 96), (144, 212)])
    p2 = Pen(d, c, LW-8)
    p2.line([(78, 132), (122, 144)])
    p2.line([(166, 144), (210, 132)])

def icon_star(d, c, filled=False):
    pts = []
    for i in range(10):
        a = math.pi/5*i - math.pi/2
        r = 100 if i % 2 == 0 else 42
        pts.append((144 + r*math.cos(a), 148 + r*math.sin(a)))
    if filled:
        d.polygon(pts, fill=c)
    else:
        Pen(d, c, LW-3).line(pts + [pts[0]])

def icon_swap(d, c):
    p = Pen(d, c)
    p.line([(60, 108), (212, 108)])
    p.line([(178, 76), (214, 108), (178, 140)])
    p.line([(228, 180), (76, 180)])
    p.line([(110, 148), (74, 180), (110, 212)])

def icon_arrow(d, c):  # 返回 ‹
    p = Pen(d, c, LW+2)
    p.line([(178, 62), (98, 144), (178, 226)])

SPECS = [
    ('search', icon_search, {'gray': GRAY, 'brand': BRAND}),
    ('settings', icon_settings, {'light': LIGHT}),
    ('trash', icon_trash, {'light': LIGHT}),
    ('share', icon_share, {'light': LIGHT}),
    ('copy', icon_copy, {'brand': BRAND, 'light': LIGHT}),
    ('dice', icon_dice, {'light': LIGHT}),
    ('book', icon_book, {'light': LIGHT}),
    ('star', icon_star, {'light': LIGHT, 'brand': BRAND}),
    ('back', icon_arrow, {'light': LIGHT, 'ink': (46,42,36,255)}),
    ('starfill', lambda d, c: icon_star(d, c, True), {'gold': GOLD, 'brand': BRAND}),
    ('swap', icon_swap, {'gold': GOLD, 'brand': BRAND}),
    ('scan', None, {}),
]

for name, fn, colors in SPECS:
    if fn is None: continue
    for cname, cval in colors.items():
        img = Image.new('RGBA', (S, S), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        # 齿轮镂空需要透明擦除 -> 用独立图层合成
        if name in ('settings', 'trash', 'scan'):
            layer = Image.new('RGBA', (S, S), (0, 0, 0, 0))
            dl = ImageDraw.Draw(layer)
            fn(dl, cval)
            img = Image.alpha_composite(img, layer)
        else:
            fn(d, cval)
        img.resize((72, 72), Image.LANCZOS).save(os.path.join(OUT, f'{name}-{cname}.png'))
        print('✓', f'{name}-{cname}')
print('done')
