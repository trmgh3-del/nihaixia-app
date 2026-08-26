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
    if not f.get('zhizhi'): f['zhizhi'] = f.get('clinical', '')
    if not f.get('composition'): f['composition'] = f.get('origin', '')
    if not f.get('contraindication') and '禁忌：' in str(f.get('note', '')): f['contraindication'] = str(f['note']).split('禁忌：', 1)[1]
fp.write_text(json.dumps(fd, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')

hp = ROOT / 'static/data/bencao.json'; hd = json.loads(hp.read_text(encoding='utf-8'))
for h in hd.get('herbs', []):
    h.setdefault('canonicalName', h.get('n', ''))
    h.setdefault('processing', '')
    h.setdefault('natureCategory', h.get('性味', ''))
    h.setdefault('flavor', '')
    h.setdefault('meridians', [])
    h.setdefault('category', h.get('g', '其他'))
    h.setdefault('aliases', [])
    h.setdefault('sources', [])
hp.write_text(json.dumps(hd, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
print(f'normalized formulas={len(fd.get("items", []))} herbs={len(hd.get("herbs", []))}')
