#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""为当前方剂/本草数据补齐统一字段，不删除旧字段，保证旧页面兼容。"""
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
fp = ROOT / 'static/data/formulas.json'; fd = json.loads(fp.read_text(encoding='utf-8'))
for f in fd.get('items', []):
    f.setdefault('alias', '')
    f.setdefault('meridian', '')
    f.setdefault('category', '')
    f.setdefault('contraindication', '')
    f.setdefault('preparation', '')
    f.setdefault('keywords', [])
    f.setdefault('expertStatus', 'pending')
    f.setdefault('reviewNotes', '')
    if not f.get('zhizhi'): f['zhizhi'] = f.get('clinical', '')
    if not f.get('composition'): f['composition'] = f.get('origin', '')
    if not f.get('contraindication') and '禁忌：' in str(f.get('note', '')): f['contraindication'] = str(f['note']).split('禁忌：', 1)[1]
hp = ROOT / 'static/data/bencao.json'; hd = json.loads(hp.read_text(encoding='utf-8'))
herb_names = sorted({str(h.get('n','')) for h in hd.get('herbs', []) if h.get('n')}, key=len, reverse=True)
herb_aliases = {'芍药': '白芍', '生地': '干地黄', '熟地': '熟地黄', '附子': '生附子', '炙甘草': '甘草'}
for f in fd.get('items', []):
    if not f.get('components'):
        text = str(f.get('origin','')) + ' ' + str(f.get('composition',''))
        found = []
        for name in herb_names:
            if name in text and name not in found: found.append(name)
        for alias, canonical in herb_aliases.items():
            if alias in text and canonical not in found: found.append(canonical)
        f['components'] = [{'name': n, 'dosage': ''} for n in found]
fp.write_text(json.dumps(fd, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')

for h in hd.get('herbs', []):
    h.setdefault('canonicalName', h.get('n', ''))
    h.setdefault('processing', '')
    h.setdefault('natureCategory', h.get('性味', ''))
    h.setdefault('flavor', '')
    h.setdefault('meridians', [])
    h.setdefault('category', h.get('g', '其他'))
    h.setdefault('aliases', [])
    h.setdefault('sources', [])
    h.setdefault('expertStatus', 'pending')
    h.setdefault('reviewNotes', '')
hp.write_text(json.dumps(hd, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
print(f'normalized formulas={len(fd.get("items", []))} herbs={len(hd.get("herbs", []))}')
