#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""对专家盲测结果做简单一致率统计；没有 engineResult 时明确标记未完成。"""
import json
import sys
from collections import Counter
from pathlib import Path

path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).with_name('expert_blind_cases.schema.json')
data = json.loads(path.read_text(encoding='utf-8'))
rows = []
for case in data.get('cases', []):
    annotations = case.get('expertAnnotations', [])
    engine = case.get('engineResult')
    if not engine:
        rows.append((case.get('id'), None)); continue
    def majority(key):
        vals = [a.get(key) for a in annotations if a.get(key) not in ('', [], None)]
        return Counter(map(str, vals)).most_common(1)[0][0] if vals else ''
    checks = {k: str(engine.get(k, '')) == majority(k) for k in ('primaryMeridian', 'formulaDirection', 'risk')}
    rows.append((case.get('id'), checks))
completed = [x for _, x in rows if x]
print(f'cases: {len(rows)}, scored: {len(completed)}')
if not completed:
    print('NOT_READY: add real blinded engineResult and independent expert annotations before calculating accuracy')
    raise SystemExit(2)
for key in ('primaryMeridian', 'formulaDirection', 'risk'):
    print(f'{key}: {sum(x[key] for x in completed) / len(completed):.1%}')
