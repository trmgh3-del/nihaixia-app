#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""输出方剂/本草详情字段完整率，避免数量增加但安全字段缺失。"""
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
formulas = json.loads((ROOT/'static/data/formulas.json').read_text())['items']
herbs = json.loads((ROOT/'static/data/bencao.json').read_text())['herbs']
def report(name, rows, fields):
    print(name, len(rows))
    for field in fields:
        n = sum(bool(x.get(field)) for x in rows)
        print(f'  {field}: {n}/{len(rows)} ({n/len(rows):.1%})')
report('formulas', formulas, ['zhizhi','composition','origin','clinical','doses','preparation','contraindication','meridian','category'])
report('herbs', herbs, ['原文','主治','倪注','用量','禁忌','canonicalName','natureCategory','meridians','category'])
