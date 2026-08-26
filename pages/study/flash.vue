<template>
  <view class="page" :class="theme === 'dark' ? 'tdark' : 'tlight'">
    <view class="modes">
      <view class="md" :class="{ on: mode === 'fang' }" @tap="switchMode('fang')">经方闪卡</view>
      <view class="md" :class="{ on: mode === 'herb' }" @tap="switchMode('herb')">本草闪卡</view>
      <view class="stat" v-if="mode === 'fang'">已掌握 {{ knownCount }}/{{ total }}</view>
      <view class="stat" v-else>已掌握 {{ knownCount }}/{{ total }}</view>
    </view>

    <view class="card-area" v-if="card">
      <view class="flip" :class="{ flipped }" @tap="flipped = !flipped">
        <view class="face front">
          <view class="f-kicker">{{ mode === 'fang' ? '方剂' : '本草' }}</view>
          <view class="f-name serif">{{ front }}</view>
          <view class="f-hint">轻触卡片翻面{{ mode === 'fang' ? '看组成与主症' : '看性味主治' }}</view>
        </view>
        <view class="face back">
          <view class="f-kicker">{{ backKicker }}</view>
          <scroll-view scroll-y class="b-scroll">
            <view class="b-line" v-for="(l, i) in backLines" :key="i">{{ l }}</view>
          </scroll-view>
        </view>
      </view>
      <view class="acts">
        <view class="act review" @tap="mark(false)">↻ 再复习</view>
        <view class="act known" @tap="mark(true)">✓ 记住了</view>
      </view>
      <view class="pos">{{ idx + 1 }} / {{ total }}</view>
    </view>
    <view class="none" v-if="!card && loaded">本轮完成！已全部过卡或复习队列为空</view>
  </view>
</template>

<script>
import { store, applyTheme } from '@/utils/store.js'
import { loadData } from '@/utils/data.js'

const KEY = 'nx_flash'
export default {
  data() {
    return { mode: 'fang', cards: [], idx: 0, flipped: false, loaded: false, progress: {} }
  },
  computed: {
    theme() { return store.theme },
    total() { return this.queue.length || this.cards.length },
    queue() {
      return this.cards.filter(c => !(this.progress[this.mode + c.id] && this.progress[this.mode + c.id].known))
    },
    card() { return this.queue[this.idx] || null },
    front() { return this.card ? (this.mode === 'fang' ? this.card.n : this.card.n) : '' },
    backKicker() { return this.mode === 'fang' ? '组成 · 主症' : '性味 · 主治' },
    backLines() {
      const c = this.card
      if (!c) return []
      if (this.mode === 'fang') {
        const L = []
        if (c.zhizhi) L.push('【主症】' + c.zhizhi)
        if (c.composition) L.push('【组成】' + c.composition)
        if (c.origin) L.push('【原方】' + c.origin)
        if (c.clinical) L.push('【临床】' + c.clinical)
        return L.length ? L : ['（详见方剂库）']
      }
      const L = []
      if (c['性味']) L.push('【性味】' + c['性味'])
      if (c['主治']) L.push('【主治】' + c['主治'])
      if (c['原文']) L.push('【原文】' + String(c['原文']).slice(0, 90) + '…')
      return L.length ? L : ['（详见本草库）']
    },
    knownCount() { return this.cards.filter(c => this.progress[this.mode + c.id] && this.progress[this.mode + c.id].known).length }
  },
  onShow() {
    applyTheme()
    try { this.progress = uni.getStorageSync(KEY) || {} } catch (e) { this.progress = {} }
    if (!this.loaded) this.load()
  },
  methods: {
    switchMode(m) { this.mode = m; this.idx = 0; this.flipped = false; this.load() },
    async load() {
      try {
        if (this.mode === 'fang') {
          const d = await loadData('formulas')
          const seen = {}
          this.cards = (d.items || []).filter(x => { if (seen[x.n]) return false; seen[x.n] = 1; return true })
        } else {
          const d = await loadData('bencao')
          this.cards = d.herbs || []
        }
        this.loaded = true
        this.idx = 0
      } catch (e) { uni.showToast({ title: '加载失败', icon: 'none' }) }
    },
    mark(known) {
      if (!this.card) return
      this.progress[this.mode + this.card.id] = { known, ts: Date.now() }
      uni.setStorageSync(KEY, this.progress)
      this.flipped = false
      // 记住了：当前卡移出队列，下一张自动顶上（idx 不动）
      // 再复习：卡片保留在队列，跳到下一张
      const len = Math.max(1, this.queue.length - (known ? 1 : 0))
      if (!known) this.idx = (this.idx + 1) % len
      if (this.idx >= len) this.idx = 0
    }
  }
}
</script>

<style scoped>
.page { min-height: 100vh; background: var(--bg); padding: 0 32rpx 80rpx; }
.modes { display: flex; gap: 14rpx; padding: 26rpx 0 22rpx; align-items: center; }
.md { flex-shrink: 0; font-size: 25rpx; color: var(--ink2); background: var(--card); border: 1rpx solid var(--line); border-radius: 30rpx; padding: 12rpx 34rpx; }
.md.on { background: var(--brand); border-color: var(--brand); color: #fff; font-weight: 700; }
.stat { margin-left: auto; font-size: 21rpx; color: var(--gold); }
.card-area { position: relative; }
.flip { position: relative; height: 620rpx; border-radius: 28rpx; perspective: 1200rpx; }
.face { position: absolute; inset: 0; backface-visibility: hidden; -webkit-backface-visibility: hidden; border-radius: 28rpx; display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 44rpx 40rpx; box-shadow: 0 10rpx 40rpx rgba(60,44,22,.1); transition: transform .5s; }
.front { background: linear-gradient(150deg, var(--brand), var(--brand-deep)); }
.back { background: var(--card); transform: rotateY(180deg); justify-content: flex-start; padding-top: 40rpx; }
.flipped .front { transform: rotateY(180deg); }
.flipped .back { transform: rotateY(0); }
.f-kicker { font-size: 20rpx; letter-spacing: 6rpx; opacity: .75; margin-bottom: 24rpx; color: #F6E7C9; }
.back .f-kicker { color: var(--gold); opacity: 1; }
.f-name { font-size: 72rpx; font-weight: 800; color: #FDF8EE; letter-spacing: 6rpx; text-align: center; line-height: 1.4; }
.f-hint { font-size: 21rpx; color: rgba(253,248,238,.7); margin-top: 40rpx; }
.b-scroll { width: 100%; flex: 1; }
.b-line { font-size: 24rpx; color: var(--ink); line-height: 1.9; margin-bottom: 14rpx; text-align: justify; }
.acts { display: flex; gap: 20rpx; margin-top: 28rpx; }
.act { flex: 1; text-align: center; border-radius: 44rpx; padding: 22rpx 0; font-size: 27rpx; font-weight: 700; }
.review { border: 2rpx solid var(--gold); color: var(--gold); }
.known { background: linear-gradient(135deg, #3F6B37, #2F5D62); color: #FDF8EE; }
.pos { text-align: center; color: var(--ink2); font-size: 21rpx; margin-top: 20rpx; }
</style>
