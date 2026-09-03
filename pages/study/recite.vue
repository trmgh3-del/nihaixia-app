<template>
  <view class="page" :class="theme === 'dark' ? 'tdark' : 'tlight'">
    <view class="ctrl">
      <view class="c-mode" :class="{ on: mode === 'blank' }" @tap="mode = 'blank'">遮盖填空</view>
      <view class="c-mode" :class="{ on: mode === 'full' }" @tap="mode = 'full'">原文对照</view>
      <view class="c-stat">今日 {{ todayCount }} 条</view>
    </view>

    <view class="rec card fade-in" v-if="cur">
      <view class="r-src">{{ cur.src }}</view>
      <view class="r-title serif">{{ cur.title }}</view>
      <view class="r-text serif" v-if="mode === 'full'">{{ cur.text }}</view>
      <view class="r-text serif" v-else>
        <text v-for="(seg, i) in blankSegs" :key="i">{{ seg.text }}<text v-if="seg.blank" class="blank" :class="{ show: revealed[i] }" @tap="reveal(i)">{{ revealed[i] ? seg.v : '　'.repeat(Math.max(2, seg.v.length)) }}</text></text>
      </view>
      <view class="r-hint" v-if="mode === 'blank'">点击空格显示答案 · 共 {{ blankCount }} 处遮盖</view>
      <view class="r-textquote" v-if="cur.note">{{ cur.note }}</view>
    </view>

    <view class="acts">
      <view class="act" @tap="prev">‹ 上一条</view>
      <view class="act main" @tap="next">背过了，下一条 ›</view>
    </view>
    <view class="pos">{{ idx + 1 }} / {{ items.length }}</view>
    <view class="warn">条文文本取自人纪伤寒论讲义（太阳篇 1-129 与下篇补齐 138-276）；背诵以理解为要，方证对应见辨证中心。</view>
  </view>
</template>

<script>
import { store, applyTheme } from '@/utils/store.js'
import { loadData } from '@/utils/data.js'

/* 核心背诵条文池：主证条文 + 关键方证条文（从讲义原文摘录） */
const POOL = [
  { title: '太阳病总纲', src: '伤寒论·第1条', text: '太阳之为病，脉浮，头项强痛而恶寒。' },
  { title: '中风', src: '伤寒论·第2条', text: '太阳病，发热，汗出，恶风，脉缓者，名为中风。' },
  { title: '伤寒', src: '伤寒论·第3条', text: '太阳病，或已发热，或未发热，必恶寒，体痛，呕逆，脉阴阳俱紧者，名为伤寒。' },
  { title: '桂枝汤主证', src: '伤寒论·第12条', text: '太阳中风，阳浮而阴弱，阳浮者热自发，阴弱者汗自出，啬啬恶寒，淅淅恶风，翕翕发热，鼻鸣干呕者，桂枝汤主之。' },
  { title: '桂枝汤服法', src: '伤寒论·第12条', text: '服已须臾，啜热稀粥一升余，以助药力，温覆令一时许，遍身漐漐微似有汗者益佳，不可令如水流离，病必不除。' },
  { title: '麻黄汤主证', src: '伤寒论·第35条', text: '太阳病，头痛发热，身疼腰痛，骨节疼痛，恶风，无汗而喘者，麻黄汤主之。' },
  { title: '传与不传', src: '伤寒论·第4条', text: '伤寒一日，太阳受之，脉若静者，为不传；颇欲吐，若躁烦，脉数急者，为传也。' },
  { title: '阳明病总纲', src: '伤寒论·第180条', text: '阳明之为病，胃家实是也。' },
  { title: '少阳病总纲', src: '伤寒论·第263条', text: '少阳之为病，口苦，咽干，目眩也。' },
  { title: '小柴胡汤主证', src: '伤寒论·第96条', text: '伤寒五六日中风，往来寒热，胸胁苦满，嘿嘿不欲饮食，心烦喜呕，或胸中烦而不呕……小柴胡汤主之。' },
  { title: '但见一证', src: '伤寒论·第101条', text: '伤寒中风，有柴胡证，但见一证便是，不必悉具。' },
  { title: '太阴病总纲', src: '伤寒论·第273条', text: '太阴之为病，腹满而吐，食不下，自利益甚，时腹自痛，若下之，必胸下结硬。' },
  { title: '少阴病总纲', src: '伤寒论·第281条', text: '少阴之为病，脉微细，但欲寐也。' },
  { title: '四逆汤证', src: '伤寒论·第388条', text: '下利清谷不止，身疼痛者，急当救里；后身疼痛，清便自调者，急当救表。救里宜四逆汤。' },
  { title: '厥阴病总纲', src: '伤寒论·第326条', text: '厥阴之为病，消渴，气上撞心，心中疼热，饥而不欲食，食则吐蛔，下之利不止。' },
  { title: '真武汤证', src: '伤寒论·第82条', text: '太阳病发汗，汗出不解，其人仍发热，心下悸，头眩，身瞤动，振振欲擗地者，真武汤主之。' },
  { title: '葛根汤证', src: '伤寒论·第31条', text: '太阳病，项背强几几，无汗恶风，葛根汤主之。' },
  { title: '大青龙汤证', src: '伤寒论·第38条', text: '太阳中风，脉浮紧，发热恶寒，身疼痛，不汗出而烦躁者，大青龙汤主之。' },
  { title: '小青龙汤证', src: '伤寒论·第40条', text: '伤寒表不解，心下有水气，干呕发热而咳，或渴，或利，或噎，或小便不利、少腹满，或喘者，小青龙汤主之。' },
  { title: '五苓散证', src: '伤寒论·第71条', text: '太阳病，发汗后，大汗出，胃中干，烦躁不得眠，欲得饮水者，少少与饮之，令胃气和则愈；若脉浮，小便不利，微热消渴者，五苓散主之。' },
  { title: '承气证候', src: '伤寒论·第208条', text: '阳明病脉迟，虽汗出不恶寒者，其身必重，短气腹满而喘，有潮热者，此外欲解，可攻里也。' },
  { title: '乌梅丸证', src: '伤寒论·第338条', text: '蛔厥者，乌梅丸主之，又主久利。' }
]

export default {
  data() {
    return { mode: 'blank', items: POOL, idx: 0, revealed: {}, todayCount: 0 }
  },
  computed: {
    theme() { return store.theme },
    cur() { return this.items[this.idx] || null },
    blankSegs() {
      if (!this.cur) return []
      // 遮盖策略：在逗号/顿号分句中随机遮 2-4 个 2-3 字词（按日+索引稳定）
      const text = this.cur.text
      const seed = (this.idx + 1) * 7 + new Date().getDate()
      const segs = []
      let rest = text
      const parts = text.split(/([，。；、：])/)
      let buf = ''
      const words = []
      // 简化：把 3-6 字的连续汉字段作为可遮候选
      const cand = []
      let m
      const re = /[\u4e00-\u9fa5]{3,8}/g
      while ((m = re.exec(text))) cand.push({ v: m[0], at: m.index })
      const chosen = []
      for (let i = 0; i < cand.length && chosen.length < 4; i++) {
        const c = cand[(seed + i * 3) % cand.length]
        if (c && c.v.length >= 3 && !chosen.some(x => Math.abs(x.at - c.at) < 4)) chosen.push(c)
      }
      // 构造分段
      let pos = 0
      chosen.sort((a, b) => a.at - b.at).forEach(c => {
        if (c.at > pos) segs.push({ text: text.slice(pos, c.at) })
        segs.push({ text: '', blank: true, v: c.v })
        pos = c.at + c.v.length
      })
      if (pos < text.length) segs.push({ text: text.slice(pos) })
      return segs
    },
    blankCount() { return this.blankSegs.filter(s => s.blank).length }
  },
  onShow() {
    applyTheme()
    try {
      const rec = uni.getStorageSync('nx_recite') || {}
      const p = n => (n < 10 ? '0' + n : n)
      const d = new Date()
      const key = `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())}`
      this.todayCount = rec[key] || 0
    } catch (e) {}
  },
  methods: {
    reveal(i) { this.revealed[i] = true },
    prev() { this.idx = (this.idx - 1 + this.items.length) % this.items.length; this.revealed = {} },
    next() {
      this.idx = (this.idx + 1) % this.items.length
      this.revealed = {}
      this.todayCount++
      try {
        const rec = uni.getStorageSync('nx_recite') || {}
        const p = n => (n < 10 ? '0' + n : n)
        const d = new Date()
        const key = `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())}`
        rec[key] = (rec[key] || 0) + 1
        uni.setStorageSync('nx_recite', rec)
      } catch (e) {}
    }
  }
}
</script>

<style scoped>
.page { min-height: 100vh; background: var(--bg); padding: 0 32rpx 80rpx; }
.ctrl { display: flex; gap: 14rpx; padding: 26rpx 0 22rpx; align-items: center; }
.c-mode { font-size: 24rpx; color: var(--ink2); background: var(--card); border: 1rpx solid var(--line); border-radius: 28rpx; padding: 10rpx 30rpx; }
.c-mode.on { background: var(--brand); border-color: var(--brand); color: #fff; font-weight: 700; }
.c-stat { margin-left: auto; font-size: 21rpx; color: var(--gold); }
.rec { padding: 34rpx 36rpx; }
.r-src { font-size: 19rpx; color: var(--gold); letter-spacing: 2rpx; }
.r-title { font-size: 34rpx; font-weight: 800; color: var(--brand); margin-top: 10rpx; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; min-width: 0; }
.r-text { font-size: 31rpx; line-height: 2.1; color: var(--ink); margin-top: 24rpx; text-align: justify; letter-spacing: 1rpx; }
.blank { color: var(--brand); background: rgba(154,46,31,.08); border-bottom: 3rpx solid var(--brand); border-radius: 6rpx; margin: 0 4rpx; }
.blank.show { background: rgba(154,46,31,.12); font-weight: 700; }
.r-hint { font-size: 20rpx; color: var(--ink2); margin-top: 26rpx; }
.acts { display: flex; gap: 18rpx; margin-top: 30rpx; }
.act { flex: 1; text-align: center; border-radius: 44rpx; padding: 20rpx 0; font-size: 25rpx; font-weight: 700; border: 2rpx solid var(--line); color: var(--ink2); }
.act.main { background: linear-gradient(135deg, var(--brand), var(--brand-deep)); color: #FDF8EE; border-color: transparent; }
.pos { text-align: center; color: var(--ink2); font-size: 21rpx; margin-top: 20rpx; }
.warn { margin-top: 28rpx; font-size: 20rpx; color: #A2651B; background: #FCF3DC; border-radius: 12rpx; padding: 16rpx 22rpx; line-height: 1.7; }
</style>
