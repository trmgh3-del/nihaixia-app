<template>
  <view class="page" :class="theme === 'dark' ? 'tdark' : 'tlight'">
    <view class="sbar">
      <view class="s-box">
        <image class="ico" src="/static/icons/search-gray.png" />
        <input class="s-input" v-model="q" placeholder="搜篇名 / 方名 / 病症…" />
      </view>
    </view>
    <view class="list">
      <view v-for="(it, i) in shown" :key="it.id" class="l-item card fade-in" @tap="open(it)">
        <view class="l-no serif">{{ i + 1 }}</view>
        <view class="l-main">
          <view class="l-t">{{ it.t }}</view>
          <view class="l-s">{{ snippet(it) }}</view>
        </view>
        <text class="l-a">›</text>
      </view>
      <view v-if="loaded && !shown.length" class="none">无匹配篇目</view>
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
    return { loaded: false, q: '', chapters: [] }
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
    loadData('jingui').then(d => { this.chapters = d.chapters || []; this.loaded = true }).catch(() => {}).finally(() => { this.loaded = true })
  },
  methods: {
    snippet(it) { return (it.b || '').replace(/[#>*`|]/g, '').replace(/\s+/g, ' ').slice(0, 80) },
    open(it) {
      const list = this.shown
      const idx = list.findIndex(x => x.id === it.id)
      openMd({ ...it, f: 'jingui' }, it.t, { items: list.map(x => ({ ...x, f: 'jingui' })), idx })
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
.list { padding: 24rpx 32rpx 0; }
.l-item { display: flex; align-items: center; padding: 26rpx 30rpx; margin-bottom: 20rpx; }
.l-no { width: 56rpx; height: 56rpx; border-radius: 16rpx; background: var(--zebra-bg); color: var(--brand); font-weight: 800; display: flex; align-items: center; justify-content: center; font-size: 24rpx; flex-shrink: 0; }
.l-main { flex: 1; margin-left: 22rpx; min-width: 0; }
.l-t { font-size: 28rpx; font-weight: 700; color: var(--ink); }
.l-s { font-size: 22rpx; color: var(--ink2); margin-top: 8rpx; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.l-a { color: var(--ink2); font-size: 30rpx; }
.none { text-align: center; color: var(--ink2); padding: 100rpx 0; }
</style>
