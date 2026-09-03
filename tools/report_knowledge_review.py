#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
from collections import Counter
from pathlib import Path
root=Path(__file__).resolve().parents[1]
for filename,key in [('zhenjiu.json','points'),('zangxiang.json','organs')]:
 rows=json.loads((root/'static/data'/filename).read_text()) .get(key,[])
 c=Counter(x.get('expertStatus','pending') for x in rows)
 print(f'{filename}: {len(rows)} | approved={c.get("approved",0)} needs_review={c.get("needs_review",0)} rejected={c.get("rejected",0)} pending={c.get("pending",0)}')
