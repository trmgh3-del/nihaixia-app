<template>
  <view class="page" :class="theme === 'dark' ? 'tdark' : 'tlight'">
    <view class="time-settings card">
      <view class="calc-title serif">计算时间设置</view>
      <view class="setting-line"><text>日期</text><picker mode="date" :value="manualDate" start="1900-01-01" end="2100-12-31" @change="manualDate = $event.detail.value; tick()"><view class="setting-value">{{ manualDate || '选择日期' }} ›</view></picker></view>
      <view class="setting-line"><text>时间</text><picker mode="time" :value="manualTime" @change="manualTime = $event.detail.value; tick()"><view class="setting-value">{{ manualTime || '选择时间' }} ›</view></picker></view>
      <view class="setting-line"><text>计算时区</text><view class="setting-value">中国标准时间（UTC+8）</view></view>
      <view class="setting-line"><text>真太阳时</text><switch :checked="useSolarTime" @change="useSolarTime = $event.detail.value; tick()" color="#9A2E1F" /></view>
      <view class="calc-note">所有计算统一使用中国标准时间（UTC+8）。启用真太阳时后在标准时间基础上作学习性修正；不同流派的子初换日和真太阳时仍可能存在差异。</view>
      <view class="snapshot-row"><view class="snapshot-btn" @tap="useSystemTime">使用当前时间</view><view class="snapshot-btn" @tap="tick">重新计算</view></view>
    </view>

    <!-- 当前灵龟开穴 -->
    <view class="lg-now">
      <view class="lg-time-row">
        <text class="lg-hour serif">{{ hourName }}时</text>
        <text class="lg-clock">{{ liveClock }}</text>
      </view>
      <view class="lg-main">
        <view class="lg-left">
          <view class="lg-label">灵龟八法 · {{ trigram }}</view>
          <view class="lg-pt serif">{{ openPoint }}</view>
          <view class="lg-meta">{{ pointMeridian }} · 通{{ confluence }}</view>
        </view>
        <view class="lg-pair">
          <view class="lg-pair-t">配对穴</view>
          <view class="lg-pair-pt serif">{{ pairPoint }}</view>
        </view>
      </view>
      <view class="lg-tip">灵龟八法按时取八脉交会穴：「{{ openPoint }}」主穴，可配「{{ pairPoint }}」同用</view>
    </view>

    <view class="calc card">
      <view class="calc-title serif">计算过程与流派设置</view>
      <view class="calc-line">日干支：{{ dayGz }}　时干支：{{ hourGz }}</view>
      <view class="calc-line">日干 {{ calcDetails.dayGan }} + 日支 {{ calcDetails.dayZhi }} + 时干 {{ calcDetails.hourGan }} + 时支 {{ calcDetails.hourZhi }} = {{ calcDetails.sum }}</view>
      <view class="calc-line">{{ calcDetails.divisor === 9 ? '阳日除9' : '阴日除6' }}，余数：{{ calcDetails.remainder }} → {{ openPoint }}</view>
      <view class="calc-setting"><text>余数5流派：</text><view v-for="o in ['照海', '内关']" :key="o" class="setting-chip" :class="{ on: rem5Mode === o }" @tap="setRem5(o)">{{ o }}</view></view>
      <view class="calc-note">余数5在不同典籍有不同取法；本设置仅影响余数5，不代表临床处方。</view>
      <view class="snapshot-row"><view class="snapshot-btn" @tap="copyCalculation">复制计算过程</view></view>
    </view>

    <!-- 八脉交会穴表 -->
    <view class="sec">
      <view class="sec-head"><text class="sec-orn">❖</text><text class="sec-title serif">八脉交会穴 · 洛书配卦</text></view>
      <view class="ba-grid">
        <view class="ba-item" v-for="b in eightPoints" :key="b.pt" :class="{ on: b.pt === openPoint }" @tap="showDetail(b)">
          <view class="ba-tri serif">{{ b.trigram }}</view>
          <view class="ba-pt serif">{{ b.pt }}</view>
          <view class="ba-mer">{{ b.meridian }}</view>
          <view class="ba-conf">通{{ b.confluence }}</view>
        </view>
      </view>
    </view>

    <!-- 全日灵龟开穴时刻表 -->
    <view class="sec">
      <view class="sec-head"><text class="sec-orn">❖</text><text class="sec-title serif">今日灵龟全日开穴</text></view>
      <view class="tbl card">
        <view class="tr th"><view class="td">时辰</view><view class="td time">时间</view><view class="td">卦</view><view class="td">开穴</view></view>
        <view class="tr" v-for="r in dayTable" :key="r.hour" :class="{ now: r.isNow }">
          <view class="td serif">{{ r.hour }}</view>
          <view class="td time">{{ r.time }}</view>
          <view class="td serif">{{ r.trigram }}</view>
          <view class="td hl serif">{{ r.pt }}</view>
        </view>
      </view>
    </view>

    <!-- 计算依据 -->
    <view class="basis card">
      <view class="bs-t serif">◈ 灵龟八法计算法</view>
      <view class="bs-li">● <text class="bs-k">日干支+时干支</text> → 按干支代数表取数 → 求和 → 阳日 mod 9 / 阴日 mod 6</view>
      <view class="bs-li">● <text class="bs-k">取穴歌</text>：坎一联申脉，照海坤二五，震三属外关，巽四临泣数，乾六是公孙，兑七后溪府，艮八系内关，离九列缺主</view>
      <view class="bs-li">● <text class="bs-k">配穴法</text>：公孙配内关（胃心胸）、后溪配申脉（颈项耳肩）、临泣配外关（目锐眦耳后）、列缺配照海（肺系咽喉）</view>
      <view class="bs-li">● <text class="bs-k">文献</text>：《针灸大成》卷五 + 《子午流注说难》</view>
    </view>
  </view>
</template>

<script>
import { store, applyTheme } from '@/utils/store.js'

const ZHI = ['子','丑','寅','卯','辰','巳','午','未','申','酉','戌','亥']
const GAN = ['甲','乙','丙','丁','戊','己','庚','辛','壬','癸']
const HOURS = [
  { h: '子', hr: 23, range: '23-01' }, { h: '丑', hr: 1, range: '01-03' },
  { h: '寅', hr: 3, range: '03-05' }, { h: '卯', hr: 5, range: '05-07' },
  { h: '辰', hr: 7, range: '07-09' }, { h: '巳', hr: 9, range: '09-11' },
  { h: '午', hr: 11, range: '11-13' }, { h: '未', hr: 13, range: '13-15' },
  { h: '申', hr: 15, range: '15-17' }, { h: '酉', hr: 17, range: '17-19' },
  { h: '戌', hr: 19, range: '19-21' }, { h: '亥', hr: 21, range: '21-23' }
]

/* 八脉交会穴：卦→穴→经→通脉→配对穴 */
const BAGUA = [
  { n: 1, tri: '坎', pt: '申脉', mer: '膀胱经', conf: '阳跷', pair: '后溪' },
  { n: 2, tri: '坤', pt: '照海', mer: '肾经', conf: '阴跷', pair: '列缺' },
  { n: 5, tri: '坤', pt: '照海', mer: '肾经', conf: '阴跷', pair: '列缺' }, // 坤二五同属
  { n: 3, tri: '震', pt: '外关', mer: '三焦经', conf: '阳维', pair: '临泣' },
  { n: 4, tri: '巽', pt: '临泣', mer: '胆经', conf: '带脉', pair: '外关' },
  { n: 6, tri: '乾', pt: '公孙', mer: '脾经', conf: '冲脉', pair: '内关' },
  { n: 7, tri: '兑', pt: '后溪', mer: '小肠经', conf: '督脉', pair: '申脉' },
  { n: 8, tri: '艮', pt: '内关', mer: '心包经', conf: '阴维', pair: '公孙' },
  { n: 9, tri: '离', pt: '列缺', mer: '肺经', conf: '任脉', pair: '照海' }
]

/* 灵龟八法干支代数：日干、日支与时干、时支使用不同的代数表。 */
function dayGanNum(gan) { return ['甲', '己'].includes(gan) ? 10 : ['乙', '庚'].includes(gan) ? 9 : ['丁', '壬'].includes(gan) ? 8 : 7 }
function dayZhiNum(zhi) { return ['辰', '戌', '丑', '未'].includes(zhi) ? 10 : ['申', '酉'].includes(zhi) ? 9 : ['寅', '卯'].includes(zhi) ? 8 : 7 }
function hourGanNum(gan) { return ['甲', '己'].includes(gan) ? 9 : ['乙', '庚'].includes(gan) ? 8 : ['丙', '辛'].includes(gan) ? 7 : ['丁', '壬'].includes(gan) ? 6 : 5 }
function hourZhiNum(zhi) { return ['子', '午'].includes(zhi) ? 9 : ['丑', '未'].includes(zhi) ? 8 : ['寅', '申'].includes(zhi) ? 7 : ['卯', '酉'].includes(zhi) ? 6 : ['辰', '戌'].includes(zhi) ? 5 : 4 }

function calcDayGanZhi(date) {
  const y = date.getUTCFullYear(), m = date.getUTCMonth() + 1, d = date.getUTCDate()
  const a = Math.floor((14 - m) / 12)
  const y2 = y + 4800 - a
  const m2 = m + 12 * a - 3
  const jdn = d + Math.floor((153 * m2 + 2) / 5) + 365 * y2 + Math.floor(y2 / 4) - Math.floor(y2 / 100) + Math.floor(y2 / 400) - 32045
  const ganIdx = (jdn + 9) % 10
  const zhiIdx = (jdn + 1) % 12
  return { gan: GAN[ganIdx], zhi: ZHI[zhiIdx], ganIdx, zhiIdx }
}

function calcHourGanZhi(dayGanIdx, hour) {
  // 时干 = (日干序号 × 2 + 时支序号) mod 10
  const hourZhiIdx = hour === 23 || hour === 0 ? 0 : Math.floor((hour + 1) / 2)
  const hourGanIdx = (dayGanIdx * 2 + hourZhiIdx) % 10
  return { gan: GAN[hourGanIdx], zhi: ZHI[hourZhiIdx] }
}

function calcLingGui(dayGan, dayZhi, hourGan, hourZhi, isYangDay) {
  const sum = dayGanNum(dayGan) + dayZhiNum(dayZhi) + hourGanNum(hourGan) + hourZhiNum(hourZhi)
  let num
  if (isYangDay) {
    num = sum % 9
    if (num === 0) num = 9
  } else {
    num = sum % 6
    if (num === 0) num = 6
  }
  // 映射到八穴
  const mapping = { 1: '申脉', 2: '照海', 3: '外关', 4: '临泣', 5: '照海', 6: '公孙', 7: '后溪', 8: '内关', 9: '列缺' }
  return { num, point: num === 5 ? null : (mapping[num] || '列缺') }
}

export default {
  data() {
    return {
      liveClock: '', hourIdx: 0, dayTable: [],
      manualDate: '', manualTime: '', timezone: 'Asia/Shanghai (UTC+8)', timezoneOptions: ['Asia/Shanghai (UTC+8)', 'Asia/Tokyo (UTC+9)', 'UTC (UTC+0)'], useSolarTime: false,
      openPoint: '', pairPoint: '', trigram: '', pointMeridian: '', confluence: '',
      rem5Mode: '照海', dayGz: '', hourGz: '', calcDetails: { dayGan: 0, dayZhi: 0, hourGan: 0, hourZhi: 0, sum: 0, divisor: 0, remainder: 0 }
    }
  },
  computed: {
    theme() { return store.theme },
    hourName() { return ZHI[this.hourIdx] },
    eightPoints() {
      // 去重：坤二五同一穴
      const seen = {}
      return BAGUA.filter(b => {
        if (seen[b.pt]) return false
        seen[b.pt] = true
        return true
      }).map(b => ({ tri: b.tri, pt: b.pt, meridian: b.mer, confluence: b.conf, pair: b.pair }))
    }
  },
  onShow() {
    applyTheme()
    if (!this.manualDate || !this.manualTime) this.useSystemTime()
    else this.tick()
    this._timer = setInterval(() => this.tick(), 1000)
  },
  onHide() { clearInterval(this._timer) },
  onUnload() { clearInterval(this._timer) },
  methods: {
    copyCalculation() {
      const c = this.calcDetails
      const text = `灵龟八法计算\n日干支：${this.dayGz}\n时干支：${this.hourGz}\n日干${c.dayGan}+日支${c.dayZhi}+时干${c.hourGan}+时支${c.hourZhi}=${c.sum}\n${c.divisor === 9 ? '阳日除9' : '阴日除6'}，余数${c.remainder}\n开穴：${this.openPoint}（配${this.pairPoint}）\n仅供学习参考。`
      uni.setClipboardData({ data: text, success: () => uni.showToast({ title: '计算过程已复制', icon: 'none' }) })
    },
    setRem5(value) { this.rem5Mode = value; this.tick() },
    getCalcDate() {
      // 统一把中国标准时间墙上时刻编码为 UTC，避免运行设备处于其他时区时干支错日、错时。
      let d
      if (this.manualDate && this.manualTime) {
        const [y, mo, day] = this.manualDate.split('-').map(Number); const [h, min] = this.manualTime.split(':').map(Number)
        d = new Date(Date.UTC(y, mo - 1, day, h, min))
      } else {
        const now = new Date(Date.now() + 8 * 3600000)
        d = new Date(Date.UTC(now.getUTCFullYear(), now.getUTCMonth(), now.getUTCDate(), now.getUTCHours(), now.getUTCMinutes(), now.getUTCSeconds()))
      }
      if (this.useSolarTime) d = new Date(d.getTime() + 4 * 60000)
      return d
    },
    useSystemTime() {
      const d = new Date(Date.now() + 8 * 3600000); const p = n => (n < 10 ? '0' + n : n)
      this.manualDate = `${d.getUTCFullYear()}-${p(d.getUTCMonth() + 1)}-${p(d.getUTCDate())}`; this.manualTime = `${p(d.getUTCHours())}:${p(d.getUTCMinutes())}`; this.tick()
    },
    tick() {
      const d = this.getCalcDate()
      const p = n => (n < 10 ? '0' + n : n)
      const h = d.getUTCHours()
      this.liveClock = `${p(h)}:${p(d.getUTCMinutes())}:${p(d.getUTCSeconds())}`
      const day = calcDayGanZhi(d)
      const isYang = day.ganIdx % 2 === 0
      this.hourIdx = h === 23 || h === 0 ? 0 : Math.floor((h + 1) / 2)
      const hourGZ = calcHourGanZhi(day.ganIdx, h)
      const raw = calcLingGui(day.gan, day.zhi, hourGZ.gan, hourGZ.zhi, isYang)
      const point = raw.point || this.rem5Mode
      const result = { ...raw, point }
      const info = BAGUA.find(b => b.pt === result.point) || BAGUA[8]
      this.dayGz = day.gan + day.zhi
      this.hourGz = hourGZ.gan + hourGZ.zhi
      this.calcDetails = { dayGan: dayGanNum(day.gan), dayZhi: dayZhiNum(day.zhi), hourGan: hourGanNum(hourGZ.gan), hourZhi: hourZhiNum(hourGZ.zhi), sum: dayGanNum(day.gan) + dayZhiNum(day.zhi) + hourGanNum(hourGZ.gan) + hourZhiNum(hourGZ.zhi), divisor: isYang ? 9 : 6, remainder: raw.num }
      this.openPoint = result.point
      this.pairPoint = info.pair
      this.trigram = info.tri
      this.pointMeridian = info.mer
      this.confluence = info.conf
      this.buildTable(day, isYang)
    },
    buildTable(day, isYang) {
      const rows = []
      for (let i = 0; i < 12; i++) {
        const h = HOURS[i]
        const [a, b] = h.range.split('-')
        const hourGZ = calcHourGanZhi(day.ganIdx, h.hr)
        const r = calcLingGui(day.gan, day.zhi, hourGZ.gan, hourGZ.zhi, isYang)
        const point = r.point || this.rem5Mode
        const info = BAGUA.find(x => x.pt === point) || BAGUA[8]
        rows.push({
          hour: h.h,
          time: `${a.padStart(2, '0')}:00~${b.padStart(2, '0')}:00`,
          trigram: info.tri,
          pt: point,
          isNow: i === this.hourIdx
        })
      }
      this.dayTable = rows
    },
    showDetail(b) {
      uni.navigateTo({ url: '/pkgZhenjiu/pages/list?pt=' + encodeURIComponent(b.pt) })
    }
  }
}
</script>

<style scoped>
.page { min-height: 100vh; background: var(--bg); padding-bottom: 80rpx; }

.lg-now { margin: 26rpx 32rpx; background: linear-gradient(150deg, #2F5D62, #1A3A3E); border-radius: 26rpx; padding: 32rpx 32rpx 28rpx; position: relative; overflow: hidden; }
.lg-now::after { content: '靈龜'; position: absolute; right: -8rpx; bottom: -18rpx; font-size: 90rpx; color: #F6E7C9; opacity: .06; font-weight: 800; letter-spacing: 8rpx; }
.lg-time-row { display: flex; align-items: baseline; }
.lg-hour { font-size: 30rpx; font-weight: 800; color: #F6E7C9; letter-spacing: 3rpx; }
.lg-clock { font-size: 22rpx; color: #FDF8EE; margin-left: 16rpx; font-family: Menlo, monospace; }
.lg-main { display: flex; align-items: center; margin-top: 14rpx; }
.lg-left { flex: 1; }
.lg-label { font-size: 20rpx; color: rgba(253,248,238,.85); }
.lg-pt { font-size: 64rpx; font-weight: 800; color: #FDF8EE; letter-spacing: 4rpx; margin-top: 8rpx; }
.lg-meta { font-size: 20rpx; color: #F6E7C9; margin-top: 6rpx; }
.lg-pair { text-align: center; border-left: 2rpx solid rgba(246,231,201,.3); padding-left: 28rpx; }
.lg-pair-t { font-size: 18rpx; color: rgba(246,231,201,.7); }
.lg-pair-pt { font-size: 38rpx; font-weight: 800; color: #F6E7C9; margin-top: 4rpx; }
.lg-tip { margin-top: 18rpx; font-size: 19rpx; color: rgba(253,248,238,.85); line-height: 1.7; background: rgba(253,248,238,.1); border-radius: 14rpx; padding: 12rpx 18rpx; }

.time-settings { margin: 20rpx 32rpx 0; padding: 22rpx 26rpx; }
.setting-line { display: flex; align-items: center; justify-content: space-between; padding: 10rpx 0; border-bottom: 1rpx solid var(--line); color: var(--ink); font-size: 21rpx; }
.setting-line input { text-align: right; color: var(--ink); font-size: 21rpx; }
.setting-value { color: var(--brand); }
.calc { margin: 18rpx 32rpx 0; padding: 22rpx 26rpx; }
.calc-title { color: var(--brand); font-size: 26rpx; font-weight: 800; margin-bottom: 10rpx; }
.calc-line { color: var(--ink); font-size: 20rpx; line-height: 1.8; }
.calc-setting { display: flex; align-items: center; gap: 10rpx; margin-top: 10rpx; font-size: 20rpx; color: var(--ink2); }
.setting-chip { padding: 6rpx 14rpx; border: 1rpx solid var(--line); border-radius: 20rpx; color: var(--ink2); }
.setting-chip.on { color: #fff; background: var(--brand); border-color: var(--brand); }
.calc-note { color: var(--ink2); font-size: 18rpx; margin-top: 8rpx; line-height: 1.6; }
.sec { margin: 26rpx 32rpx 0; }
.sec-head { display: flex; align-items: center; margin-bottom: 16rpx; }
.sec-orn { color: var(--gold); font-size: 22rpx; margin-right: 10rpx; }
.sec-title { font-size: 29rpx; font-weight: 800; color: var(--ink); letter-spacing: 2rpx; }

.ba-grid { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 12rpx; }
.ba-item { background: var(--card); border: 1rpx solid var(--line); border-radius: 16rpx; padding: 16rpx 8rpx 14rpx; text-align: center; position: relative; min-width: 0; }
.ba-item.on { border-color: #2F5D62; background: linear-gradient(160deg, #E9F1F2, var(--card)); box-shadow: 0 4rpx 14rpx rgba(47,93,98,.15); }
.ba-tri { font-size: 24rpx; font-weight: 800; color: var(--gold); }
.ba-item.on .ba-tri { color: #2F5D62; }
.ba-pt { font-size: 28rpx; font-weight: 800; color: var(--ink); margin-top: 4rpx; }
.ba-item.on .ba-pt { color: #2F5D62; }
.ba-mer { font-size: 16rpx; color: var(--ink2); margin-top: 2rpx; }
.ba-conf { font-size: 16rpx; color: var(--gold); margin-top: 2rpx; }

.tbl { padding: 0; overflow: hidden; }
.tr { display: flex; }
.tr.th { background: linear-gradient(135deg, #2F5D62, #234449); }
.th .td { color: #FDF8EE; font-weight: 700; font-size: 20rpx; }
.tr.now { background: rgba(47,93,98,.08); }
.td { flex: 0.8; text-align: center; padding: 13rpx 3rpx; font-size: 18rpx; color: var(--ink); border-top: 1rpx solid var(--line); white-space: nowrap; }
.td.time { flex: 1.9; font-size: 15rpx; letter-spacing: -0.5rpx; }
.td.hl { color: #2F5D62; font-weight: 700; }
.tr.now .td:first-child::before { content: '▶'; color: #2F5D62; font-size: 13rpx; margin-right: 3rpx; }

.basis { margin: 20rpx 32rpx; padding: 22rpx 28rpx; background: var(--quote-bg); }
.bs-t { font-size: 24rpx; font-weight: 800; color: var(--brand); margin-bottom: 10rpx; }
.bs-li { font-size: 19rpx; color: var(--ink2); line-height: 2; }
.bs-k { font-weight: 700; color: var(--ink); }
</style>
