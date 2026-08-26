import { filterFormulaSafety } from '../utils/sizhen-engine.js'

const assert = (condition, message) => { if (!condition) throw new Error(message) }
const all = ['桂枝汤', '麻黄汤', '大青龙汤', '四逆汤']
let r = filterFormulaSafety(all, { 汗: '有汗自汗' }, {}, [])
assert(!r.formulas.includes('麻黄汤') && !r.formulas.includes('大青龙汤'), '有汗应过滤发汗峻剂')
assert(r.formulas.includes('桂枝汤'), '有汗不应误过滤桂枝汤')
r = filterFormulaSafety(all, { 汗: '无汗' }, {}, [])
assert(!r.formulas.includes('桂枝汤'), '无汗应过滤桂枝汤')
r = filterFormulaSafety(all, {}, { pregnant: true }, [])
assert(!r.formulas.includes('麻黄汤') && !r.formulas.includes('四逆汤'), '孕期应过滤高风险方剂')
r = filterFormulaSafety(all, {}, { caseType: '慢性内伤' }, [])
assert(!r.formulas.includes('麻黄汤') && !r.formulas.includes('小柴胡汤'), '慢性内伤应过滤急性外感方')
r = filterFormulaSafety(all, {}, {}, ['胸痛/胸闷'])
assert(r.formulas.length === 0 && r.blocked.length === all.length, '红旗症状应过滤全部方剂')
console.log('PASS: formula safety cases 5')
