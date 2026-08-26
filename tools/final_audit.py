import json, os, re
SRC='/tmp/repo'
OUT=os.path.join(os.path.dirname(__file__), '..', 'static', 'data')
rd=lambda p: open(os.path.join(SRC,p),encoding='utf-8').read().replace('\r\n','\n')
app=[]
def collect(o):
    if isinstance(o,dict):
        for v in o.values(): collect(v)
    elif isinstance(o,list):
        for v in o: collect(v)
    elif isinstance(o,str) and len(o)>2: app.append(o)
for f in ['shanghan','jingui','neijing','bencao','zhenjiu','tianji','formulas','cases_table','cases_narr','yian','skill_units','diagnosis','articles','meta','skill_raw']:
    collect(json.load(open(os.path.join(OUT,f+'.json'))))
APP=re.sub(r'[\s\*\|#\->`·—─│├└]+','', '\n'.join(app))
strip=lambda l: re.sub(r'[\s\*\|#\->`·—─│├└]+','',l)
# 字段标签行：标签为结构化字段名，剥离后比对值
def strip2(l):
    x = re.sub(r'^[-\s\*]*(原文|性味|主治|倪注|容川|用量|禁忌|日期|疾病|六经)\*?\*?[：:]\s*', '', l.strip())
    return strip(x)
FILES=['SKILL.md','expression_style.md','distilled_cases.md','README.md','README_EN.MD','CHANGELOG.md','index.html']
for d in ['modules','cases','references/distilled','references/research','references/audit']:
    FILES += [f'{d}/{fn}' for fn in sorted(os.listdir(os.path.join(SRC,d))) if fn.endswith(('.md','.txt'))]
total_miss=0
for f in FILES:
    src=rd(f); miss=[]
    if f=='cases/00_merged_table.md':
        for l in src.split('\n'):
            if not l.strip().startswith('|'): continue
            for c in l.strip().strip('|').split('|'):
                cs=strip(c)
                if len(cs)>=12 and cs not in APP: miss.append(c)
    else:
        for l in src.split('\n'):
            ls=strip2(l)
            if len(ls)<12: continue
            if ls not in APP and strip(l) not in APP: miss.append(l)
    if miss:
        total_miss+=len(miss)
        print(f'⚠️ {f}: {len(miss)} 处 -> ' + ' | '.join(str(m).strip()[:44] for m in miss[:3]))
print(f'\n===== 全库 50 文件逐行审计完成，总缺失: {total_miss} 处 =====')
