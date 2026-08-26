#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""输出诊断知识条目到可执行规则的覆盖率。"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
source = json.loads((ROOT / 'static/data/diagnosis.json').read_text(encoding='utf-8'))
compiled = json.loads((ROOT / 'static/data/sizhen-rules.json').read_text(encoding='utf-8'))
items = [item for group in source.get('groups', []) for item in group.get('items', [])]
rule_sources = {sid for r in compiled.get('rules', []) for sid in (r.get('sourceIds') or [r.get('sourceId')]) if sid}
covered = [x for x in items if x.get('id') in rule_sources]
uncovered = [x for x in items if x.get('id') not in rule_sources]
ratio = len(covered) / len(items) * 100 if items else 0
print(f'knowledge items: {len(items)}')
print(f'referenced by executable rules: {len(covered)} ({ratio:.1f}%)')
print(f'not directly referenced: {len(uncovered)}')
for x in uncovered:
    print(f'- {x.get("id")}: {x.get("t")}')
