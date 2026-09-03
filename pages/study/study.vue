<template>
  <view class="page" :class="theme === 'dark' ? 'tdark' : 'tlight'">
    <view class="hero">
      <view class="h-t serif">学习中心</view>
      <view class="h-s">背诵 · 速记 · 安全配伍 · 煎法 · 报告 —— 中医功课一站备齐</view>
    </view>

    <view class="grid">
      <view class="g card fade-in" v-for="g in grids" :key="g.k" @tap="go(g.url)">
        <view class="g-ico serif" :style="{ background: g.bg, color: g.fg }">{{ g.ico }}</view>
        <view class="g-main">
          <view class="g-t serif">{{ g.t }}</view>
          <view class="g-d">{{ g.d }}</view>
        </view>
        <text class="g-a">›</text>
      </view>
    </view>

    <view class="tips card">
      <view class="tp-t serif">◈ 今日功课建议</view>
      <view class="tp-li" v-for="(t, i) in tips" :key="i">{{ t }}</view>
    </view>
  </view>
</template>

<script>
import { store, applyTheme } from '@/utils/store.js'

export default {
  data() {
    return {
      grids: [
        { t: '闪卡背诵', ico: '卡', d: '经方 157 方 · 本草 378 味翻卡记忆', bg: '#FBEAE3', fg: '#9A2E1F', url: '/pages/study/flash' },
        { t: '条文背诵', ico: '背', d: '伤寒论条文遮盖填空自测', bg: '#FCF3DC', fg: '#8A6414', url: '/pages/study/recite' },
        { t: '十八反·十九畏', ico: '反', d: '两味药配伍禁忌即查', bg: '#F5E8E8', fg: '#833B3B', url: '/pages/study/compat' },
        { t: '煎药指南', ico: '煎', d: '先煎后下烊化冲服速查', bg: '#E9F1F2', fg: '#2F5D62', url: '/pages/study/decoct' },
        { t: '学习报告', ico: '报', d: '阅读/背诵/打卡成就墙', bg: '#EDE9F4', fg: '#54427C', url: '/pages/study/report' },
        { t: '纳甲法开穴', ico: '开', d: '子午流注按时取穴自动计算', bg: '#FBEAE3', fg: '#9A2E1F', url: '/pages/study/najia' },
        { t: '四诊合参', ico: '诊', d: '望闻问切 → 八纲六经辨证报告', bg: '#FBEAE3', fg: '#9A2E1F', url: '/pages/diagnosis/sizhen' },
        { t: '灵龟八法', ico: '龜', d: '八脉交会穴按时开穴计算', bg: '#E9F1F2', fg: '#2F5D62', url: '/pages/study/linggui' },
        { t: '我的笔记', ico: '记', d: '阅读时记录的学习批注', bg: '#EAF0EE', fg: '#2F5D62', url: '/pages/study/notes' }
      ],
      tips: [
        '晨起（寅时肺经当令）读条文一章，配合条文背诵遮盖自测',
        '午前过闪卡 20 张：先经方后本草，错卡自动进入复习队列',
        '开方前查「十八反·十九畏」，煎药前核对先煎后下',
        '睡前完成六大健康标准自测，观七日趋势'
      ]
    }
  },
  computed: { theme() { return store.theme } },
  onShow() { applyTheme() },
  methods: {
    go(url) { uni.navigateTo({ url }) }
  }
}
</script>

<style scoped>
.page { min-height: 100vh; background: var(--bg); padding-bottom: 70rpx; }
.hero { background: linear-gradient(140deg, var(--hero1), var(--hero2)); padding: 44rpx 36rpx 50rpx; }
.h-t { font-size: 42rpx; font-weight: 800; color: #FDF8EE; letter-spacing: 4rpx; }
.h-s { font-size: 21rpx; color: rgba(253,248,238,.85); margin-top: 12rpx; }
.grid { margin: -30rpx 32rpx 0; position: relative; display: flex; flex-direction: column; gap: 16rpx; }
.g { display: flex; align-items: center; padding: 24rpx 26rpx; }
.g-ico { width: 84rpx; height: 84rpx; border-radius: 20rpx; display: flex; align-items: center; justify-content: center; font-size: 32rpx; font-weight: 800; flex-shrink: 0; }
.g-main { flex: 1; margin-left: 22rpx; min-width: 0; }
.g-t { font-size: 30rpx; font-weight: 800; color: var(--ink); }
.g-d { font-size: 21rpx; color: var(--ink2); margin-top: 6rpx; }
.g-a { color: var(--ink2); font-size: 32rpx; }
.tips { margin: 24rpx 32rpx 0; padding: 24rpx 30rpx; }
.tp-t { font-size: 26rpx; font-weight: 800; color: var(--brand); margin-bottom: 14rpx; }
.tp-li { font-size: 22rpx; color: var(--ink2); line-height: 2; }
</style>
