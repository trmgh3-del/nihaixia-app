#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""验证 1257 条结构化医案是否满足辨证学习检索所需的字段质量。"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
rows = json.loads((ROOT / 'static/data/cases_table.json').read_text(encoding='utf-8')).get('rows', [])
required = {'n', 'date', 'patient', 'diag', 'bingji', 'fangji', 'zhenjiu', 'zhifa', 'result', 'yizhu', 'guandian'}
assert len(rows) == 1257, f'expected 1257 cases, got {len(rows)}'
assert len({r.get('n') for r in rows}) == len(rows), 'duplicate case numbers'
assert all(required <= set(r) for r in rows), 'case schema incomplete'
nonempty = {k: sum(bool(str(r.get(k, '')).strip()) for r in rows) for k in required if k != 'n'}
print('PASS: 1257 structured cases; non-empty fields:')
for k, v in sorted(nonempty.items()): print(f'  {k}: {v}')
