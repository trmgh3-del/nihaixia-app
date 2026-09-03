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
    if not engine or not any(engine.get(k) for k in ('primaryMeridian', 'formulaDirection', 'risk')):
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
# 风险安全性单独统计：高风险漏报比普通一致率更重要。
expert_high = 0; engine_high = 0; true_positive = 0
for case in data.get('cases', []):
    ann = case.get('expertAnnotations', []); eng = case.get('engineResult') or {}
    gold = majority_value = Counter(str(a.get('risk')) for a in ann if a.get('risk')).most_common(1)
    gold_high = bool(gold and gold[0][0] in ('高风险', 'high'))
    sys_high = eng.get('risk') in ('高风险', 'high')
    expert_high += int(gold_high); engine_high += int(sys_high); true_positive += int(gold_high and sys_high)
if expert_high:
    print(f'high-risk recall: {true_positive / expert_high:.1%}')
if engine_high:
    print(f'high-risk precision: {true_positive / engine_high:.1%}')
