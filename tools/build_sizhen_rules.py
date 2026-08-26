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
        items.append({'id': item.get('id'), 'title': item.get('t', ''), 'group': group.get('label', ''), 'excerpt': ' '.join(str(item.get('b', '')).split())[:320]})

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
 # 知识库复合舌象与真寒假热/真热假寒
 {'id':'tongue-taiyin-wet','name':'太阴脾虚湿盛舌象','meridian':'太阴','score':3,'when':['舌质=胖大有齿痕','舌苔=白腻'],'sourceTitle':'舌诊速查'},
 {'id':'tongue-yangming-dry','name':'阳明腑实舌象','meridian':'阳明','score':3,'when':['舌质=红','舌苔=燥裂'],'sourceTitle':'舌诊速查'},
 {'id':'tongue-shaoyin-cold','name':'少阴寒化兼瘀血舌象','meridian':'少阴','score':2,'when':['舌质=紫暗','舌苔=薄白'],'sourceTitle':'舌诊速查'},
 {'id':'tongue-shaoyin-hot','name':'少阴热化舌象','meridian':'少阴','score':3,'when':['舌质=红','舌苔=剥落','睡眠=彻夜不眠'],'sourceTitle':'舌诊速查'},
 {'id':'true-cold-false-hot','name':'真寒假热鉴别','meridian':'','score':0,'when':['舌质=淡白','口渴=渴不欲饮','小便=清长'],'sourceTitle':'真寒假热'},
 {'id':'true-hot-false-cold','name':'真热假寒鉴别','meridian':'','score':0,'when':['舌质=红','舌苔=燥裂','口渴=渴喜冷饮','小便=短赤'],'sourceTitle':'真热假寒'},
 # 合病、并病和七步中的关键组合
 {'id':'hebing-taiyang-yangming','name':'太阳阳明合病','meridian':'太阳、阳明','score':2,'when':['汗=无汗','寒热=恶寒','口渴=渴喜冷饮'],'sourceTitle':'合病'},
 {'id':'bing-shaoyin-jueyin','name':'少阴厥阴并病','meridian':'少阴、厥阴','score':2,'when':['手足温度=手脚冰凉','舌质=红','舌苔=薄白'],'sourceTitle':'并病'},
 {'id':'transmission-taiyin-shaoyin','name':'太阴传少阴观察','meridian':'太阴、少阴','score':1,'when':['头身=身重困倦','脉形=细','睡眠=但欲寐'],'sourceTitle':'七步走'},
 # 用药铁律：只产出安全证据，不直接增加方剂分数
 {'id':'rule-no-mahuang-with-sweat','name':'有汗不可用麻黄方向','meridian':'','score':0,'when':['汗=有汗自汗'],'sourceTitle':'用药铁律'},
 {'id':'rule-no-guizhi-without-sweat','name':'无汗不可直接用桂枝方向','meridian':'','score':0,'when':['汗=无汗'],'sourceTitle':'用药铁律'},
 {'id':'rule-shaoyang-three禁','name':'少阳三禁：不可汗、下、吐','meridian':'','score':0,'when':['寒热=往来寒热'],'sourceTitle':'用药铁律'},
 {'id':'rule-shaoyin-no-sweat','name':'少阴不可随意发汗','meridian':'','score':0,'when':['睡眠=但欲寐','脉形=细'],'sourceTitle':'用药铁律'},
 # 闻诊、饮食、二便和心腹证据
 {'id':'wen-deficiency','name':'闻诊虚证','meridian':'太阴、少阴','score':1,'when':['声音=语声低微','呼吸=呼吸微弱'],'sourceTitle':'诊病十问'},
 {'id':'wen-excess','name':'闻诊实热','meridian':'阳明','score':1,'when':['声音=语声高亢','呼吸=呼吸气粗'],'sourceTitle':'诊病十问'},
 {'id':'shaoyang-chest','name':'少阳胸胁苦满','meridian':'少阳','score':2,'when':['疼痛=胸胁苦满','口渴=口苦咽干'],'sourceTitle':'少阳病'},
 {'id':'taiyin-no-thirst','name':'太阴湿在中焦','meridian':'太阴','score':2,'when':['口渴=不渴','大便=溏泄','胃口=差/食少'],'sourceTitle':'太阴病'},
 {'id':'shaoyin-lower-urine','name':'少阴下焦虚寒','meridian':'少阴','score':2,'when':['小便=清长','手足温度=手脚冰凉'],'sourceTitle':'少阴病'},
 {'id':'jueyin-chong','name':'厥阴寒热错杂核心证','meridian':'厥阴','score':3,'when':['口渴=消渴多饮','胃口=饥而不欲食','疼痛=气上撞心/心中疼热'],'sourceTitle':'厥阴病'},
 # 八纲、脉舌和传变补充规则
 {'id':'taiyang-ge','name':'太阳项强无汗','meridian':'太阳','score':2,'when':['头身=头痛项强','汗=无汗'],'sourceTitle':'太阳病'},
 {'id':'taiyang-body','name':'太阳身痛恶寒','meridian':'太阳','score':2,'when':['头身=身痛骨节痛','寒热=恶寒'],'sourceTitle':'太阳病'},
 {'id':'yangming-four','name':'阳明四大证','meridian':'阳明','score':4,'when':['寒热=但热不寒','汗=大汗不止','口渴=渴喜冷饮','脉形=洪'],'sourceTitle':'阳明病'},
 {'id':'yangming-urine','name':'阳明里热小便短赤','meridian':'阳明','score':1,'when':['小便=短赤','口渴=渴喜冷饮'],'sourceTitle':'阳明病'},
 {'id':'shaoyang-mouth','name':'少阳口苦咽干','meridian':'少阳','score':2,'when':['口渴=口苦咽干','寒热=往来寒热'],'sourceTitle':'少阳病'},
 {'id':'shaoyang-dizziness','name':'少阳目眩','meridian':'少阳','score':1,'when':['头身=头晕目眩','脉形=弦'],'sourceTitle':'少阳病'},
 {'id':'taiyin-abdomen','name':'太阴腹满食不下','meridian':'太阴','score':2,'when':['腹满=腹满','胃口=差/食少'],'sourceTitle':'太阴病'},
 {'id':'taiyin-white','name':'太阴苔白腻不渴','meridian':'太阴','score':3,'when':['舌苔=白腻','口渴=不渴'],'sourceTitle':'舌诊速查'},
 {'id':'shaoyin-sleep','name':'少阴但欲寐脉微细','meridian':'少阴','score':4,'when':['睡眠=但欲寐','脉形=细','脉力=微'],'sourceTitle':'少阴病'},
 {'id':'shaoyin-urine','name':'少阴小便清长','meridian':'少阴','score':2,'when':['小便=清长','手足温度=手脚冰凉'],'sourceTitle':'少阴病'},
 {'id':'shaoyin-heart','name':'少阴心悸','meridian':'少阴','score':1,'when':['胸腹=心悸','脉力=无力'],'sourceTitle':'少阴病'},
 {'id':'jueyin-thirst','name':'厥阴消渴饥不欲食','meridian':'厥阴','score':3,'when':['口渴=消渴多饮','胃口=饥而不欲食'],'sourceTitle':'厥阴病'},
 {'id':'pulse-float-tight','name':'浮紧太阳伤寒脉','meridian':'太阳','score':3,'when':['复合脉=浮紧'],'sourceTitle':'脉诊速查'},
 {'id':'pulse-sunken-late','name':'沉迟太阴寒湿脉','meridian':'太阴','score':3,'when':['复合脉=沉迟'],'sourceTitle':'脉诊速查'},
 {'id':'pulse-sunken-weak','name':'沉微少阴阳虚脉','meridian':'少阴','score':3,'when':['复合脉=沉微'],'sourceTitle':'脉诊速查'},
 {'id':'pulse-string-fast','name':'弦数少阳郁热脉','meridian':'少阳','score':3,'when':['复合脉=弦数'],'sourceTitle':'脉诊速查'},
 {'id':'pulse-weak-fine','name':'微细欲绝高风险脉','meridian':'少阴','score':4,'when':['复合脉=微细欲绝'],'sourceTitle':'脉诊速查'},
 {'id':'pulse-knotted','name':'结代心动悸脉','meridian':'少阴','score':2,'when':['复合脉=结代'],'sourceTitle':'脉诊速查'},
 {'id':'cold-false-hot','name':'舌淡脉数真寒假热','meridian':'少阴','score':2,'when':['舌质=淡白','脉率=数','口渴=渴不欲饮'],'sourceTitle':'真寒假热'},
 {'id':'hot-false-cold','name':'舌红脉沉真热假寒','meridian':'阳明','score':2,'when':['舌质=红','脉位=沉','口渴=渴喜冷饮'],'sourceTitle':'真热假寒'},
 # 单项证据：将上游提纲和七步走中的关键观察点纳入统一评分
 {'id':'taiyang-fever','name':'太阳发热恶风','meridian':'太阳','score':1,'when':['寒热=恶风'],'sourceTitle':'太阳病'},
 {'id':'taiyang-neck','name':'太阳项背强痛','meridian':'太阳','score':2,'when':['头身=头痛项强'],'sourceTitle':'太阳病'},
 {'id':'yangming-sweat','name':'阳明大汗','meridian':'阳明','score':1,'when':['汗=大汗不止'],'sourceTitle':'阳明病'},
 {'id':'yangming-hard','name':'阳明胃家实','meridian':'阳明','score':2,'when':['大便=便秘'],'sourceTitle':'阳明病'},
 {'id':'shaoyang-string','name':'少阳弦脉','meridian':'少阳','score':2,'when':['脉形=弦'],'sourceTitle':'少阳病'},
 {'id':'shaoyang-throat','name':'少阳咽干口苦','meridian':'少阳','score':2,'when':['口渴=口苦咽干'],'sourceTitle':'少阳病'},
 {'id':'taiyin-abdomen-full','name':'太阴腹满','meridian':'太阴','score':2,'when':['胸腹=腹满'],'sourceTitle':'太阴病'},
 {'id':'taiyin-not-thirsty','name':'太阴不渴','meridian':'太阴','score':1,'when':['口渴=不渴'],'sourceTitle':'太阴病'},
 {'id':'taiyin-food','name':'太阴食不下','meridian':'太阴','score':2,'when':['胃口=差/食少'],'sourceTitle':'太阴病'},
 {'id':'shaoyin-deep','name':'少阴沉脉','meridian':'少阴','score':1,'when':['脉位=沉'],'sourceTitle':'少阴病'},
 {'id':'shaoyin-late','name':'少阴迟脉','meridian':'少阴','score':1,'when':['脉率=迟'],'sourceTitle':'少阴病'},
 {'id':'shaoyin-cold-ext','name':'少阴恶寒厥冷','meridian':'少阴','score':2,'when':['寒热=恶寒','手足温度=手脚冰凉'],'sourceTitle':'少阴病'},
 {'id':'jueyin-cold-hot','name':'厥阴寒热并见','meridian':'厥阴','score':2,'when':['舌质=红','舌苔=薄白'],'sourceTitle':'厥阴病'},
 {'id':'jueyin-heart','name':'厥阴心中疼热','meridian':'厥阴','score':2,'when':['疼痛=气上撞心/心中疼热'],'sourceTitle':'厥阴病'},
 {'id':'jueyin-extreme','name':'厥阴手足厥冷','meridian':'厥阴','score':2,'when':['手足温度=手脚冰凉','舌质=红'],'sourceTitle':'厥阴病'},
 {'id':'bagang-excess','name':'实证声音洪亮有力','meridian':'阳明','score':1,'when':['声音=语声高亢','脉力=有力'],'sourceTitle':'七步走'},
 {'id':'bagang-deficiency','name':'虚证声音低微无力','meridian':'太阴、少阴','score':1,'when':['声音=语声低微','脉力=无力'],'sourceTitle':'七步走'},
 {'id':'pulse-float-slow','name':'浮缓表虚','meridian':'太阳','score':2,'when':['脉位=浮','脉率=迟','汗=有汗自汗'],'sourceTitle':'脉诊速查'},
 {'id':'pulse-float-tight-combo','name':'浮紧表实','meridian':'太阳','score':2,'when':['脉位=浮','脉形=紧','汗=无汗'],'sourceTitle':'脉诊速查'},
 {'id':'pulse-string-slow','name':'弦缓少阳太阴','meridian':'少阳、太阴','score':2,'when':['脉形=弦','脉率=迟'],'sourceTitle':'脉诊速查'},
 {'id':'tongue-red-white','name':'舌红苔白寒热错杂','meridian':'厥阴','score':2,'when':['舌质=红','舌苔=薄白'],'sourceTitle':'舌象组合速查'},
 {'id':'tongue-pale-white','name':'舌淡苔白太阴寒湿','meridian':'太阴','score':2,'when':['舌质=淡白','舌苔=薄白'],'sourceTitle':'舌象组合速查'},
 {'id':'tongue-yellow-dry','name':'舌红苔燥阳明热','meridian':'阳明','score':2,'when':['舌质=红','舌苔=燥裂'],'sourceTitle':'舌象组合速查'},
 {'id':'transmission-warning','name':'脉微细伴嗜睡提示由太阴入少阴','meridian':'少阴','score':1,'when':['脉形=细','睡眠=但欲寐'],'sourceTitle':'传变预警'},
 {'id':'formula-check-sweat','name':'有汗麻黄禁忌复核','meridian':'','score':0,'when':['汗=有汗自汗'],'sourceTitle':'用药铁律'},
 {'id':'formula-check-shaoyang','name':'少阳三禁复核','meridian':'','score':0,'when':['寒热=往来寒热'],'sourceTitle':'少阳三禁'},
 # 开阖枢、六经交界与传变动态
 {'id':'kai-taiyang','name':'太阳为开·表防御','meridian':'太阳','score':1,'when':['脉位=浮'],'sourceTitle':'六经开阖枢'},
 {'id':'shu-shaoyang','name':'少阳为枢·半表半里','meridian':'少阳','score':1,'when':['寒热=往来寒热'],'sourceTitle':'六经开阖枢'},
 {'id':'he-yangming','name':'阳明为阖·里热胃家实','meridian':'阳明','score':1,'when':['寒热=但热不寒'],'sourceTitle':'六经开阖枢'},
 {'id':'taiyin-yangming-diff','name':'太阴阳明鉴别','meridian':'太阴、阳明','score':2,'when':['大便=溏泄','口渴=不渴'],'sourceTitle':'太阴 vs 阳明'},
 {'id':'taiyin-yangming-hot','name':'太阴阳明鉴别·阳明侧','meridian':'阳明','score':2,'when':['大便=便秘','口渴=渴喜冷饮'],'sourceTitle':'太阴 vs 阳明'},
 {'id':'taiyin-shaoyin-border','name':'太阴少阴交界','meridian':'太阴、少阴','score':2,'when':['头身=身重困倦','睡眠=但欲寐'],'sourceTitle':'太阴与少阴交界'},
 {'id':'jue-re-progress','name':'厥多热少·病进','meridian':'厥阴','score':2,'when':['厥热胜复=厥多热少（病进）'],'sourceTitle':'厥热胜复'},
 {'id':'jue-re-recover','name':'热多厥少·病退','meridian':'厥阴','score':2,'when':['厥热胜复=热多厥少（病退）'],'sourceTitle':'厥热胜复'},
 {'id':'jue-re-stable','name':'厥热相等·病稳','meridian':'厥阴','score':1,'when':['厥热胜复=厥热相等（病稳）'],'sourceTitle':'厥热胜复'},
 {'id':'transmission-warning-solar','name':'太阳日久传少阳预警','meridian':'少阳','score':1,'when':['duration=超过2周','寒热=往来寒热'],'sourceTitle':'传变预警'},
 {'id':'mistreat-lizhong','name':'表证误下利不止·急救复核','meridian':'太阴','score':1,'when':['misTreatment=表证误下·利不止'],'sourceTitle':'误治急救方案'},
 {'id':'mistreat-siyin','name':'少阴误汗亡阳·急救复核','meridian':'少阴','score':1,'when':['misTreatment=少阴误汗·亡阳'],'sourceTitle':'误治急救方案'},
 {'id':'misc-chibi','name':'金匮胸痹六经归属','meridian':'少阴、厥阴','score':1,'when':['miscDisease=胸痹'],'sourceTitle':'金匮杂病六经归属'},
 {'id':'misc-tan-yin','name':'金匮痰饮咳嗽六经归属','meridian':'太阳、太阴','score':1,'when':['miscDisease=痰饮咳嗽'],'sourceTitle':'金匮杂病六经归属'},
 {'id':'misc-xulao','name':'金匮虚劳六经归属','meridian':'太阴、少阴','score':1,'when':['miscDisease=虚劳'],'sourceTitle':'金匮杂病六经归属'},
 {'id':'misc-xiaoke','name':'金匮消渴六经归属','meridian':'阳明、少阴','score':1,'when':['miscDisease=消渴'],'sourceTitle':'金匮杂病六经归属'},
 {'id':'misc-lijie','name':'金匮历节六经归属','meridian':'太阳、少阴','score':1,'when':['miscDisease=历节'],'sourceTitle':'金匮杂病六经归属'},
 {'id':'shaoyin-reheat-outline','name':'少阴热化提纲','meridian':'少阴','score':2,'when':['脉率=数','睡眠=彻夜不眠'],'sourceTitle':'少阴热化证'},
 {'id':'shaoyin-cold-hot-diff','name':'少阴寒化热化鉴别','meridian':'少阴','score':1,'when':['脉形=细','脉率=数','舌质=红'],'sourceTitle':'少阴寒化 vs 热化'},
 {'id':'quick-flow-solar','name':'快速流程·恶寒脉浮','meridian':'太阳','score':2,'when':['寒热=恶寒','脉位=浮'],'sourceTitle':'快速诊断流程图'},
 {'id':'quick-flow-shaoyin','name':'快速流程·恶寒脉沉','meridian':'少阴','score':2,'when':['寒热=恶寒','脉位=沉'],'sourceTitle':'快速诊断流程图'},
 {'id':'quick-flow-yangming','name':'快速流程·不恶寒反恶热','meridian':'阳明','score':2,'when':['寒热=但热不寒'],'sourceTitle':'快速诊断流程图'},
 {'id':'kaihe-sanyin','name':'三阴开阖枢动态','meridian':'太阴、少阴、厥阴','score':1,'when':['手足温度=手脚冰凉'],'sourceTitle':'六经表里关系与气血特征'},
 {'id':'transmission-solar-yangming','name':'太阳传阳明预警','meridian':'阳明','score':1,'when':['duration=超过2周','口渴=渴喜冷饮','大便=便秘'],'sourceTitle':'正传（由表入里）'},
 {'id':'transmission-mistreat','name':'误治传变需复核','meridian':'','score':0,'when':['misTreatment=表证误下·利不止'],'sourceTitle':'误治传变与急救方案'},
 {'id':'pulse-tongue-float-thick','name':'脉浮苔厚腻·里证为主','meridian':'太阴','score':2,'when':['脉位=浮','舌苔=白腻'],'sourceTitle':'脉舌矛盾决策树'},
 {'id':'pulse-tongue-deep-red','name':'脉沉舌红苔黄·真热假寒','meridian':'阳明','score':2,'when':['脉位=沉','舌质=红','舌苔=黄'],'sourceTitle':'脉舌矛盾决策树'},
 {'id':'pulse-combo-floating-slow','name':'浮缓脉太阳中风','meridian':'太阳','score':2,'when':['复合脉=浮缓'],'sourceTitle':'脉象组合速查'},
 {'id':'pulse-combo-deep-late','name':'沉迟脉里寒','meridian':'太阴','score':2,'when':['复合脉=沉迟'],'sourceTitle':'脉象组合速查'},
 {'id':'pulse-combo-fine','name':'微细欲绝亡阳预警','meridian':'少阴','score':2,'when':['复合脉=微细欲绝'],'sourceTitle':'脉象组合速查'},
 {'id':'jingui-qi-bi','name':'金匮胸痹少阴厥阴','meridian':'少阴、厥阴','score':2,'when':['miscDisease=胸痹'],'sourceTitle':'金匮特有方剂六经归属'},
 {'id':'jingui-cough','name':'金匮咳喘太阳太阴','meridian':'太阳、太阴','score':2,'when':['miscDisease=痰饮咳嗽'],'sourceTitle':'金匮特有方剂六经归属'},
 {'id':'jingui-deficiency','name':'金匮虚劳补虚','meridian':'太阴、少阴','score':2,'when':['miscDisease=虚劳'],'sourceTitle':'金匮特有方剂六经归属'},
 {'id':'jingui-joint','name':'金匮历节痹证','meridian':'太阳、少阴','score':2,'when':['miscDisease=历节','疼痛=冷痛'],'sourceTitle':'金匮特有方剂六经归属'},
 {'id':'jingui-pain','name':'金匮胸痹急症筛查','meridian':'少阴','score':1,'when':['miscDisease=胸痹','疼痛=胸痛彻背'],'sourceTitle':'金匮特有方剂六经归属'},
 {'id':'clinical-no-attack','name':'临床心法·表证不可攻里','meridian':'','score':0,'when':['脉位=浮','寒热=恶寒','大便=便秘'],'sourceTitle':'临床心法'},
 {'id':'clinical-shaoyang-single','name':'临床心法·少阳但见一证','meridian':'少阳','score':1,'when':['寒热=往来寒热'],'sourceTitle':'临床心法'},
 {'id':'clinical-yangming-stop','name':'临床心法·阳明病位停止传变','meridian':'阳明','score':1,'when':['寒热=但热不寒'],'sourceTitle':'临床心法'},
 {'id':'clinical-liver-spleen','name':'金匮心法·见肝先实脾','meridian':'太阴','score':1,'when':['miscDisease=虚劳','胃口=差/食少'],'sourceTitle':'金匮心法'},
 {'id':'clinical-warm-phlegm','name':'金匮心法·痰饮温药和之','meridian':'太阴','score':1,'when':['miscDisease=痰饮咳嗽','舌苔=白腻'],'sourceTitle':'金匮心法'},
 {'id':'lung-phlegm','name':'病机经验·诸气膹郁属肺','meridian':'太阴','score':1,'when':['呼吸=喘','胸腹=胸腹胀满'],'sourceTitle':'病机十九条'},
 {'id':'spleen-wet','name':'病机经验·诸湿肿满属脾','meridian':'太阴','score':1,'when':['胸腹=腹满','头身=身重困倦'],'sourceTitle':'病机十九条'},
 {'id':'heart-pain-itch','name':'病机经验·诸痛痒疮属心','meridian':'阳明','score':1,'when':['疼痛=灼痛','舌质=红'],'sourceTitle':'病机十九条'},
 {'id':'lower-jiao','name':'病机经验·诸厥固泄属下','meridian':'少阴','score':1,'when':['手足温度=手脚冰凉','小便=不利/癃闭'],'sourceTitle':'病机十九条'},
 {'id':'upper-middle','name':'病机经验·诸痿喘呕属上','meridian':'阳明','score':1,'when':['呼吸=喘','胃口=食入即吐'],'sourceTitle':'病机十九条'},
 {'id':'fire-spasm','name':'病机经验·诸热瞀瘛属火','meridian':'阳明','score':1,'when':['望神=失神','脉率=数'] ,'sourceTitle':'病机十九条'},
 {'id':'time-taiyang','name':'欲解时·太阳','meridian':'太阳','score':0,'when':['symptomTime=中午（巳至未）'],'sourceTitle':'欲解时'},
 {'id':'time-yangming','name':'欲解时·阳明','meridian':'阳明','score':0,'when':['symptomTime=黄昏（申至戌）'],'sourceTitle':'欲解时'},
 {'id':'time-shaoyang','name':'欲解时·少阳','meridian':'少阳','score':0,'when':['symptomTime=清晨（寅至辰）'],'sourceTitle':'欲解时'},
 {'id':'time-sanyin','name':'欲解时·三阴时段','meridian':'太阴、少阴、厥阴','score':0,'when':['symptomTime=深夜（子至寅）'],'sourceTitle':'欲解时'},
 {'id':'formula-gui-zhi-source','name':'桂枝汤经方资料索引','meridian':'太阳','score':0,'when':['汗=有汗自汗'],'sourceTitle':'治感冒六大经方'},
 {'id':'formula-ma-huang-source','name':'麻黄汤经方资料索引','meridian':'太阳','score':0,'when':['汗=无汗'],'sourceTitle':'治感冒六大经方'},
 {'id':'formula-ge-gen-source','name':'葛根汤经方资料索引','meridian':'太阳','score':0,'when':['头身=头痛项强'],'sourceTitle':'治感冒六大经方'},
 {'id':'formula-da-qing-long-source','name':'大青龙汤经方资料索引','meridian':'太阳','score':0,'when':['汗=无汗','口渴=渴喜冷饮'],'sourceTitle':'治感冒六大经方'},
 {'id':'formula-xiao-qing-long-source','name':'小青龙汤经方资料索引','meridian':'太阳','score':0,'when':['呼吸=喘','汗=无汗'],'sourceTitle':'治感冒六大经方'},
 {'id':'formula-xiao-chai-hu-source','name':'小柴胡汤经方资料索引','meridian':'少阳','score':0,'when':['寒热=往来寒热'],'sourceTitle':'治感冒六大经方'},
]

# 绑定最接近的原始条目，保留所有条目作为可检索的知识索引。
for rule in rules:
    candidates = [x for x in items if rule['sourceTitle'] in x['title']]
    rule['sourceIds'] = [x['id'] for x in candidates]
    rule['sourceId'] = candidates[0]['id'] if candidates else None
rule_source_ids = {sid for rule in rules for sid in rule.get('sourceIds', []) if sid}
context_items = [item for item in items if item.get('id') not in rule_source_ids]
out = {'version':'2026.08.26', 'source':'static/data/diagnosis.json', 'rules':rules, 'knowledgeItems':items, 'contextItems':context_items}
(ROOT / 'static/data/sizhen-rules.json').write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding='utf-8')
print('compiled rules:', len(rules), 'knowledge items:', len(items))
