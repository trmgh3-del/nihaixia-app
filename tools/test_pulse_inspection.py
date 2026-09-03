#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
from pathlib import Path
root=Path(__file__).resolve().parents[1]
p=json.loads((root/'static/data/pulse.json').read_text()); i=json.loads((root/'static/data/inspection.json').read_text())
assert len(p['pulses']) >= 16 and len({x['name'] for x in p['pulses']}) == len(p['pulses'])
assert all(x.get('touch') and x.get('bagang') is not None and x.get('meridians') is not None for x in p['pulses'])
assert len(i['colors']) == 5 and len(i['spirit']) >= 5
assert any(x['risk']=='high' for x in p['pulses']) and any(x['risk']=='high' for x in i['spirit'])
print(f'PASS: pulses={len(p["pulses"])}, inspection colors={len(i["colors"])}, spirit={len(i["spirit"])}')
