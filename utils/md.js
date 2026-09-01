/* ================= 轻量 Markdown -> 结构块 解析器 =================
 * 输出块: {ty:'h1'|'h2'|'h3'|'h4'|'p'|'quote'|'ul'|'ol'|'code'|'table'|'hr', ...}
 * ul/ol: {items:[{lvl,segs}]}  table:{head:[],rows:[[]]}
 * 段内行内格式 -> segs: [{t:'b'|'i'|'c'|'a'|'txt', v}]
 */

/* 方剂名词典（启动后注入；渲染时自动把正文方名变为可点击段）
   用全局对象存储，避免打包器模块实例隔离导致状态不共享 */
const __FANG_KEY = '__NX_FANGS__'
export function setFangNames(arr) {
  const names = (arr || []).filter(n => n && n.length >= 2).sort((a, b) => b.length - a.length)
  try { uni.setStorageSync('nx_fang_cache', names) } catch (e) { /* noop */ }
  const g = typeof globalThis !== 'undefined' ? globalThis : (typeof window !== 'undefined' ? window : uni)
  g[__FANG_KEY] = names
}
export function getFangNames() {
  const g = typeof globalThis !== 'undefined' ? globalThis : (typeof window !== 'undefined' ? window : uni)
  if (g[__FANG_KEY]) return g[__FANG_KEY]
  try { const cached = uni.getStorageSync('nx_fang_cache'); if (cached && cached.length) { g[__FANG_KEY] = cached; return cached } } catch (e) { /* noop */ }
  return []
}

export function inlineSegs(s) {
  const segs = []
  let rest = String(s == null ? '' : s)
  const re = /(\*\*([^*]+)\*\*)|(`([^`]+)`)|(\[([^\]]+)\]\(([^)]+)\))|(~~([^~]+)~~)/
  while (rest) {
    const m = rest.match(re)
    if (!m) { segs.push({ t: 'txt', v: rest }); break }
    if (m.index > 0) segs.push({ t: 'txt', v: rest.slice(0, m.index) })
    if (m[2] !== undefined) segs.push({ t: 'b', v: m[2] })
    else if (m[4] !== undefined) segs.push({ t: 'c', v: m[4] })
    else if (m[6] !== undefined) {
      const url = String(m[7] || '').replace(/，安装$/, '').replace(/[，。；：！？、]+$/, '')
      segs.push({ t: 'a', v: m[6], u: url })
    }
    else if (m[9] !== undefined) segs.push({ t: 'd', v: m[9] })
    rest = rest.slice(m.index + m[0].length)
  }
  if (!segs.length) segs.push({ t: 'txt', v: '' })
  const fangs = getFangNames()
  const linked = fangs.length ? linkify(segs, fangs) : segs
  return linkifyUrls(linked)
}

/* 将裸露的 http/https 地址也变为可点击、可长按复制的链接。 */
function linkifyUrls(segs) {
  const out = []
  const re = /(https?:\/\/[^\s<>)\]》】,，。；：！？、]+)/gi
  segs.forEach(seg => {
    if (seg.t !== 'txt') { out.push(seg); return }
    let rest = seg.v
    let m
    while ((m = re.exec(rest))) {
      if (m.index > 0) out.push({ t: 'txt', v: rest.slice(0, m.index) })
      const url = m[0].replace(/[.,;:!?，。；：！？]+$/, '')
      out.push({ t: 'a', v: url, u: url })
      if (url.length < m[0].length) out.push({ t: 'txt', v: m[0].slice(url.length) })
      rest = rest.slice(m.index + m[0].length)
      re.lastIndex = 0
    }
    if (rest) out.push({ t: 'txt', v: rest })
  })
  return out.length ? out : segs
}

/* 把文本段中的方剂名替换为链接段 */
function linkify(segs, FANG_NAMES) {
  const out = []
  segs.forEach(seg => {
    // 处理纯文本和加粗文本段；医典常用 **桂枝汤** 标注方剂，不能因加粗而失去互链。
    if (!['txt', 'b'].includes(seg.t) || !/[汤丸散丹饮膏]/.test(seg.v)) { out.push(seg); return }
    const sourceType = seg.t
    let rest = seg.v
    const buf = []
    let guard = 0
    while (rest && guard++ < 30) {
      let hit = null
      for (const n of FANG_NAMES) {
        const at = rest.indexOf(n)
        if (at >= 0) { hit = { n, at }; break }
      }
      if (!hit) { buf.push({ t: sourceType, v: rest }); break }
      if (hit.at > 0) buf.push({ t: sourceType, v: rest.slice(0, hit.at) })
      buf.push({ t: 'fang', v: hit.n })
      rest = rest.slice(hit.at + hit.n.length)
    }
    buf.forEach(x => out.push(x))
  })
  return out
}

const stripMd = s => String(s || '')
  .replace(/\*\*([^*]+)\*\*/g, '$1')
  .replace(/`([^`]+)`/g, '$1')

export function parseMd(md) {
  const blocks = []
  if (!md) return blocks
  const lines = String(md).replace(/\r\n/g, '\n').replace(/\r/g, '\n').split('\n')
  let i = 0
  const flushP = buf => {
    if (!buf.length) return
    blocks.push({ ty: 'p', segs: inlineSegs(buf.map(stripLead).join(' ')) })
  }
  const stripLead = s => s
  while (i < lines.length) {
    let line = lines[i]
    const t = line.trim()
    if (!t) { i++; continue }
    // 代码块
    if (t.startsWith('```')) {
      i++
      const buf = []
      while (i < lines.length && !lines[i].trim().startsWith('```')) { buf.push(lines[i]); i++ }
      i++
      blocks.push({ ty: 'code', text: buf.join('\n') })
      continue
    }
    // 标题
    let m = t.match(/^(#{1,4})\s+(.*)$/)
    if (m) {
      blocks.push({ ty: 'h' + m[1].length, segs: inlineSegs(m[2].replace(/\s*#+\s*$/, '')) })
      i++; continue
    }
    // 分隔线
    if (/^(-{3,}|\*{3,}|_{3,})$/.test(t)) { blocks.push({ ty: 'hr' }); i++; continue }
    // 表格
    if (t.startsWith('|') && i + 1 < lines.length && /^\|?[\s:|-]+\|/.test(lines[i + 1].trim())) {
      const cells = l => l.trim().replace(/^\|/, '').replace(/\|$/, '').split('|').map(c => c.trim())
      const head = cells(t)
      i += 2
      const rows = []
      while (i < lines.length && lines[i].trim().startsWith('|')) {
        const cs = cells(lines[i])
        while (cs.length < head.length) cs.push('')
        rows.push(cs.slice(0, head.length))
        i++
      }
      blocks.push({ ty: 'table', head, rows })
      continue
    }
    // 引用块
    if (t.startsWith('>')) {
      const buf = []
      while (i < lines.length && lines[i].trim().startsWith('>')) {
        buf.push(lines[i].trim().replace(/^>\s?/, ''))
        i++
      }
      const inner = buf.join('\n')
      // 引用内不再递归表格/标题，按行渲染（保持原味）
      const tbl = tryInnerTable(inner)
      if (tbl) { blocks.push(tbl); continue }
      blocks.push({ ty: 'quote', lines: buf.filter(x => x.trim() !== '').map(x => inlineSegs(x)) })
      continue
    }
    // 无序列表
    if (/^[-*+]\s+/.test(t)) {
      const items = []
      while (i < lines.length) {
        const lt = lines[i].trim()
        const lm = lt.match(/^([-*+])\s+(.*)$/)
        if (!lm) break
        const indent = lines[i].length - lines[i].trimStart().length
        items.push({ lvl: indent >= 2 ? 1 : 0, segs: inlineSegs(lm[2]) })
        i++
      }
      blocks.push({ ty: 'ul', items })
      continue
    }
    // 有序列表
    if (/^\d+[.、]\s+/.test(t)) {
      const items = []
      while (i < lines.length) {
        const lt = lines[i].trim()
        const lm = lt.match(/^(\d+)[.、]\s+(.*)$/)
        if (!lm) break
        const indent = lines[i].length - lines[i].trimStart().length
        items.push({ lvl: indent >= 2 ? 1 : 0, n: lm[1], segs: inlineSegs(lm[2]) })
        i++
      }
      blocks.push({ ty: 'ol', items })
      continue
    }
    // 段落（合并至空行）
    const buf = []
    while (i < lines.length && lines[i].trim() !== '' &&
      !/^(#{1,4}\s|>|[-*+]\s|\d+[.、]\s|```|\|)/.test(lines[i].trim())) {
      buf.push(lines[i].trim())
      i++
    }
    if (buf.length) {
      const joined = buf.join(' ')
      // 穴位/药物等详情常用“定位：…、主治：…”连续行，拆成学习卡字段，避免整段挤在一起。
      const labelNames = '定位|主治|操作|注意|禁忌|倪师特色|来源|功效|配伍|取穴|针法|灸法|归经|性味|用量|炮制'
      const labels = new RegExp('^(' + labelNames + ')[：:]')
      const labeled = buf.map(line => line.match(labels)).filter(Boolean)
      const fields = splitLabeledFields(joined, labelNames)
      if (fields.length >= 2) {
        fields.forEach(field => blocks.push({ ty: 'kv', k: field.k, segs: inlineSegs(field.v) }))
      } else if (labeled.length >= 2 && labeled.length === buf.length) {
        buf.forEach(line => {
          const m0 = line.match(/^([^：:]{1,12})[：:]\s*(.*)$/)
          if (m0) blocks.push({ ty: 'kv', k: m0[1], segs: inlineSegs(m0[2]) })
        })
      } else {
        // 「**字段**：值」单行 -> kv 块，视觉更佳
        const kv = joined.match(/^\*\*([^*]{1,12})\*\*[：:]\s*(.*)$/)
        if (kv && joined.length < 400) {
          blocks.push({ ty: 'kv', k: kv[1], segs: inlineSegs(kv[2]) })
        } else {
          // 中文长段落：首行缩进两字（古典排版）
          const plain = joined.replace(/\*\*?/g, '')
          const ind = plain.length > 50 && /^[\u4e00-\u9fa5「《（]/.test(plain)
          blocks.push({ ty: 'p', segs: inlineSegs(joined), ind })
        }
      }
    } else {
      i++
    }
  }
  return blocks
}

function splitLabeledFields(text, labelNames) {
  const re = new RegExp('(' + labelNames + ')[：:]', 'g')
  const hits = []
  let m
  while ((m = re.exec(String(text || '')))) hits.push({ k: m[1], at: m.index, start: m.index + m[0].length })
  if (hits.length < 2 || hits[0].at > 8) return []
  return hits.map((h, i) => ({
    k: h.k,
    v: String(text).slice(h.start, i + 1 < hits.length ? hits[i + 1].at : undefined).replace(/[\\s。；;]+$/, '').trim()
  })).filter(x => x.v)
}

function tryInnerTable(inner) {
  const ls = inner.split('\n').filter(x => x.trim())
  if (ls.length >= 3 && ls.every(x => x.trim().startsWith('|'))) {
    const cells = l => l.trim().replace(/^\|/, '').replace(/\|$/, '').split('|').map(c => c.trim())
    const head = cells(ls[0])
    if (/^[\s:|-]+$/.test(ls[1])) {
      const rows = ls.slice(2).map(cells)
      return { ty: 'table', head, rows }
    }
  }
  return null
}

export function plainText(md, max = 120) {
  const s = stripMd(String(md || '')).replace(/[#>`|*\-]+/g, ' ').replace(/\s+/g, ' ').trim()
  return s.slice(0, max)
}
