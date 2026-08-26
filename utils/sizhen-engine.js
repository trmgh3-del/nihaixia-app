/* 知识库驱动的四诊规则层
 * 规则名称与 static/data/diagnosis.json 中的六经公式、脉舌速查、七步走相对应。
 * 本模块只生成学习用证据，不输出医疗诊断或处方。
 */
import { loadData } from './data.js'

const MERIDIANS = ['太阳', '阳明', '少阳', '太阴', '少阴', '厥阴']
const RULES = [
  ['太阳', 3, ['脉位=浮', '寒热=恶寒']], ['太阳', 3, ['汗=无汗', '脉形=紧']], ['太阳', 3, ['汗=有汗自汗', '寒热=恶风']],
  ['阳明', 3, ['寒热=但热不寒', '口渴=渴喜冷饮']], ['阳明', 3, ['大便=便秘', '脉形=洪']],
  ['少阳', 3, ['寒热=往来寒热', '脉形=弦']], ['少阳', 3, ['胸腹=胸胁苦满', '口渴=口苦咽干']],
  ['太阴', 3, ['大便=溏泄', '胃口=差/食少']], ['太阴', 3, ['头身=身重困倦', '舌苔=白腻']],
  ['少阴', 3, ['睡眠=但欲寐', '脉形=细']], ['少阴', 3, ['手足温度=手脚冰凉', '脉力=微']],
  ['厥阴', 3, ['口渴=消渴多饮', '手足温度=手心热脚凉']],
  ['太阳少阳合病', 2, ['寒热=恶寒', '脉形=弦']], ['少阳阳明合病', 2, ['寒热=往来寒热', '大便=便秘']],
  ['少阳太阴合病', 2, ['寒热=往来寒热', '大便=溏泄']], ['太阳少阴两感', 2, ['寒热=恶寒', '脉位=沉']],
  ['太阴少阴并病', 2, ['大便=溏泄', '脉形=细', '手足温度=手脚冰凉']]
]
const KB_QUERIES = [
  { title: '快速诊断流程图', keys: ['恶寒', '脉浮', '脉沉', '往来寒热', '但热不寒'] },
  { title: '脉诊速查', keys: ['浮缓', '浮紧', '沉迟', '沉微', '弦数', '弦缓', '微细欲绝', '结代'] },
  { title: '舌诊速查', keys: ['舌淡胖大齿痕', '舌红绛', '舌青紫', '舌红苔白', '舌淡苔白'] },
  { title: '脉舌矛盾', keys: ['脉数但舌淡', '脉沉但舌红', '脉浮但舌苔厚腻'] },
  { title: '七步走', keys: ['定表里', '分阴阳', '辨寒热', '判传变', '审体质', '选方剂'] },
  { title: '用药铁律', keys: ['有汗用麻黄', '无汗用桂枝', '少阳用汗法', '少阴用汗法'] }
]

function values(pick) { return Object.keys(pick || {}).filter(k => pick[k]).map(k => k + '=' + pick[k]) }
function matchRule(rule, vals) { return rule[2].every(x => vals.includes(x)) }

function runRules(pick, basic, rules) {
  const vals = values(pick)
  const scores = {}; const evidence = []
  MERIDIANS.forEach(m => { scores[m] = 0 })
  rules.forEach(rule => {
    const name = Array.isArray(rule) ? rule[0] : rule.name
    const points = Array.isArray(rule) ? rule[1] : rule.score
    const needs = Array.isArray(rule) ? rule[2] : rule.when
    if (!needs.every(x => vals.includes(x))) return
    const mers = MERIDIANS.filter(m => name.includes(m))
    mers.forEach(m => { scores[m] += points })
    evidence.push({ name, points, needs, source: Array.isArray(rule) ? '六经辨证诊断公式·临床速查' : (rule.sourceTitle || '六经辨证诊断公式·临床速查'), sourceId: rule.sourceId || '' })
  })
  if (basic.caseType === '慢性内伤') evidence.push({ name: '外感规则不宜直接套用', points: 0, needs: [], source: '六经辨证公式·适用边界' })
  if (basic.duration === '超过2周' || basic.duration === '反复发作') evidence.push({ name: '病程较长，建议结合内伤/杂病资料复核', points: 0, needs: [], source: '七步走辨证思维模式' })
  return { scores, evidence: evidence.slice(0, 24) }
}

export function evaluateKnowledge(pick, basic = {}) { return runRules(pick, basic, RULES) }

export async function evaluateKnowledgeAsync(pick, basic = {}) {
  try {
    const compiled = await loadData('sizhen-rules')
    return { ...runRules(pick, basic, compiled.rules || []), modelVersion: compiled.version || 'unknown' }
  } catch (e) {
    return { ...runRules(pick, basic, RULES), modelVersion: 'fallback-local' }
  }
}

export async function findKnowledgeSources(pick) {
  try {
    const data = await loadData('diagnosis')
    const items = (data.groups || []).flatMap(g => g.items || [])
    const text = values(pick).join(' ')
    const found = []
    for (const query of KB_QUERIES) {
      const hit = items.find(it => it.t.includes(query.title) && query.keys.some(k => text.includes(k) || String(it.b || '').includes(k)))
      if (hit) found.push({ id: hit.id, title: hit.t, source: query.title })
    }
    return found.slice(0, 6)
  } catch (e) { return [] }
}

export { MERIDIANS }
