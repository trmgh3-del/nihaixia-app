/* 知识库驱动四诊引擎：页面只负责采集/展示，辨证、方证、安全和证据均在此完成。 */
import { loadData } from './data.js'

export const MERIDIANS = ['太阳', '阳明', '少阳', '太阴', '少阴', '厥阴']
const STEP_FIELDS = [
  ['望色', '舌质', '舌苔', '望神'], ['声音', '呼吸'],
  ['汗', '头身', '大便', '小便', '口渴', '睡眠', '手足温度', '胃口', '疼痛', '胸腹', '耳', '妇女', '寒热', '厥热胜复'],
  ['脉位', '脉率', '脉形', '脉力', '复合脉']
]
const FALLBACK_RULES = [
  ['太阳', 3, ['脉位=浮', '寒热=恶寒']], ['太阳', 3, ['汗=无汗', '脉形=紧']], ['太阳', 3, ['汗=有汗自汗', '寒热=恶风']],
  ['阳明', 3, ['寒热=但热不寒', '口渴=渴喜冷饮']], ['阳明', 3, ['大便=便秘', '脉形=洪']],
  ['少阳', 3, ['寒热=往来寒热', '脉形=弦']], ['太阴', 3, ['大便=溏泄', '胃口=差/食少']],
  ['少阴', 3, ['睡眠=但欲寐', '脉形=细']], ['少阴', 3, ['手足温度=手脚冰凉', '脉力=微']],
  ['厥阴', 3, ['口渴=消渴多饮', '手足温度=手心热脚凉']]
]
function values(pick, basic = {}) {
  const a = Object.keys(pick || {}).filter(k => pick[k]).flatMap(k => Array.isArray(pick[k]) ? pick[k].map(v => k + '=' + v) : [k + '=' + pick[k]])
  return a.concat(Object.keys(basic).filter(k => basic[k]).map(k => k + '=' + basic[k]))
}
function has(pick, k, v) { return Array.isArray(pick[k]) ? pick[k].includes(v) : pick[k] === v }
function runRules(pick, basic, rules) {
  const vals = values(pick, basic); const scores = {}; const evidence = []
  MERIDIANS.forEach(m => { scores[m] = 0 })
  for (const rule of rules) {
    const name = Array.isArray(rule) ? rule[0] : rule.name; const score = Array.isArray(rule) ? rule[1] : rule.score; const when = Array.isArray(rule) ? rule[2] : (rule.required || rule.when); const reference = Array.isArray(rule) ? [] : (rule.reference || []); const exclude = Array.isArray(rule) ? [] : (rule.exclude || [])
    if (!when.every(x => vals.includes(x)) || exclude.some(x => vals.includes(x))) continue
    const refHits = reference.filter(x => vals.includes(x)).length
    const effectiveScore = score + refHits

    const meridianText = Array.isArray(rule) ? name : (rule.meridian || name)
    MERIDIANS.filter(m => meridianText.includes(m)).forEach(m => { scores[m] += effectiveScore })
    evidence.push({ name, points: effectiveScore, required: when, referenceHits: refHits, source: Array.isArray(rule) ? '本地兜底规则' : (rule.sourceTitle || '六经辨证诊断公式'), sourceId: rule.sourceId || '' })
  }
  const matchedRules = evidence.filter(e => e.points > 0).length
  return { scores, evidence, matchedRules }
}
export function evaluateCompiledRules(compiled, pick, basic = {}) {
  const r = runRules(pick, basic, (compiled && compiled.rules) || [])
  return { ...r, modelVersion: (compiled && compiled.version) || 'unknown', ruleCount: ((compiled && compiled.rules) || []).length }
}

export async function evaluateKnowledgeAsync(pick, basic = {}) {
  try {
    const compiled = await loadData('sizhen-rules'); const r = evaluateCompiledRules(compiled, pick, basic)
    return { ...r, modelVersion: compiled.version || 'unknown', ruleCount: (compiled.rules || []).length }
  } catch (e) { return { ...runRules(pick, basic, FALLBACK_RULES), modelVersion: 'fallback-local', ruleCount: FALLBACK_RULES.length } }
}
export function filterFormulaSafety(names = [], pick = {}, basic = {}, redFlags = []) {
  const blocked = []; const warnings = []; const hasValue = (k, v) => has(pick, k, v)
  const block = (name, reason) => blocked.push({ name, reason })
  names.forEach(name => {
    if (hasValue('汗', '有汗自汗') && /麻黄|大青龙|小青龙/.test(name)) block(name, '有汗时不可直接使用发汗峻剂')
    if (hasValue('汗', '无汗') && /桂枝汤/.test(name)) block(name, '无汗时不可直接套用桂枝汤方向')
    if (hasValue('寒热', '往来寒热') && /麻黄|桂枝|承气/.test(name)) block(name, '少阳阶段需先复核汗、吐、下三禁')
    if (basic.pregnant && /麻黄|附子|细辛|承气|乌梅|四逆汤|真武汤/.test(name)) block(name, '孕期/备孕需医师确认')
    if (basic.caseType === '慢性内伤' && /麻黄|大青龙|小青龙|葛根|小柴胡/.test(name)) block(name, '慢性内伤不直接套用急性外感方')
    if (basic.caseType === '心肺症状') block(name, '心肺症状需先完成现代医学急症排查')
    if (basic.age && (Number(basic.age) < 12 || Number(basic.age) >= 65)) block(name, '儿童或高龄需医师确认剂量与适应证')
  })
  if (basic.chronic) warnings.push('存在慢性病或正在用药，方剂方向必须由医师复核')
  if (basic.caseType === '慢性内伤') warnings.push('当前为慢性内伤模式，建议结合金匮杂病和内伤资料复核')
  if (basic.caseType === '心肺症状') warnings.push('心肺症状已停止方剂推荐，请先完成现代医学急症排查')
  if (redFlags.length) { names.forEach(name => block(name, '存在红旗症状，已停止所有方剂推荐')); warnings.push('存在红旗症状，已停止所有方剂推荐') }
  const unique = blocked.filter((x, i, a) => a.findIndex(y => y.name === x.name) === i)
  return { formulas: names.filter(name => !unique.some(x => x.name === name)), blocked: unique, warnings }
}
export async function findFormulaDetails(names = []) {
  try { const data = await loadData('formulas'); return names.map(name => { const clean = String(name).replace(/（.*?）/g, '').replace(/类.*/, ''); const item = (data.items || []).find(x => x.n === clean || x.n.includes(clean)); return item ? { name, id: item.id, composition: item.composition || item.组成 || item.origin || '', clinical: item.clinical || item.主治 || '', caution: item.禁忌 || (String(item.note || '').match(/禁忌[^。；]*/u) || [''])[0] } : { name } }) } catch (e) { return names.map(name => ({ name })) }
}
export async function findKnowledgeSources(pick) {
  try { const d = await loadData('sizhen-rules'); const terms = values(pick).map(x => x.split('=').slice(1)[0]).filter(x => x.length > 1); return (d.knowledgeItems || []).map(i => ({ i, hits: terms.filter(t => (i.title + ' ' + i.excerpt).includes(t)) })).filter(x => x.hits.length).sort((a, b) => b.hits.length - a.hits.length).slice(0, 8).map(x => ({ id: x.i.id, title: x.i.title, source: x.i.group, hits: x.hits })) } catch (e) { return [] }
}
export async function findSimilarCases(pick, meridians = []) {
  try { const d = await loadData('cases_table'); const terms = values(pick).map(x => x.split('=').slice(1)[0]).filter(x => x.length > 1); return (d.rows || []).map(row => { const hay = [row.diag, row.bingji, row.fangji, row.result, row.guandian].join(' '); const hits = terms.filter(t => hay.includes(t)).concat(meridians.filter(m => hay.includes(m))); return { row, hits, score: hits.length } }).filter(x => x.score).sort((a, b) => b.score - a.score).slice(0, 3).map(x => ({ id: 'c' + x.row.n, date: x.row.date || '日期未载', title: x.row.diag || '未标注诊断', excerpt: String(x.row.bingji || x.row.result || '').replace(/[#*`]/g, '').slice(0, 160), formula: String(x.row.fangji || '').replace(/[#*`]/g, '').slice(0, 120), hits: x.hits })) } catch (e) { return [] }
}
export async function findRelatedAcupoints(meridians = []) {
  try {
    const data = await loadData('zhenjiu')
    const points = data.points || []
    return points.filter(point => meridians.some(m => String(point.t || '').includes(m))).slice(0, 8).map(point => ({ id: point.id, title: point.t, excerpt: String(point.b || '').replace(/[#*`]/g, '').slice(0, 120) }))
  } catch (e) { return [] }
}

export async function analyzeSizhen(pick, basic = {}, redFlags = [], pulseSource = '不确定') {
  const effectiveFlags = [...redFlags]
  if (has(pick, '疼痛', '胸痛彻背') && !effectiveFlags.includes('胸痛/胸闷')) effectiveFlags.push('胸痛/胸闷')
  if (has(pick, '妇女', '孕期出血或腹痛') && !effectiveFlags.includes('孕期出血/腹痛')) effectiveFlags.push('孕期出血/腹痛')
  const kb = await evaluateKnowledgeAsync(pick, basic); const scores = MERIDIANS.map(name => ({ name, score: kb.scores[name] || 0, reason: kb.evidence.filter(e => e.name.includes(name)).map(e => e.name).slice(0, 3).join('、') })).filter(x => x.score > 0).sort((a, b) => b.score - a.score).map((x, i) => ({ ...x, role: i === 0 ? '主证' : i === 1 ? '兼证' : '待排' }))
  const bg = new Set(); const patterns = []; const formulas = []
  if (has(pick, '汗', '无汗')) formulas.push('麻黄汤'); if (has(pick, '汗', '有汗自汗')) formulas.push('桂枝汤'); if (has(pick, '寒热', '往来寒热')) formulas.push('小柴胡汤'); if (has(pick, '大便', '便秘')) formulas.push('承气汤类'); if (has(pick, '口渴', '渴喜冷饮')) formulas.push('白虎汤'); if (has(pick, '手足温度', '手脚冰凉')) formulas.push('四逆汤'); if (has(pick, '手足温度', '手心热脚凉')) formulas.push('乌梅丸')
  if (has(pick, '脉位', '浮') || has(pick, '寒热', '恶寒')) bg.add('表'); if (has(pick, '脉位', '沉') || has(pick, '大便', '便秘')) bg.add('里'); if (has(pick, '脉率', '迟') || has(pick, '小便', '清长')) bg.add('寒'); if (has(pick, '脉率', '数') || has(pick, '口渴', '渴喜冷饮')) bg.add('热'); if (has(pick, '脉力', '无力') || has(pick, '睡眠', '但欲寐')) bg.add('虚'); if (has(pick, '脉力', '有力') || has(pick, '大便', '便秘')) bg.add('实')
  const conflicts = []; if (has(pick, '寒热', '恶寒') && has(pick, '寒热', '但热不寒')) conflicts.push('恶寒与但热不寒并见，寒热错杂需复核'); if (has(pick, '口渴', '渴喜冷饮') && has(pick, '舌苔', '白腻')) conflicts.push('渴喜冷饮但苔白腻，需鉴别真寒假热'); if (has(pick, '脉位', '沉') && (has(pick, '舌质', '红') || has(pick, '舌苔', '黄'))) conflicts.push('脉沉但舌红/苔黄，需鉴别真热假寒')
  patterns.push(...conflicts.map(x => '输入复核：' + x)); if (basic.caseType === '慢性内伤') patterns.push('慢性内伤不宜直接套用急性外感流程'); if (basic.miscDisease && basic.miscDisease !== '不适用/未说明') patterns.push('金匮杂病归属：' + basic.miscDisease)
  const riskReasons = [...conflicts]; if (effectiveFlags.length) riskReasons.push('红旗症状：' + effectiveFlags.join('、')); if (basic.pregnant) riskReasons.push('孕期/备孕'); if (basic.chronic) riskReasons.push('慢性病或正在用药'); if (basic.age && (Number(basic.age) < 12 || Number(basic.age) >= 65)) riskReasons.push('儿童或高龄'); if (pulseSource !== '医师诊察' && STEP_FIELDS[3].some(k => pick[k])) riskReasons.push('切诊来源非医师诊察')
  const safety = filterFormulaSafety([...new Set(formulas)], pick, basic, effectiveFlags); patterns.push(...safety.warnings, ...safety.blocked.map(x => '方剂安全过滤：' + x.name + '（' + x.reason + '）'))
  const hasHigh = effectiveFlags.length || ['神志异常', '存在脱液或亡阳风险'].some(x => riskReasons.includes(x)); const risk = { level: hasHigh ? 'high' : riskReasons.length || safety.blocked.length ? 'medium' : 'low', label: hasHigh ? '高风险' : riskReasons.length || safety.blocked.length ? '需复核' : '一般', reasons: [...new Set(riskReasons.concat(safety.warnings))] }
  const selected = values(pick).concat(Object.keys(basic).filter(k => basic[k]).map(k => k + '：' + basic[k])).map(x => x.replace('=', '：')); const completedSteps = STEP_FIELDS.filter(fs => fs.some(k => pick[k])).length
  const topMeridians = scores.slice(0, 3).map(x => x.name)
  const [sourceList, cases, formulaDetails, acupoints] = await Promise.all([findKnowledgeSources(pick), findSimilarCases(pick, topMeridians), findFormulaDetails(safety.formulas), findRelatedAcupoints(topMeridians)])
  return { bagang: [...bg], meridians: scores.map(x => x.name), formulas: safety.formulas, formulaDetails, scores, selected, completeness: Math.round(completedSteps / STEP_FIELDS.length * 100), risk, sevenSteps: [{ k: '定表里', v: bg.has('表') && bg.has('里') ? '表里同病' : bg.has('表') ? '偏表' : bg.has('里') ? '偏里' : '证据不足' }, { k: '分阴阳', v: bg.has('寒') && bg.has('热') ? '寒热错杂' : bg.has('寒') ? '偏阴' : bg.has('热') ? '偏阳' : '证据不足' }, { k: '辨寒热', v: bg.has('寒') && bg.has('热') ? '寒热并见，需鉴别真伪' : bg.has('寒') ? '偏寒' : bg.has('热') ? '偏热' : '证据不足' }, { k: '判虚实', v: bg.has('虚') && bg.has('实') ? '虚实夹杂' : bg.has('虚') ? '偏虚' : bg.has('实') ? '偏实' : '证据不足' }, { k: '定六经', v: scores[0] ? scores[0].name : '暂不明确' }, { k: '合病传变', v: scores.length > 1 ? '需复核：' + scores.slice(0, 3).map(x => x.name).join('、') : '暂未发现明确依据' }, { k: '方证复核', v: risk.level === 'high' ? '高风险，停止方剂推荐' : '需结合禁忌和医师面诊' }], combination: conflicts.join('；'), sources: sourceList, kbEvidence: kb.evidence, kbVersion: kb.modelVersion, kbCoverage: kb.ruleCount ? Math.round((kb.matchedRules || 0) / kb.ruleCount * 100) : 0, kbMatches: sourceList.length, cases, acupoints }
}
