#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""完整度审计：源仓库每个文件 vs App 数据收录率"""
import json, os, re, sys

SRC = '/tmp/repo'
OUT = os.path.join(os.path.dirname(__file__), '..', 'static', 'data')

def rd(p):
    with open(os.path.join(SRC, p), encoding='utf-8') as f:
        return f.read().replace('\r\n', '\n')

def jload(name):
    with open(os.path.join(OUT, name), encoding='utf-8') as f:
        return json.load(f)

# 收集 App 数据里的全部文本
app_text = []
def collect(obj, key=''):
    if isinstance(obj, dict):
        for v in obj.values(): collect(v)
    elif isinstance(obj, list):
        for v in obj: collect(v)
    elif isinstance(obj, str) and len(obj) > 6:
        app_text.append(obj)

for f in ['shanghan', 'jingui', 'neijing', 'bencao', 'zhenjiu', 'tianji', 'formulas',
          'cases_table', 'cases_narr', 'yian', 'skill_units', 'diagnosis', 'articles', 'meta', 'skill_raw']:
    collect(jload(f + '.json'))

APP = re.sub(r'[\s\*\|#\->`·—─│├└]+', '', '\n'.join(app_text))
print(f'App 数据文本总量(净内容): {len(APP)/10000:.0f} 万字\n')

FILES = {
 'SKILL.md': 1, 'expression_style.md': 1, 'distilled_cases.md': 1, 'README.md': 1, 'README_EN.MD': 1, 'CHANGELOG.md': 1, 'index.html': 0,
}
for d in ['modules', 'cases', 'references/distilled', 'references/research', 'references/audit']:
    for fn in sorted(os.listdir(os.path.join(SRC, d))):
        if fn.endswith(('.md', '.txt')):
            FILES[f'{d}/{fn}'] = 1

print(f'{"收录率":>7}  {"源文件":<46} {"缺失代表内容"}')
print('-' * 100)
missing_files = []
for f, need in FILES.items():
    src = rd(f)
    # 抽样检测：滑窗取样，剔除空白与 markdown 语法符后比对
    body = re.sub(r'[\s\*\|#\->`·—─│├└]+', '', src)
    samples = []
    n = len(body)
    if n < 300:
        samples = [body]
    else:
        for i in range(16):
            at = int(n * i / 16)
            samples.append(body[at:at + 50])
    hit = sum(1 for s in samples if s and s in APP)
    ratio = hit / len(samples)
    flag = '' if ratio >= 0.9 else ('⚠️' if ratio >= 0.4 else '❌')
    if ratio < 0.9:
        # 找出第一个未命中的样本作代表
        rep = ''
        for s in samples:
            if s not in APP:
                rep = s[:40]
                break
        print(f'{ratio:>5.0%} {flag}  {f:<44} {rep}')
        if ratio < 0.4:
            missing_files.append(f)
    else:
        print(f'{ratio:>5.0%}    {f}')
print('\n❌ 严重缺失文件:', missing_files if missing_files else '无')
