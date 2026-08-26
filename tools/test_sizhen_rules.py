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
assert all(sid in ids for x in rules['rules'] for sid in x.get('sourceIds', [])), 'orphan source ids'
allowed_fields = {'望色','舌质','舌苔','望神','声音','呼吸','汗','头身','大便','小便','口渴','睡眠','手足温度','胃口','腹满','疼痛','胸腹','耳','妇女','厥热胜复','misTreatment','miscDisease','duration','寒热','脉位','脉率','脉形','脉力','复合脉'}
for rule in rules['rules']:
    for condition in rule['when']:
        field, sep, value = condition.partition('=')
        assert sep and field in allowed_fields and value, f'unknown condition: {condition}'
    fields = [condition.split('=', 1)[0] for condition in rule['when']]
    assert len(fields) == len(set(fields)), f'mutually exclusive duplicate field in rule: {rule["id"]}'

# 标准六经回归样例：只验证规则排序，不宣称医疗诊断。
cases = [
    ({'脉位':'浮', '寒热':'恶寒', '汗':'无汗', '脉形':'紧'}, '太阳'),
    ({'寒热':'但热不寒', '口渴':'渴喜冷饮', '汗':'大汗不止', '脉形':'洪'}, '阳明'),
    ({'寒热':'往来寒热', '脉形':'弦', '口渴':'口苦咽干'}, '少阳'),
    ({'大便':'溏泄', '胃口':'差/食少', '舌苔':'白腻'}, '太阴'),
    ({'睡眠':'但欲寐', '脉形':'细', '脉力':'微'}, '少阴'),
    ({'口渴':'消渴多饮', '胃口':'饥而不欲食', '疼痛':'气上撞心/心中疼热'}, '厥阴'),
    # 合病、并病和脉舌组合
    ({'寒热':'往来寒热', '大便':'便秘', '脉形':'弦'}, '少阳'),
    ({'大便':'溏泄', '脉形':'细', '手足温度':'手脚冰凉', '睡眠':'但欲寐', '脉力':'微'}, '少阴'),
    ({'舌质':'淡白', '脉率':'数', '口渴':'渴不欲饮'}, '少阴'),
    ({'舌质':'红', '脉位':'沉', '口渴':'渴喜冷饮'}, '阳明'),
    ({'复合脉':'浮紧'}, '太阳'),
    ({'复合脉':'弦数'}, '少阳'),
    ({'厥热胜复':'厥多热少（病进）'}, '厥阴'),
    ({'miscDisease':'胸痹'}, '少阴'),
    ({'miscDisease':'痰饮咳嗽', '舌苔':'白腻', '大便':'溏泄', '胃口':'差/食少'}, '太阴'),
]
for pick, expected in cases:
    scores = {}
    for rule in rules['rules']:
        if all(pick.get(c.split('=', 1)[0]) == c.split('=', 1)[1] for c in rule['when']):
            for mer in rule.get('meridian', '').replace('、', ',').split(','):
                if mer: scores[mer] = scores.get(mer, 0) + rule['score']
    assert scores and max(scores, key=scores.get) == expected, f'case expected {expected}, got {scores}'
print(f'PASS: {len(rules["rules"])} executable rules, {len(rules["knowledgeItems"])} indexed items, {len(cases)} regression cases')
