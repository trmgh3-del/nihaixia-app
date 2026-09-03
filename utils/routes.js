/* ================= 检索索引 -> 页面导航 ================= */
import { store, pushHistory } from './store.js'
import { loadData } from './data.js'

/* 各数据文件对应详情页打开方式 */
export const FILE_PAGE = {
  shanghan: { page: '/pkgTexts/pages/reader' },
  jingui: { page: '/pkgTexts/pages/reader' },
  neijing: { page: '/pkgTexts/pages/reader' },
  zhenjiu: { page: '/pkgTexts/pages/reader' },
  bencao: { page: '/pkgBencao/pages/herb', herb: true },
  formulas: { page: '/pkgFormula/pages/detail', formula: true },
  casesTable: { page: '/pkgCase/pages/row', row: true },
  casesNarr: { page: '/pkgTexts/pages/reader' },
  yian: { page: '/pkgTexts/pages/reader' },
  skill: { page: '/pkgTexts/pages/reader' },
  diag: { page: '/pkgTexts/pages/reader' },
  articles: { page: '/pkgTexts/pages/reader' },
  tianji: { page: '/pkgTexts/pages/reader' }
}

export const FILE_LABEL = {
  shanghan: '伤寒论', jingui: '金匮要略', neijing: '黄帝内经', zhenjiu: '针灸',
  bencao: '本草', formulas: '方剂', casesTable: '结构化医案', casesNarr: '叙事医案',
  yian: '医案集', skill: 'SKILL内核', diag: '辨证', articles: '文库', tianji: '天纪'
}

/* 在数据文件中按 id 找到完整条目 */
/* 索引逻辑键 -> 实际数据文件名（部分文件名与键不同） */
const FILE_MAP = { casesNarr: 'cases_narr', casesTable: 'cases_table', skill: 'skill_units', diag: 'diagnosis' }
const fileName = f => FILE_MAP[f] || f

export async function resolveItem(entry) {
  let f = entry.f
  const iid = entry.i || ''
  if (!entry.c) {
    // 收藏/历史记录可能缺分类：按 id 前缀推断所属文件
    if (/^hb_/.test(iid)) f = 'bencao'
    else if (/^fm\d|^fa/.test(iid)) f = 'formulas'
    else if (/^c\d+$/.test(iid)) f = 'casesTable'
    else if (/^nc\d|^nc_head/.test(iid)) f = 'casesNarr'
    else if (/^ya/.test(iid)) f = 'yian'
  }
  const data = await loadData(fileName(f))
  const find = arr => (arr || []).find(x => x.id === entry.i)
  switch (f) {
    case 'shanghan': {
      let it = find(data.sun) || find(data.que) || find(data.wujing)
      return it && { ...it, f: f, cat: entry.c || f }
    }
    case 'jingui': return find(data.chapters) && { ...find(data.chapters), f: entry.f, cat: entry.c }
    case 'neijing': return find(data.chapters) && { ...find(data.chapters), f: entry.f, cat: entry.c }
    case 'bencao': {
      if (entry.c === 'herb' || /^hb_/.test(iid)) {
        const it = (data.herbs || []).find(x => x.id === entry.i)
        return it && { ...it, f: entry.f, cat: 'herb' }
      }
      const it = find(data.intro)
      return it && { ...it, f: entry.f, cat: 'bencao' }
    }
    case 'zhenjiu': {
      const it = find(data.tutorial) || find(data.quickref) || find(data.highlights) || find(data.points)
      return it && { ...it, f: f, cat: entry.c || f }
    }
    case 'formulas': {
      const wantFormula = entry.c ? entry.c === 'formula' : /^fm/.test(iid)
      if (wantFormula) {
        const it = (data.items || []).find(x => x.id === entry.i)
        return it && { ...it, f: entry.f, cat: 'formula' }
      }
      const it = find(data.articles)
      return it && { ...it, f: entry.f, cat: 'article' }
    }
    case 'casesTable': {
      const it = (data.rows || []).find(x => 'c' + x.n === entry.i)
      return it && { ...it, f: entry.f, cat: 'case', t: it.diag, s: it.fangji }
    }
    case 'casesNarr': {
      for (const g of data.groups || []) {
        const it = find(g.items)
        if (it) return { ...it, f: entry.f, cat: 'caseN', t: it.t }
      }
      return null
    }
    case 'yian': return find(data.items) && { ...find(data.items), f: entry.f, cat: 'yian' }
    case 'skill': return find(data.units) && { ...find(data.units), f: entry.f, cat: 'skill' }
    case 'diag': {
      for (const g of data.groups || []) {
        const it = find(g.items)
        if (it) return { ...it, f: entry.f, cat: 'diag', g: g.label }
      }
      return null
    }
    case 'articles': return find(data.items) && { ...find(data.items), f: entry.f, cat: 'article' }
    case 'tianji': return find(data.sections) && { ...find(data.sections), f: entry.f, cat: 'tianji' }
  }
  return null
}

/* 打开索引条目/任意条目 */
export async function openEntry(entry, opt = {}) {
  const conf = FILE_PAGE[entry.f]
  if (!conf) return
  let item = entry._full
  if (!item) {
    uni.showLoading({ title: '加载中' })
    try { item = await resolveItem(entry) } catch (e) {
      console.error('打开条目失败', entry, e)
    } finally { uni.hideLoading() }
  }
  if (!item) { uni.showToast({ title: '未找到内容', icon: 'none' }); return }
  item.f = item.f || entry.f
  const cat = item.cat || entry.c
  if (cat === 'herb') {
    store.readerItem = { kind: 'herb', item }
    uni.navigateTo({ url: '/pkgBencao/pages/herb' })
  } else if (cat === 'formula') {
    store.readerItem = { kind: 'formula', item }
    uni.navigateTo({ url: '/pkgFormula/pages/detail' })
  } else if (cat === 'case' && conf.row) {
    store.readerItem = { kind: 'row', item }
    uni.navigateTo({ url: conf.page })
  } else {
    // 所有 md 内容（含方剂文库文章/本草总义等）统一进阅读器
    store.readerItem = { kind: 'md', item }
    pushHistory({ f: item.f, i: item.id, t: item.t || item.n || '文档', c: cat })
    uni.navigateTo({ url: opt.page || '/pkgTexts/pages/reader' })
  }
}

export function openMd(item, title, listCtx) {
  store.readerItem = { kind: 'md', item }
  if (listCtx && listCtx.items) store.readList = listCtx
  pushHistory({ f: item.f || 'misc', i: item.id || 'x', t: title || item.t || '文档' })
  uni.navigateTo({ url: '/pkgTexts/pages/reader' })
}
