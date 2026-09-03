import { NAJIA } from '../utils/najia-data.js'
const assert = (ok, msg) => { if (!ok) throw new Error(msg) }
const expected = {
  0: [0, 2, 4, 6, 8, 10], 1: [1, 3, 5, 7, 9, 11], 2: [0, 2, 4, 6, 8, 10], 3: [1, 3, 5, 7, 9, 11],
  4: [0, 2, 4, 6, 8, 10], 5: [1, 3, 5, 7, 9, 11], 6: [0, 2, 4, 6, 8, 10], 7: [1, 3, 5, 7, 9, 11],
  8: [0, 2, 4, 6, 8, 10], 9: [1, 3, 5, 7, 9, 11]
}
for (const [day, hours] of Object.entries(expected)) {
  assert(hours.every(h => NAJIA[day] && NAJIA[day][h]), `missing opening slot day ${day}`)
  assert(Object.keys(NAJIA[day]).every(h => Number(h) >= 0 && Number(h) <= 11), `invalid hour index day ${day}`)
}
assert(NAJIA[0][10].p === '窍阴' && NAJIA[0][0].p === '前谷', '甲日 sequence mismatch')
assert(NAJIA[8][2].p === '至阴' && NAJIA[8][0].p === '关冲', '壬日 sequence mismatch')
console.log('PASS: najia table 10 day stems, 60 opening slots')
