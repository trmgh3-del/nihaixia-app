#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""四诊规则编译产物回归检查：不运行 UI，只检查规则可加载、出处可追溯、条件不越界。"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
rules = json.loads((ROOT / 'static/data/sizhen-rules.json').read_text(encoding='utf-8'))
assert rules.get('rules'), 'rules must not be empty'
assert rules.get('knowledgeItems'), 'knowledge index must not be empty'
ids = {x['id'] for x in rules['knowledgeItems']}
rule_ids = [x.get('id') for x in rules['rules']]
assert len(rule_ids) == len(set(rule_ids)), 'duplicate rule id'
assert all(x.get('name') and isinstance(x.get('when'), list) for x in rules['rules']), 'invalid rule schema'
assert all(not x.get('sourceId') or x['sourceId'] in ids for x in rules['rules']), 'orphan source id'
allowed_fields = {'望色','舌质','舌苔','望神','声音','呼吸','汗','头身','大便','小便','口渴','睡眠','手足温度','胃口','腹满','疼痛','胸腹','耳','妇女','寒热','脉位','脉率','脉形','脉力','复合脉'}
for rule in rules['rules']:
    for condition in rule['when']:
        field, sep, value = condition.partition('=')
        assert sep and field in allowed_fields and value, f'unknown condition: {condition}'
print(f'PASS: {len(rules["rules"])} executable rules, {len(rules["knowledgeItems"])} indexed items')
