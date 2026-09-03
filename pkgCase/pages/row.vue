<template>
  <view class="page" :class="theme === 'dark' ? 'tdark' : 'tlight'">
    <view class="hero" v-if="r">
      <view class="r-no serif">#{{ r.n }}</view>
      <view class="r-diag serif">{{ r.diag || '未记诊断' }}</view>
      <view class="r-date" v-if="r.date">{{ r.date }}</view>
      <view class="r-fav" @tap="doFav">{{ fav ? '★' : '☆' }}</view>
    </view>
    <view class="body" v-if="r">
      <view class="kv card fade-in" v-for="f in fields" :key="f.k">
        <view class="k-head">
          <text class="k-orn">▍</text><text class="k-t serif">{{ f.k }}</text>
        </view>
        <view class="k-v" :style="{ fontSize: fs }" :class="{ hl: f.k === '具体方剂' }">{{ f.v }}</view>
      </view>
      <view class="copybar" @tap="copyAll"><image class="ico-s" src="/static/icons/copy-brand.png" />复制本医案</view>
      <view class="src">来源：1257 例结构化医案总表（2005-2009 汉唐中医）</view>
    </view>
    <view class="empty-state" v-if="!r">
    <view class="es-orn serif">空</view>
    <view class="es-t">请从「医案库」选择医案进入</view>
    <view class="es-btn" @tap="goBack">‹ 返回</view>
  </view>
</view>
</template>

<script>
import { store, isFav, toggleFav, pushHistory , applyTheme } from '@/utils/store.js'

const FIELDS = [
  ['patient', '患者'], ['bingji', '中医病机'], ['xiyi', '西医背景'], ['fangji', '具体方剂/治疗组成'],
  ['zhenjiu', '针灸方案'], ['zhifa', '治法原则'], ['result', '疗程/结果'], ['yizhu', '生活医嘱'], ['guandian', '倪师观点']
]

export default {
  onShow() { applyTheme() },
  computed: {
    theme() { return store.theme },
    r() { const x = store.readerItem; return x && x.kind === 'row' ? x.item : null },
    fav() { return this.r ? isFav('casesTable', 'c' + this.r.n) : false },
    fields() {
      const r = this.r
      if (!r) return []
      return FIELDS.filter(([k]) => r[k] && String(r[k]).trim()).map(([k, label]) => ({ k: label, v: r[k] }))
    },
    fs() { return Math.round(25 * (store.fontScale || 1)) + 'rpx' }
  },
  mounted() {
    if (this.r) {
      uni.setNavigationBarTitle({ title: ('#' + this.r.n + ' ' + (this.r.diag || '')).slice(0, 16) , fail: () => {} })
      pushHistory({ f: 'casesTable', i: 'c' + this.r.n, t: `医案#${this.r.n} ${this.r.diag || ''}`, c: 'case' })
    }
  },
  methods: {
    goBack() { uni.navigateBack({ fail: () => uni.switchTab({ url: '/pages/index/index' }) }) },
    copyAll() {
      const r = this.r
      const L = [['编号', '#' + r.n], ['日期', r.date], ['诊断', r.diag], ['患者', r.patient], ['病机', r.bingji], ['西医背景', r.xiyi], ['方剂', r.fangji], ['针灸', r.zhenjiu], ['治法', r.zhifa], ['结果', r.result], ['医嘱', r.yizhu], ['倪师观点', r.guandian]]
      const txt = '【倪师医案】\n' + L.filter(x => x[1]).map(x => x[0] + '：' + x[1]).join('\n') + '\n（倪师经方App · 仅供学习参考）'
      uni.setClipboardData({ data: txt })
    },
    doFav() {
      const r = this.r
      const added = toggleFav({ f: 'casesTable', i: 'c' + r.n, t: `医案#${r.n} ${r.diag || ''}`, s: (r.fangji || '').slice(0, 60), c: 'case' })
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
.hero { position: relative; background: linear-gradient(140deg, var(--hero1), var(--hero2)); padding: 44rpx 36rpx 52rpx; }
.r-no { font-size: 26rpx; color: rgba(253,248,238,.8); letter-spacing: 2rpx; }
.r-diag { font-size: 46rpx; font-weight: 800; color: #FDF8EE; margin-top: 8rpx; letter-spacing: 2rpx; }
.r-date { font-size: 21rpx; color: rgba(253,248,238,.75); margin-top: 10rpx; }
.r-fav { position: absolute; right: 36rpx; top: 44rpx; font-size: 46rpx; color: #F6E7C9; }
.body { margin-top: -26rpx; padding: 0 32rpx; }
.kv { padding: 26rpx 30rpx; margin-bottom: 20rpx; }
.k-head { display: flex; align-items: center; margin-bottom: 12rpx; }
.k-orn { color: var(--brand); }
.k-t { font-size: 27rpx; font-weight: 800; color: var(--ink); margin-left: 8rpx; }
.k-v { font-size: 25rpx; color: var(--ink); line-height: 1.85; text-align: justify; }
.k-v.hl { color: var(--brand); }
.copybar { display: flex; align-items: center; justify-content: center; background: var(--zebra-bg); border: 1rpx solid var(--line); color: var(--brand); border-radius: 40rpx; padding: 18rpx 0; font-size: 25rpx; font-weight: 700; margin-top: 26rpx; }
.copybar .ico-s { margin-right: 10rpx; }
.src { text-align: center; color: var(--ink2); font-size: 20rpx; margin-top: 30rpx; opacity: .75; }
</style>
