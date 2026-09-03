#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""输出方剂和本草逐条专家审核状态。"""
import json
from collections import Counter
from pathlib import Path
root=Path(__file__).resolve().parents[1]
for label, path, key in [('formulas', root/'static/data/formulas.json', 'items'), ('herbs', root/'static/data/bencao.json', 'herbs')]:
    rows=json.loads(path.read_text(encoding='utf-8')).get(key, [])
    counts=Counter(x.get('expertStatus','pending') for x in rows)
    print(f'{label}: {len(rows)} | ' + ' '.join(f'{k}={counts.get(k,0)}' for k in ('approved','needs_review','rejected','pending')))
