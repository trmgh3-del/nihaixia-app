#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""加强版完整性审计 v2：阈值降到2字（覆盖药名/短词），规范化标题编号，全行覆盖"""
import json, os, re

SRC = os.environ.get('NIHAIXIA_SRC', '/tmp/repo')
OUT = os.path.join(os.path.dirname(__file__), '..', 'static', 'data')

def rd(p):
    return open(os.path.join(SRC, p), encoding='utf-8').read().replace('\r\n', '\n')

app = []
def collect(o):
    if isinstance(o, dict):
        for v in o.values(): collect(v)
    elif isinstance(o, list):
        for v in o: collect(v)
    elif isinstance(o, str) and len(o) >= 2:
        app.append(o)
    elif isinstance(o, (int, float)):
        app.append(str(o))
for f in ['shanghan', 'jingui', 'neijing', 'bencao', 'zhenjiu', 'tianji', 'formulas',
          'cases_table', 'cases_narr', 'yian', 'skill_units', 'diagnosis', 'articles', 'meta', 'skill_raw']:
    collect(json.load(open(os.path.join(OUT, f + '.json'))))
APP = re.sub(r'[\s\*\|#\->`·—─│├└]+', '', '\n'.join(app))
print(f'App 净文本: {len(APP)/10000:.0f} 万字，样本串 {len(app)} 条\n')

SYM = re.compile(r'[\s\*\|#\->`·—─│├└]+')
def strip2(l):
    # 剥字段标签 / 列表编号 / 标题标记
    x = re.sub(r'^[-\s\*]*(原文|性味|主治|倪注|容川|用量|禁忌|日期|疾病|六经|字数|摘要|患者|方剂)[\*]*[：:]\s*', '', l.strip())
    x = re.sub(r'^\d+[.、]\s*', '', x)
    return SYM.sub('', x)

def is_noise(l):
    t = l.strip()
    if not t: return True
    if re.fullmatch(r'[-=]{3,}|[\|:\-\s]+|(#{1,6})\s*', t): return True
    if t.startswith('|') and re.match(r'^\|[\s:|-]+\|$', t): return True
    if t in ('---', '***', '```'): return True
    return False

FILES = ['SKILL.md', 'expression_style.md', 'distilled_cases.md', 'README.md', 'README_EN.MD', 'CHANGELOG.md', 'index.html']
for d in ['modules', 'cases', 'references/distilled', 'references/research', 'references/audit']:
    FILES += [f'{d}/{fn}' for fn in sorted(os.listdir(os.path.join(SRC, d))) if fn.endswith(('.md', '.txt'))]

total_miss = 0
for f in FILES:
    src = rd(f)
    miss = []
    if f == 'cases/00_merged_table.md':
        for l in src.split('\n'):
            if not l.strip().startswith('|'): continue
            for c in l.strip().strip('|').split('|'):
                cs = SYM.sub('', c)
                if len(cs) >= 2 and cs not in APP:
                    miss.append(c)
    else:
        for l in src.split('\n'):
            if is_noise(l): continue
            ls = strip2(l)
            if len(ls) < 2: continue
            if ls not in APP and SYM.sub('', l) not in APP:
                miss.append(l)
    if miss:
        total_miss += len(miss)
        print(f'⚠️ {f}: {len(miss)} 处')
        for m in miss[:6]:
            print('   ', str(m).strip()[:76])
print(f'\n===== 加强审计（阈值2字）总缺失: {total_miss} 处 =====')
