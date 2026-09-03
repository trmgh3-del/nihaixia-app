#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
from pathlib import Path
p = Path(__file__).resolve().parents[1] / 'static/data/zangxiang.json'
d = json.loads(p.read_text(encoding='utf-8'))
organs = d.get('organs', [])
assert len(organs) >= 11
assert len({x['name'] for x in organs}) == len(organs)
assert all(x.get('evidence') and x.get('meridians') for x in organs)
assert all(x.get('expertStatus') in ('pending', 'approved', 'needs_review', 'rejected') and 'reviewNotes' in x for x in organs), 'zangxiang review metadata incomplete'
assert all(x.get('fiveElement') and x.get('pulse') for x in organs)
print(f'PASS: zangxiang dataset {len(organs)} organs')
