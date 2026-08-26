#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""验证脱敏专家盲测数据格式；不生成或臆测专家金标准。"""
import json
import sys
from pathlib import Path

path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).with_name('expert_blind_cases.schema.json')
data = json.loads(path.read_text(encoding='utf-8'))
cases = data.get('cases', [])
assert cases, 'cases must not be empty'
for case in cases:
    assert case.get('id') and isinstance(case.get('input'), dict), 'case id/input missing'
    annotations = case.get('expertAnnotations', [])
    assert len(annotations) >= 3, f'{case["id"]}: need at least 3 independent experts'
    ids = [a.get('expertId') for a in annotations]
    assert len(ids) == len(set(ids)) and all(ids), f'{case["id"]}: expert ids must be unique'
    for a in annotations:
        for key in ('bagang', 'primaryMeridian', 'secondaryMeridians', 'formulaDirection', 'risk'):
            assert key in a, f'{case["id"]}: missing annotation field {key}'
print(f'PASS: {len(cases)} blind-test cases, minimum 3 independent annotations each')
