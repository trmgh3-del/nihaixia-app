#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tabbar 图标 v2：统一视觉语言（等线宽/圆头端点/呼吸留白），选中态 朱砂+鎏金 双色点缀"""
from PIL import Image, ImageDraw
import math, os

S = 360          # 画布（4.44x 输出，抗锯齿）
LW = 21          # 主线宽
GOLD = (200, 164, 92, 255)    # 鎏金 #C8A45C
OUT = os.path.join(os.path.dirname(__file__), '..', 'static', 'tabbar')
os.makedirs(OUT, exist_ok=True)

def C(color, alpha=255):
    return (color[0], color[1], color[2], alpha)

def canvas():
    return Image.new('RGBA', (S, S), (0, 0, 0, 0)), None

class Pen:
    """圆头笔画：线段+端点圆，弧线分段描"""
    def __init__(self, d, color, w=LW):
        self.d, self.c, self.w = d, color, w
    def line(self, pts):
        self.d.line([tuple(p) for p in pts], fill=self.c, width=self.w, joint='curve')
        r = self.w / 2
        for p in (pts[0], pts[-1]):
            self.d.ellipse([p[0]-r, p[1]-r, p[0]+r, p[1]+r], fill=self.c)
    def arc(self, box, a0, a1, seg=48):
        cx, cy = (box[0]+box[2])/2, (box[1]+box[3])/2
        rx, ry = (box[2]-box[0])/2, (box[3]-box[1])/2
        pts = []
        for i in range(seg+1):
            a = math.radians(a0 + (a1-a0)*i/seg)
            pts.append((cx + rx*math.cos(a), cy + ry*math.sin(a)))
        self.line(pts)
    def circle(self, x, y, r, fill=True):
        if fill:
            self.d.ellipse([x-r, y-r, x+r, y+r], fill=self.c)
        else:
            self.arc([x-r, y-r, x+r, y+r], 0, 360)
    def dot(self, x, y, r):
        self.d.ellipse([x-r, y-r, x+r, y+r], fill=self.c)

# ---------- 五枚图标 ----------
def icon_home(d, col, gold):
    p = Pen(d, col)
    # 屋顶（带烟囱）+ 墙体 + 拱门
    p.line([(56, 175), (180, 72), (304, 175)])
    p.line([(104, 150), (104, 264), (256, 264), (256, 150)])
    p.arc([150, 196, 210, 262], 180, 360)   # 拱门
    p.line([(150, 264), (150, 229)])
    p.line([(210, 264), (210, 229)])
    # 烟囱（鎏金点缀，仅选中态有色；普通态同色）
    g = Pen(d, gold, LW-4)
    g.line([(236, 96), (236, 60)])
    g.dot(236, 46, 11)

def icon_book(d, col, gold):
    p = Pen(d, col)
    # 打开的书：左右页弧 + 书脊
    p.arc([60, 62, 180, 300], 210, 330)
    p.arc([180, 62, 300, 300], 210, 330)
    p.line([(180, 110), (180, 268)])
    # 页线
    pl = Pen(d, col, LW-8)
    pl.line([(100, 158), (152, 172)])
    pl.line([(100, 202), (152, 216)])
    pl.line([(208, 172), (260, 158)])
    pl.line([(208, 216), (260, 202)])
    # 书签（金）
    g = Pen(d, gold, LW-6)
    g.line([(180, 108), (180, 84)])
    g.dot(180, 68, 12)

def icon_yinyang(d, col, gold):
    p = Pen(d, col)
    cx, cy, r = 180, 184, 112
    p.arc([cx-r, cy-r, cx+r, cy+r], 0, 360)
    p.arc([cx-r, cy-r, cx, cy+r], 270, 90)
    p.arc([cx, cy-r, cx+r, cy+r], 90, 270)
    p.dot(cx, cy - 56, 17)
    # 鱼眼用鎏金
    g = Pen(d, gold, LW)
    g.dot(cx, cy + 56, 17)

def icon_ai(d, col, gold):
    p = Pen(d, col)
    # 圆角对话气泡 + 尾角
    p.arc([58, 66, 302, 240], 150, 390)
    p.line([(128, 232), (96, 272)])
    # 三点
    p.dot(138, 152, 14); p.dot(180, 152, 14); p.dot(222, 152, 14)
    # 顶右星光（金）
    g = Pen(d, gold, LW-8)
    pts = []
    for i in range(10):
        ang = math.pi/5*i - math.pi/2
        rr = 26 if i % 2 == 0 else 11
        pts.append((296 + rr*math.cos(ang), 62 + rr*math.sin(ang)))
    d.polygon(pts, fill=gold)

def icon_user(d, col, gold):
    p = Pen(d, col)
    p.circle(180, 116, 54, fill=False)
    p.arc([70, 190, 290, 356], 182, 358)
    # 领结金点
    g = Pen(d, gold, LW-6)
    g.dot(180, 288, 13)

ICONS = {'home': icon_home, 'book': icon_book, 'yinyang': icon_yinyang, 'ai': icon_ai, 'user': icon_user}
NORMAL = (138, 129, 114, 255)   # #8A8172
ACTIVE = (154, 46, 31, 255)     # #9A2E1F

for name, fn in ICONS.items():
    # 普通态：单色（金点缀用半透明主色，保持素雅）
    img, _ = canvas()
    d = ImageDraw.Draw(img)
    fn(d, NORMAL, (138, 129, 114, 200))
    img.resize((81, 81), Image.LANCZOS).save(os.path.join(OUT, name + '.png'))
    # 选中态：朱砂主色 + 鎏金点缀
    img, _ = canvas()
    d = ImageDraw.Draw(img)
    fn(d, ACTIVE, GOLD)
    img.resize((81, 81), Image.LANCZOS).save(os.path.join(OUT, name + '-on.png'))
    print('✓', name, '/', name + '-on')
print('done')
