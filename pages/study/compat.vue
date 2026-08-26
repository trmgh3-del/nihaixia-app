<template>
  <view class="page" :class="theme === 'dark' ? 'tdark' : 'tlight'">
    <view class="checker card">
      <view class="c-t serif">⟡ 配伍禁忌速查</view>
      <view class="c-row">
        <input class="c-in" v-model="a" placeholder="药一（如：半夏）" @input="check" />
        <text class="c-x">×</text>
        <input class="c-in" v-model="b" placeholder="药二（如：乌头）" @input="check" />
      </view>
      <view class="c-res" v-if="verdict">
        <view class="v-badge" :class="verdict.level">{{ verdict.level === 'danger' ? '⛔ 禁忌' : verdict.level === 'warn' ? '⚠ 相畏' : '✓ 未见相反相畏' }}</view>
        <view class="v-desc">{{ verdict.desc }}</view>
      </view>
    </view>

    <view class="sec">
      <view class="sec-head"><text class="sec-orn">❖</text><text class="sec-title serif">十八反</text></view>
      <view class="grp card">
        <view class="g-song serif">本草明言十八反——半蒌贝蔹及攻乌，藻戟遂芫俱战草，诸参辛芍叛藜芦。</view>
        <view class="g-li" v-for="g in shiba" :key="g.main"><text class="g-main">{{ g.main }}</text> 反 <text class="g-sub">{{ g.subs }}</text></view>
      </view>
    </view>

    <view class="sec">
      <view class="sec-head"><text class="sec-orn">❖</text><text class="sec-title serif">十九畏</text></view>
      <view class="grp card">
        <view class="g-li" v-for="p in shijiu" :key="p.a"><text class="g-main">{{ p.a }}</text> 畏 <text class="g-sub">{{ p.b }}</text></view>
      </view>
    </view>

    <view class="warn">十八反十九畏为传统配伍禁忌通则（通用中医常识，非本库蒸馏内容）。倪师临床对个别禁忌有独到运用（如半夏配附子），一切以执业医师处方为准。</view>
  </view>
</template>

<script>
import { store, applyTheme } from '@/utils/store.js'

const SHIBA = [
  { main: '甘草', keys: ['甘草'], subs: '甘遂、大戟、海藻、芫花', subKeys: ['甘遂', '大戟', '海藻', '芫花'] },
  { main: '乌头（川乌/草乌/附子）', keys: ['乌头', '川乌', '草乌', '附子'], subs: '贝母、瓜蒌、半夏、白蔹、白及', subKeys: ['贝母', '瓜蒌', '天花', '半夏', '白蔹', '白及'] },
  { main: '藜芦', keys: ['藜芦'], subs: '人参、沙参、丹参、玄参、苦参、细辛、芍药', subKeys: ['人参', '沙参', '丹参', '玄参', '苦参', '细辛', '芍药', '白芍', '赤芍'] }
]
const SHIJIU = [
  { a: '硫黄', ak: ['硫黄', '硫磺'], b: '朴硝（芒硝）', bk: ['朴硝', '芒硝'] },
  { a: '水银', ak: ['水银'], b: '砒霜', bk: ['砒霜', '砒'] },
  { a: '狼毒', ak: ['狼毒'], b: '密陀僧', bk: ['密陀僧'] },
  { a: '巴豆', ak: ['巴豆'], b: '牵牛', bk: ['牵牛'] },
  { a: '丁香', ak: ['丁香'], b: '郁金', bk: ['郁金', '玉金'] },
  { a: '川乌、草乌', ak: ['川乌', '草乌'], b: '犀角', bk: ['犀角'] },
  { a: '牙硝', ak: ['牙硝'], b: '三棱', bk: ['三棱'] },
  { a: '官桂（肉桂）', ak: ['官桂', '肉桂'], b: '赤石脂', bk: ['赤石脂', '石脂'] },
  { a: '人参', ak: ['人参'], b: '五灵脂', bk: ['五灵脂'] }
]

export default {
  data() {
    return { a: '', b: '', verdict: null, shiba: SHIBA, shijiu: SHIJIU }
  },
  computed: { theme() { return store.theme } },
  onShow() { applyTheme() },
  methods: {
    hit(list, kw) {
      return list.find(item => item.keys.some(k => kw.includes(k)))
    },
    check() {
      const A = this.a.trim()
      const B = this.b.trim()
      if (!A || !B) { this.verdict = null; return }
      // 十八反
      for (const g of SHIBA) {
        const aHit = g.keys.some(k => A.includes(k)) || g.subKeys.some(k => A.includes(k))
        const bHit = g.keys.some(k => B.includes(k)) || g.subKeys.some(k => B.includes(k))
        const aMain = g.keys.some(k => A.includes(k))
        const bMain = g.keys.some(k => B.includes(k))
        if ((aMain && g.subKeys.some(k => B.includes(k))) || (bMain && g.subKeys.some(k => A.includes(k))) || (aHit && bHit && aMain !== bMain)) {
          this.verdict = { level: 'danger', desc: `「${g.main}」与「${g.subs}」相反（十八反），传统视为配伍禁忌。` }
          return
        }
      }
      for (const p of SHIJIU) {
        if ((p.ak.some(k => A.includes(k)) && p.bk.some(k => B.includes(k))) || (p.bk.some(k => A.includes(k)) && p.ak.some(k => B.includes(k)))) {
          this.verdict = { level: 'warn', desc: `「${p.a}」畏「${p.b}」（十九畏）。` }
          return
        }
      }
      this.verdict = { level: 'ok', desc: '两味药未在十八反/十九畏通则中出现禁忌组合。' }
    }
  }
}
</script>

<style scoped>
.page { min-height: 100vh; background: var(--bg); padding-bottom: 70rpx; }
.checker { margin: 26rpx 32rpx 0; padding: 30rpx; }
.c-t { font-size: 30rpx; font-weight: 800; color: var(--brand); margin-bottom: 22rpx; }
.c-row { display: flex; align-items: center; gap: 14rpx; }
.c-in { flex: 1; background: var(--zebra-bg); border-radius: 14rpx; height: 76rpx; line-height: 76rpx; padding: 0 24rpx; font-size: 26rpx; color: var(--ink); }
.c-x { color: var(--ink2); font-size: 30rpx; }
.c-res { margin-top: 24rpx; background: var(--zebra-bg); border-radius: 16rpx; padding: 22rpx 26rpx; }
.v-badge { display: inline-block; font-size: 24rpx; font-weight: 800; border-radius: 12rpx; padding: 8rpx 22rpx; }
.v-badge.danger { background: #9A2E1F; color: #FDF8EE; }
.v-badge.warn { background: #C8A45C; color: #fff; }
.v-badge.ok { background: #3F6B37; color: #FDF8EE; }
.v-desc { font-size: 23rpx; color: var(--ink); line-height: 1.8; margin-top: 14rpx; }
.sec { margin: 30rpx 32rpx 0; }
.sec-head { display: flex; align-items: center; margin-bottom: 16rpx; }
.sec-orn { color: var(--gold); font-size: 22rpx; margin-right: 10rpx; }
.sec-title { font-size: 30rpx; font-weight: 800; color: var(--ink); }
.grp { padding: 24rpx 30rpx; }
.g-song { font-size: 25rpx; color: var(--brand); line-height: 2; background: var(--quote-bg); border-radius: 12rpx; padding: 14rpx 20rpx; margin-bottom: 18rpx; letter-spacing: 1rpx; }
.g-li { font-size: 24rpx; color: var(--ink); padding: 12rpx 0; border-bottom: 1rpx dashed var(--line); line-height: 1.7; }
.g-li:last-child { border-bottom: none; }
.g-main { font-weight: 700; color: var(--brand); }
.g-sub { color: var(--ink); }
.warn { margin: 30rpx 32rpx 0; font-size: 20rpx; color: #A2651B; background: #FCF3DC; border-radius: 12rpx; padding: 16rpx 22rpx; line-height: 1.7; }
</style>
