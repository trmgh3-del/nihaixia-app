<template>
  <view class="page" :class="theme === 'dark' ? 'tdark' : 'tlight'">
    <view class="hero" v-if="h">
      <view class="h-name serif">{{ h.n }}</view>
      <view class="h-flags">
        <view class="h-tag" :class="gradeClass">{{ h.g }}</view>
        <view class="h-fav" @tap="doFav">{{ fav ? '★' : '☆' }}</view>
      </view>
    </view>

    <view class="body" v-if="h">
      <view class="kv card fade-in" v-for="f in fields" :key="f.k">
        <view class="k-head">
          <text class="k-orn">▍</text>
          <text class="k-t serif">{{ f.k }}</text>
        </view>
        <view class="k-v" :style="{ fontSize: fs }">{{ f.v }}</view>
      </view>

      <view class="related card fade-in" v-if="relatedFormulas.length">
        <view class="k-head"><text class="k-orn">▍</text><text class="k-t serif">含此药材的方剂</text></view>
        <view class="related-item" v-for="f in relatedFormulas" :key="f.id" @tap="openFormula(f)"><text>{{ f.n }}</text><text class="related-arrow">›</text></view>
      </view>
      <view class="kv card fade-in" v-if="h['口述']">
        <view class="k-head">
          <text class="k-orn">▍</text>
          <text class="k-t serif">倪师临床口述</text>
          <text class="k-badge">视频讲义</text>
        </view>
        <view class="k-v oral" :style="{ fontSize: fs }">{{ h['口述'] }}</view>
      </view>

      <view class="r-foot"><text>—— 神农本草经 · 人纪 ——</text></view>
    </view>
    <view class="empty-state" v-if="!h">
    <view class="es-orn serif">空</view>
    <view class="es-t">请从「神农本草」列表选择药物进入</view>
    <view class="es-btn" @tap="goBack">‹ 返回</view>
  </view>
</view>
</template>

<script>
import { store, isFav, toggleFav, pushHistory , applyTheme } from '@/utils/store.js'
import { loadData } from '@/utils/data.js'

export default {
  onShow() { applyTheme() },
  data() {
    return { favState: false, relatedFormulas: [] }
  },
  computed: {
    theme() { return store.theme },
    h() { const r = store.readerItem; return r && r.kind === 'herb' ? r.item : null },
    fav() { return this.h ? isFav('bencao', this.h.id) : false },
    fields() {
      const h = this.h
      if (!h) return []
      const extra = []
      if (h.canonicalName && h.canonicalName !== h.n) extra.push({ k: '正名', v: h.canonicalName })
      if (h.processing) extra.push({ k: '炮制', v: h.processing })
      if (h.natureCategory) extra.push({ k: '性味分类', v: h.natureCategory })
      if (h.flavor) extra.push({ k: '五味', v: h.flavor })
      if (h.meridians && h.meridians.length) extra.push({ k: '归经', v: h.meridians.join('、') })
      if (h.aliases && h.aliases.length) extra.push({ k: '别名', v: h.aliases.join('、') })
      return extra.concat(['原文', '性味', '主治', '倪注', '容川', '用量', '禁忌', '补注']
        .filter(k => h[k] && String(h[k]).trim())
        .map(k => ({ k, v: h[k] })))
    },
    gradeClass() { return this.h && this.h.g === '上经' ? 'up' : this.h && this.h.g === '中经' ? 'mid' : 'down' },
    fs() { return Math.round(26 * (store.fontScale || 1)) + 'rpx' }
  },
  mounted() {
    if (this.h) {
      uni.setNavigationBarTitle({ title: this.h.n , fail: () => {} })
      pushHistory({ f: 'bencao', i: this.h.id, t: this.h.n, c: 'herb' })
      loadData('formulas').then(d => {
        const name = this.h.n
        const names = [name, this.h.canonicalName, ...(this.h.aliases || [])].filter(Boolean)
        this.relatedFormulas = (d.items || []).filter(f => {
          const hasComponent = (f.components || []).some(c => names.includes(c.name))
          const textHit = names.some(n => String(f.composition || f.origin || '').includes(n))
          return hasComponent || textHit
        }).slice(0, 8)
      }).catch(() => {})
    }
  },
  methods: {
    goBack() { uni.navigateBack({ fail: () => uni.switchTab({ url: '/pages/index/index' }) }) },
    openFormula(f) {
      store.readerItem = { kind: 'formula', item: f }
      uni.navigateTo({ url: '/pkgFormula/pages/detail' })
    },
    doFav() {
      const added = toggleFav({ f: 'bencao', i: this.h.id, t: this.h.n, s: (this.h['主治'] || '').slice(0, 60), c: 'herb' })
      uni.showToast({ title: added ? '已收藏' : '已取消', icon: 'none' })
    }
  }
}
</script>

<style scoped>
.empty-state { display: flex; flex-direction: column; align-items: center; padding: 220rpx 60rpx; }
.es-orn { width: 120rpx; height: 120rpx; border: 4rpx solid var(--line); border-radius: 24rpx; color: var(--gold); opacity: .5; font-size: 52rpx; font-weight: 800; display: flex; align-items: center; justify-content: center; }
.es-t { font-size: 25rpx; color: var(--ink2); margin-top: 30rpx; }
.es-btn { margin-top: 40rpx; font-size: 24rpx; color: var(--brand); border: 2rpx solid var(--brand); border-radius: 40rpx; padding: 12rpx 60rpx; font-weight: 700; }
.page { min-height: 100vh; background: var(--bg); padding-bottom: 60rpx; }
.hero { background: linear-gradient(140deg, var(--hero1), var(--hero2)); padding: 44rpx 36rpx 52rpx; display: flex; align-items: center; }
.h-name { font-size: 54rpx; font-weight: 800; color: #FDF8EE; letter-spacing: 4rpx; }
.h-flags { margin-left: auto; display: flex; align-items: center; }
.h-tag { font-size: 22rpx; border-radius: 10rpx; padding: 6rpx 18rpx; background: rgba(253,248,238,.2); color: #FDF8EE; border: 1rpx solid rgba(253,248,238,.5); }
.h-fav { margin-left: 20rpx; font-size: 44rpx; color: #F6E7C9; }
.body { margin-top: -26rpx; padding: 0 32rpx; }
.related { padding: 24rpx 30rpx; margin-bottom: 22rpx; }
.related-item { display: flex; justify-content: space-between; border-top: 1rpx dashed var(--line); padding: 14rpx 0; color: var(--brand); font-size: 23rpx; }
.related-arrow { font-size: 28rpx; color: var(--ink2); }
.kv { padding: 28rpx 30rpx; margin-bottom: 22rpx; }
.k-head { display: flex; align-items: center; margin-bottom: 14rpx; }
.k-orn { color: var(--brand); font-size: 26rpx; }
.k-t { font-size: 29rpx; font-weight: 800; color: var(--ink); margin-left: 10rpx; }
.k-badge { margin-left: auto; font-size: 19rpx; color: var(--gold); border: 1rpx solid var(--gold); border-radius: 8rpx; padding: 2rpx 12rpx; }
.k-v { font-size: 26rpx; color: var(--ink); line-height: 1.9; text-align: justify; }
.oral { color: var(--ink2); background: var(--quote-bg); border-radius: 14rpx; padding: 20rpx 24rpx; }
.r-foot { text-align: center; color: var(--gold); font-size: 21rpx; margin: 40rpx 0; letter-spacing: 4rpx; }
</style>
