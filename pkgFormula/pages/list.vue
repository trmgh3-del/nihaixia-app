<template>
  <view class="page" :class="theme === 'dark' ? 'tdark' : 'tlight'">
    <view class="sbar">
      <view class="s-box">
        <image class="ico" src="/static/icons/search-gray.png" />
        <input class="s-input" v-model="q" :placeholder="'搜 ' + total + ' 方：方名 / 主症 / 药物…'" />
      </view>
      <view class="s-right">
        <view class="s-art" @tap="goConvert">剂量换算器 ›</view>
      </view>
    </view>

    <view class="jingbar" v-if="!cmpMode">
      <view class="j-chip" :class="{ on: jing === '' }" @tap="jing = ''">全部 {{ items.length }}</view>
      <view v-for="j in jings" :key="j.k" class="j-chip" :class="{ on: jing === j.k }" @tap="jing = j.k">{{ j.k }} {{ j.n }}</view>
    </view>
    <view class="catbar" v-if="!cmpMode && categories.length">
      <view class="cat-chip" :class="{ on: category === '' }" @tap="category = ''">分类不限</view>
      <view v-for="c in categories" :key="c" class="cat-chip" :class="{ on: category === c }" @tap="category = category === c ? '' : c">{{ c }}</view>
    </view>
    <view class="cmp-bar" v-if="cmpMode">
      <text class="cmp-tip">对比模式：已选 {{ cmpSel.length }}/2</text>
      <view class="cmp-btn go" v-if="cmpSel.length === 2" @tap="doCompare">开始对比</view>
      <view class="cmp-btn" @tap="exitCmp">退出</view>
    </view>
    <view class="sbar2" v-else>
      <view class="f-srcbar" @tap="enterCmp"><image class="ico-s" src="/static/icons/swap-gold.png" />方剂对比</view>
    </view>

    <view class="list">
      <view v-for="it in shown" :key="it.id" class="f-item card fade-in" @tap="onItem(it)">
        <view class="f-check" v-if="cmpMode" :class="{ on: inSel(it) }">{{ inSel(it) ? '✓' : '' }}</view>
        <view class="f-main">
          <view class="f-head">
            <view class="f-name serif">{{ it.n }}<text class="f-jing" v-if="fJing(it)">{{ fJing(it) }}</text></view>
            <view class="f-src">{{ shortSrc(it.src) }}</view>
          </view>
          <view class="f-row" v-if="it.zhizhi"><text class="f-k">主症</text><text class="f-v">{{ it.zhizhi }}</text></view>
          <view class="f-row" v-if="it.composition"><text class="f-k">组成</text><text class="f-v">{{ it.composition }}</text></view>
          <view class="f-row" v-if="it.clinical"><text class="f-k">临床</text><text class="f-v hl">{{ it.clinical }}</text></view>
          <view class="f-row" v-if="!it.clinical && it.doses"><text class="f-k">剂量</text><text class="f-v">{{ it.doses }}</text></view>
        </view>
      </view>
      <view v-if="!shown.length" class="none">无匹配方剂</view>
    </view>

    <!-- 对比浮层 -->
    <view class="cmp-mask" v-if="cmpView" @tap="cmpView = null">
      <view class="cmp-panel card" @tap.stop>
        <view class="cp-title serif">⟡ 方剂对比</view>
        <scroll-view scroll-y class="cp-scroll">
          <view class="cp-cols">
            <view class="cp-card" v-for="(a, i) in cmpView" :key="i" :class="{ alt: i === 1 }">
              <view class="cpc-head" :class="{ alt: i === 1 }">
                <view class="cpc-name serif">{{ a.n }}</view>
                <view class="cpc-src">{{ a.src || '经方' }}</view>
              </view>
              <view class="cpc-field" v-for="f in cmpFields" :key="f.k">
                <view class="cpc-lab">{{ f.k }}</view>
                <view class="cpc-val" :class="{ hl: f.v === 'clinical' }">{{ a[f.v] || '—' }}</view>
              </view>
            </view>
          </view>
          <view class="cp-note">剂量体系：原方为汉朝度量衡（1两≈15.6g）；临床为倪师台湾制（1钱≈3.75g）。仅供学习参考，遵医嘱。</view>
        </scroll-view>
        <view class="cp-close" @tap="cmpView = null">关闭</view>
      </view>
    </view>
  </view>
</template>

<script>
import { store , applyTheme } from '@/utils/store.js'
import { loadData } from '@/utils/data.js'

export default {
  onShow() { applyTheme() },
  data() {
    return {
      q: '', items: [], jing: '', category: '', cmpMode: false, cmpSel: [], cmpView: null,
      cmpFields: [
        { k: '主症关键', v: 'zhizhi' }, { k: '组成', v: 'composition' }, { k: '原方剂量', v: 'origin' },
        { k: '倪师临床', v: 'clinical' }, { k: '逐味剂量', v: 'doses' }, { k: '备注', v: 'note' }
      ]
    }
  },
  computed: {
    theme() { return store.theme },
    total() { return this.items.length },
    jings() {
      const map = {}
      this.items.forEach(it => {
        const j = this.fJing(it)
        if (j) map[j] = (map[j] || 0) + 1
      })
      const order = ['太阳', '阳明', '少阳', '太阴', '少阴', '厥阴']
      return order.filter(k => map[k]).map(k => ({ k, n: map[k] }))
    },
    categories() {
      return [...new Set(this.items.map(it => it.category).filter(Boolean))].slice(0, 18)
    },
    shown() {
      let list = this.items
      if (this.jing) list = list.filter(it => this.fJing(it) === this.jing)
      if (this.category) list = list.filter(it => it.category === this.category)
      const q = this.q.trim()
      if (q) list = list.filter(it => (it.n + (it.alias || '') + (Array.isArray(it.keywords) ? it.keywords.join('') : '') + (it.category || '') + (it.meridian || '') + (it.zhizhi || '') + (it.clinical || '') + (it.origin || '') + (it.composition || '') + (it.note || '') + (it.doses || '')).includes(q))
      return list
    }
  },
  mounted() {
    loadData('formulas').then(d => {
      const map = new Map()
      for (const it of d.items || []) {
        if (!map.has(it.n)) map.set(it.n, it)
      }
      this.items = [...map.values()]
    }).catch(() => {})
  },
  methods: {
    fJing(it) {
      const n = it.n || ''
      if (it.meridian) return String(it.meridian).split(/[、,，/]/)[0]
      if (/柴胡/.test(n)) return '少阳'
      if (/承气|白虎/.test(n)) return '阳明'
      if (/麻黄汤|桂枝汤$|桂枝加|葛根汤|青龙/.test(n)) return '太阳'
      if (/理中|建中/.test(n)) return '太阴'
      if (/四逆|真武|附子|通脉/.test(n)) return '少阴'
      if (/乌梅|当归四逆|吴茱萸/.test(n)) return '厥阴'
      if (/泻心|陷胸|十枣/.test(n)) return '太阳'
      if (/黄连阿胶/.test(n)) return '少阴'
      return ''
    },
    shortSrc(s) {
      if (!s) return '经方'
      if (s.includes('感冒')) return '感冒六方'
      if (s.includes('关键方剂')) return '六经主方'
      if (s.includes('速查卡')) return '剂量速查卡'
      if (s.includes('C类')) return 'C类勘误'
      return '剂量速查'
    },
    goArticles() { uni.navigateTo({ url: '/pkgFormula/pages/articles' }) },
    goConvert() { uni.navigateTo({ url: '/pkgFormula/pages/convert' }) },
    open(it) {
      store.readerItem = { kind: 'formula', item: it }
      uni.navigateTo({ url: '/pkgFormula/pages/detail' })
    },
    enterCmp() { this.cmpMode = true; this.cmpSel = [] },
    exitCmp() { this.cmpMode = false; this.cmpSel = [] },
    inSel(it) { return this.cmpSel.some(x => x.id === it.id) },
    onItem(it) {
      if (!this.cmpMode) { this.open(it); return }
      const k = this.cmpSel.findIndex(x => x.id === it.id)
      if (k >= 0) { this.cmpSel.splice(k, 1); return }
      if (this.cmpSel.length >= 2) { uni.showToast({ title: '最多选 2 方', icon: 'none' }); return }
      this.cmpSel.push(it)
    },
    doCompare() { this.cmpView = [this.cmpSel[0], this.cmpSel[1]] }
  }
}
</script>

<style scoped>
.page { min-height: 100vh; background: var(--bg); padding-bottom: 50rpx; }
.sbar { display: flex; align-items: center; padding: 22rpx 32rpx; background: var(--card); }
.s-box { flex: 1; display: flex; align-items: center; background: var(--zebra-bg); border-radius: 38rpx; padding: 0 28rpx; height: 74rpx; }
.s-ico { margin-right: 14rpx; font-size: 26rpx; }
.s-input { flex: 1; font-size: 26rpx; color: var(--ink); }
.s-right { flex-shrink: 0; margin-left: 20rpx; }
.s-art { font-size: 23rpx; color: var(--brand); }
.jingbar { display: flex; flex-wrap: wrap; background: var(--card); padding: 4rpx 24rpx 16rpx; }
.j-chip { font-size: 21rpx; color: var(--ink2); background: var(--zebra-bg); border-radius: 24rpx; padding: 8rpx 22rpx; margin: 0 12rpx 10rpx 0; display: flex; align-items: center; }
.j-chip.on { background: var(--brand); color: #fff; font-weight: 700; }
.f-jing { font-size: 17rpx; color: #fff; background: var(--gold); border-radius: 8rpx; padding: 2rpx 10rpx; margin-left: 14rpx; font-weight: 500; }
.sbar2 { background: var(--card); padding: 0 32rpx 18rpx; display: flex; justify-content: flex-end; }
.f-srcbar { display: flex; align-items: center; font-size: 22rpx; color: var(--gold); border: 1rpx solid var(--gold); border-radius: 26rpx; padding: 6rpx 22rpx; }
.f-srcbar .ico-s { margin-right: 8rpx; }
.catbar { display: flex; flex-wrap: wrap; padding: 4rpx 24rpx 14rpx; background: var(--card); }
.cat-chip { font-size: 20rpx; color: var(--ink2); background: var(--zebra-bg); border-radius: 24rpx; padding: 7rpx 18rpx; margin: 0 10rpx 8rpx 0; }
.cat-chip.on { background: var(--gold); color: #fff; }
.cmp-bar { display: flex; align-items: center; background: var(--card); padding: 14rpx 32rpx; border-bottom: 1rpx solid var(--line); }
.cmp-tip { flex: 1; font-size: 24rpx; color: var(--brand); font-weight: 700; }
.cmp-btn { font-size: 22rpx; color: var(--ink2); border: 1rpx solid var(--line); border-radius: 26rpx; padding: 8rpx 26rpx; margin-left: 14rpx; }
.cmp-btn.go { background: var(--brand); color: #fff; border-color: var(--brand); font-weight: 700; }
.list { padding: 24rpx 32rpx 0; }
.f-item { display: flex; padding: 26rpx 30rpx; margin-bottom: 22rpx; }
.f-check { width: 44rpx; height: 44rpx; border-radius: 50%; border: 3rpx solid var(--line); margin-right: 20rpx; flex-shrink: 0; display: flex; align-items: center; justify-content: center; color: #fff; font-size: 24rpx; margin-top: 6rpx; }
.f-check.on { background: var(--brand); border-color: var(--brand); }
.f-main { flex: 1; min-width: 0; }
.f-head { display: flex; align-items: center; margin-bottom: 12rpx; }
.f-name { font-size: 33rpx; font-weight: 800; color: var(--brand); letter-spacing: 2rpx; }
.f-src { margin-left: auto; display: flex; align-items: center; height: 40rpx; box-sizing: border-box; font-size: 19rpx; color: var(--gold); border: 1rpx solid var(--gold); border-radius: 8rpx; padding: 0 12rpx; }
.f-row { display: flex; margin-top: 10rpx; font-size: 23rpx; }
.f-k { flex-shrink: 0; width: 72rpx; color: var(--ink2); }
.f-v { flex: 1; color: var(--ink); line-height: 1.6; }
.hl { color: var(--brand); }
.none { text-align: center; color: var(--ink2); padding: 100rpx 0; }
/* 对比浮层 */
.cmp-mask { position: fixed; inset: 0; background: rgba(20,12,6,.55); z-index: 999; display: flex; align-items: center; justify-content: center; }
.cmp-panel { width: 94%; max-height: 82vh; display: flex; flex-direction: column; overflow: hidden; box-sizing: border-box; }
.cp-title { text-align: center; font-size: 32rpx; font-weight: 800; color: var(--brand); padding: 26rpx 0 16rpx; }
.cp-scroll { max-height: 60vh; padding: 0 16rpx; box-sizing: border-box; width: 100%; }
.cp-cols { display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 1fr); gap: 10rpx; }
.cp-card { border-radius: 16rpx; overflow: hidden; border: 2rpx solid var(--brand); min-width: 0; }
.cp-card.alt { border-color: #2F5D62; }
.cpc-head { background: linear-gradient(135deg, rgba(154,46,31,.92), rgba(124,58,33,.92)); padding: 14rpx 12rpx 12rpx; text-align: center; }
.cpc-head.alt { background: linear-gradient(135deg, #2F5D62, #234449); }
.cpc-name { font-size: 25rpx; font-weight: 800; color: #FDF8EE; word-break: break-all; line-height: 1.4; }
.cpc-src { font-size: 16rpx; color: rgba(253,248,238,.75); margin-top: 2rpx; }
.cpc-field { padding: 10rpx 10rpx 8rpx; border-top: 1rpx solid var(--line); min-width: 0; }
.cpc-lab { font-size: 17rpx; color: var(--gold); font-weight: 700; margin-bottom: 2rpx; }
.cpc-val { font-size: 18rpx; color: var(--ink); line-height: 1.55; word-break: break-all; min-height: 34rpx; }
.cpc-val.hl { color: var(--brand); font-weight: 600; }







.cp-note { font-size: 19rpx; color: #A2651B; background: #FCF3DC; border-radius: 10rpx; padding: 12rpx 16rpx; margin: 18rpx 0; line-height: 1.6; }
.cp-close { text-align: center; padding: 22rpx 0; border-top: 1rpx solid var(--line); color: var(--ink2); font-size: 26rpx; }
</style>
