#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
from pathlib import Path
p = Path(__file__).resolve().parents[1] / 'static/data/zangxiang.json'
d = json.loads(p.read_text(encoding='utf-8'))
organs = d.get('organs', [])
assert len(organs) >= 5
assert len({x['name'] for x in organs}) == len(organs)
assert all(x.get('evidence') and x.get('meridians') for x in organs)
print(f'PASS: zangxiang dataset {len(organs)} organs')
