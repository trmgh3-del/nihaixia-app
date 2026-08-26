#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""输出四诊规则专家审核清单，不伪造专家结论。"""
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
data = json.loads((ROOT/'static/data/sizhen-rules.json').read_text(encoding='utf-8'))
rules = data.get('rules', [])
from collections import Counter
count = Counter(r.get('expertStatus', 'pending') for r in rules)
print(f'rules: {len(rules)}')
for status in ('approved', 'needs_review', 'rejected', 'pending'):
    print(f'{status}: {count.get(status, 0)}')
print('\nreview queue:')
for r in rules:
    if r.get('expertStatus', 'pending') == 'pending':
        print(f"- {r['id']} | {r['name']} | required={';'.join(r.get('required', []))} | source={','.join(r.get('sourceIds', []))}")
