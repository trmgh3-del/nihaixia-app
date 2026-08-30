<template>
  <view class="page" :class="theme === 'dark' ? 'tdark' : 'tlight'">
    <!-- 换算器 -->
    <view class="calc card">
      <view class="c-title serif">⟡ 经方剂量换算器</view>
      <view class="c-row">
        <input class="c-num" type="digit" v-model="num" placeholder="数量" @input="calc" />
        <picker mode="selector" :range="unitNames" @change="onUnit" class="c-picker">
          <view class="c-unit">{{ unit }}<text class="c-caret">▾</text></view>
        </picker>
      </view>
      <view class="c-out" v-if="result">
        <view class="o-line">
          <text class="o-k">汉制·考证</text>
          <view class="o-v serif">{{ result.g }} <text class="o-u">克</text></view>
        </view>
        <view class="o-line">
          <text class="o-k">台湾钱制</text>
          <view class="o-v serif">{{ result.qian }} <text class="o-u">钱</text><text class="o-u2">（{{ result.qianG }} 克）</text></view>
        </view>
        <view class="o-line" v-if="unit === '两'">
          <text class="o-k">倪师习惯</text>
          <view class="o-v serif hl">古方 {{ num }}两 → 临床 {{ num }}钱（{{ result.qianG }} 克）</view>
        </view>
        <view class="o-note" v-if="cur && cur.note">{{ cur.note }}</view>
      </view>
    </view>

    <!-- 三套体系 -->
    <view class="sec">
      <view class="sec-head"><text class="sec-orn">❖</text><text class="sec-title serif">三套度量衡（严禁混用）</text><text class="sec-more" @tap="openRef">换算标准原文 ›</text></view>
      <view class="sys card">
        <view class="s-item">
          <view class="s-t">① 汉朝原方</view>
          <view class="s-d">1斤=16两≈248g<br />1两=24铢≈15.625g<br />1升=200ml</view>
          <view class="s-u">用于"古方X两"表述</view>
        </view>
        <view class="s-item">
          <view class="s-t">② 台湾临床</view>
          <view class="s-d">1两=10钱≈37.5g<br />1钱=10分≈3.75g</view>
          <view class="s-u">倪师临床"X钱/X两"体系</view>
        </view>
        <view class="s-item">
          <view class="s-t">③ 倪师换算口诀</view>
          <view class="s-d">古方一两 → 临床一钱</view>
          <view class="s-u">"三两把它换成三钱"（倪师原话）</view>
        </view>
      </view>
    </view>

    <!-- 实物单位表 -->
    <view class="sec">
      <view class="sec-head"><text class="sec-orn">❖</text><text class="sec-title serif">实物单位速查</text></view>
      <view class="tblwrap card">
        <view class="tr th"><view class="td">单位</view><view class="td">换算</view></view>
        <view class="tr" v-for="(r, i) in table" :key="r[0]" :class="{ zebra: i % 2 === 1 }">
          <view class="td">{{ r[0] }}</view><view class="td">{{ r[1] }}</view>
        </view>
      </view>
    </view>

    <view class="warn">⚠ 引用剂量必须注明体系（汉制/台湾钱制）；峻药（生附子/生半夏/麻黄/细辛/硫磺）给完整范围并附煎服法；实际用药请遵执业医嘱。</view>
  </view>
</template>

<script>
import { store, applyTheme } from '@/utils/store.js'
import { openMd } from '@/utils/routes.js'
import { loadData } from '@/utils/data.js'

const UNITS = [
  { k: '两', g: 15.625, note: '汉朝度量衡：1两=24铢≈15.625克（1斤=16两≈248克）' },
  { k: '斤', g: 248, note: '汉制约248克（16两）' },
  { k: '铢', g: 0.651, note: '24铢=1两' },
  { k: '分', g: 4.05, note: '约3.9-4.2克' },
  { k: '钱', g: 3.75, note: '台湾度量衡：1钱=10分≈3.75克（1两=10钱）' },
  { k: '升(液体)', g: 200, note: '1升=200毫升（液体计）' },
  { k: '升(半夏)', g: 130, note: '半夏一升≈130克；五味子/吴茱萸/蜀椒一升≈50克；葶苈子一升≈60克' },
  { k: '合', g: 20, note: '10合=1升，约20毫升' },
  { k: '枚(附子大)', g: 25, note: '附子大者1枚20-30克（中者15克）；倪师口述一枚≈3-4钱' },
  { k: '枚(杏仁)', g: 0.4, note: '杏仁10枚≈4克；桃仁比例相近' },
  { k: '枚(枳实)', g: 14.4, note: '枳实1枚≈14.4克；瓜蒌1枚≈46克' },
  { k: '枚(乌头)', g: 4, note: '乌头小者≈3克、大者≈5-6克' },
  { k: '个(石膏鸡子大)', g: 40, note: '石膏鸡子大1枚≈40克' },
  { k: '方寸匕', g: 2, note: '约2克（金石类约2.74克）' },
  { k: '钱匕', g: 1.65, note: '约1.5-1.8克' },
  { k: '克', g: 1, note: '' }
]

export default {
  data() {
    return {
      num: '1',
      unit: '钱',
      unitIdx: 4,
      result: null,
      table: [
        ['附子大者1枚', '20-30克（中者15克；倪师口述一枚≈3-4钱）'],
        ['半夏一升', '≈130克'],
        ['五味子/吴茱萸/蜀椒一升', '≈50克'],
        ['葶苈子一升', '≈60克'],
        ['杏仁10枚', '≈4克'],
        ['石膏鸡子大', '≈40克'],
        ['枳实1枚', '≈14.4克；瓜蒌1枚≈46克'],
        ['乌头', '小者≈3克、大者≈5-6克'],
        ['1方寸匕', '≈2克（金石类2.74克）'],
        ['1钱匕', '≈1.5-1.8克'],
        ['1分', '≈3.9-4.2克'],
        ['1寸', '2.31厘米（长度）']
      ]
    }
  },
  computed: {
    theme() { return store.theme },
    unitNames() { return UNITS.map(u => u.k) },
    cur() { return UNITS[this.unitIdx] }
  },
  onShow() { applyTheme(); this.calc() },
  methods: {
    onUnit(e) {
      this.unitIdx = Number(e.detail.value)
      this.unit = UNITS[this.unitIdx].k
      this.calc()
    },
    calc() {
      const n = parseFloat(this.num)
      if (!(n >= 0)) { this.result = null; return }
      const u = UNITS[this.unitIdx]
      const g = n * u.g
      const gR = Math.round(g * 100) / 100
      const qian = Math.round(g / 3.75 * 100) / 100
      const qianG = Math.round(qian * 3.75 * 100) / 100
      this.result = { g: gR, qian, qianG }
    },
    async openRef() {
      try {
        const d = await loadData('formulas')
        const it = (d.articles || []).find(x => x.t.includes('换算标准') || x.t.includes('差异对照'))
        if (it) openMd({ ...it, f: 'formulas', c: 'article' }, it.t)
        else uni.navigateTo({ url: '/pkgFormula/pages/articles' })
      } catch (e) {
        uni.navigateTo({ url: '/pkgFormula/pages/articles' })
      }
    }
  }
}
</script>

<style scoped>
.page { min-height: 100vh; background: var(--bg); padding-bottom: 60rpx; }
.calc { margin: 26rpx 32rpx 0; padding: 30rpx; }
.c-title { font-size: 31rpx; font-weight: 800; color: var(--brand); margin-bottom: 24rpx; }
.c-row { display: flex; gap: 18rpx; }
.c-num { flex: 1; background: var(--zebra-bg); border-radius: 16rpx; height: 88rpx; line-height: 88rpx; padding: 0 28rpx; font-size: 34rpx; font-weight: 800; color: var(--brand); }
.c-picker { flex-shrink: 0; }
.c-unit { background: var(--zebra-bg); border-radius: 16rpx; height: 88rpx; line-height: 88rpx; padding: 0 30rpx; font-size: 29rpx; color: var(--ink); display: flex; align-items: center; }
.c-caret { margin-left: 12rpx; color: var(--ink2); }
.c-out { margin-top: 26rpx; background: var(--zebra-bg); border-radius: 18rpx; padding: 8rpx 26rpx; }
.o-line { display: flex; align-items: center; padding: 20rpx 0; border-bottom: 1rpx dashed var(--line); }
.o-line:last-of-type { border-bottom: none; }
.o-k { width: 170rpx; font-size: 23rpx; color: var(--ink2); flex-shrink: 0; }
.o-v { font-size: 40rpx; font-weight: 800; color: var(--ink); }
.o-v.hl { font-size: 30rpx; color: var(--brand); }
.o-u { font-size: 22rpx; color: var(--ink2); font-weight: 400; }
.o-u2 { font-size: 20rpx; color: var(--ink2); font-weight: 400; }
.o-note { font-size: 20rpx; color: var(--ink2); line-height: 1.7; padding: 12rpx 0 20rpx; }
.sec { margin: 30rpx 32rpx 0; }
.sec-head { display: flex; align-items: center; margin-bottom: 18rpx; }
.sec-orn { color: var(--gold); font-size: 22rpx; margin-right: 10rpx; }
.sec-title { font-size: 31rpx; font-weight: 800; color: var(--ink); letter-spacing: 2rpx; }
.sec-more { margin-left: auto; font-size: 23rpx; color: var(--ink2); }
.sys { display: flex; padding: 26rpx 0; }
.s-item { flex: 1; padding: 0 22rpx; border-right: 1rpx dashed var(--line); }
.s-item:last-child { border-right: none; }
.s-t { font-size: 24rpx; font-weight: 800; color: var(--brand); margin-bottom: 12rpx; }
.s-d { font-size: 22rpx; color: var(--ink); line-height: 1.9; }
.s-u { font-size: 18rpx; color: var(--ink2); margin-top: 12rpx; }
.tblwrap { padding: 10rpx 0; }
.tr { display: flex; }
.th { background: linear-gradient(135deg, rgba(154,46,31,.92), rgba(124,58,33,.92)); border-radius: 12rpx 12rpx 0 0; }
.th .td { color: #FDF8EE; font-weight: 700; border-top: none; }
.td { flex: 1; padding: 14rpx 22rpx; font-size: 22rpx; color: var(--ink); border-top: 1rpx solid var(--line); line-height: 1.7; }
.zebra .td { background: var(--zebra-bg); }
.warn { margin: 30rpx 32rpx 0; font-size: 20rpx; color: #A2651B; background: #FCF3DC; border-radius: 12rpx; padding: 16rpx 22rpx; line-height: 1.7; }
</style>
