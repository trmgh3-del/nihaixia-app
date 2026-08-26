#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把诊断知识库编译为可运行的四诊规则索引。
源数据由 tools/build_data.py 生成，本脚本不改变原始知识内容，只建立规则和出处索引。
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
data = json.loads((ROOT / 'static/data/diagnosis.json').read_text(encoding='utf-8'))
items = []
for group in data.get('groups', []):
    for item in group.get('items', []):
        items.append({'id': item.get('id'), 'title': item.get('t', ''), 'group': group.get('label', '')})

# 规则条件为 field=value；全部满足才命中。分数用于排序，sourceId 对应原始 diagnosis 条目。
rules = [
 {'id':'taiyang-outline','name':'太阳病提纲','meridian':'太阳','score':3,'when':['脉位=浮','寒热=恶寒'],'sourceTitle':'太阳病'},
 {'id':'taiyang-wind','name':'太阳中风','meridian':'太阳','score':3,'when':['汗=有汗自汗','寒热=恶风'],'sourceTitle':'太阳病'},
 {'id':'taiyang-cold','name':'太阳伤寒','meridian':'太阳','score':3,'when':['汗=无汗','脉形=紧'],'sourceTitle':'太阳病'},
 {'id':'yangming-meridian','name':'阳明经证','meridian':'阳明','score':3,'when':['寒热=但热不寒','口渴=渴喜冷饮'],'sourceTitle':'阳明病'},
 {'id':'yangming-fu','name':'阳明腑证','meridian':'阳明','score':3,'when':['大便=便秘','脉形=洪'],'sourceTitle':'阳明病'},
 {'id':'shaoyang-outline','name':'少阳病提纲','meridian':'少阳','score':3,'when':['寒热=往来寒热','脉形=弦'],'sourceTitle':'少阳病'},
 {'id':'taiyin-cold','name':'太阴寒湿','meridian':'太阴','score':3,'when':['大便=溏泄','胃口=差/食少'],'sourceTitle':'太阴病'},
 {'id':'shaoyin-cold','name':'少阴寒化','meridian':'少阴','score':3,'when':['睡眠=但欲寐','脉形=细'],'sourceTitle':'少阴病'},
 {'id':'shaoyin-yangxu','name':'少阴阳虚','meridian':'少阴','score':3,'when':['手足温度=手脚冰凉','脉力=微'],'sourceTitle':'少阴病'},
 {'id':'jueyin-coldheat','name':'厥阴寒热错杂','meridian':'厥阴','score':3,'when':['口渴=消渴多饮','手足温度=手心热脚凉'],'sourceTitle':'厥阴病'},
 {'id':'hebing-taiyang-shaoyang','name':'太阳少阳合病','meridian':'太阳、少阳','score':2,'when':['寒热=恶寒','脉形=弦'],'sourceTitle':'合病'},
 {'id':'hebing-shaoyang-yangming','name':'少阳阳明合病','meridian':'少阳、阳明','score':2,'when':['寒热=往来寒热','大便=便秘'],'sourceTitle':'合病'},
 {'id':'hebing-shaoyang-taiyin','name':'少阳太阴合病','meridian':'少阳、太阴','score':2,'when':['寒热=往来寒热','大便=溏泄'],'sourceTitle':'合病'},
 {'id':'bing-taiyang-shaoyin','name':'太阳少阴两感','meridian':'太阳、少阴','score':2,'when':['寒热=恶寒','脉位=沉'],'sourceTitle':'并病'},
 {'id':'bing-taiyin-shaoyin','name':'太阴少阴并病','meridian':'太阴、少阴','score':2,'when':['大便=溏泄','脉形=细','手足温度=手脚冰凉'],'sourceTitle':'并病'},
 {'id':'shaoyin-rehua','name':'少阴热化','meridian':'少阴','score':3,'when':['脉率=数','舌质=红','睡眠=彻夜不眠'],'sourceTitle':'少阴病'},
 {'id':'taiyin-wet','name':'太阴脾虚湿盛','meridian':'太阴','score':3,'when':['舌质=胖大有齿痕','舌苔=白腻'],'sourceTitle':'舌诊速查'},
 {'id':'yangming-dry','name':'阳明腑实舌象','meridian':'阳明','score':3,'when':['舌质=红','舌苔=燥裂'],'sourceTitle':'舌诊速查'},
 {'id':'jueyin-tongue','name':'厥阴寒热错杂舌象','meridian':'厥阴','score':3,'when':['舌质=红','舌苔=薄白'],'sourceTitle':'舌诊速查'},
]
# 绑定最接近的原始条目，保留所有条目作为可检索的知识索引。
for rule in rules:
    candidates = [x for x in items if rule['sourceTitle'] in x['title']]
    rule['sourceId'] = candidates[0]['id'] if candidates else None
out = {'version':'2026.08.26', 'source':'static/data/diagnosis.json', 'rules':rules, 'knowledgeItems':items}
(ROOT / 'static/data/sizhen-rules.json').write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding='utf-8')
print('compiled rules:', len(rules), 'knowledge items:', len(items))
