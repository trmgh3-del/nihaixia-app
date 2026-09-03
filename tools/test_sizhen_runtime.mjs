import fs from 'node:fs'
import { evaluateCompiledRules } from '../utils/sizhen-engine.js'

const compiled = JSON.parse(fs.readFileSync(new URL('../static/data/sizhen-rules.json', import.meta.url), 'utf8'))
const assert = (ok, msg) => { if (!ok) throw new Error(msg) }
const top = pick => {
  const r = evaluateCompiledRules(compiled, pick)
  return Object.entries(r.scores).sort((a, b) => b[1] - a[1])[0][0]
}
assert(top({ '寒热': ['恶寒', '发热'], '汗': ['无汗'], '脉位': '浮', '脉形': '紧' }) === '太阳', 'multi-select solar runtime failed')
assert(top({ '寒热': ['往来寒热'], '脉形': '弦', '大便': ['便秘'] }) === '少阳', 'shaoyang runtime failed')
assert(top({ 'miscDisease': '胸痹', '疼痛': ['胸痛彻背'] }) === '少阴', 'Jingui chest-bi runtime failed')
assert(top({ '厥热胜复': '热多厥少（病退）' }) === '厥阴', 'jueyin dynamic runtime failed')
console.log(`PASS: compiled runtime cases 4, rules ${compiled.rules.length}`)
