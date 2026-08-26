#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""合并上游 nihaixia-app 的结构化方剂/本草，不覆盖本项目已有的同名详注。"""
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('/tmp/upstream-app/assets/data')

def norm(s): return ''.join(str(s or '').strip().lower().replace('（','(').replace('）',')').split())

def read(name): return json.loads((SRC / name).read_text(encoding='utf-8'))

# 方剂：保留当前项目同名条目，补入上游结构化字段。
fp = ROOT / 'static/data/formulas.json'; current = json.loads(fp.read_text(encoding='utf-8'))
items = current.get('items', []); names = {norm(x.get('n')) for x in items}
for f in read('formulas.json').get('formulas', []):
    n = f.get('name', '')
    if norm(n) in names: continue
    comps = f.get('components') or []
    comp_text = '、'.join(str(c.get('name','')) + ((' ' + str(c.get('dosage'))) if c.get('dosage') else '') for c in comps)
    items.append({'id': 'up_' + str(f.get('id') or len(items)), 'n': n, 'origin': comp_text, 'clinical': f.get('indication',''), 'note': '别名：' + f.get('alias','') + ('；' if f.get('alias') else '') + f.get('explanation','') + ('；禁忌：' + f.get('contraindication','') if f.get('contraindication') else ''), 'src': '上游 nihaixia-app · ' + str(f.get('category',''))})
    names.add(norm(n))
current['items'] = items
fp.write_text(json.dumps(current, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')

# 本草：旧字段全部保留；上游字段映射到当前阅读器字段，同时保留炮制、归经和比较资料。
hp = ROOT / 'static/data/bencao.json'; herbs_data = json.loads(hp.read_text(encoding='utf-8'))
herbs = herbs_data.get('herbs', []); herb_names = {norm(x.get('n')) for x in herbs}
for h in read('herbs.json').get('herbs', []):
    n = h.get('name','')
    if norm(n) in herb_names: continue
    herbs.append({'id': 'up_hb_' + norm(n), 'n': n, 'g': h.get('category','其他'), '原文': h.get('original',''), '性味': h.get('nature','') or h.get('flavor',''), '主治': h.get('action',''), '倪注': h.get('ni_note',''), '容川': '', '用量': h.get('dosage',''), '禁忌': h.get('contraindication',''), '口述': h.get('clinical_notes',''), '补注': h.get('historical_notes','') + ('；归经：' + '、'.join(h.get('meridians',[])) if h.get('meridians') else '')})
    herb_names.add(norm(n))
herbs_data['herbs'] = herbs
hp.write_text(json.dumps(herbs_data, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
print(f'merged formulas={len(items)} herbs={len(herbs)}')
