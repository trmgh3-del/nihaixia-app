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
  const vals = values(pick).concat(Object.keys(basic || {}).filter(k => basic[k]).map(k => k + '=' + basic[k]))
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
  const matched = evidence.filter(e => e.points > 0).length
  const ranked = Object.values(scores).sort((a, b) => b - a)
  const confidence = matched === 0 ? '不足' : ranked[0] >= 7 && ranked[0] - (ranked[1] || 0) >= 2 ? '较高' : matched >= 2 ? '一般' : '较低'
  return { scores, evidence: evidence.slice(0, 24), matchedRules: matched, ruleCount: rules.length, coverage: rules.length ? Math.round(matched / rules.length * 100) : 0, confidence }
}

export function evaluateKnowledge(pick, basic = {}) { return runRules(pick, basic, RULES) }

export async function evaluateKnowledgeAsync(pick, basic = {}) {
  try {
    const compiled = await loadData('sizhen-rules')
    const result = runRules(pick, basic, compiled.rules || [])
    const terms = values(pick).map(x => x.split('=').slice(1)[0]).filter(x => x.length > 1)
    const allKnowledgeMatches = (compiled.knowledgeItems || []).map(item => {
      const hay = item.title + ' ' + item.excerpt
      const hits = terms.filter(t => hay.includes(t))
      return { id: item.id, title: item.title, group: item.group, hits, score: hits.length }
    }).filter(x => x.score > 0).sort((a, b) => b.score - a.score)
    return { ...result, knowledgeMatches: allKnowledgeMatches.slice(0, 12), knowledgeMatchCount: allKnowledgeMatches.length, modelVersion: compiled.version || 'unknown' }
  } catch (e) {
    return { ...runRules(pick, basic, RULES), knowledgeMatches: [], knowledgeMatchCount: 0, modelVersion: 'fallback-local' }
  }
}

export async function findKnowledgeSources(pick) {
  try {
    const compiled = await loadData('sizhen-rules')
    const items = compiled.knowledgeItems || []
    const terms = Object.keys(pick || {}).filter(k => pick[k]).map(k => String(pick[k])).filter(x => x.length > 1)
    const scored = items.map(it => {
      const hay = it.title + ' ' + it.excerpt
      const hits = terms.filter(t => hay.includes(t))
      return { it, hits, score: hits.length * 2 + (hay.includes('诊断公式') ? 1 : 0) }
    }).filter(x => x.score > 0).sort((a, b) => b.score - a.score)
    return scored.slice(0, 8).map(({ it, hits }) => ({ id: it.id, title: it.title, source: it.group, hits }))
  } catch (e) {
    try {
      const data = await loadData('diagnosis')
      const items = (data.groups || []).flatMap(g => g.items || [])
      const text = values(pick).join(' ')
      return items.filter(it => text.includes(it.t) || String(it.b || '').split('').some(c => text.includes(c))).slice(0, 3).map(it => ({ id: it.id, title: it.t, source: '辨证知识库', hits: [] }))
    } catch (err) { return [] }
  }
}

export function filterFormulaSafety(names = [], pick = {}, basic = {}, redFlags = []) {
  const blocked = []; const warnings = []
  const block = (name, reason) => { blocked.push({ name, reason }) }
  names.forEach(name => {
    if (pick['汗'] === '有汗自汗' && /麻黄|大青龙|小青龙/.test(name)) block(name, '有汗时不可直接使用发汗峻剂')
    if (pick['汗'] === '无汗' && /桂枝汤/.test(name)) block(name, '无汗时不可直接套用桂枝汤方向')
    if (pick['寒热'] === '往来寒热' && /麻黄|桂枝|承气/.test(name)) block(name, '少阳阶段需先复核三禁，不直接汗、下')
    if (basic.pregnant && /麻黄|附子|细辛|承气|乌梅|四逆汤|真武汤/.test(name)) block(name, '孕期/备孕需医师确认')
    if (basic.caseType === '慢性内伤' && /麻黄|大青龙|小青龙|葛根|小柴胡/.test(name)) block(name, '慢性内伤不直接套用急性外感方')
    if (basic.caseType === '心肺症状') block(name, '心肺症状需先完成现代医学急症排查')
    if (basic.age && (Number(basic.age) < 12 || Number(basic.age) >= 65)) block(name, '儿童或高龄需医师确认剂量与适应证')
  })
  if (basic.chronic)
     warnings.push('存在慢性病或正在用药，方剂方向必须由医师复核')
  if (basic.caseType === '慢性内伤') warnings.push('当前为慢性内伤模式，建议结合金匮杂病和内伤资料复核')
  if (basic.caseType === '心肺症状') warnings.push('心肺症状已停止方剂推荐，请先完成现代医学急症排查')
  if (redFlags.length) {
    names.forEach(name => block(name, '存在红旗症状，已停止所有方剂推荐'))
    warnings.push('存在红旗症状，已停止所有方剂推荐')
  }
  const blockedNames = blocked.map(x => x.name)
  return { formulas: names.filter(name => !blockedNames.includes(name)), blocked, warnings }
}

export async function findFormulaDetails(names = []) {
  try {
    const data = await loadData('formulas')
    return names.map(name => {
      const clean = String(name).replace(/（.*?）/g, '').replace(/类.*/, '')
      const item = (data.items || []).find(x => x.n === clean || x.n.includes(clean))
      return item ? { name, id: item.id, composition: item.composition || item.组成 || item.origin || '', clinical: item.clinical || item.主治 || '', caution: item.禁忌 || (String(item.note || '').match(/禁忌[^。；]*/u) || [''])[0] } : { name }
    })
  } catch (e) { return names.map(name => ({ name })) }
}

export async function findSimilarCases(pick, meridians = []) {
  try {
    const data = await loadData('cases_table')
    const terms = Object.keys(pick || {}).filter(k => pick[k]).map(k => String(pick[k])).filter(x => x.length > 1)
    const mers = meridians || []
    const ranked = (data.rows || []).map(row => {
      const hay = [row.diag, row.bingji, row.fangji, row.result, row.guandian].join(' ')
      const hits = terms.filter(t => hay.includes(t))
      const merHits = mers.filter(m => hay.includes(m))
      return { row, score: hits.length * 2 + merHits.length, hits: hits.concat(merHits) }
    }).filter(x => x.score > 0).sort((a, b) => b.score - a.score)
    return ranked.slice(0, 3).map(({ row, hits }) => ({
      id: 'c' + row.n, date: row.date || '日期未载', title: row.diag || '未标注诊断',
      excerpt: String(row.bingji || row.result || '').replace(/[#*`]/g, '').slice(0, 160), formula: String(row.fangji || '').replace(/[#*`]/g, '').slice(0, 120), hits
    }))
  } catch (e) { return [] }
}

export { MERIDIANS }
