import { setFangNames, inlineSegs } from '../utils/md.js'
setFangNames(['桂枝汤', '小柴胡汤'])
const parts = inlineSegs('**桂枝汤**，与小柴胡汤')
if (!parts.some(x => x.t === 'fang' && x.v === '桂枝汤')) throw new Error('bold formula is not linked')
if (!parts.some(x => x.t === 'fang' && x.v === '小柴胡汤')) throw new Error('plain formula is not linked')
console.log('PASS: bold and plain formula links')
