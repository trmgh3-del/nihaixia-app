<template>
  <view class="page" :class="theme === 'dark' ? 'tdark' : 'tlight'">
    <view class="sbar">
      <view class="s-box">
        <image class="ico" src="/static/icons/search-gray.png" />
        <input class="s-input" v-model="q" placeholder="搜条文编号 / 方名 / 症状…" @input="filter" />
      </view>
    </view>
    <view class="tabs">
      <view class="tab" :class="{ on: tab === 'sun' }" @tap="switchTab('sun')">太阳篇 1-129</view>
      <view class="tab" :class="{ on: tab === 'que' }" @tap="switchTab('que')">下篇补齐 138-276</view>
      <view class="tab" :class="{ on: tab === 'wj' }" @tap="switchTab('wj')">五经总结</view>
    </view>

    <view class="intro card" v-if="tab === 'sun' && !q">
      <view class="i-title serif">《伤寒论》· 人纪讲义</view>
      <view class="i-body">太阳篇条文 1-129 完整解读（含补遗 24-32），加 2026-08 补齐的太阳下篇（结胸/痞证/泻心汤 138-193）与阳明篇（承气白虎逐条 194-276），再加阳明至少阴厥阴五经总结与倪师诊病十问。</view>
    </view>

    <view class="list">
      <view v-for="it in shown" :key="it.id" class="l-item card fade-in" @tap="open(it)">
        <view class="l-head">
          <view class="l-badge" v-if="it.n">条文 {{ it.n }}</view>
          <view class="l-badge soft" v-else-if="it.g && it.g[0]">{{ it.g[0] }}</view>
          <view class="l-t">{{ titleOf(it) }}</view>
        </view>
        <view class="l-s">{{ snippet(it) }}</view>
      </view>
      <view v-if="!shown.length" class="none">无匹配条目</view>
    </view>
  </view>
</template>

<script>
import { store , applyTheme } from '@/utils/store.js'
import { loadData } from '@/utils/data.js'
import { openMd } from '@/utils/routes.js'

export default {
  onShow() { applyTheme() },
  data() {
    return { q: '', tab: 'sun', sun: [], que: [], wujing: [], loading: true }
  },
  computed: {
    theme() { return store.theme },
    shown() {
      const q = this.q.trim()
      let list = this.tab === 'sun' ? this.sun : this.tab === 'que' ? this.que : this.wujing
      if (!q) return list
      return list.filter(it => (it.t + (it.b || '')).includes(q))
    }
  },
  mounted() { this.init() },
  methods: {
    async init() {
      try {
        const d = await loadData('shanghan')
        this.sun = d.sun || []
        this.que = d.que || []
        this.wujing = d.wujing || []
      } catch (e) { uni.showToast({ title: '加载失败', icon: 'none' }) }
      this.loading = false
    },
    switchTab(t) { this.tab = t },
    titleOf(it) { return it.t },
    snippet(it) { return (it.b || '').replace(/[#>*`|]/g, '').replace(/\s+/g, ' ').slice(0, 86) },
    open(it) {
      const list = this.shown
      const idx = list.findIndex(x => x.id === it.id)
      openMd({ ...it, f: 'shanghan' }, it.t, { items: list.map(x => ({ ...x, f: 'shanghan' })), idx })
    }
  }
}
</script>

<style scoped>
.page { min-height: 100vh; background: var(--bg); padding-bottom: 50rpx; }
.sbar { padding: 22rpx 32rpx; background: var(--card); }
.s-box { display: flex; align-items: center; background: var(--zebra-bg); border-radius: 38rpx; padding: 0 28rpx; height: 74rpx; }
.s-ico { margin-right: 14rpx; font-size: 26rpx; }
.s-input { flex: 1; font-size: 26rpx; color: var(--ink); }
.tabs { display: flex; background: var(--card); padding: 0 20rpx 20rpx; gap: 12rpx; }
.tab { flex: 1; text-align: center; font-size: 23rpx; padding: 14rpx 0; border-radius: 30rpx; background: var(--zebra-bg); color: var(--ink2); }
.tab.on { background: var(--brand); color: #fff; font-weight: 700; }
.intro { margin: 24rpx 32rpx 0; padding: 26rpx 30rpx; }
.i-title { font-size: 30rpx; font-weight: 800; color: var(--brand); margin-bottom: 12rpx; }
.i-body { font-size: 23rpx; color: var(--ink2); line-height: 1.8; }
.list { padding: 24rpx 32rpx 0; }
.l-item { padding: 26rpx 30rpx; margin-bottom: 20rpx; }
.l-head { display: flex; align-items: center; }
.l-badge { font-size: 20rpx; color: #fff; background: var(--brand); border-radius: 8rpx; padding: 4rpx 14rpx; margin-right: 16rpx; flex-shrink: 0; }
.l-badge.soft { background: var(--gold); }
.l-t { font-size: 28rpx; font-weight: 700; color: var(--ink); }
.l-s { font-size: 23rpx; color: var(--ink2); margin-top: 12rpx; line-height: 1.6; }
.none { text-align: center; color: var(--ink2); padding: 100rpx 0; }
</style>
