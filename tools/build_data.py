#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
倪海厦 Skill -> UniApp 数据构建脚本
把 github.com/jangviktor-web/nihaixia 仓库的 50 个 Markdown 文件
解析为 App 使用的结构化 JSON（static/data/*.json）
用法: python3 build_data.py [source_dir] [out_dir]
"""
import json, os, re, sys, hashlib
from collections import OrderedDict

SRC = sys.argv[1] if len(sys.argv) > 1 else '/tmp/repo'
OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.join(os.path.dirname(__file__), '..', 'static', 'data')
os.makedirs(OUT, exist_ok=True)

def rd(p):
    with open(os.path.join(SRC, p), encoding='utf-8') as f:
        return f.read().replace('\r\n', '\n').replace('\r', '\n')

def wjson(name, obj):
    with open(os.path.join(OUT, name), 'w', encoding='utf-8') as f:
        json.dump(obj, f, ensure_ascii=False, separators=(',', ':'))
    print(f'  ✓ {name}  ({os.path.getsize(os.path.join(OUT,name))/1024:.0f} KB)')

INDEX = []   # 全局检索索引
def idx(f, cat, id_, title, sub='', tags=None):
    INDEX.append({'f': f, 'c': cat, 'i': id_, 't': title, 's': (sub or '')[:180], 'g': tags or []})

def strip_header_meta(md):
    """保留全部内容（含文件头的来源/用途说明块），仅去首尾空行"""
    return md.strip('\n')

def split_by(md, pattern):
    """按标题正则切分，返回 [(title, body)]；首段（标题前内容）作为 ('', ...) 丢弃前缀空白"""
    res, cur_t, cur_b = [], None, []
    for line in md.split('\n'):
        m = re.match(pattern, line)
        if m:
            if cur_t is not None:
                res.append((cur_t, '\n'.join(cur_b).strip('\n')))
            cur_t, cur_b = m.group(1).strip(), []
        else:
            cur_b.append(line)
    if cur_t is not None:
        res.append((cur_t, '\n'.join(cur_b).strip('\n')))
    return res

def parse_table(block):
    """解析 markdown 表格 -> (headers, rows) 或 None（要求整个文本块主体为表格）"""
    lines = [l for l in block.split('\n') if l.strip()]
    if len(lines) < 2 or not all(l.lstrip().startswith('|') for l in lines):
        return None
    cells = lambda l: [c.strip() for c in l.strip().strip('|').split('|')]
    head = cells(lines[0])
    rows = []
    for l in lines[2:]:
        cs = cells(l)
        if len(cs) < len(head):
            cs += [''] * (len(head) - len(cs))
        rows.append(cs[:len(head)])
    return head, rows

def parse_tables(block):
    """扫描文本块中的所有表格 -> [(headers, rows)]（容忍表格前后的说明文字）"""
    tables, buf = [], []
    for l in block.split('\n'):
        if l.strip().startswith('|') and l.strip().endswith('|'):
            buf.append(l)
        else:
            if len(buf) >= 3:
                cells = lambda s: [c.strip() for c in s.strip().strip('|').split('|')]
                head = cells(buf[0])
                rows = []
                for r in buf[2:]:
                    cs = cells(r)
                    if len(cs) < len(head):
                        cs += [''] * (len(head) - len(cs))
                    rows.append(cs[:len(head)])
                if rows: tables.append((head, rows))
            buf = []
    if len(buf) >= 3:
        cells = lambda s: [c.strip() for c in s.strip().strip('|').split('|')]
        head = cells(buf[0])
        rows = []
        for r in buf[2:]:
            cs = cells(r)
            if len(cs) < len(head):
                cs += [''] * (len(head) - len(cs))
            rows.append(cs[:len(head)])
        if rows: tables.append((head, rows))
    return tables

def clean(s):
    return re.sub(r'\s+', ' ', s or '').strip()

def excerpt(md, n=140):
    t = re.sub(r'[#>*`|\-—•\s]+', ' ', md)
    t = re.sub(r'\*\*?', '', t)
    return clean(t)[:n]

# ============================================================ 1. 伤寒论
print('» 伤寒论')
shanghan = {'sun': [], 'que': [], 'wujing': [], 'intro': ''}
md01 = strip_header_meta(rd('modules/01_shanghan_sun.md'))
secs = split_by(md01, r'^###\s+(.*)$')
pre = md01.split('\n###')[0]
shanghan['intro'] = pre.strip()
# 太阳篇导言作为首个条目（含篇目说明），防丢内容
if pre.strip() and len(pre.strip()) > 60:
    _it = {'id': 'sun_intro', 't': '太阳篇·导言与篇目总览', 'b': pre.strip(), 'g': ['导言']}
    shanghan['sun'].insert(0, _it)
    idx('shanghan', 'shanghan', _it['id'], _it['t'], excerpt(pre), ['导言'])
for t, b in secs:
    tags = ['太阳篇'] if '太阳' in t else []
    if t.startswith('模型'):
        tags = ['心智模型']
    item = {'id': 'sun%d' % len(shanghan['sun']), 't': t, 'b': b, 'g': tags}
    shanghan['sun'].append(item)
    idx('shanghan', 'shanghan', item['id'], t, excerpt(b), tags)

md13 = strip_header_meta(rd('modules/13_shanghan_quebing.md'))
_que_pre = md13.split('\n####')[0].strip()
if _que_pre and len(_que_pre) > 20:
    _it = {'id': 'que_head', 'n': 0, 't': '下篇补齐·导言（讲课编号与宋本对照说明）', 'b': _que_pre, 'g': ['导言']}
    shanghan['que'].insert(0, _it)
    idx('shanghan', 'shanghan', _it['id'], _it['t'], excerpt(_que_pre), ['导言'])
for t, b in split_by(md13, r'^####\s+(.*)$'):
    m = re.match(r'条文(\d+)', t)
    num = int(m.group(1)) if m else 0
    item = {'id': 'que%d' % num, 'n': num, 't': t, 'b': b, 'g': ['太阳下篇' if num <= 193 else '阳明篇']}
    shanghan['que'].append(item)
    idx('shanghan', 'shanghan', item['id'], t, excerpt(b), item['g'])

md02 = strip_header_meta(rd('modules/02_shanghan_other.md'))
_wj_pre = md02.split('\n##')[0].strip()
if _wj_pre and len(_wj_pre) > 60:
    _it = {'id': 'wj_head', 't': '五经篇·导言', 'b': _wj_pre}
    shanghan['wujing'].insert(0, _it)
    idx('shanghan', 'shanghan', _it['id'], _it['t'], excerpt(_wj_pre))
for t, b in split_by(md02, r'^##\s+(.*)$'):
    item = {'id': 'wj%d' % len(shanghan['wujing']), 't': t, 'b': b}
    shanghan['wujing'].append(item)
    idx('shanghan', 'shanghan', item['id'], t, excerpt(b))
wjson('shanghan.json', shanghan)

# ============================================================ 2. 金匮要略
print('» 金匮要略')
CN = {'一':1,'二':2,'三':3,'四':4,'五':5,'六':6,'七':7,'八':8,'九':9,'十':10,'十一':11,'十二':12,'十三':13,'十四':14,'十五':15,'十六':16,'十七':17,'十八':18,'十九':19,'二十':20,'二十一':21,'二十二':22,'二十三':23}
def chap_no(t):
    m = re.search(r'第([一二三四五六七八九十]+)', t)
    if not m: return None
    s = m.group(1)
    if s == '十': return 10
    if s.startswith('十'): return 10 + CN.get(s[1:], 0)
    if s.endswith('十'): return CN.get(s[0], 0) * 10
    if '十' in s:
        a, _, b = s.partition('十'); return CN.get(a,0)*10 + CN.get(b,0)
    return CN.get(s, 0)

jingui = {'chapters': []}
seen = {}
def add_jg(t, b, srcfile):
    no = chap_no(t)
    key = no if no else ('前言' if '前言' in t else t)
    if key in seen:
        return
    seen[key] = True
    item = {'id': 'jg%s' % key, 'no': no or 0, 't': t, 'b': b, 'g': [srcfile]}
    jingui['chapters'].append(item)

for f, tag in [('modules/04_jingui.md', '04'), ('modules/05_huangdi_neijing.md', '05')]:
    _src = strip_header_meta(rd(f))
    # ## 之前的散落导言并入首章，防丢
    _pre = _src.split('\n##')[0].strip()
    if _pre and len(_pre) > 20:
        add_jg(f'金匮·卷首导言（{tag}）', _pre, tag)
    for t, b in split_by(_src, r'^##\s+(.*)$'):
        add_jg(t, b, tag)
def sortkey(c):
    if '前言' in c['t']: return -1
    if c['no']: return c['no'] if c['no'] <= 23 else 100 + c['no']
    return 200
jingui['chapters'].sort(key=sortkey)
for c in jingui['chapters']:
    idx('jingui', 'jingui', c['id'], c['t'], excerpt(c['b']))
wjson('jingui.json', jingui)

# ============================================================ 3. 黄帝内经
print('» 黄帝内经')
neijing = {'chapters': []}
md08 = strip_header_meta(rd('modules/08_huangdi_detail.md'))
_nj_pre = md08.split('\n##')[0].strip()
if _nj_pre and len(_nj_pre) > 60:
    _it = {'id': 'nj_head', 't': '内经·篇目总览', 'n': '篇目总览', 'b': _nj_pre}
    neijing['chapters'].insert(0, _it)
    idx('neijing', 'neijing', _it['id'], '篇目总览', excerpt(_nj_pre))
for t, b in split_by(md08, r'^##\s+(.*)$'):
    name = t.replace('【人纪·黄帝内经】', '').replace('篇', '')
    item = {'id': 'nj%d' % len(neijing['chapters']), 't': t, 'n': name, 'b': b}
    neijing['chapters'].append(item)
    idx('neijing', 'neijing', item['id'], name or t, excerpt(b))
wjson('neijing.json', neijing)

# ============================================================ 4. 针灸
print('» 针灸')
zhenjiu = {'tutorial': [], 'quickref': [], 'highlights': [], 'points': []}
md09 = rd('modules/09_zhenjiu_bencao.md')
pos_bencao = md09.find('## 人纪·神农本草经')
pos_tianji = md09.find('## 天纪·天机道')
pos_shumu = md09.find('## 【倪海厦推荐书目】')
pos_hantang = md09.find('## 【汉唐文章精华】')
zj_md = md09[:pos_bencao]
_zj_pre = zj_md.split('\n###')[0].strip()
if _zj_pre and len(_zj_pre) > 60:
    _it = {'id': 'zj_head', 't': '针灸教程·总览', 'b': _zj_pre}
    zhenjiu['tutorial'].insert(0, _it)
    idx('zhenjiu', 'zhenjiu', _it['id'], _it['t'], excerpt(_zj_pre), ['教程'])
for t, b in split_by(zj_md, r'^###\s+(.*)$'):
    item = {'id': 'zj%d' % len(zhenjiu['tutorial']), 't': t, 'b': b}
    zhenjiu['tutorial'].append(item)
    idx('zhenjiu', 'zhenjiu', item['id'], t, excerpt(b), ['教程'])
# 04 针灸精髓
md04z = strip_header_meta(rd('references/distilled/04-acupuncture-highlights.md'))
_zh_pre = md04z.split('\n##')[0].strip()
if _zh_pre and len(_zh_pre) > 12:
    zhenjiu['highlights'].insert(0, {'id': 'zh_head', 't': '针灸精髓·文档说明', 'b': _zh_pre})
    idx('zhenjiu', 'zhenjiu', 'zh_head', '针灸精髓·文档说明', excerpt(_zh_pre), ['精髓'])
for t, b in split_by(md04z, r'^##\s+(.*)$'):
    if not t.strip():
        continue
    item = {'id': 'zh%d' % len(zhenjiu['highlights']), 't': t, 'b': b}
    zhenjiu['highlights'].append(item)
    idx('zhenjiu', 'zhenjiu', item['id'], t, excerpt(b), ['精髓'])
# 02 速查
md02z = strip_header_meta(rd('references/distilled/02-acupuncture-quick-ref.md'))
_zq_pre = md02z.split('\n##')[0].strip()
if _zq_pre and len(_zq_pre) > 12:
    zhenjiu['quickref'].insert(0, {'id': 'zq_head', 't': '针灸速查·文档说明', 'b': _zq_pre})
    idx('zhenjiu', 'zhenjiu', 'zq_head', '针灸速查·文档说明', excerpt(_zq_pre), ['速查'])
for t, b in split_by(md02z, r'^##\s+(.*)$'):
    item = {'id': 'zq%d' % len(zhenjiu['quickref']), 't': t, 'b': b}
    zhenjiu['quickref'].append(item)
    idx('zhenjiu', 'zhenjiu', item['id'], t, excerpt(b), ['速查'])
# 09 中针灸后半（针灸补遗/治症经验/经脉逐穴）——位于本草之后
tail = md09[pos_hantang:]  # 先处理后面再回头
zj_tail = md09[md09.find('## 针灸补遗'):] if '## 针灸补遗' in md09 else ''
_zjt_pre = zj_tail.split('\n###')[0].strip()
if _zjt_pre and len(_zjt_pre) > 12:
    zhenjiu['points'].insert(0, {'id': 'pt_head', 't': '针灸补遗·说明（P0 审计补齐）', 'b': _zjt_pre})
    idx('zhenjiu', 'point', 'pt_head', '针灸补遗·说明', excerpt(_zjt_pre), ['穴位'])
for t, b in split_by(zj_tail, r'^###\s+(.*)$'):
    m = re.match(r'^(.{1,7}?)[（(]', t)
    name = m.group(1) if m else t
    if '穴' in t or '经' in t or re.match(r'^[\u4e00-\u9fa5]{1,5}$', name):
        item = {'id': 'pt%d' % len(zhenjiu['points']), 't': t, 'b': b}
        zhenjiu['points'].append(item)
        idx('zhenjiu', 'point', item['id'], name, excerpt(b), ['穴位'])
wjson('zhenjiu.json', zhenjiu)

# ============================================================ 5. 神农本草经
print('» 神农本草经')
bencao = {'intro': [], 'herbs': []}
bc_md = md09[pos_bencao:pos_tianji]
# 三经区间
def sec_range(txt, start_pat, end_pat):
    s = re.search(start_pat, txt, re.M)
    if not s: return ''
    rest = txt[s.end():]
    e = re.search(end_pat, rest, re.M)
    return rest[: e.start()] if e else rest
grade_map = [('上经', 'upper', '### 上经'), ('中经', 'middle', '### 中经'), ('下经', 'lower', '### 下经')]
# 前言部分（药性总义等）
intro_md = bc_md[:bc_md.find('### 上经')]
_bc_pre = intro_md.split('\n###')[0].strip()
if _bc_pre and len(_bc_pre) > 60:
    bencao['intro'].append({'id': 'bi_head', 't': '神农本草经·总览', 'b': _bc_pre})
    idx('bencao', 'bencao', 'bi_head', '神农本草经·总览', excerpt(_bc_pre), ['总义'])
for t, b in split_by(intro_md, r'^###\s+(.*)$'):
    item = {'id': 'bi%d' % len(bencao['intro']), 't': t, 'b': b}
    bencao['intro'].append(item)
    idx('bencao', 'bencao', item['id'], t, excerpt(b), ['总义'])
for gname, gid, pat in grade_map:
    seg = sec_range(bc_md, re.escape(pat) + r'.*', r'^###\s')
    m_heading = re.search(re.escape(pat) + r'[^\n]*', bc_md)
    grade_title = m_heading.group(0).strip() if m_heading else ''
    # 段首杂文 = 第一个 **药名** 行之前的内容（防丢；无药名则整段为杂文）
    m_herb0 = re.search(r'^\*\*[^*{][^*]*?\*\*\s*$', seg, re.M)
    lead = seg[: m_herb0.start()] if m_herb0 else ''
    lead_txt = (grade_title + '\n\n' + lead.strip()).strip() if lead.strip() else grade_title
    if lead_txt:
        bencao['intro'].append({'id': 'bi_lead_%s' % gid, 't': '%s·导言与补注' % gname, 'b': lead_txt})
    # 按 **药名** 行切分
    parts = re.split(r'^\*\*([^*{][^*]*?)\*\*\s*$', seg, flags=re.M)
    if parts and parts[0].strip():
        pass  # 段首杂文已单独收录
    i = 1
    while i + 1 < len(parts) + 1 and i < len(parts):
        name = parts[i].strip()
        body = parts[i+1] if i+1 < len(parts) else ''
        i += 2
        if not name or '倪师' in name or '临床' in name:
            continue
        fields, notes, para, in_note = {}, [], [], False
        for line in body.split('\n'):
            ls = line.strip()
            if ls.startswith('**倪师'):
                in_note = True; continue
            if ls.startswith('- '):
                m = re.match(r'^-\s+\*?\*?(原文|性味|主治|倪注|容川|用量|禁忌)\*?\*?[：:]\s*(.*)$', ls)
                if m:
                    in_note = False
                    fields[m.group(1)] = m.group(2).strip()
                else:
                    (notes if in_note else para).append(ls[2:])
            elif ls:
                (notes if in_note else para).append(ls)
        herb = {'id': 'hb_%s_%d' % (gid, len(bencao['herbs'])), 'n': name, 'g': gname}
        herb.update({k: fields.get(k, '') for k in ['原文', '性味', '主治', '倪注', '容川', '用量', '禁忌']})
        herb['口述'] = '\n'.join(notes).strip()
        herb['补注'] = '\n'.join(para).strip()
        bencao['herbs'].append(herb)
        idx('bencao', 'herb', herb['id'], name, clean(herb.get('主治', '') or herb.get('原文', ''))[:120], [gname])
print(f'    本草: {len(bencao["herbs"])} 味  上{sum(1 for h in bencao["herbs"] if h["g"]=="上经")}/中{sum(1 for h in bencao["herbs"] if h["g"]=="中经")}/下{sum(1 for h in bencao["herbs"] if h["g"]=="下经")}')
# 倪师口吻参考
kou_md = sec_range(bc_md, r'^###\s+倪师口吻参考.*$', r'^##\s')
if kou_md.strip():
    bencao['intro'].append({'id': 'bi_kou', 't': '倪师口吻参考（视频讲义精华）', 'b': '### 倪师口吻参考（视频讲义精华）\n' + kou_md})
wjson('bencao.json', bencao)

# ============================================================ 6. 天纪
print('» 天纪')
tianji = {'sections': []}
tj_md = md09[pos_tianji:pos_shumu]
for t, b in split_by(tj_md, r'^##\s+(.*)$'):
    subs = split_by(b, r'^###\s+(.*)$')
    _tj_pre = b.split('\n###')[0].strip()
    if _tj_pre and len(_tj_pre) > 12 and subs:
        _it = {'id': 'tjp%d' % len(tianji['sections']), 't': t + ' · 概览', 'b': _tj_pre, 'g': [t.replace('天纪·', '')]}
        tianji['sections'].append(_it)
        idx('tianji', 'tianji', _it['id'], t + '·概览', excerpt(_tj_pre), _it['g'])
    if subs:
        for st, sb in subs:
            item = {'id': 'tj%d' % len(tianji['sections']), 't': f'{t} · {st}', 'b': f'### {st}\n{sb}', 'g': [t.replace('天纪·', '')]}
            tianji['sections'].append(item)
            idx('tianji', 'tianji', item['id'], st, excerpt(sb), item['g'])
    else:
        item = {'id': 'tj%d' % len(tianji['sections']), 't': t, 'b': b, 'g': [t.replace('天纪·', '')]}
        tianji['sections'].append(item)
        idx('tianji', 'tianji', item['id'], t, excerpt(b), item['g'])
wjson('tianji.json', tianji)

# ============================================================ 7. 方剂库
print('» 方剂库')
formulas = {'items': [], 'articles': []}
def add_formula(name, **kw):
    name = re.sub(r'\*\*', '', clean(name))
    if not name: return
    item = {'id': 'fm%d' % len(formulas['items']), 'n': name}
    item.update({k: v for k, v in kw.items() if v})
    formulas['items'].append(item)
    idx('formulas', 'formula', item['id'], name, clean(kw.get('zhizhi') or kw.get('clinical') or kw.get('note') or '')[:150])

# 05 临床剂量速查
md05d = strip_header_meta(rd('references/distilled/05-clinical-dose-quickref.md'))
for t, b in split_by(md05d, r'^###\s+(.*)$'):
    tbs = parse_tables(b)
    if not tbs:
        formulas['articles'].append({'id': 'fa%d' % len(formulas['articles']), 't': t, 'b': f'### {t}\n{b}'})
        continue
    for head, rows in tbs:
        for r in rows:
            add_formula(r[0], origin=r[1] if len(r) > 1 else '', clinical=r[2] if len(r) > 2 else '',
                        note=r[3] if len(r) > 3 else '', src='临床剂量速查·' + t)
# 06 C类剂量
md06d = strip_header_meta(rd('references/distilled/06-clinical-dose-c99.md'))
for t, b in split_by(md06d, r'^##\s+(.*)$'):
    tbs = parse_tables(b)
    if not tbs:
        formulas['articles'].append({'id': 'fa%d' % len(formulas['articles']), 't': t, 'b': f'## {t}\n{b}'})
        continue
    for head, rows in tbs:
        for r in rows:
            if len(head) >= 4:
                add_formula(r[0], origin=r[1], clinical=r[2], note=r[3], src='C类剂量·' + t)
            else:
                add_formula(r[0], clinical=r[1] if len(r) > 1 else '', note=r[2] if len(r) > 2 else '', src='C类剂量·' + t)
# SKILL 感冒六经 + 关键方剂 + 速查卡
skill_raw = rd('SKILL.md')
def skill_section(title_pat, src):
    lines = skill_raw.split('\n')
    out, cap = [], False
    pat = re.compile(title_pat)
    for ln in lines:
        if re.match(r'^#{2,3}\s', ln):
            cap = bool(pat.match(ln))
            if cap: out = [ln]
            continue
        if cap: out.append(ln)
    return '\n'.join(out)
sec_e = skill_section(r'^##\s+E\.\s*感冒六大经方速查', '感冒六经速查')
tb = parse_tables(sec_e)
if tb:
    for r in tb[0][1]:
        add_formula(r[0], zhizhi=r[1] if len(r) > 1 else '', origin=r[2] if len(r) > 2 else '', clinical=r[3] if len(r) > 3 else '', src='感冒六大经方')
sec_k = skill_section(r'^###\s*关键方剂速查', '关键方剂速查')
tb = parse_tables(sec_k)
if tb:
    for r in tb[0][1]:
        add_formula(r[0], composition=r[1] if len(r) > 1 else '', zhizhi=r[2] if len(r) > 2 else '', src='六经关键方剂')
sec_card = skill_section(r'^###\s*方剂剂量速查卡', '速查卡')
tb = parse_tables(sec_card.split('⚠️')[0])
if tb:
    for r in tb[0][1]:
        add_formula(r[0], doses=r[1] if len(r) > 1 else '', note=r[2] if len(r) > 2 else '', src='剂量速查卡')
formulas['articles'].append({'id': 'fa_ver', 't': '倪师讲课版 vs 宋本差异对照 + 剂量换算标准', 'b': ('⚠️' + sec_card.split('⚠️', 1)[1] if '⚠️' in sec_card else sec_card) + '\n\n' + skill_section(r'^###\s*剂量换算标准', '')})
formulas['articles'].append({'id': 'fa_jun', 't': '峻药剂量速查（生附子/炮附子/细辛/石膏…）', 'b': skill_section(r'^###\s*峻药剂量速查', '')})
formulas['articles'].append({'id': 'fa_fuzi', 't': '生附子 vs 炮附子 vs 生硫磺', 'b': skill_section(r'^###\s*生附子\s*vs', '')})
names = {}
for it in formulas['items']:
    names[it['n']] = names.get(it['n'], 0) + 1
print(f'    方剂条目: {len(formulas["items"])} 条 / 去重 {len(names)} 方')
for a in formulas['articles']:
    idx('formulas', 'article', a['id'], a['t'], excerpt(a['b']))
wjson('formulas.json', formulas)

# ============================================================ 8. 医案（结构化表 1257）
print('» 医案·结构化表')
cases_tbl = {'rows': []}
mdc = rd('cases/00_merged_table.md')
cases_head = mdc.split('## 医案表格')[0]
_tbl_zone = mdc.split('## 医案表格')[1] if '## 医案表格' in mdc else ''
cases_head = cases_head.rstrip() + '\n\n## 医案表格（字段）\n\n' + '\n'.join(_tbl_zone.split('\n')[:3])
head, rows = None, []
for t, b in split_by(mdc, r'^##\s+(.*)$'):
    tb = parse_table(b)
    if tb and tb[0][0] == '序号':
        head, rows = tb
if not head:
    tbl = parse_table(mdc); head, rows = tbl
FIELDS = ['n', 'date', 'patient', 'diag', 'bingji', 'xiyi', 'fangji', 'zhenjiu', 'zhifa', 'result', 'yizhu', 'guandian']
for r in rows:
    if not r or clean(r[0]) in ('', '---') or not clean(r[0]).isdigit():
        continue
    row = {FIELDS[i]: clean(r[i]) if i < len(r) else '' for i in range(len(FIELDS))}
    for k, v in row.items():
        if v == '---': row[k] = ''
    row['n'] = int(row['n'])
    cases_tbl['rows'].append(row)
    idx('casesTable', 'case', 'c%d' % row['n'], f"{row['diag'] or '未记诊断'}", clean(row['fangji'] + ' ' + row['bingji'] + ' ' + row['result'])[:150], [row['diag'][:6]])
print(f'    结构化医案: {len(cases_tbl["rows"])} 行')
wjson('cases_table.json', cases_tbl)

# ============================================================ 9. 叙事医案（243）+ 医案集（410）
print('» 医案·叙事')
narr = {'groups': []}
GRP = [('cases/01_cancer.md', '癌症', 147), ('cases/02_cardiovascular.md', '心血管', None), ('cases/03_metabolic.md', '代谢', None),
       ('cases/04_autoimmune.md', '免疫', None), ('cases/05_neurological.md', '神经', None), ('cases/06_other.md', '其他', None)]
for f, label, _ in GRP:
    md = rd(f)
    items = []
    _grp_pre = md.split('\n###')[0].strip()
    if _grp_pre and len(_grp_pre) > 30:
        items.append({'id': 'nc_head_%s' % label, 'n': 0, 't': label + '医案·分类说明', 'g': label,
                      'date': '', 'disease': '', 'meridian': '', 'words': '',
                      'b': _grp_pre, '_pre': True})
    for t, b in split_by(md, r'^###\s+(.*)$'):
        m = re.match(r'^(\d+)\.\s*(.*)$', t)
        if not m and items and not items[-1].get('_pre'):
            prev = items[-1]
            prev['b'] += '\n\n### ' + t + '\n' + b
            continue
        no = int(m.group(1)) if m else len(items) + 1
        title = m.group(2) if m else t
        meta = {'date': '', 'disease': '', 'meridian': '', 'words': ''}
        for k, pat in [('date', r'\*\*日期\*\*：(.*)'), ('disease', r'\*\*疾病\*\*：(.*)'), ('meridian', r'\*\*六经\*\*：(.*)'), ('words', r'\*\*字数\*\*：(.*)')]:
            mm = re.search(pat, b)
            meta[k] = clean(mm.group(1)) if mm else ''
        sm = re.search(r'\*\*摘要\*\*：(.*)', b, re.S)
        item = {'id': 'nc%d' % no, 'n': no, 't': title, 'g': label, **meta, 'b': b}
        items.append(item)
        idx('casesNarr', 'caseN', item['id'], f"{title}（{label}）", clean(sm.group(1))[:150] if sm else excerpt(b), [label, meta['disease']])
    narr['groups'].append({'g': label, 'items': items})
print(f'    叙事医案: {sum(len(g["items"]) for g in narr["groups"])} 条')
for g in narr['groups']:
    for it in g['items']:
        it.pop('_pre', None)
wjson('cases_narr.json', narr)

yian = {'items': []}
md03y = strip_header_meta(rd('modules/03_yian.md'))
# ### 之前的导言（含【人纪·医案集】说明），防止内容丢失
_yian_pre = md03y.split('\n###')[0].strip()
if _yian_pre and len(_yian_pre) > 30:
    it0 = {'id': 'ya_head', 't': '医案集·导言与索引', 'date': '', 'disease': '', 'meridian': '', 'b': _yian_pre, '_pre': False}
    yian['items'].append(it0)
    idx('yian', 'yian', it0['id'], it0['t'], excerpt(_yian_pre))
REAL_CASE = re.compile(r'^(\d{6}|\d{2}日期未知|【|人纪|医案集)')
def _clean_meta_head(b):
    # 保留原文全部行（日期/疾病/六经已结构化入字段，正文亦保留原行，确保内容零丢失）
    return b.strip()
for t, b in split_by(md03y, r'^###\s+(.*)$'):
    meta = {'date': '', 'disease': '', 'meridian': ''}
    for k, pat in [('date', r'\*\*日期\*\*：(.*)'), ('disease', r'\*\*疾病\*\*：(.*)'), ('meridian', r'\*\*六经\*\*：(.*)')]:
        mm = re.search(pat, b)
        meta[k] = clean(mm.group(1)) if mm else ''
    body = _clean_meta_head(b)
    if yian['items'] and not REAL_CASE.match(t) and not yian['items'][-1].get('_pre'):
        # 内嵌病历小节（来诊原因/问诊/脉诊…）并回父病例，内容零丢失
        yian['items'][-1]['b'] += '\n\n### ' + t + '\n' + body
        continue
    item = {'id': 'ya%d' % len(yian['items']), 't': t, **meta, 'b': body}
    yian['items'].append(item)
    idx('yian', 'yian', item['id'], t, excerpt(body), [meta['disease']])
print(f'    医案集: {len(yian["items"])} 条')
for it in yian['items']:
    it.pop('_pre', None)
wjson('yian.json', yian)

# ============================================================ 10. SKILL 树（诊断/视角/速查）
print('» SKILL 全树')
def skill_tree():
    lines = skill_raw.split('\n')
    units, h1 = [], ''
    h2 = h3 = None
    buf = []
    def flush():
        nonlocal buf
        body = '\n'.join(buf).strip('\n')
        if (h2 or h3) and body.strip():
            title = h3 or h2
            units.append({'h2': h2 or '', 't': title, 'b': body})
        buf = []
    for ln in lines:
        m1 = re.match(r'^#\s+(?!倪师表达速查卡|知识库蒸馏|关键词索引)(.*)$', ln)
        m2 = re.match(r'^##\s+(.*)$', ln)
        m3 = re.match(r'^###\s+(.*)$', ln)
        if m2:
            flush(); h2 = m2.group(1).strip(); h3 = None; continue
        if m3:
            flush(); h3 = m3.group(1).strip(); continue
        if m1 and not h2:
            h1 = m1.group(1).strip(); continue
        buf.append(ln)
    flush()
    return units
units = skill_tree()
skill_units = {'units': units}
for u in units:
    uid = 'sk' + hashlib.md5(u['t'].encode()).hexdigest()[:8]
    u['id'] = uid
    idx('skill', 'skill', uid, u['t'], excerpt(u['b']), [u['h2'][:10]])
wjson('skill_units.json', skill_units)

# distilled 01 / 03 → 诊断
diag = {'groups': []}
def load_group(fname, gid, label):
    md = strip_header_meta(rd(fname))
    items = []
    for t, b in split_by(md, r'^##\s+(.*)$'):
        if not t.strip(): continue
        subs = split_by(b, r'^###\s+(.*)$')
        _pre2 = b.split('\n###')[0].strip()
        if _pre2 and len(_pre2) > 60 and len(subs) >= 2:
            items.append({'id': '%s_%d' % (gid, len(items)), 't': t + ' · 概览', 'b': _pre2})
        # 子项标题并入 h2 上下文（如"公式一：太阳病 · 提纲"），避免碎片重名
        def joint(h2, st):
            if st == h2 or h2 in st or st in h2:
                return st
            return h2 + ' · ' + st
        if len(subs) >= 2:
            for st, sb in subs:
                items.append({'id': '%s_%d' % (gid, len(items)), 't': joint(t, st), 'b': f'## {t}\n### {st}\n{sb}'})
        else:
            items.append({'id': '%s_%d' % (gid, len(items)), 't': t, 'b': f'## {t}\n{b}'})
    diag['groups'].append({'g': gid, 'label': label, 'items': items})
    return items
g1 = load_group('references/distilled/01-six-meridian-formulas.md', 'liu', '六经辨证诊断公式（完整版）')
for it in g1:
    idx('diag', 'diag', it['id'], it['t'], excerpt(it['b']))
g3 = load_group('references/distilled/03-clinical-experience.md', 'exp', '诊断经验汇编（感冒六方·病机十九条）')
for it in g3:
    idx('diag', 'diag', it['id'], it['t'], excerpt(it['b']))
wjson('diagnosis.json', diag)

# ============================================================ 11. 讲义文库（文章）
print('» 讲义文库')
articles = {'items': []}
def add_article(title, body, src, group='讲座讲义'):
    item = {'id': 'ar%d' % len(articles['items']), 't': title, 'b': body, 'src': src, 'g': group}
    articles['items'].append(item)
    idx('articles', 'article', item['id'], title, excerpt(body), [src])
for f, label in [('modules/06_liangdong.md', '梁冬对话精华'), ('modules/07_bimen_hantang.md', '人纪闭门课·七大重病'),
                 ('modules/10_fuyang_luntan.md', '扶阳论坛演讲'), ('modules/11_zhongjing_xinfa.md', '仲景心法'),
                 ('modules/12_stanford_jingfang.md', '斯坦福演讲·经方妙用'), ('modules/14_yijinjing_bidu.md', '易筋经与五脏逼毒法')]:
    md = strip_header_meta(rd(f))
    _pre = md.split('\n##')[0].strip()
    if _pre and len(_pre) > 60:
        add_article(label + '·导言', _pre, label)
    secs = split_by(md, r'^##\s+(.*)$')
    if len(secs) >= 2:
        for t, b in secs:
            add_article(t, f'## {t}\n{b}', label)
    else:
        add_article(label, md, label)
# 09 汉唐文章/诊疗日志/推荐书目
ht = md09[pos_shumu:]
for t, b in split_by(ht, r'^##\s+(.*)$'):
    subs = split_by(b, r'^###\s+(.*)$')
    if t.startswith('【倪海厦推荐书目】'):
        add_article('倪海厦推荐书目', '## 【倪海厦推荐书目】\n' + (ht[:ht.find('## 【汉唐文章精华】')] if '## 【汉唐文章精华】' in ht else b), '汉唐文章', '汉唐文库')
        continue
    if len(subs) >= 2:
        for st, sb in subs:
            add_article(st, f'## {t}\n### {st}\n{sb}', '汉唐文章', '汉唐文库')
    else:
        add_article(t, f'## {t}\n{b}', '汉唐文章', '汉唐文库')
# research
for fn in sorted(os.listdir(os.path.join(SRC, 'references/research'))):
    md = strip_header_meta(rd('references/research/' + fn))
    add_article(md.split('\n')[0].lstrip('# ').strip() or fn, md, '调研资料', '调研附录')
# distilled_cases / audit
add_article('医案蒸馏清单（243 例超长医案索引）', strip_header_meta(rd('distilled_cases.md')), '医案蒸馏', '调研附录')
add_article('蒸馏审计注记', strip_header_meta(rd('references/distilled/audit-notes.md')), '审计', '调研附录')
add_article('表达风格全库（expression_style）', strip_header_meta(rd('expression_style.md')), '表达风格', 'AI内核')
# —— 补齐：仓库其余文件全量收录（审计清单/蒸馏README/英文说明/官网预览/医案总表头）——
add_article('医案总表·数据来源统计（1257 例来源与年度说明）', cases_head.strip(), '医案总表', '调研附录')
add_article('知识库蒸馏精华说明（distilled/README）', strip_header_meta(rd('references/distilled/README.md')), '蒸馏说明', '调研附录')
for fn, ttl in [('references/audit/fangji_112.txt', '伤寒论六经方剂覆盖自查清单（112方）'),
                ('references/audit/zhenjiu_164.txt', '人纪针灸164项覆盖自查清单')]:
    add_article(ttl, rd(fn), '审计清单', '调研附录')
add_article('README_EN（English Introduction）', strip_header_meta(rd('README_EN.MD')), '项目说明', '调研附录')
add_article('README.md 原文存档（含安装指引/平台徽章/目录树）', rd('README.md'), '项目说明', '调研附录')
add_article('仓库官网预览页（index.html 源码）', '```html\n' + rd('index.html') + '\n```', '项目说明', '调研附录')
add_article('SKILL.md 完整原文（AI 内核 · 132KB）', '```markdown\n' + skill_raw + '\n```', 'SKILL原文', 'AI内核')
add_article('经方临床剂量速查表·原文全档（05）', rd('references/distilled/05-clinical-dose-quickref.md'), '剂量速查', '调研附录')
add_article('C类方剂临床剂量速查表·原文全档（06）', rd('references/distilled/06-clinical-dose-c99.md'), '剂量速查', '调研附录')
add_article('六经辨证诊断公式·原文全档（distilled/01）', rd('references/distilled/01-six-meridian-formulas.md'), '六经公式', '调研附录')
add_article('诊断经验汇编·原文全档（distilled/03）', rd('references/distilled/03-clinical-experience.md'), '诊断经验', '调研附录')
wjson('articles.json', articles)

def clean_readme(md):
    """README 展示清洗：剥 GitHub 徽章/HTML 标签行/裸链接行；目录树等超长代码块压缩"""
    FENCE = '`' * 3
    lines = md.split('\n')
    out, i = [], 0
    while i < len(lines):
        l = lines[i]
        # 代码块：>24 行的目录树等折叠为提示行
        if l.strip().startswith(FENCE):
            j = i + 1
            while j < len(lines) and not lines[j].strip().startswith(FENCE):
                j += 1
            n = j - i - 1
            if n > 24:
                out.append('> （此处为 %d 行代码/目录块，详见仓库原文）' % n)
            else:
                out.extend(lines[i:j + 1])
            i = j + 1
            continue
        st = l.strip()
        # HTML 标签行 / 徽章行 / 裸链接行
        if (st.startswith('<') and st.endswith('>')) or st.startswith('![') or (st.startswith('https://') and ' ' not in st and len(st) < 120):
            i += 1
            continue
        # 连续 --- 分隔线压成一条
        if st == '---' and out and out[-1].strip() == '---':
            i += 1
            continue
        out.append(l)
        i += 1
    return '\n'.join(out)

# ============================================================ 12. 元信息 + AI 原文
print('» 元信息')
changelog_full = rd('CHANGELOG.md')
changelog = changelog_full[:4000]
readme = rd('README.md')
meta = {
    'app': '倪师经方',
    'version': 'v2026.8.15b',
    'source': 'github.com/jangviktor-web/nihaixia',
    'builtAt': __import__('datetime').datetime.now().strftime('%Y-%m-%d'),
    'counts': {
        'shanghanSun': len(shanghan['sun']), 'shanghanQue': len(shanghan['que']), 'wujing': len(shanghan['wujing']),
        'jingui': len(jingui['chapters']), 'neijing': len(neijing['chapters']),
        'herbs': len(bencao['herbs']), 'formulas': len(names),
        'casesTable': len(cases_tbl['rows']), 'casesNarr': sum(len(g['items']) for g in narr['groups']),
        'yian': len(yian['items']), 'zhenjiu': len(zhenjiu['tutorial']) + len(zhenjiu['quickref']) + len(zhenjiu['highlights']),
        'points': len(zhenjiu['points']), 'tianji': len(tianji['sections']), 'articles': len(articles['items']),
    },
    'readme': clean_readme(readme),
    'changelog': changelog_full,
}
wjson('meta.json', meta)
wjson('skill_raw.json', {'md': skill_raw})
wjson('index.json', INDEX)
print(f'\n✅ 共索引 {len(INDEX)} 个条目；输出目录: {os.path.abspath(OUT)}')
