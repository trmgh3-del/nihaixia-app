<template>
  <view class="page" :class="theme === 'dark' ? 'tdark' : 'tlight'">
    <view class="hero">
      <view class="hero-deco" />
      <view class="h-t serif">学习报告</view>
      <view class="h-s">积跬步以至千里 —— 你的中医功课足迹</view>
      <view class="h-level">
        <view class="lv-ring">
          <view class="lv-inner">
            <view class="lv-num serif">{{ gotCount }}</view>
            <view class="lv-lab">成就</view>
          </view>
        </view>
        <view class="lv-info">
          <view class="lv-title serif">{{ levelTitle }}</view>
          <view class="lv-sub">{{ gotCount }} / {{ badges.length }} 枚徽章已点亮</view>
          <view class="lv-bar"><view class="lv-in" :style="{ width: pct + '%' }" /></view>
        </view>
      </view>
    </view>

    <view class="stats card fade-in">
      <view class="st" v-for="s in statList" :key="s.k">
        <view class="st-n serif" :style="{ color: s.color || 'var(--brand)' }">{{ s.v }}</view>
        <view class="st-k">{{ s.k }}</view>
      </view>
    </view>

    <view class="sec">
      <view class="sec-head">
        <text class="sec-orn">❖</text>
        <text class="sec-title serif">成就墙</text>
        <text class="sec-more">已点亮 {{ gotCount }} 枚</text>
      </view>

      <!-- 已点亮：3列印章 -->
      <view class="earned-title" v-if="earned.length">
        <view class="et-line" />
        <text class="et-txt serif">已 点 亮</text>
        <view class="et-line" />
      </view>
      <view class="badge-grid" v-if="earned.length">
        <view class="bg-item earned" v-for="b in earned" :key="b.k" @tap="showBadge(b)">
          <view class="bg-ring">
            <view class="bg-seal serif">{{ b.seal }}</view>
          </view>
          <view class="bg-t serif">{{ b.t }}</view>
          <view class="bg-d">{{ b.d }}</view>
        </view>
      </view>

      <!-- 未点亮：灰调列表 -->
      <view class="earned-title lock" v-if="locked.length">
        <view class="et-line" />
        <text class="et-txt serif">待 解 锁</text>
        <view class="et-line" />
      </view>
      <view class="locked-list" v-if="locked.length">
        <view class="lk-item" v-for="b in locked" :key="b.k">
          <view class="lk-seal serif">{{ b.seal }}</view>
          <view class="lk-main">
            <view class="lk-t">{{ b.t }}</view>
            <view class="lk-d">{{ b.d }}</view>
          </view>
          <view class="lk-bar">
            <view class="lk-in" :style="{ width: b.progress + '%' }" />
          </view>
          <text class="lk-pct">{{ b.progress }}%</text>
        </view>
      </view>
    </view>

    <view class="quote card">
      <view class="q-mark serif">「</view>
      <view class="q-body serif">中医是化繁为简，看到就知道做什么；不要被病名吓到，看的是证，不是病。</view>
      <view class="q-from">—— 倪师</view>
    </view>
  </view>
</template>

<script>
import { store, applyTheme } from '@/utils/store.js'

export default {
  data() {
    return { readWeek: 0, reciteWeek: 0, flashKnown: 0, healthDays: 0, noteCount: 0, badges: [] }
  },
  computed: {
    theme() { return store.theme },
    favCount() { return store.favorites.length },
    gotCount() { return this.badges.filter(b => b.got).length },
    pct() { return Math.round(this.gotCount / Math.max(1, this.badges.length) * 100) },
    earned() { return this.badges.filter(b => b.got) },
    locked() { return this.badges.filter(b => !b.got) },
    levelTitle() {
      const n = this.gotCount
      if (n >= 8) return '经方宗师'
      if (n >= 6) return '岐黄高手'
      if (n >= 4) return '入门进阶'
      if (n >= 2) return '初窥门径'
      return '蒙学新生'
    },
    statList() {
      return [
        { k: '本周阅读', v: this.readWeek, color: '#9A2E1F' },
        { k: '本周背诵', v: this.reciteWeek, color: '#8A6414' },
        { k: '闪卡掌握', v: this.flashKnown, color: '#3F6B37' },
        { k: '收藏', v: this.favCount, color: '#2F5D62' },
        { k: '打卡', v: this.healthDays, color: '#54427C' },
        { k: '笔记', v: this.noteCount, color: '#833B3B' }
      ]
    }
  },
  onShow() {
    applyTheme()
    this.gather()
  },
  methods: {
    weekKeys() {
      const ks = []
      for (let i = 0; i < 7; i++) {
        const d = new Date(Date.now() - i * 86400000)
        const p = n => (n < 10 ? '0' + n : n)
        ks.push(`${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())}`)
      }
      return ks
    },
    gather() {
      const wk = this.weekKeys()
      this.readWeek = store.history.filter(h => {
        const d = new Date(h.ts)
        const p = n => (n < 10 ? '0' + n : n)
        return wk.includes(`${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())}`)
      }).length
      try {
        const rec = uni.getStorageSync('nx_recite') || {}
        this.reciteWeek = wk.reduce((s, k) => s + (rec[k] || 0), 0)
      } catch (e) { this.reciteWeek = 0 }
      try {
        const fl = uni.getStorageSync('nx_flash') || {}
        this.flashKnown = Object.values(fl).filter(x => x && x.known).length
      } catch (e) { this.flashKnown = 0 }
      try { this.healthDays = (uni.getStorageSync('nx_health') || []).length } catch (e) { this.healthDays = 0 }
      try { this.noteCount = Object.keys(uni.getStorageSync('nx_notes') || {}).length } catch (e) { this.noteCount = 0 }
      const totalRecite = Object.values(uni.getStorageSync('nx_recite') || {}).reduce((s, x) => s + x, 0)
      const flashKnown = this.flashKnown
      const readTotal = store.history.length
      const favN = store.favorites.length
      const healthN = this.healthDays
      // 进度计算（0-100）
      const prog = (cur, target) => Math.min(100, Math.round(cur / target * 100))
      this.badges = [
        { k: 'first', seal: '初', ico: '🌱', t: '初窥门径', d: '完成首次阅读', got: readTotal >= 1, progress: prog(readTotal, 1) },
        { k: 'read50', seal: '读', ico: '📖', t: '手不释卷', d: '累计阅读 50 条', got: readTotal >= 50, progress: prog(readTotal, 50) },
        { k: 'read200', seal: '通', ico: '📚', t: '韦编三绝', d: '累计阅读 200 条', got: readTotal >= 200, progress: prog(readTotal, 200) },
        { k: 'fang10', seal: '方', ico: '🎴', t: '方剂初识', d: '闪卡掌握 10 方', got: flashKnown >= 10, progress: prog(flashKnown, 10) },
        { k: 'fang50', seal: '精', ico: '🏛', t: '方剂入门', d: '闪卡掌握 50 方', got: flashKnown >= 50, progress: prog(flashKnown, 50) },
        { k: 'fang100', seal: '宗', ico: '👑', t: '经方通人', d: '闪卡掌握 100 方', got: flashKnown >= 100, progress: prog(flashKnown, 100) },
        { k: 'recite7', seal: '诵', ico: '🕯', t: '口不绝吟', d: '背诵 7 条条文', got: totalRecite >= 7, progress: prog(totalRecite, 7) },
        { k: 'health7', seal: '康', ico: '💪', t: '起居有常', d: '健康打卡 7 天', got: healthN >= 7, progress: prog(healthN, 7) },
        { k: 'fav10', seal: '藏', ico: '⭐', t: '博采众方', d: '收藏 10 条', got: favN >= 10, progress: prog(favN, 10) }
      ]
    },
    showBadge(b) {
      uni.showToast({ title: `「${b.t}」${b.d}`, icon: 'none', duration: 2000 })
    }
  }
}
</script>

<style scoped>
.page { min-height: 100vh; background: var(--bg); padding-bottom: 70rpx; }

/* Hero + 等级卡 */
.hero { position: relative; overflow: hidden; background: linear-gradient(140deg, var(--hero1), var(--hero2)); padding: 42rpx 36rpx 40rpx; }
.hero-deco { position: absolute; width: 400rpx; height: 400rpx; border-radius: 50%; background: #F6E7C9; opacity: .07; top: -160rpx; right: -100rpx; }
.h-t { font-size: 40rpx; font-weight: 800; color: #FDF8EE; letter-spacing: 3rpx; }
.h-s { font-size: 21rpx; color: rgba(253,248,238,.8); margin-top: 10rpx; }
.h-level { display: flex; align-items: center; margin-top: 30rpx; }
.lv-ring { width: 140rpx; height: 140rpx; border-radius: 50%; border: 5rpx solid rgba(246,231,201,.6); display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.lv-inner { width: 118rpx; height: 118rpx; border-radius: 50%; background: rgba(253,248,238,.12); display: flex; flex-direction: column; align-items: center; justify-content: center; }
.lv-num { font-size: 44rpx; font-weight: 800; color: #FDF8EE; line-height: 1.1; }
.lv-lab { font-size: 18rpx; color: rgba(253,248,238,.75); }
.lv-info { flex: 1; margin-left: 28rpx; }
.lv-title { font-size: 32rpx; font-weight: 800; color: #F6E7C9; letter-spacing: 3rpx; }
.lv-sub { font-size: 19rpx; color: rgba(253,248,238,.75); margin-top: 6rpx; }
.lv-bar { height: 12rpx; background: rgba(253,248,238,.15); border-radius: 8rpx; overflow: hidden; margin-top: 14rpx; }
.lv-in { height: 100%; border-radius: 8rpx; background: linear-gradient(90deg, #C8A45C, #F6E7C9); transition: width .3s; }

/* 统计卡 */
.stats { margin: 24rpx 32rpx 0; display: flex; flex-wrap: wrap; padding: 26rpx 10rpx 14rpx; }
.st { width: 33.33%; text-align: center; margin-bottom: 16rpx; }
.st-n { font-size: 38rpx; font-weight: 800; }
.st-k { font-size: 20rpx; color: var(--ink2); margin-top: 4rpx; }

/* 成就墙 */
.sec { margin: 30rpx 32rpx 0; }
.sec-head { display: flex; align-items: center; margin-bottom: 20rpx; }
.sec-orn { color: var(--gold); font-size: 22rpx; margin-right: 10rpx; }
.sec-title { font-size: 30rpx; font-weight: 800; color: var(--ink); letter-spacing: 2rpx; }
.sec-more { margin-left: auto; font-size: 20rpx; color: var(--ink2); }

.earned-title { display: flex; align-items: center; margin: 24rpx 0 18rpx; }
.et-line { flex: 1; height: 1rpx; background: var(--gold); opacity: .4; }
.et-txt { font-size: 22rpx; color: var(--gold); letter-spacing: 8rpx; margin: 0 20rpx; }
.earned-title.lock .et-line { background: var(--ink2); opacity: .2; }
.earned-title.lock .et-txt { color: var(--ink2); opacity: .6; }

/* 已点亮：3列印章网格 */
.badge-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 16rpx; }
.bg-item { display: flex; flex-direction: column; align-items: center; padding: 24rpx 10rpx 20rpx; background: var(--card); border: 1rpx solid var(--gold); border-radius: 20rpx; position: relative; min-width: 0; }
.bg-item.earned::after { content: ''; position: absolute; inset: 5rpx; border: 1rpx dashed rgba(200,164,92,.3); border-radius: 15rpx; pointer-events: none; }
.bg-ring { width: 100rpx; height: 100rpx; border-radius: 50%; border: 4rpx solid var(--gold); background: linear-gradient(140deg, rgba(200,164,92,.08), rgba(154,46,31,.06)); display: flex; align-items: center; justify-content: center; }
.bg-seal { font-size: 44rpx; font-weight: 800; color: var(--brand); }
.bg-t { font-size: 24rpx; font-weight: 800; color: var(--ink); margin-top: 14rpx; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 100%; }
.bg-d { font-size: 17rpx; color: var(--ink2); margin-top: 4rpx; text-align: center; line-height: 1.5; }

/* 未点亮：带进度条列表 */
.locked-list { display: flex; flex-direction: column; gap: 14rpx; }
.lk-item { display: flex; align-items: center; background: var(--card); border: 1rpx solid var(--line); border-radius: 18rpx; padding: 18rpx 24rpx; opacity: .75; }
.lk-seal { width: 64rpx; height: 64rpx; border-radius: 50%; border: 3rpx solid var(--line); color: var(--ink2); opacity: .5; font-size: 28rpx; font-weight: 800; display: flex; align-items: center; justify-content: center; margin-right: 20rpx; flex-shrink: 0; }
.lk-main { flex: 1; min-width: 0; }
.lk-t { font-size: 25rpx; font-weight: 700; color: var(--ink); }
.lk-d { font-size: 18rpx; color: var(--ink2); margin-top: 2rpx; }
.lk-bar { width: 120rpx; height: 10rpx; background: var(--zebra-bg); border-radius: 6rpx; overflow: hidden; margin-left: 16rpx; flex-shrink: 0; }
.lk-in { height: 100%; border-radius: 6rpx; background: var(--gold); opacity: .7; }
.lk-pct { width: 64rpx; text-align: right; font-size: 17rpx; color: var(--ink2); flex-shrink: 0; margin-left: 8rpx; }

/* 寄语 */
.quote { margin: 30rpx 32rpx 0; padding: 30rpx 34rpx; background: linear-gradient(135deg, var(--quote-bg), var(--card)); position: relative; overflow: hidden; }
.q-mark { position: absolute; left: 18rpx; top: 2rpx; font-size: 80rpx; color: var(--gold); opacity: .3; }
.q-body { font-size: 25rpx; color: var(--ink); line-height: 1.9; letter-spacing: 1rpx; text-align: justify; position: relative; }
.q-from { text-align: right; font-size: 19rpx; color: var(--gold); margin-top: 12rpx; }
</style>
