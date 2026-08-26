<template>
  <view class="page" :class="theme === 'dark' ? 'tdark' : 'tlight'">
    <view class="sbar">
      <view class="s-box">
        <image class="ico" src="/static/icons/search-gray.png" />
        <input class="s-input" v-model="q" placeholder="搜药名 / 性味 / 主治…" />
      </view>
    </view>
    <view class="tabs">
      <view class="tab" :class="{ on: g === '' }" @tap="g = ''">全部 {{ herbs.length }}</view>
      <view class="tab" :class="{ on: g === '上经' }" @tap="g = '上经'">上经 {{ count('上经') }}</view>
      <view class="tab" :class="{ on: g === '中经' }" @tap="g = '中经'">中经 {{ count('中经') }}</view>
      <view class="tab" :class="{ on: g === '下经' }" @tap="g = '下经'">下经 {{ count('下经') }}</view>
      <view class="tab" :class="{ on: g === 'intro' }" @tap="g = 'intro'">药性总义</view>
    </view>

    <view v-if="g === 'intro'" class="list">
      <view v-for="it in intro" :key="it.id" class="l-item card fade-in" @tap="openIntro(it)">
        <view class="l-t">{{ it.t }}</view>
        <view class="l-s">{{ snippet(it.b) }}</view>
        <text class="l-a">›</text>
      </view>
    </view>
    <view class="xwbar" v-if="g !== 'intro'">
      <view class="xw-chip" :class="{ on: xw === '' }" @tap="xw = ''">性味不限</view>
      <view v-for="x in xws" :key="x" class="xw-chip" :class="{ on: xw === x }" @tap="xw = xw === x ? '' : x">{{ x }}</view>
    </view>
    <scroll-view v-if="g !== 'intro'" scroll-y class="herbs">
      <view class="h-grid">
        <view v-for="h in shown" :key="h.id" class="h-card card fade-in" @tap="open(h)">
          <view class="h-name serif">{{ h.n }}</view>
          <view class="h-tag" :class="gradeClass(h.g)">{{ h.g }}</view>
          <view class="h-xw" v-if="h['性味']">{{ h['性味'] }}</view>
          <view class="h-zz">{{ (h['主治'] || h['原文'] || '').slice(0, 40) }}</view>
        </view>
      </view>
      <view v-if="!shown.length" class="none">无匹配药物</view>
    </scroll-view>
  </view>
</template>

<script>
import { store , applyTheme } from '@/utils/store.js'
import { loadData } from '@/utils/data.js'
import { openMd } from '@/utils/routes.js'

export default {
  onShow() { applyTheme() },
  data() {
    return { q: '', g: '', herbs: [], intro: [], xw: '', xws: ['寒', '热', '温', '凉', '平', '有毒'] }
  },
  computed: {
    theme() { return store.theme },
    shown() {
      let list = this.herbs
      if (this.g) list = list.filter(h => h.g === this.g)
      if (this.xw) {
        const xw = this.xw
        list = list.filter(h => (h['性味'] || '').includes(xw) || (h.natureCategory || '').includes(xw) || (h['原文'] || '').slice(0, 30).includes('味' + xw))
      }
      const q = this.q.trim()
      if (q) {
        list = list.filter(h => (h.n + (h.canonicalName || '') + (h.g || '') + (h.category || '') + (h.natureCategory || '') + (h.flavor || '') + (h.meridians || []).join('') + (h.aliases || []).join('') + (h['性味'] || '') + (h['主治'] || '') + (h['原文'] || '') + (h['倪注'] || '')).includes(q))
      }
      return list
    }
  },
  mounted() {
    loadData('bencao').then(d => {
      this.herbs = d.herbs || []
      this.intro = d.intro || []
    }).catch(() => {})
  },
  methods: {
    count(g) { return this.herbs.filter(h => h.g === g).length },
    gradeClass(g) { return g === '上经' ? 'up' : g === '中经' ? 'mid' : 'down' },
    snippet(b) { return (b || '').replace(/[#>*`|]/g, '').replace(/\s+/g, ' ').slice(0, 60) },
    open(h) {
      store.readerItem = { kind: 'herb', item: h }
      uni.navigateTo({ url: '/pkgBencao/pages/herb' })
    },
    openIntro(it) { openMd({ ...it, f: 'bencao' }, it.t) }
  }
}
</script>

<style scoped>
.page { height: 100vh; display: flex; flex-direction: column; background: var(--bg); }
.sbar { padding: 22rpx 32rpx; background: var(--card); flex-shrink: 0; }
.s-box { display: flex; align-items: center; background: var(--zebra-bg); border-radius: 38rpx; padding: 0 28rpx; height: 74rpx; }
.s-ico { margin-right: 14rpx; font-size: 26rpx; }
.s-input { flex: 1; font-size: 26rpx; color: var(--ink); }
.tabs { display: flex; background: var(--card); padding: 0 20rpx 20rpx; gap: 10rpx; flex-shrink: 0; }
.tab { text-align: center; font-size: 22rpx; padding: 12rpx 0; border-radius: 28rpx; background: var(--zebra-bg); color: var(--ink2); flex: 1; }
.tab.on { background: var(--brand); color: #fff; font-weight: 700; }
.herbs { flex: 1; }
.h-grid { display: flex; flex-wrap: wrap; padding: 24rpx 20rpx 60rpx; }
.h-card { width: 46.5%; margin: 1.5%; padding: 24rpx; box-sizing: border-box; position: relative; }
.h-name { font-size: 32rpx; font-weight: 800; color: var(--ink); }
.xwbar { display: flex; flex-wrap: wrap; padding: 4rpx 24rpx 16rpx; background: var(--card); flex-shrink: 0; }
.xw-chip { font-size: 21rpx; color: var(--ink2); background: var(--zebra-bg); border-radius: 24rpx; padding: 8rpx 24rpx; margin: 0 12rpx 10rpx 0; }
.xw-chip.on { background: var(--brand); color: #fff; }
.h-tag { position: absolute; top: 22rpx; right: 22rpx; font-size: 18rpx; border-radius: 8rpx; padding: 3rpx 12rpx; }
.h-tag.up { background: #FBEAE3; color: #9A2E1F; }
.h-tag.mid { background: #FCF3DC; color: #8A6414; }
.h-tag.down { background: #E8F0E4; color: #3F6B37; }
.h-xw { font-size: 21rpx; color: var(--gold); margin-top: 8rpx; }
.h-zz { font-size: 21rpx; color: var(--ink2); margin-top: 6rpx; line-height: 1.5; height: 96rpx; overflow: hidden; }
.list { padding: 24rpx 32rpx 0; }
.l-item { display: flex; align-items: center; padding: 28rpx 30rpx; margin-bottom: 20rpx; }
.l-t { font-size: 28rpx; font-weight: 700; color: var(--ink); flex: 1; }
.l-s { font-size: 21rpx; color: var(--ink2); flex: 2; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; margin-left: 20rpx; }
.l-a { color: var(--ink2); margin-left: 12rpx; }
.none { text-align: center; color: var(--ink2); padding: 100rpx 0; }
</style>
