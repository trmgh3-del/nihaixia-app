<template>
  <view class="page" :class="theme === 'dark' ? 'tdark' : 'tlight'">
    <view class="sbar">
      <view class="s-box">
        <image class="ico" src="/static/icons/search-gray.png" />
        <input class="s-input" v-model="q" placeholder="搜文章 / 讲座 / 主题…" />
      </view>
    </view>
    <view class="tabs">
      <view class="tab" :class="{ on: g === '' }" @tap="g = ''">全部 {{ items.length }}</view>
      <view v-for="gg in groups" :key="gg" class="tab" :class="{ on: g === gg }" @tap="g = gg">{{ gg }}</view>
    </view>
    <view class="list">
      <view v-for="it in shown" :key="it.id" class="a-item card fade-in" @tap="open(it)">
        <view class="a-t serif">{{ it.t }}</view>
        <view class="a-meta"><text class="a-src">{{ it.src }}</text></view>
        <view class="a-s">{{ snippet(it) }}</view>
      </view>
      <view v-if="!shown.length" class="none">无匹配文章</view>
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
    return { q: '', g: '', items: [] }
  },
  computed: {
    theme() { return store.theme },
    groups() {
      const s = []
      this.items.forEach(it => { if (it.g && !s.includes(it.g)) s.push(it.g) })
      return s
    },
    shown() {
      let list = this.items
      if (this.g) list = list.filter(it => it.g === this.g)
      const q = this.q.trim()
      if (q) list = list.filter(it => (it.t + (it.b || '') + (it.src || '')).includes(q))
      return list
    }
  },
  mounted() {
    loadData('articles').then(d => { this.items = d.items || [] }).catch(() => {})
  },
  methods: {
    snippet(it) { return (it.b || '').replace(/[#>*`|]/g, '').replace(/\s+/g, ' ').slice(0, 76) },
    open(it) {
      const list = this.shown
      const idx = list.findIndex(x => x.id === it.id)
      openMd({ ...it, f: 'articles' }, it.t, { items: list.map(x => ({ ...x, f: 'articles' })), idx })
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
.a-item { padding: 26rpx 30rpx; margin-bottom: 20rpx; }
.a-t { font-size: 29rpx; font-weight: 800; color: var(--ink); line-height: 1.5; }
.a-meta { margin-top: 8rpx; }
.a-src { font-size: 19rpx; color: var(--gold); background: var(--zebra-bg); border-radius: 8rpx; padding: 3rpx 14rpx; }
.a-s { font-size: 22rpx; color: var(--ink2); margin-top: 12rpx; line-height: 1.6; }
.none { text-align: center; color: var(--ink2); padding: 100rpx 0; }
</style>
