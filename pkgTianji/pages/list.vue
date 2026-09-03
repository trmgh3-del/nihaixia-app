<template>
  <view class="page" :class="theme === 'dark' ? 'tdark' : 'tlight'">
    <view class="banner">
      <view class="b-t serif">天纪 · 人间道 · 地脉道</view>
      <view class="b-s">紫微斗数 · 易经六十四卦 · 阳宅风水 —— 倪师另一套体系</view>
    </view>
    <view class="tabs">
      <view class="tab" :class="{ on: g === '' }" @tap="g = ''">全部 {{ sections.length }}</view>
      <view v-for="gg in groups" :key="gg" class="tab" :class="{ on: g === gg }" @tap="g = gg">{{ gg }}</view>
    </view>
    <view class="list">
      <view v-for="it in shown" :key="it.id" class="t-item card fade-in" @tap="open(it)">
        <view class="t-t serif">{{ it.t }}</view>
        <view class="t-s">{{ snippet(it) }}</view>
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
    return { loaded: false, g: '', sections: [] }
  },
  computed: {
    theme() { return store.theme },
    groups() {
      const s = []
      this.sections.forEach(x => { if (x.g && x.g[0] && !s.includes(x.g[0])) s.push(x.g[0]) })
      return s
    },
    shown() {
      let list = this.sections
      if (this.g) list = list.filter(x => x.g && x.g[0] === this.g)
      return list
    }
  },
  mounted() {
    loadData('tianji').then(d => { this.sections = d.sections || []; this.loaded = true }).catch(() => {}).finally(() => { this.loaded = true })
  },
  methods: {
    snippet(it) { return (it.b || '').replace(/[#>*`|]/g, '').replace(/\s+/g, ' ').slice(0, 80) },
    open(it) {
      const list = this.shown
      const idx = list.findIndex(x => x.id === it.id)
      openMd({ ...it, f: 'tianji' }, it.t, { items: list.map(x => ({ ...x, f: 'tianji' })), idx })
    }
  }
}
</script>

<style scoped>
.page { min-height: 100vh; background: var(--bg); padding-bottom: 50rpx; }
.banner { background: linear-gradient(140deg, #241713, #3A241E); padding: 44rpx 36rpx 52rpx; }
.b-t { font-size: 40rpx; font-weight: 800; color: #FDF8EE; letter-spacing: 3rpx; }
.b-s { font-size: 21rpx; color: rgba(253,248,238,.8); margin-top: 12rpx; }
.tabs { display: flex; flex-wrap: wrap; padding: 24rpx 24rpx 0; }
.tab { font-size: 22rpx; color: var(--ink2); background: var(--card); border: 1rpx solid var(--line); border-radius: 26rpx; padding: 10rpx 28rpx; margin: 0 12rpx 12rpx 0; }
.tab.on { background: var(--brand); border-color: var(--brand); color: #fff; font-weight: 700; }
.list { padding: 16rpx 32rpx 0; }
.t-item { padding: 26rpx 30rpx; margin-bottom: 20rpx; }
.t-t { font-size: 29rpx; font-weight: 800; color: var(--ink); }
.t-s { font-size: 22rpx; color: var(--ink2); margin-top: 10rpx; line-height: 1.6; }
.none { text-align: center; color: var(--ink2); padding: 100rpx 0; }
</style>
