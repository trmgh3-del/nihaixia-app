<template>
  <view class="page" :class="theme === 'dark' ? 'tdark' : 'tlight'">
    <view class="hero">
      <view class="h-t serif">倪氏六大健康标准</view>
      <view class="h-s">倪师：此六项俱佳者，阳足胃气旺，百病难侵 —— 每日一测，观其趋势</view>
    </view>

    <view class="sec card fade-in">
      <view class="item" v-for="it in items" :key="it.k">
        <view class="i-head">
          <text class="i-k serif">{{ it.k }}</text>
          <text class="i-good">{{ it.opts[0] }}</text>
        </view>
        <view class="i-opts">
          <view v-for="(o, i) in it.opts" :key="i" class="i-opt" :class="{ on: picked[it.k] === i, bad: i === 2 }" @tap="pick(it.k, i)">{{ o }}</view>
        </view>
        <view class="i-tip" v-if="picked[it.k] === 2 && tips[it.k]">⚠ {{ tips[it.k] }}</view>
      </view>
      <view class="go" :class="{ dis: !done }" @tap="submit">{{ done ? '记录今日健康' : '请完成六项勾选' }}</view>
    </view>

    <view class="trend card fade-in" v-if="history.length">
      <view class="tr-t serif">⟡ 近 7 日趋势 <text class="tr-avg">均分 {{ avg }}</text></view>
      <view class="tr-bars">
        <view class="tb-col" v-for="h in history" :key="h.date">
          <view class="tb-bar" :style="{ height: barH(h.total), background: h.total <= 2 ? '#3F6B37' : h.total <= 5 ? '#C8A45C' : '#9A2E1F' }" />
          <view class="tb-n">{{ h.total }}</view>
          <view class="tb-d">{{ h.date.slice(5) }}</view>
        </view>
      </view>
      <view class="tr-legend">0-2 阳足 · 3-5 注意 · 6+ 需重视</view>
    </view>

    <view class="std card">
      <view class="std-t serif">倪师六标准 · 原文口径</view>
      <view class="std-li" v-for="(v, i) in std" :key="i">● {{ v }}</view>
    </view>
    <view class="warn">⚠ 自测仅供养生参考：分数高或单项持续异常（尤其手足厥冷、彻夜不眠、完谷不化）请及时就医；急重症立即就医。</view>
  </view>
</template>

<script>
import { store, applyTheme } from '@/utils/store.js'

/* 源自 SKILL「倪氏六健康标准」+ 倪师口述 */
const ITEMS = [
  { k: '睡眠', opts: ['一夜到天亮', '易醒/入睡难', '彻夜难眠或嗜睡'] },
  { k: '胃口', opts: ['饥饱有度食量正常', '胃口差或亢进', '毫无胃口/食入即吐'] },
  { k: '大便', opts: ['晨起成形一次', '偏秘或偏溏', '多日不便或下利清谷'] },
  { k: '小便', opts: ['淡黄通畅', '深黄或尿频', '癃闭或夜尿频频'] },
  { k: '手足温度', opts: ['手脚常年温热', '脚凉手温', '手冷至肘脚冷至膝'] },
  { k: '汗', opts: ['运动才见汗', '静坐自汗或盗汗', '大汗不止或无汗身痛'] }
]
const TIPS = {
  '睡眠': '彻夜难眠多属阴虚火旺或里有实邪；但欲寐嗜睡当查少阴。',
  '胃口': '胃气为生死关键——毫无胃口是胃气将绝之兆，亟需重视。',
  '大便': '下利清谷（完谷不化）为里寒重症，太阴少阴方向。',
  '小便': '小便癃闭责之于肾与膀胱气化；夜尿频多属下焦虚寒。',
  '手足温度': '倪师：脚是冷的就定义成「寒」——小肠火不足；手冷至肘、脚冷至膝为四逆证。',
  '汗': '静坐自汗为表阳不固（炮附子证）；大汗不止防亡阳。'
}

export default {
  data() {
    return {
      items: ITEMS,
      tips: TIPS,
      picked: {},
      history: [],
      std: [
        '一、睡眠：一夜睡到天亮（睡眠中断需辨经）',
        '二、胃口：正常饥饱感、食量稳定',
        '三、大便：每日晨起一次、成形',
        '四、小便：颜色淡黄、小便通畅',
        '五、手足温度：手脚常年温热（脚冷即寒）',
        '六、汗：平常无汗，运动或天热才汗；汗流头面独多者为虚'
      ]
    }
  },
  computed: {
    theme() { return store.theme },
    done() { return ITEMS.every(it => this.picked[it.k] !== undefined) },
    avg() {
      if (!this.history.length) return '—'
      return (this.history.reduce((s, h) => s + h.total, 0) / this.history.length).toFixed(1)
    }
  },
  onShow() {
    applyTheme()
    try { this.history = (uni.getStorageSync('nx_health') || []).slice(-7) } catch (e) { this.history = [] }
  },
  methods: {
    pick(k, i) { this.picked[k] = i },
    submit() {
      if (!this.done) return
      const total = ITEMS.reduce((s, it) => s + this.picked[it.k], 0)
      const today = new Date()
      const p = n => (n < 10 ? '0' + n : n)
      const date = `${today.getFullYear()}-${p(today.getMonth() + 1)}-${p(today.getDate())}`
      const list = (this.history || []).filter(h => h.date !== date)
      list.push({ date, total, items: { ...this.picked } })
      this.history = list.slice(-7)
      uni.setStorageSync('nx_health', list.slice(-30))
      const msg = total <= 2 ? '阳足胃气旺，甚佳！' : total <= 5 ? '略有偏差，注意起居饮食' : '多项异常，建议就诊调理'
      uni.showModal({ title: `今日 ${total} 分`, content: msg + (total >= 6 ? '；尤其手足温度与胃口两项为倪师最重之指标。' : ''), showCancel: false, confirmText: '知道了' })
    },
    barH(total) {
      return Math.max(12, 22 - total * 6) + '%'
    }
  }
}
</script>

<style scoped>
.page { min-height: 100vh; background: var(--bg); padding-bottom: 80rpx; }
.hero { background: linear-gradient(140deg, var(--hero1), var(--hero2)); padding: 40rpx 36rpx 44rpx; }
.h-t { font-size: 40rpx; font-weight: 800; color: #FDF8EE; letter-spacing: 3rpx; }
.h-s { font-size: 21rpx; color: rgba(253,248,238,.85); margin-top: 12rpx; line-height: 1.7; }
.sec { margin: -28rpx 32rpx 0; position: relative; padding: 10rpx 30rpx 30rpx; }
.item { padding: 24rpx 0; border-bottom: 1rpx solid var(--line); }
.item:last-of-type { border-bottom: none; }
.i-head { display: flex; align-items: baseline; }
.i-k { font-size: 29rpx; font-weight: 800; color: var(--ink); }
.i-good { margin-left: auto; font-size: 19rpx; color: #3F6B37; background: #E8F0E4; border-radius: 8rpx; padding: 3rpx 14rpx; }
.i-opts { display: flex; gap: 12rpx; margin-top: 16rpx; }
.i-opt { flex: 1; text-align: center; font-size: 21rpx; color: var(--ink2); background: var(--zebra-bg); border: 2rpx solid transparent; border-radius: 14rpx; padding: 14rpx 4rpx; }
.i-opt.on { border-color: var(--brand); color: var(--brand); font-weight: 700; background: rgba(154,46,31,.05); }
.i-opt.on.bad { border-color: #833B3B; color: #833B3B; background: rgba(131,59,59,.06); }
.i-tip { margin-top: 12rpx; font-size: 20rpx; color: #833B3B; background: #F5E8E8; border-radius: 10rpx; padding: 12rpx 18rpx; line-height: 1.7; }
.go { margin-top: 26rpx; background: linear-gradient(135deg, var(--brand), var(--brand-deep)); color: #FDF8EE; text-align: center; border-radius: 44rpx; padding: 24rpx 0; font-size: 28rpx; font-weight: 700; letter-spacing: 2rpx; }
.go.dis { opacity: .45; }
.trend { margin: 24rpx 32rpx 0; padding: 26rpx 30rpx; }
.tr-t { font-size: 28rpx; font-weight: 800; color: var(--brand); margin-bottom: 20rpx; }
.tr-avg { font-size: 20rpx; color: var(--ink2); font-weight: 400; margin-left: 14rpx; }
.tr-bars { display: flex; align-items: flex-end; height: 200rpx; gap: 10rpx; }
.tb-col { flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: flex-end; height: 100%; }
.tb-bar { width: 60%; border-radius: 10rpx 10rpx 4rpx 4rpx; min-height: 14rpx; }
.tb-n { font-size: 19rpx; color: var(--ink2); margin-top: 6rpx; }
.tb-d { font-size: 16rpx; color: var(--ink2); opacity: .75; }
.tr-legend { margin-top: 16rpx; font-size: 18rpx; color: var(--ink2); text-align: center; }
.std { margin: 24rpx 32rpx 0; padding: 24rpx 30rpx; }
.std-t { font-size: 26rpx; font-weight: 800; color: var(--ink); margin-bottom: 14rpx; }
.std-li { font-size: 22rpx; color: var(--ink2); line-height: 2; }
.warn { margin: 24rpx 32rpx 0; font-size: 20rpx; color: #A2651B; background: #FCF3DC; border-radius: 12rpx; padding: 16rpx 22rpx; line-height: 1.7; }
</style>
