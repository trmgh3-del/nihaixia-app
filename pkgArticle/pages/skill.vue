<template>
  <view class="page" :class="theme === 'dark' ? 'tdark' : 'tlight'">
    <view class="sbar">
      <view class="s-box">
        <image class="ico" src="/static/icons/search-gray.png" />
        <input class="s-input" v-model="q" placeholder="搜速查卡 / 规则 / 公式…" />
      </view>
    </view>
    <view class="tabs">
      <view class="tab" :class="{ on: h2 === '' }" @tap="h2 = ''">全部 {{ units.length }}</view>
      <view v-for="g in h2s" :key="g" class="tab" :class="{ on: h2 === g }" @tap="h2 = g">{{ g }}</view>
    </view>
    <view class="list">
      <view v-for="it in shown" :key="it.id" class="s-item card fade-in" @tap="open(it)">
        <view class="s-t">{{ it.t }}</view>
        <view class="s-h2">{{ it.h2 }}</view>
      </view>
      <view v-if="loaded && !shown.length" class="none">无匹配内容</view>
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
    return { loaded: false, q: '', h2: '', units: [] }
  },
  computed: {
    theme() { return store.theme },
    h2s() {
      const s = []
      this.units.forEach(u => { if (u.h2 && !s.includes(u.h2) && s.length < 20) s.push(u.h2) })
      return s
    },
    shown() {
      let list = this.units
      if (this.h2) list = list.filter(u => u.h2 === this.h2)
      const q = this.q.trim()
      if (q) list = list.filter(u => (u.t + (u.b || '')).includes(q))
      return list
    }
  },
  mounted() {
    loadData('skill_units').then(d => { this.units = d.units || []; this.loaded = true }).catch(() => {}).finally(() => { this.loaded = true })
  },
  methods: {
    open(it) {
      const list = this.shown
      const idx = list.findIndex(x => x.id === it.id)
      openMd({ ...it, f: 'skill' }, it.t, { items: list.map(x => ({ ...x, f: 'skill' })), idx })
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
.tabs { display: flex; flex-wrap: wrap; background: var(--card); padding: 0 24rpx 20rpx; }
.tab { font-size: 22rpx; color: var(--ink2); background: var(--zebra-bg); border-radius: 26rpx; padding: 10rpx 26rpx; margin: 0 12rpx 10rpx 0; }
.tab.on { background: var(--brand); color: #fff; font-weight: 700; }
.list { padding: 20rpx 32rpx 0; }
.s-item { padding: 26rpx 30rpx; margin-bottom: 18rpx; }
.s-t { font-size: 28rpx; font-weight: 700; color: var(--ink); }
.s-h2 { font-size: 20rpx; color: var(--ink2); margin-top: 8rpx; }
.none { text-align: center; color: var(--ink2); padding: 100rpx 0; }
</style>
