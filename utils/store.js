import { reactive, watch } from 'vue'

/* ================= 全局状态（设置/收藏/历史/AI配置） ================= */

const DEF_AI = {
  baseUrl: 'https://api.deepseek.com',
  apiKey: '',
  model: 'deepseek-chat',
  mode: 'lite', // lite 精简内核 | full 完整SKILL | rag 内核+检索增强
  stream: true,
  temperature: 0.7
}

function load(key, def) {
  try {
    const v = uni.getStorageSync(key)
    return v === '' || v === undefined || v === null ? def : v
  } catch (e) {
    return def
  }
}

export const store = reactive({
  ready: false,
  theme: 'light', // light | dark
  fontScale: 1, // 0.9 / 1 / 1.15 / 1.3
  fontFam: 'sans', // sans 黑体 | serif 宋体
  readList: null, // {items:[...], idx} 阅读上下文（上一篇/下一篇）
  pendingDiag: '', // 跨页跳转待定位的六经名
  favorites: [], // {f,i,t,s,ts}
  history: [], // {f,i,t,ts}
  ai: { ...DEF_AI },
  chats: [], // [{role,content,ts}]
  readerItem: null, // 阅读页数据交接
  readerReturn: null, // 兼容旧版单层返回上下文
  readerStack: [], // 方剂↔本草↔文章多级返回栈
  sizhenReport: null, // 四诊历史报告详情交接
  meta: null
})

export function initSettings() {
  store.theme = load('nx_theme', 'light')
  store.fontScale = load('nx_font', 1)
  store.fontFam = load('nx_fontfam', 'sans')
  store.favorites = load('nx_fav', [])
  store.history = load('nx_hist', [])
  store.ai = Object.assign({}, DEF_AI, load('nx_ai', {}))
  store.chats = load('nx_chats', [])
  store.ready = true
  applyTheme()
}

export function applyTheme() {
  try {
    const dark = store.theme === 'dark'
    const noop = () => {}
    const safe = task => { try { if (task && task.catch) task.catch(noop) } catch (e) { /* noop */ } }
    safe(uni.setTabBarStyle({
      color: dark ? '#8B8272' : '#8A8172',
      selectedColor: dark ? '#D06A4E' : '#9A2E1F',
      backgroundColor: dark ? '#1B1815' : '#FDFBF5',
      borderStyle: 'black',
      success: noop,
      fail: noop
    }))
    safe(uni.setNavigationBarColor({
      frontColor: dark ? '#ffffff' : '#000000',
      backgroundColor: dark ? '#1B1815' : '#F6F1E7',
      success: noop,
      fail: noop
    }))
  } catch (e) { /* 页面级调用时 tabbar 可能不存在 */ }
}

export function setTheme(t) {
  store.theme = t
  uni.setStorageSync('nx_theme', t)
  applyTheme()
}

export function setFontScale(v) {
  store.fontScale = v
  uni.setStorageSync('nx_font', v)
}

export function setFontFam(v) {
  store.fontFam = v
  uni.setStorageSync('nx_fontfam', v)
}

function persist() {
  if (!store.ready) return
  uni.setStorageSync('nx_fav', store.favorites)
  uni.setStorageSync('nx_hist', store.history.slice(0, 80))
  uni.setStorageSync('nx_ai', store.ai)
  uni.setStorageSync('nx_chats', store.chats.slice(-60))
}
let timer = null
function persistSoon() {
  clearTimeout(timer)
  timer = setTimeout(persist, 400)
}

export function isFav(f, i) {
  return store.favorites.some(x => x.f === f && x.i === i)
}

export function toggleFav(item) {
  const k = store.favorites.findIndex(x => x.f === item.f && x.i === item.i)
  if (k >= 0) store.favorites.splice(k, 1)
  else store.favorites.unshift({ f: item.f, i: item.i, t: item.t, s: (item.s || '').slice(0, 100), c: item.c || '', ts: Date.now() })
  persistSoon()
  return k < 0
}

export function pushHistory(item) {
  if (!item || !item.f) return
  const k = store.history.findIndex(x => x.f === item.f && x.i === item.i)
  if (k >= 0) store.history.splice(k, 1)
  store.history.unshift({ f: item.f, i: item.i, t: item.t, c: item.c || '', ts: Date.now() })
  store.history = store.history.slice(0, 80)
  persistSoon()
}

export function saveAI(cfg) {
  store.ai = Object.assign({}, store.ai, cfg)
  persistSoon()
}

export function setChats(chats) {
  store.chats = chats || []
  persistSoon()
}
