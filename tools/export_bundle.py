#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""导出热更新数据包：合并 static/data/*.json -> data-update.json
（部署到任意静态服务器/OSS，App 内「内容更新」页填地址即可热更新）"""
import json, os, sys

SRC = os.path.join(os.path.dirname(__file__), '..', 'static', 'data')
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), '..', 'data-update.json')

SKIP = ['skill_raw']  # 132KB SKILL 原文也可含；默认包含则去掉此行
MERGE = {}
for fn in os.listdir(SRC):
    if not fn.endswith('.json'):
        continue
    key = fn[:-5]
    if key in SKIP:
        continue
    with open(os.path.join(SRC, fn), encoding='utf-8') as f:
        MERGE[key] = json.load(f)

with open(OUT, 'w', encoding='utf-8') as f:
    json.dump(MERGE, f, ensure_ascii=False, separators=(',', ':'))
size = os.path.getsize(OUT) / 1024 / 1024
print(f'✓ data-update.json 已生成：{OUT}（{size:.1f} MB，{len(MERGE)} 个数据集）')
