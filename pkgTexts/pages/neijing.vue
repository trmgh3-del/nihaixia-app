<template>
  <view class="page" :class="theme === 'dark' ? 'tdark' : 'tlight'">
    <view class="sbar">
      <view class="s-box">
        <image class="ico" src="/static/icons/search-gray.png" />
        <input class="s-input" v-model="q" placeholder="搜 72 篇篇名 / 正文…" />
      </view>
    </view>
    <view class="grid">
      <view v-for="(it, i) in shown" :key="it.id" class="g-item card fade-in" @tap="open(it)">
        <view class="g-idx serif">{{ i + 1 < 10 ? '0' + (i + 1) : i + 1 }}</view>
        <view class="g-t serif">{{ it.n || it.t }}</view>
        <view class="g-s">{{ snippet(it) }}</view>
      </view>
    </view>
    <view v-if="!shown.length" class="none">无匹配篇目</view>
  </view>
</template>

<script>
import { store , applyTheme } from '@/utils/store.js'
import { loadData } from '@/utils/data.js'
import { openMd } from '@/utils/routes.js'

export default {
  onShow() { applyTheme() },
  data() {
    return { q: '', chapters: [] }
  },
  computed: {
    theme() { return store.theme },
    shown() {
      const q = this.q.trim()
      if (!q) return this.chapters
      return this.chapters.filter(it => (it.t + (it.b || '')).includes(q))
    }
  },
  mounted() {
    loadData('neijing').then(d => { this.chapters = d.chapters || [] }).catch(() => {})
  },
  methods: {
    snippet(it) { return (it.b || '').replace(/[#>*`|]/g, '').replace(/\s+/g, ' ').slice(0, 64) },
    open(it) {
      const list = this.shown
      const idx = list.findIndex(x => x.id === it.id)
      openMd({ ...it, f: 'neijing' }, it.n || it.t, { items: list.map(x => ({ ...x, f: 'neijing' })), idx })
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
.grid { display: flex; flex-wrap: wrap; padding: 24rpx 20rpx 0; }
.g-item { width: 46.5%; margin: 1.5%; padding: 26rpx 26rpx 22rpx; box-sizing: border-box; }
.g-idx { font-size: 22rpx; color: var(--gold); font-weight: 800; letter-spacing: 2rpx; }
.g-t { font-size: 30rpx; font-weight: 800; color: var(--ink); margin: 10rpx 0 8rpx; }
.g-s { font-size: 21rpx; color: var(--ink2); line-height: 1.5; height: 64rpx; overflow: hidden; }
.none { text-align: center; color: var(--ink2); padding: 100rpx 0; }
</style>
