#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
from pathlib import Path
root=Path(__file__).resolve().parents[1]
formulas=json.loads((root/'static/data/formulas.json').read_text())['items']
herbs=json.loads((root/'static/data/bencao.json').read_text())['herbs']
assert len(formulas)>=322 and len(herbs)>=465
assert len({x['id'] for x in formulas})==len(formulas)
assert len({x['id'] for x in herbs})==len(herbs)
assert all(x.get('n') for x in formulas) and all(x.get('n') for x in herbs)
assert all(all(k in x for k in ('alias', 'meridian', 'category', 'contraindication', 'preparation', 'keywords')) for x in formulas)
assert all(all(k in x for k in ('canonicalName', 'processing', 'natureCategory', 'flavor', 'meridians', 'aliases', 'sources')) for x in herbs)
assert sum(bool(x.get('clinical') or x.get('origin') or x.get('note')) for x in formulas)>=322
up = [x for x in formulas if str(x.get('id','')).startswith('up_')]
assert up and all(x.get('zhizhi') and x.get('composition') and x.get('doses') for x in up), 'upstream formula detail mapping incomplete'
assert sum(bool(x.get('原文') or x.get('倪注') or x.get('主治')) for x in herbs)>=465
print(f'PASS: formulas={len(formulas)}, herbs={len(herbs)}')
