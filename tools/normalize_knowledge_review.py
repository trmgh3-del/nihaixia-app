#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""为穴位和藏象资料增加逐条专家审核元数据，不修改原始教学内容。"""
import json
from pathlib import Path
root=Path(__file__).resolve().parents[1]
for filename, key in [('zhenjiu.json','points'), ('zangxiang.json','organs')]:
    p=root/'static/data'/filename; data=json.loads(p.read_text(encoding='utf-8'))
    for item in data.get(key, []):
        item.setdefault('expertStatus','pending'); item.setdefault('reviewNotes',''); item.setdefault('sources', [])
    p.write_text(json.dumps(data,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
    print(f'{filename}: {len(data.get(key, []))}')
