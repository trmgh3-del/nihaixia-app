<template>
  <view class="page" :class="theme === 'dark' ? 'tdark' : 'tlight'">
    <view class="zw-row">
      <view class="zw-banner" @tap="goZiwu">
        <view class="zb-ico serif">子午</view>
        <view class="zb-main"><view class="zb-t">子午流注</view><view class="zb-s">十二时辰气血流注</view></view>
        <text class="zb-a">›</text>
      </view>
      <view class="zw-banner tr" @tap="goTreat">
        <view class="zb-ico serif">查穴</view>
        <view class="zb-main"><view class="zb-t">症状查穴</view><view class="zb-s">按症状反查穴位处方</view></view>
        <text class="zb-a">›</text>
      </view>
    </view>
    <view class="sbar">
      <view class="s-box">
        <image class="ico" src="/static/icons/search-gray.png" />
        <input class="s-input" v-model="q" placeholder="搜穴位 / 经络 / 治症…" />
      </view>
    </view>
    <view class="tabs">
      <view v-for="t in tabs" :key="t.k" class="tab" :class="{ on: tab === t.k }" @tap="switchTab(t.k)">{{ t.label }} {{ numOf(t.k) }}</view>
    </view>
    <view class="jingbar" v-if="tab === 'points'">
      <view class="j-chip" :class="{ on: jing === '' }" @tap="jing = ''">全部经络</view>
      <view v-for="j in jings" :key="j" class="j-chip" :class="{ on: jing === j }" @tap="jing = jing === j ? '' : j">{{ j }}</view>
    </view>

    <view class="list">
      <view v-for="it in shown" :key="it.id" class="l-item card fade-in" @tap="open(it)">
        <view class="l-head">
          <view class="l-badge">{{ badgeOf(it) }}</view>
          <view class="l-t serif">{{ it.t }}</view>
        </view>
        <view class="l-s">{{ snippet(it) }}</view>
      </view>
      <view v-if="!shown.length" class="none">无匹配内容</view>
    </view>
  </view>
</template>

<script>
import { store , applyTheme } from '@/utils/store.js'
import { loadData } from '@/utils/data.js'
import { openMd } from '@/utils/routes.js'

export default {
  onShow() { applyTheme() },
  onLoad(query) {
    if (query && query.pt) {
      this._pendingPt = decodeURIComponent(query.pt)
    }
  },
  data() {
    return {
      q: '', tab: 'tutorial', jing: '',
      tabs: [
        { k: 'tutorial', label: '教程' }, { k: 'quickref', label: '速查' },
        { k: 'highlights', label: '精髓' }, { k: 'points', label: '穴位' }
      ],
      data: { tutorial: [], quickref: [], highlights: [], points: [] }
    }
  },
  computed: {
    theme() { return store.theme },
    jings() {
      const seen = []
      for (const it of this.data.points || []) {
        const m = it.t.match(/（([^）]*经[^）]*)）/)
        if (m && !seen.includes(m[1])) seen.push(m[1])
      }
      return seen.slice(0, 16)
    },
    shown() {
      let list = this.data[this.tab] || []
      if (this.tab === 'points' && this.jing) list = list.filter(it => it.t.includes(this.jing))
      const q = this.q.trim()
      if (q) list = list.filter(it => (it.t + (it.b || '')).includes(q))
      return list
    }
  },
  mounted() {
    loadData('zhenjiu').then(d => {
      this.data = d
      if (this._pendingPt) {
        this.tab = 'points'
        this.q = this._pendingPt
      }
    }).catch(() => {})
  },
  methods: {
    numOf(k) { return (this.data[k] || []).length },
    switchTab(k) { this.tab = k; this.jing = '' },
    goZiwu() { uni.navigateTo({ url: '/pkgZhenjiu/pages/ziwu' }) },
    goTreat() { uni.navigateTo({ url: '/pkgZhenjiu/pages/treat' }) },
    badgeOf(it) { return this.tab === 'points' ? '穴' : this.tab === 'quickref' ? '查' : this.tab === 'highlights' ? '讲' : '教' },
    snippet(it) { return (it.b || '').replace(/[#>*`|]/g, '').replace(/\s+/g, ' ').slice(0, 76) },
    open(it) {
      const list = this.shown
      const idx = list.findIndex(x => x.id === it.id)
      openMd({ ...it, f: 'zhenjiu' }, it.t, { items: list.map(x => ({ ...x, f: 'zhenjiu' })), idx })
    }
  }
}
</script>

<style scoped>
.page { min-height: 100vh; background: var(--bg); padding-bottom: 50rpx; }
.zw-row { display: flex; }
.zw-banner { flex: 1; display: flex; align-items: center; background: linear-gradient(135deg, #2F5D62, #234449); padding: 18rpx 22rpx; }
.zw-banner.tr { background: linear-gradient(135deg, #95541C, #7A4212); margin-left: 14rpx; }
.zb-ico { width: 68rpx; height: 68rpx; border-radius: 16rpx; background: rgba(253,248,238,.15); border: 2rpx solid rgba(253,248,238,.4); color: #FDF8EE; font-size: 26rpx; font-weight: 800; display: flex; align-items: center; justify-content: center; }
.zb-main { flex: 1; margin-left: 20rpx; }
.zb-t { font-size: 24rpx; font-weight: 800; color: #FDF8EE; }
.zb-s { font-size: 17rpx; color: rgba(253,248,238,.75); margin-top: 4rpx; white-space: nowrap; }
.zb-a { color: rgba(253,248,238,.8); font-size: 32rpx; }
.sbar { padding: 22rpx 32rpx; background: var(--card); }
.s-box { display: flex; align-items: center; background: var(--zebra-bg); border-radius: 38rpx; padding: 0 28rpx; height: 74rpx; }
.s-ico { margin-right: 14rpx; font-size: 26rpx; }
.s-input { flex: 1; font-size: 26rpx; color: var(--ink); }
.tabs { display: flex; background: var(--card); padding: 0 20rpx 20rpx; gap: 10rpx; }
.tab { flex: 1; text-align: center; font-size: 23rpx; padding: 14rpx 0; border-radius: 28rpx; background: var(--zebra-bg); color: var(--ink2); }
.tab.on { background: var(--brand); color: #fff; font-weight: 700; }
.jingbar { display: flex; flex-wrap: wrap; padding: 4rpx 24rpx 16rpx; background: var(--card); }
.j-chip { font-size: 21rpx; color: var(--ink2); background: var(--zebra-bg); border-radius: 24rpx; padding: 8rpx 24rpx; margin: 0 12rpx 10rpx 0; }
.j-chip.on { background: #54427C; color: #fff; }
.list { padding: 24rpx 32rpx 0; }
.l-item { padding: 26rpx 30rpx; margin-bottom: 20rpx; }
.l-head { display: flex; align-items: center; }
.l-badge { width: 44rpx; height: 44rpx; border-radius: 12rpx; background: #EDE9F4; color: #54427C; font-size: 22rpx; display: flex; align-items: center; justify-content: center; margin-right: 18rpx; flex-shrink: 0; font-weight: 700; }
.l-t { font-size: 28rpx; font-weight: 700; color: var(--ink); }
.l-s { font-size: 22rpx; color: var(--ink2); margin-top: 10rpx; line-height: 1.6; }
.none { text-align: center; color: var(--ink2); padding: 100rpx 0; }
</style>
