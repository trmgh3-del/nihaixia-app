<template>
  <view class="page" :class="theme === 'dark' ? 'tdark' : 'tlight'">
    <view class="hero"><view class="hero-title serif">历史辨证报告</view><view class="hero-sub">四诊合参 · 知识库驱动学习记录</view></view>
    <view class="report card" v-if="report">
      <view class="report-time">{{ formatTime(report.ts) }}</view>
      <text class="report-text">{{ report.text }}</text>
      <view class="actions"><view class="btn main" @tap="copy">复制完整报告</view><view class="btn" v-if="history.length" @tap="comparePrevious">对比上一份</view><view class="btn" @tap="restore">恢复为当前问诊</view><view class="btn" @tap="goBack">返回</view></view>
    </view>
    <view class="empty" v-else>未找到历史报告</view>
  </view>
</template>
<script>
import { store, applyTheme } from '@/utils/store.js'
export default {
  data() { return { report: null, history: [] } },
  computed: { theme() { return store.theme } },
  onShow() { applyTheme(); this.report = store.sizhenReport || null; try { this.history = (uni.getStorageSync('nx_sizhen_reports') || []).filter(x => !this.report || x.ts !== this.report.ts).slice(0, 10) } catch (e) { this.history = [] } },
  methods: {
    formatTime(ts) { return ts ? new Date(ts).toLocaleString() : '' },
    copy() { if (this.report) uni.setClipboardData({ data: this.report.text, success: () => uni.showToast({ title: '报告已复制', icon: 'none' }) }) },
    comparePrevious() {
      const prev = this.history[0]
      if (!prev || !this.report) return
      const a = this.report.result || {}; const b = prev.result || {}
      const lines = ['当前报告：' + (a.meridians || []).join('、') + ' / ' + ((a.risk && a.risk.label) || '未知'), '上一报告：' + (b.meridians || []).join('、') + ' / ' + ((b.risk && b.risk.label) || '未知'), '六经变化：' + ((b.meridians || []).join('、') || '无') + ' → ' + ((a.meridians || []).join('、') || '无'), '风险变化：' + ((b.risk && b.risk.label) || '未知') + ' → ' + ((a.risk && a.risk.label) || '未知')]
      uni.showModal({ title: '与上一份报告对比', content: lines.join('\\n'), showCancel: false, confirmText: '关闭' })
    },
    restore() {
      if (!this.report || !this.report.pick) { uni.showToast({ title: '该报告没有可恢复的采集记录', icon: 'none' }); return }
      uni.setStorageSync('nx_sizhen_draft', { ts: Date.now(), pick: this.report.pick, basic: this.report.basic || {}, redFlags: this.report.redFlags || [], pulseSource: this.report.pulseSource || '不确定', step: 0 })
      uni.navigateTo({ url: '/pages/diagnosis/sizhen' })
    },
    goBack() { uni.navigateBack({ fail: () => uni.switchTab({ url: '/pages/diagnosis/diagnosis' }) }) }
  }
}
</script>
<style scoped>
.page { min-height: 100vh; background: var(--bg); padding-bottom: 80rpx; }
.hero { background: linear-gradient(140deg, var(--hero1), var(--hero2)); padding: 42rpx 36rpx 48rpx; color: #FDF8EE; }
.hero-title { font-size: 42rpx; font-weight: 800; }.hero-sub { font-size: 21rpx; margin-top: 12rpx; opacity: .8; }
.report { margin: -24rpx 32rpx 0; position: relative; padding: 28rpx; }
.report-time { color: var(--ink2); font-size: 20rpx; padding-bottom: 18rpx; border-bottom: 1rpx solid var(--line); }
.report-text { display: block; white-space: pre-wrap; color: var(--ink); font-size: 24rpx; line-height: 1.85; margin-top: 18rpx; }
.actions { display: flex; gap: 14rpx; margin-top: 26rpx; }.btn { flex: 1; text-align: center; border: 2rpx solid var(--brand); color: var(--brand); border-radius: 40rpx; padding: 20rpx 0; font-size: 24rpx; }.btn.main { background: var(--brand); color: #fff; }.empty { text-align: center; color: var(--ink2); padding: 180rpx 0; }
</style>
