#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""验证针灸知识库可用于四诊结果后的学习联动。"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
data = json.loads((ROOT / 'static/data/zhenjiu.json').read_text(encoding='utf-8'))
points = data.get('points', [])
assert len(points) >= 301, f'expected at least 301 points, got {len(points)}'
assert len({p.get('id') for p in points}) == len(points), 'duplicate acupoint ids'
assert all(p.get('id') and p.get('t') for p in points), 'acupoint title/id incomplete'
assert all(p.get('expertStatus') in ('pending', 'approved', 'needs_review', 'rejected') and 'reviewNotes' in p for p in points), 'acupoint review metadata incomplete'
assert sum(bool(p.get('b')) for p in points) >= 280, 'too many points without explanations'
print(f'PASS: {len(points)} acupoints, {sum(bool(p.get("b")) for p in points)} with explanations')
