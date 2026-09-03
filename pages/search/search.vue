<template>
  <view class="page" :class="theme === 'dark' ? 'tdark' : 'tlight'">
    <view class="sbar">
      <view class="s-box">
        <image class="ico" src="/static/icons/search-gray.png" />
        <input class="s-input" v-model="q" :focus="autofocus" placeholder="方名 / 症状 / 穴位 / 药物 / 病症…" confirm-type="search" @confirm="doSearch" @input="onInput" />
        <text class="s-clr" v-if="q" @tap="clear">✕</text>
      </view>
      <view class="s-go" @tap="doSearch">搜索</view>
    </view>

    <view class="filters" v-if="searched">
      <scroll-view scroll-x class="f-scroll">
        <view class="f-row">
          <view class="f-chip" :class="{ on: fc === '' }" @tap="setFc('')">全部 {{ results.length }}</view>
          <view v-for="c in catChips" :key="c.k" class="f-chip" :class="{ on: fc === c.k }" @tap="setFc(c.k)">{{ c.label }} {{ countOf(c.k) }}</view>
        </view>
      </scroll-view>
      <view class="deep" @tap="deep = !deep">
        <view class="d-dot" :class="{ on: deep }" />
        <text>深度全文</text>
      </view>
    </view>

    <view v-if="!searched" class="hots">
      <view class="h-t" v-if="hist.length">搜索历史 <text class="h-clear" @tap="clearHist">清空</text></view>
      <view class="h-wrap" v-if="hist.length">
        <view v-for="h in hist" :key="h" class="h-chip old" @tap="quick(h)">{{ h }}</view>
      </view>
      <view class="h-t" style="margin-top:34rpx">大家都在搜</view>
      <view class="h-wrap">
        <view v-for="h in hots" :key="h" class="h-chip" @tap="quick(h)">{{ h }}</view>
      </view>
      <view class="h-tip">索引覆盖 {{ indexCount }} 条目{{ deep ? ' · 深度模式将扫描全部正文' : '' }}</view>
    </view>

    <view class="results">
      <view v-for="r in shown" :key="r.f + r.i" class="r-item card" @tap="open(r)">
        <view class="r-head">
          <view class="r-badge" :style="{ background: badgeBg(r.c), color: badgeFg(r.c) }">{{ badge(r.c) }}</view>
          <view class="r-title"><rich-text :nodes="hl(r.t)" /></view>
        </view>
        <view class="r-snippet"><rich-text :nodes="hl(r.s || '…')" /></view>
      </view>
      <view v-if="searched && !shown.length && !loading" class="none">
        <text>未找到「{{ q }}」相关内容</text>
        <text class="none-sub">试试：桂枝汤 / 口苦 / 失眠 / 足三里 / 肺癌 / 上经</text>
      </view>
      <view v-if="loading" class="none"><text>检索中…</text></view>
      <view v-if="deepScanning" class="deep-scan">◎ 深度扫描全部正文 {{ deepFile }}…</view>
    </view>
  </view>
</template>

<script>
import { store , applyTheme } from '@/utils/store.js'
import { loadData } from '@/utils/data.js'
import { openEntry } from '@/utils/routes.js'

const CATS = {
  shanghan: ['伤寒', '#FBEAE3', '#9A2E1F'], jingui: ['金匮', '#FCF3DC', '#8A6414'], neijing: ['内经', '#E8F0E4', '#3F6B37'],
  bencao: ['本草', '#E9F1F2', '#2F5D62'], formulas: ['方剂', '#F5E8E8', '#833B3B'], zhenjiu: ['针灸', '#EDE9F4', '#54427C'],
  casesTable: ['医案', '#FBEEE3', '#95541C'], casesNarr: ['医案', '#FBEEE3', '#95541C'], yian: ['医案', '#FBEEE3', '#95541C'],
  articles: ['文库', '#EAF0EE', '#2F5D62'], article: ['文章', '#EAF0EE', '#2F5D62'], tianji: ['天纪', '#F3EDE4', '#6B5B3E'], skill: ['内核', '#FCF3DC', '#8A6414'],
  diag: ['辨证', '#FBEAE3', '#9A2E1F'], point: ['穴位', '#EDE9F4', '#54427C'], herb: ['本草', '#E9F1F2', '#2F5D62'],
  formula: ['方剂', '#F5E8E8', '#833B3B'], case: ['医案', '#FBEEE3', '#95541C'], caseN: ['医案', '#FBEEE3', '#95541C']
}

export default {
  onShow() { applyTheme() },
  data() {
    return {
      q: '', fc: '', searched: false, loading: false,
      results: [], deep: false, autofocus: true, deepScanning: false, deepFile: '',
      indexCount: 0,
      hist: [],
      hots: ['桂枝汤', '小柴胡汤', '口苦', '失眠', '便秘', '乌梅丸', '肺癌', '足三里', '黄芪', '六经辨证', '真武汤', '中风'],
      _timer: null, _idx: null, _deepDone: {}
    }
  },
  computed: {
    theme() { return store.theme },
    shown() {
      let list = this.fc ? this.results.filter(r => this.fcOf(r) === this.fc) : this.results
      return list.slice(0, 100)
    },
    catChips() {
      const seen = {}
      this.results.forEach(r => { const k = this.fcOf(r); seen[k] = (seen[k] || 0) + 1 })
      return Object.keys(seen).map(k => ({ k, label: (CATS[k] || [k])[0], n: seen[k] })).slice(0, 10)
    }
  },
  mounted() {
    try { this.hist = uni.getStorageSync('nx_shist') || [] } catch (e) { this.hist = [] }
  },
  methods: {
    fcOf(r) { return CATS[r.c] ? r.c : r.f },
    badge(c) { return (CATS[c] || CATS[this.fcOf(c)] || ['?'])[0] },
    badgeBg(c) { return (CATS[c] || [0, '#EEE', '#333'])[1] },
    badgeFg(c) { return (CATS[c] || [0, 0, '#333'])[2] },
    countOf(k) { return this.results.filter(r => this.fcOf(r) === k).length },
    setFc(k) { this.fc = k },
    clear() { this.q = ''; this.searched = false; this.results = [] },
    quick(h) { this.q = h; this.doSearch() },
    onInput() {
      clearTimeout(this._timer)
      this._timer = setTimeout(() => { if (this.q.trim().length >= 2) this.doSearch() }, 600)
    },
    async idx() {
      if (!this._idx) this._idx = await loadData('index')
      this.indexCount = this._idx.length
      return this._idx
    },
    saveHist(q) {
      const h = this.hist.filter(x => x !== q)
      h.unshift(q)
      this.hist = h.slice(0, 12)
      uni.setStorageSync('nx_shist', this.hist)
    },
    clearHist() { this.hist = []; uni.setStorageSync('nx_shist', []) },
    async doSearch() {
      clearTimeout(this._timer)
      const q = this.q.trim()
      if (!q) return
      this.saveHist(q)
      this.searched = true
      this.loading = true
      this.results = []
      try {
        const idx = await this.idx()
        const low = q.toLowerCase()
        const hits = idx.filter(e => (e.t && e.t.toLowerCase().includes(low)) || (e.s && e.s.toLowerCase().includes(low)) || (e.g || []).some(x => x.includes(q)))
        this.results = hits.slice(0, 200)
        this.loading = false
        if (this.deep) this.deepSearch(q)
      } catch (e) {
        this.loading = false
        uni.showToast({ title: '索引加载失败', icon: 'none' })
      }
    },
    async deepSearch(q) {
      // [逻辑键(索引/跳转用), 实际json文件名]
      const files = [
        ['shanghan', 'shanghan'], ['jingui', 'jingui'], ['neijing', 'neijing'], ['bencao', 'bencao'],
        ['zhenjiu', 'zhenjiu'], ['formulas', 'formulas'], ['yian', 'yian'], ['casesNarr', 'cases_narr'],
        ['articles', 'articles'], ['tianji', 'tianji'], ['skill', 'skill_units'],
        ['casesTable', 'cases_table'], ['diagnosis', 'diagnosis']
      ]
      const token = (this._deepToken = (this._deepToken || 0) + 1)
      this.deepScanning = true
      const found = {}
      const LABELS = { shanghan: '伤寒论', jingui: '金匮', neijing: '内经', bencao: '本草', zhenjiu: '针灸', formulas: '方剂', yian: '医案集', casesNarr: '叙事医案', articles: '文库', tianji: '天纪', skill: 'SKILL', casesTable: '1257医案表', diagnosis: '辨证' }
      for (const pair of files) {
        const f = pair[0]
        if (this.q.trim() !== q || token !== this._deepToken) { this.deepScanning = false; return } // 换词/新一轮中断
        this.deepFile = LABELS[f] || f
        try {
          const data = await loadData(pair[1])
          const items = this.flatItems(f, data)
          const add = []
          for (const it of items) {
            const hay = (it._hay2 || it._hay || (it._hay = (it.t || it.n || '') + '\n' + (it.b || it.原文 || it.clinical || it.主治 || '')))
            const at = hay.indexOf(q)
            if (at >= 0) {
              const key = f + '|' + it.id
              if (!found[key]) {
                found[key] = true
                add.push({ f, c: it._c, i: it.id, t: it.t || it.n || '条目', s: hay.slice(Math.max(0, at - 40), at + 90).replace(/\n/g, ' ') })
              }
            }
          }
          if (add.length) {
            this.results = this.results.concat(add).slice(0, 300)
          }
        } catch (e) { /* skip file */ }
      }
      this.deepScanning = false
      this.loading = false
    },
    esc(t) {
      return String(t == null ? '' : t).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
    },
    hl(t) {
      const q = this.q.trim()
      if (!q || !t) return this.esc(t || '')
      const safe = this.esc(t)
      const idx = safe.toLowerCase().indexOf(q.toLowerCase())
      if (idx < 0) return safe
      return safe.slice(0, idx) + '<span style="color:#9A2E1F;font-weight:700;background:rgba(154,46,31,.08);border-radius:4px;padding:0 2px">' + safe.slice(idx, idx + q.length) + '</span>' + safe.slice(idx + q.length)
    },
    flatItems(f, data) {
      let items = []
      if (f === 'shanghan') items = [...(data.sun || []), ...(data.que || []), ...(data.wujing || [])]
      else if (f === 'jingui' || f === 'neijing') items = data.chapters || []
      else if (f === 'bencao') items = (data.herbs || []).map(h => ({ ...h, t: h.n, _c: 'herb', b: [h.原文, h.性味, h.主治, h.倪注, h.口述].join('\n') }))
      else if (f === 'zhenjiu') items = [...(data.tutorial || []), ...(data.quickref || []), ...(data.highlights || []), ...(data.points || [])]
      else if (f === 'formulas') items = (data.items || []).map(x => ({ ...x, t: x.n, _c: 'formula', b: [x.origin, x.clinical, x.note, x.composition, x.doses, x.zhizhi].join('\n') }))
      else if (f === 'yian') items = data.items || []
      else if (f === 'casesNarr') items = (data.groups || []).flatMap(g => g.items || [])
      else if (f === 'articles') items = data.items || []
      else if (f === 'tianji') items = data.sections || []
      else if (f === 'skill') items = data.units || []
      else if (f === 'casesTable') items = (data.rows || []).map(r => ({ id: 'c' + r.n, t: (r.diag || '未记诊断') + '（#' + r.n + '）', _c: 'case', _hay2: [r.patient, r.date, r.diag, r.bingji, r.xiyi, r.fangji, r.zhenjiu, r.zhifa, r.result, r.yizhu, r.guandian].join('\n') }))
      else if (f === 'diagnosis') items = (data.groups || []).flatMap(g => (g.items || []).map(x => ({ ...x, _c: 'diag' })))
      items.forEach(it => { if (!it._c) it._c = f })
      return items
    },
    open(r) {
      openEntry({ f: r.f, c: r.c, i: r.i, t: r.t })
    }
  }
}
</script>

<style scoped>
.page { min-height: 100vh; background: var(--bg); padding-bottom: 60rpx; }
.sbar { display: flex; align-items: center; padding: 24rpx 32rpx; background: var(--card); }
.s-box { flex: 1; display: flex; align-items: center; background: var(--zebra-bg); border-radius: 40rpx; padding: 0 28rpx; height: 78rpx; }
.s-ico { font-size: 28rpx; margin-right: 14rpx; }
.s-input { flex: 1; font-size: 27rpx; color: var(--ink); }
.s-clr { color: var(--ink2); padding: 10rpx; }
.s-go { margin-left: 22rpx; color: #FDF8EE; background: linear-gradient(135deg, var(--brand), var(--brand-deep)); border-radius: 40rpx; padding: 0 38rpx; height: 78rpx; line-height: 78rpx; font-size: 27rpx; font-weight: 700; }
.filters { display: flex; align-items: center; background: var(--card); padding: 0 24rpx 18rpx; box-shadow: 0 6rpx 16rpx rgba(60,44,22,.04); }
.f-scroll { flex: 1; }
.f-row { display: flex; }
.f-chip { flex-shrink: 0; background: var(--zebra-bg); color: var(--ink2); border-radius: 26rpx; font-size: 22rpx; padding: 8rpx 22rpx; margin-right: 12rpx; }
.f-chip.on { background: var(--brand); color: #fff; }
.deep { display: flex; align-items: center; margin-left: 8rpx; font-size: 21rpx; color: var(--ink2); flex-shrink: 0; }
.d-dot { width: 28rpx; height: 28rpx; border-radius: 50%; border: 3rpx solid var(--ink2); margin-right: 8rpx; position: relative; }
.d-dot.on { border-color: var(--brand); background: var(--brand); }
.hots { padding: 40rpx 36rpx; }
.h-t { font-size: 26rpx; color: var(--ink2); margin-bottom: 24rpx; }
.h-wrap { display: flex; flex-wrap: wrap; }
.h-chip { background: var(--card); border: 1rpx solid var(--line); color: var(--ink); border-radius: 34rpx; padding: 14rpx 34rpx; font-size: 25rpx; margin: 0 18rpx 18rpx 0; }
.h-chip.old { color: var(--ink2); background: var(--zebra-bg); border-color: transparent; }
.h-clear { float: right; font-size: 21rpx; color: var(--ink2); font-weight: 400; }
.h-tip { margin-top: 20rpx; font-size: 21rpx; color: var(--ink2); opacity: .7; }
.results { padding: 24rpx 32rpx 0; }
.r-item { padding: 24rpx 28rpx; margin-bottom: 20rpx; }
.r-head { display: flex; align-items: center; }
.r-badge { font-size: 19rpx; border-radius: 8rpx; padding: 4rpx 14rpx; margin-right: 16rpx; flex-shrink: 0; }
.r-title { font-size: 28rpx; font-weight: 700; color: var(--ink); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.r-snippet { font-size: 23rpx; color: var(--ink2); margin-top: 12rpx; line-height: 1.6; }
.none { text-align: center; color: var(--ink2); padding: 80rpx 0; font-size: 26rpx; display: flex; flex-direction: column; align-items: center; }
.none-sub { font-size: 22rpx; margin-top: 16rpx; opacity: .7; }
.deep-scan { text-align: center; color: var(--brand); font-size: 22rpx; padding: 14rpx 0; animation: pulse 1.2s infinite; }
@keyframes pulse { 50% { opacity: .45; } }
</style>
