<template>
  <view class="page" :class="theme === 'dark' ? 'tdark' : 'tlight'">
    <!-- 当前开穴（纳甲法） -->
    <view class="open-now">
      <view class="on-time-row">
        <text class="on-hour serif">{{ hourName }}时</text>
        <text class="on-clock">{{ liveClock }}</text>
        <text class="on-range">（{{ hourRangeFmt }}）</text>
      </view>
      <view class="on-main">
        <view class="on-left">
          <view class="on-label">{{ dayType }}日 · {{ dayMeridian }} · 纳甲法</view>
          <view class="open-pt serif" @tap="goPoint(najiaPoint)">{{ najiaPoint }}</view>
          <view class="open-meta">{{ najiaMeta }}</view>
        </view>
        <view class="on-seal serif" v-if="najiaOpen">开</view>
        <view class="on-seal off serif" v-else>阖</view>
      </view>
    </view>

    <view class="time-settings card">
      <view class="calc-title serif">计算时间设置</view>
      <view class="setting-line"><text>日期</text><picker mode="date" :value="manualDate" start="1900-01-01" end="2100-12-31" @change="manualDate = $event.detail.value; tick()"><view class="setting-value">{{ manualDate || '选择日期' }} ›</view></picker></view>
      <view class="setting-line"><text>时间</text><picker mode="time" :value="manualTime" @change="manualTime = $event.detail.value; tick()"><view class="setting-value">{{ manualTime || '选择时间' }} ›</view></picker></view>
      <view class="setting-line"><text>计算时区</text><view class="setting-value">中国标准时间（UTC+8）</view></view>
      <view class="setting-line"><text>子初换日</text><switch :checked="ziChuChange" @change="ziChuChange = $event.detail.value; tick()" color="#9A2E1F" /></view>
      <view class="setting-line"><text>真太阳时</text><switch :checked="useSolarTime" @change="useSolarTime = $event.detail.value; tick()" color="#9A2E1F" /></view>
      <view class="calc-note">所有计算统一使用中国标准时间（UTC+8）；开启子初换日后，23:00 起按次日干支计算。真太阳时为可选的学习性修正，开启后会在标准时间基础上调整。</view>
      <view class="calc-line">日干支：{{ dayGz }}　时干支：{{ hourGz }}</view>
      <view class="calc-line">纳甲依据：{{ dayGan }}日 · {{ hourName }}时 · {{ najiaMeta || '暂无开穴' }}</view>
      <view class="snapshot-row"><view class="snapshot-btn" @tap="copyCalculation">复制计算过程</view></view>
      <view class="snapshot-row"><view class="snapshot-btn" @tap="useSystemTime">使用当前时间</view><view class="snapshot-btn" @tap="tick">重新计算</view></view>
    </view>

    <!-- 纳支法补泻开穴 -->
    <view class="buxie">
      <view class="bx-head">
        <view class="bx-t serif">纳支法补泻 · {{ naZhi.mer }}经当令</view>
        <view class="bx-sub">按时辰取补泻穴：虚则补其母，实则泻其子</view>
      </view>
      <view class="bx-cards">
        <view class="bx-card bu">
          <view class="bx-label">补（虚证）</view>
          <view class="bx-pt serif">{{ naZhi.mu }}</view>
          <view class="bx-why">{{ naZhi.muWhy }}</view>
        </view>
        <view class="bx-card xie">
          <view class="bx-label">泻（实证）</view>
          <view class="bx-pt serif">{{ naZhi.zi }}</view>
          <view class="bx-why">{{ naZhi.ziWhy }}</view>
        </view>
      </view>
      <view class="bx-tip">{{ naZhi.tip }}</view>
    </view>

    <!-- 两法对照 -->
    <view class="sec">
      <view class="sec-head"><text class="sec-orn">❖</text><text class="sec-title serif">两法对照</text><text class="sec-more" @tap="goLinggui">灵龟八法 ›</text></view>
      <view class="duo card">
        <view class="d-half">
          <view class="dh-t serif">纳甲法</view>
          <view class="dh-d">日干+时支 → 五输穴开穴</view>
          <view class="dh-cur">{{ najiaPoint }} <text class="dh-tag">{{ najiaOpen ? '开' : '阖→原穴代' }}</text></view>
        </view>
        <view class="d-line" />
        <view class="d-half">
          <view class="dh-t serif">纳支法</view>
          <view class="dh-d">时支 → 当令经补泻穴</view>
          <view class="dh-cur">补{{ naZhi.mu }} · 泻{{ naZhi.zi }}</view>
        </view>
      </view>
    </view>

    <!-- 纳甲法全日开穴表 -->
    <view class="sec">
      <view class="sec-head"><text class="sec-orn">❖</text><text class="sec-title serif">纳甲法全日开穴 · {{ dayGan }}日（{{ dayMeridian }}）</text></view>
      <view class="tbl card">
        <view class="tr th">
          <view class="td">时辰</view>
          <view class="td time">时间</view>
          <view class="td">时干支</view>
          <view class="td">开穴</view>
          <view class="td">五输</view>
          <view class="td">状态</view>
        </view>
        <view class="tr" v-for="r in najiaTable" :key="r.hour" :class="{ now: r.isNow }">
          <view class="td serif">{{ r.hour }}</view>
          <view class="td time">{{ r.time }}</view>
          <view class="td serif">{{ r.ganzhi }}</view>
          <view class="td hl serif" @tap="goPoint(r.pt)">{{ r.pt }}</view>
          <view class="td">{{ r.shu }}</view>
          <view class="td">
            <text v-if="r.open" class="st-open">开</text>
            <text v-else class="st-close">阖</text>
          </view>
        </view>
      </view>
    </view>

    <!-- 纳支法全日补泻表 -->
    <view class="sec">
      <view class="sec-head"><text class="sec-orn">❖</text><text class="sec-title serif">纳支法全日补泻 · 母穴/子穴</text></view>
      <view class="tbl card">
        <view class="tr th">
          <view class="td">时辰</view>
          <view class="td time">时间</view>
          <view class="td">当令经</view>
          <view class="td">补穴</view>
          <view class="td">泻穴</view>
        </view>
        <view class="tr" v-for="(row, i) in fullDay" :key="i" :class="{ now: row.isNow }">
          <view class="td serif">{{ row.hour }}</view>
          <view class="td time">{{ row.time }}</view>
          <view class="td">{{ row.mer }}</view>
          <view class="td bu serif">{{ row.mu }}</view>
          <view class="td xie serif">{{ row.zi }}</view>
        </view>
      </view>
    </view>

    <!-- 六十甲子日学习表 -->
    <view class="sec">
      <view class="sec-head"><text class="sec-orn">❖</text><text class="sec-title serif">六十甲子日 · 日干支速查</text></view>
      <view class="cycle-grid"><view v-for="d in sexagenaryDays" :key="d.index" class="cycle-chip" :class="{ on: d.index === dayCycleIndex }" @tap="selectCycleDay(d)">{{ d.name }}</view></view>
      <view class="calc-note">当前日：{{ dayGz }}。点击仅用于学习查看，不会修改系统日期。</view>
    </view>

    <!-- 依据 -->
    <view class="basis card">
      <view class="bs-t serif">◈ 计算依据</view>
      <view class="bs-li">● <text class="bs-k">纳甲法</text>：日干+时支推五输穴，《针灸大成》卷五</view>
      <view class="bs-li">● <text class="bs-k">纳支法</text>：时支看当令经，按五行生克取母穴/子穴</view>
      <view class="bs-li">● <text class="bs-k">补法</text>：虚则补其母——在本经五输穴中取属「母」的穴（如肺虚补太渊，土生金）</view>
      <view class="bs-li">● <text class="bs-k">泻法</text>：实则泻其子——取属「子」的穴（如肺实泻尺泽，金生水）</view>
      <view class="bs-li">● <text class="bs-k">补泻时辰</text>：当令时辰内气最旺时用泻，气始衰时用补（倪师临床习惯：迎随补泻）</view>
    </view>
  </view>
</template>

<script>
import { store, applyTheme } from '@/utils/store.js'

const ZHI = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
const HOURS = [
  { h: '子', range: '23-01', hr: 23 }, { h: '丑', range: '01-03', hr: 1 },
  { h: '寅', range: '03-05', hr: 3 }, { h: '卯', range: '05-07', hr: 5 },
  { h: '辰', range: '07-09', hr: 7 }, { h: '巳', range: '09-11', hr: 9 },
  { h: '午', range: '11-13', hr: 11 }, { h: '未', range: '13-15', hr: 13 },
  { h: '申', range: '15-17', hr: 15 }, { h: '酉', range: '17-19', hr: 17 },
  { h: '戌', range: '19-21', hr: 19 }, { h: '亥', range: '21-23', hr: 21 }
]
const GAN = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
const GAN_MERIDIAN = { 0: '胆经', 1: '肝经', 2: '小肠经', 3: '心经', 4: '胃经', 5: '脾经', 6: '大肠经', 7: '肺经', 8: '膀胱经', 9: '肾经' }

/* 纳甲法开穴表（同 najia.vue） */
import { NAJIA, NAZHI_BASIC } from '@/utils/najia-data.js'

/* 纳支法补泻数据：每经的母穴（补）与子穴（泻） */
const BUXIE = {
  肺:   { mer: '手太阴肺经', mu: '太渊', muWhy: '土生金', zi: '尺泽', ziWhy: '金生水', yuan: '太渊' },
  大肠: { mer: '手阳明大肠经', mu: '曲池', muWhy: '土生金', zi: '二间', ziWhy: '金生水', yuan: '合谷' },
  胃:   { mer: '足阳明胃经', mu: '解溪', muWhy: '火生土', zi: '厉兑', ziWhy: '土生金', yuan: '冲阳' },
  脾:   { mer: '足太阴脾经', mu: '大都', muWhy: '火生土', zi: '商丘', ziWhy: '土生金', yuan: '太白' },
  心:   { mer: '手少阴心经', mu: '少冲', muWhy: '木生火', zi: '神门', ziWhy: '火生土', yuan: '神门' },
  小肠: { mer: '手太阳小肠经', mu: '后溪', muWhy: '木生火', zi: '小海', ziWhy: '火生土', yuan: '腕骨' },
  膀胱: { mer: '足太阳膀胱经', mu: '至阴', muWhy: '金生水', zi: '束骨', ziWhy: '水生木', yuan: '京骨' },
  肾:   { mer: '足少阴肾经', mu: '复溜', muWhy: '金生水', zi: '涌泉', ziWhy: '水生木', yuan: '太溪' },
  心包: { mer: '手厥阴心包经', mu: '中冲', muWhy: '木生火', zi: '大陵', ziWhy: '火生土', yuan: '大陵' },
  三焦: { mer: '手少阳三焦经', mu: '中渚', muWhy: '木生火', zi: '天井', ziWhy: '火生土', yuan: '阳池' },
  胆:   { mer: '足少阳胆经', mu: '侠溪', muWhy: '水生木', zi: '阳辅', ziWhy: '木生火', yuan: '丘墟' },
  肝:   { mer: '足厥阴肝经', mu: '曲泉', muWhy: '水生木', zi: '行间', ziWhy: '木生火', yuan: '太冲' }
}

/* 小时→当令经名映射（覆盖24小时） */
const HOUR_TO_MER = {
  23: '胆', 0: '胆', 1: '肝', 2: '肝', 3: '肺', 4: '肺', 5: '大肠', 6: '大肠',
  7: '胃', 8: '胃', 9: '脾', 10: '脾', 11: '心', 12: '心', 13: '小肠', 14: '小肠',
  15: '膀胱', 16: '膀胱', 17: '肾', 18: '肾', 19: '心包', 20: '心包', 21: '三焦', 22: '三焦'
}

export default {
  data() {
    return {
      dayGanIdx: 0, dayZhiIdx: 0, dayCycleIndex: 0, hourIdx: 0, nowHour: 0,
      najiaPoint: '', najiaMeta: '', najiaOpen: false,
      liveClock: '', fullDay: [], najiaTable: [], dayGz: '', hourGz: '', manualDate: '', manualTime: '', timezone: 'Asia/Shanghai (UTC+8)', timezoneOptions: ['Asia/Shanghai (UTC+8)', 'Asia/Tokyo (UTC+9)', 'UTC (UTC+0)'], ziChuChange: false, useSolarTime: false
    }
  },
  computed: {
    theme() { return store.theme },
    dayGan() { return GAN[this.dayGanIdx] },
    dayMeridian() { return GAN_MERIDIAN[this.dayGanIdx] },
    dayType() { return this.dayGanIdx % 2 === 0 ? '阳' : '阴' },
    hourName() { return ZHI[this.hourIdx] },
    sexagenaryDays() { return Array.from({ length: 60 }, (_, i) => ({ index: i, name: GAN[i % 10] + ZHI[i % 12] })) },
    hourRangeFmt() {
      const h = HOURS[this.hourIdx]
      if (!h) return ''
      const [a, b] = h.range.split('-')
      return `${a.padStart(2, '0')}:00 ~ ${b.padStart(2, '0')}:00`
    },
    naZhi() {
      const merName = HOUR_TO_MER[this.nowHour] || '胆'
      const bx = BUXIE[merName] || BUXIE['胆']
      return {
        mer: merName,
        full: bx.mer,
        mu: bx.mu, muWhy: bx.muWhy,
        zi: bx.zi, ziWhy: bx.ziWhy,
        yuan: bx.yuan,
        tip: `${bx.mer}当令。虚证（久病、乏力、脉弱）补母穴「${bx.mu}」（${bx.muWhy}）；实证（新病、痛剧、脉盛）泻子穴「${bx.zi}」（${bx.ziWhy}）。`
      }
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
      const text = `子午流注纳甲法\n日干支：${this.dayGz}\n时干支：${this.hourGz}\n日干：${this.dayGan}（${this.dayType}日）\n时辰：${this.hourName}时\n开穴：${this.najiaPoint || '当前闭穴'}\n依据：${this.najiaMeta || '纳支法原穴代用'}\n仅供学习参考。`
      uni.setClipboardData({ data: text, success: () => uni.showToast({ title: '计算过程已复制', icon: 'none' }) })
    },
    goPoint(name) {
      const point = String(name || '').split('/')[0]
      if (point && point !== '—') uni.navigateTo({ url: '/pkgZhenjiu/pages/list?pt=' + encodeURIComponent(point) })
    },
    goLinggui() { uni.navigateTo({ url: '/pages/study/linggui' }) },
    getCalcDate() {
      // 将中国标准时间的墙上时刻编码到 UTC，后续统一使用 UTC getter，避免设备时区影响干支计算。
      const p = n => (n < 10 ? '0' + n : n)
      let d
      if (this.manualDate && this.manualTime) {
        const [y, mo, day] = this.manualDate.split('-').map(Number)
        const [h, min] = this.manualTime.split(':').map(Number)
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
    calcDayGan(date = new Date()) {
      const d = date
      const y = d.getUTCFullYear(), m = d.getUTCMonth() + 1, day = d.getUTCDate()
      const a = Math.floor((14 - m) / 12)
      const y2 = y + 4800 - a
      const m2 = m + 12 * a - 3
      const jdn = day + Math.floor((153 * m2 + 2) / 5) + 365 * y2 + Math.floor(y2 / 4) - Math.floor(y2 / 100) + Math.floor(y2 / 400) - 32045
      return (jdn + 9) % 10
    },
    calcDayZhi(date = new Date()) {
      const y = date.getUTCFullYear(), m = date.getUTCMonth() + 1, day = date.getUTCDate()
      const a = Math.floor((14 - m) / 12); const y2 = y + 4800 - a; const m2 = m + 12 * a - 3
      const jdn = day + Math.floor((153 * m2 + 2) / 5) + 365 * y2 + Math.floor(y2 / 4) - Math.floor(y2 / 100) + Math.floor(y2 / 400) - 32045
      return (jdn + 1) % 12
    },
    getHourIdx(h) {
      if (h === 23 || h === 0) return 0
      return Math.floor((h + 1) / 2)
    },
    tick() {
      const d = this.getCalcDate()
      const p = n => (n < 10 ? '0' + n : n)
      const h = d.getUTCHours()
      this.liveClock = `${p(h)}:${p(d.getUTCMinutes())}:${p(d.getUTCSeconds())}`
      const dayForGan = this.ziChuChange && h >= 23 ? new Date(d.getTime() + 24 * 3600000) : d
      this.dayGanIdx = this.calcDayGan(dayForGan)
      const dayZhiIdx = this.calcDayZhi(dayForGan)
      this.dayZhiIdx = dayZhiIdx
      this.dayCycleIndex = Array.from({ length: 60 }, (_, i) => [i % 10, i % 12]).findIndex(x => x[0] === this.dayGanIdx && x[1] === dayZhiIdx)
      const hourGanIdx = (this.dayGanIdx * 2 + this.getHourIdx(h)) % 10
      this.dayGz = GAN[this.dayGanIdx] + ZHI[dayZhiIdx]
      this.hourGz = GAN[hourGanIdx] + ZHI[this.getHourIdx(h)]
      this.nowHour = h
      this.hourIdx = this.getHourIdx(this.nowHour)
      this.calcNajia()
      this.buildNajiaTable()
      this.buildFullDay()
    },
    calcNajia() {
      const table = NAJIA[this.dayGanIdx] || {}
      const entry = table[this.hourIdx]
      if (entry) {
        this.najiaPoint = entry.p
        this.najiaMeta = `${this.dayMeridian} · ${entry.s}`
        this.najiaOpen = true
      } else {
        const merName = HOUR_TO_MER[this.nowHour] || '胆'
        const bx = BUXIE[merName]
        this.najiaPoint = bx ? bx.yuan : '丘墟'
        this.najiaMeta = `${merName}经原穴（纳支法代用）`
        this.najiaOpen = false
      }
    },
    buildNajiaTable() {
      const table = NAJIA[this.dayGanIdx] || {}
      const rows = []
      for (let i = 0; i < 12; i++) {
        const h = HOURS[i]
        const [a, b] = h.range.split('-')
        const entry = table[i]
        rows.push({
          hour: h.h,
          time: `${a.padStart(2, '0')}:00~${b.padStart(2, '0')}:00`,
          ganzhi: GAN[(this.dayGanIdx * 2 + i) % 10] + ZHI[i],
          pt: entry ? entry.p : '—',
          shu: entry ? entry.s : '—',
          open: !!entry,
          isNow: i === this.hourIdx
        })
      }
      this.najiaTable = rows
    },
    selectCycleDay(d) {
      uni.showToast({ title: `${d.name}日：请在上方输入具体公历日期复盘`, icon: 'none', duration: 2200 })
    },
    buildFullDay() {
      const rows = []
      for (let i = 0; i < 12; i++) {
        const h = HOURS[i]
        const [a, b] = h.range.split('-')
        const merName = HOUR_TO_MER[h.hr] || '胆'
        const bx = BUXIE[merName] || BUXIE['胆']
        rows.push({
          hour: h.h,
          time: `${a.padStart(2, '0')}:00~${b.padStart(2, '0')}:00`,
          mer: merName,
          mu: bx.mu,
          zi: bx.zi,
          isNow: i === this.hourIdx
        })
      }
      this.fullDay = rows
    }
  }
}
</script>

<style scoped>
.page { min-height: 100vh; background: var(--bg); padding-bottom: 80rpx; }
.time-settings { margin: 20rpx 32rpx 0; padding: 22rpx 26rpx; }
.setting-line { display: flex; align-items: center; justify-content: space-between; padding: 10rpx 0; border-bottom: 1rpx solid var(--line); color: var(--ink); font-size: 21rpx; }
.setting-line input { text-align: right; color: var(--ink); font-size: 21rpx; }
.setting-value { color: var(--brand); }
.calc-title { color: var(--brand); font-size: 26rpx; font-weight: 800; margin-bottom: 10rpx; }
.calc-note { color: var(--ink2); font-size: 18rpx; margin-top: 8rpx; line-height: 1.6; }
.calc-line { color: var(--ink); font-size: 20rpx; line-height: 1.8; margin-top: 6rpx; }
.cycle-grid { display: grid; grid-template-columns: repeat(6, 1fr); gap: 10rpx; padding: 18rpx; background: var(--card); border-radius: 16rpx; }
.cycle-chip { text-align: center; color: var(--ink2); background: var(--zebra-bg); border-radius: 10rpx; padding: 10rpx 0; font-size: 21rpx; }
.cycle-chip.on { background: var(--brand); color: #fff; font-weight: 700; }
.snapshot-row { display: flex; gap: 12rpx; margin-top: 14rpx; }
.snapshot-btn { flex: 1; text-align: center; border: 1rpx solid var(--line); border-radius: 24rpx; padding: 9rpx 0; color: var(--brand); font-size: 20rpx; }

/* 纳甲法开穴卡 */
.open-now { margin: 26rpx 32rpx; background: linear-gradient(150deg, var(--hero1), var(--hero2)); border-radius: 26rpx; padding: 32rpx 32rpx 28rpx; position: relative; overflow: hidden; }
.open-now::after { content: '開穴'; position: absolute; right: -8rpx; bottom: -18rpx; font-size: 90rpx; color: #F6E7C9; opacity: .06; font-weight: 800; letter-spacing: 8rpx; }
.on-time-row { display: flex; align-items: baseline; }
.on-hour { font-size: 30rpx; font-weight: 800; color: #F6E7C9; letter-spacing: 3rpx; }
.on-clock { font-size: 22rpx; color: #FDF8EE; margin-left: 16rpx; font-family: Menlo, monospace; }
.on-range { font-size: 18rpx; color: rgba(246,231,201,.7); margin-left: 8rpx; }
.on-main { display: flex; align-items: center; margin-top: 14rpx; }
.on-left { flex: 1; }
.on-label { font-size: 20rpx; color: rgba(253,248,238,.85); }
.open-pt { font-size: 64rpx; font-weight: 800; color: #FDF8EE; letter-spacing: 4rpx; margin-top: 8rpx; line-height: 1.2; }
.open-meta { font-size: 20rpx; color: #F6E7C9; margin-top: 6rpx; }
.on-seal { width: 96rpx; height: 96rpx; border: 5rpx solid rgba(246,231,201,.8); border-radius: 20rpx; color: #F6E7C9; font-size: 48rpx; font-weight: 800; display: flex; align-items: center; justify-content: center; transform: rotate(6deg); flex-shrink: 0; }
.on-seal.off { opacity: .5; border-style: dashed; }

/* 纳支法补泻卡 */
.buxie { margin: 22rpx 32rpx; }
.bx-head { margin-bottom: 14rpx; }
.bx-t { font-size: 27rpx; font-weight: 800; color: var(--brand); }
.bx-sub { font-size: 19rpx; color: var(--ink2); margin-top: 4rpx; }
.bx-cards { display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 1fr); gap: 14rpx; }
.bx-card { border-radius: 18rpx; padding: 20rpx 18rpx 16rpx; border: 2rpx solid; min-width: 0; }
.bx-card.bu { border-color: #3F6B37; background: linear-gradient(160deg, #E8F0E4, var(--card)); }
.bx-card.xie { border-color: #9A2E1F; background: linear-gradient(160deg, #FBEAE3, var(--card)); }
.bx-label { font-size: 18rpx; font-weight: 700; margin-bottom: 6rpx; }
.bx-card.bu .bx-label { color: #3F6B37; }
.bx-card.xie .bx-label { color: #9A2E1F; }
.bx-pt { font-size: 40rpx; font-weight: 800; letter-spacing: 3rpx; }
.bx-card.bu .bx-pt { color: #2F5D62; }
.bx-card.xie .bx-pt { color: #9A2E1F; }
.bx-why { font-size: 17rpx; color: var(--ink2); margin-top: 4rpx; }
.bx-tip { margin-top: 14rpx; font-size: 19rpx; color: var(--ink2); line-height: 1.75; background: var(--quote-bg); border-radius: 12rpx; padding: 12rpx 18rpx; }

/* 两法对照 */
.sec { margin: 26rpx 32rpx 0; }
.sec-head { display: flex; align-items: center; margin-bottom: 16rpx; }
.sec-more { margin-left: auto; font-size: 20rpx; color: var(--ink2); }
.sec-orn { color: var(--gold); font-size: 22rpx; margin-right: 10rpx; }
.sec-title { font-size: 29rpx; font-weight: 800; color: var(--ink); letter-spacing: 2rpx; }
.duo { display: flex; padding: 24rpx 0; }
.d-half { flex: 1; padding: 0 22rpx; min-width: 0; }
.d-line { width: 1rpx; background: var(--line); }
.dh-t { font-size: 23rpx; font-weight: 800; color: var(--brand); margin-bottom: 4rpx; }
.dh-d { font-size: 17rpx; color: var(--ink2); margin-bottom: 8rpx; }
.dh-cur { font-size: 24rpx; font-weight: 800; color: var(--ink); }
.dh-tag { font-size: 16rpx; color: var(--gold); margin-left: 8rpx; }

/* 全日表 */
.tbl { padding: 0; overflow: hidden; }
.tr { display: flex; }
.tr.th { background: linear-gradient(135deg, rgba(154,46,31,.92), rgba(124,58,33,.92)); }
.th .td { color: #FDF8EE; font-weight: 700; font-size: 19rpx; }
.td.time { flex: 1.9; font-size: 15rpx; letter-spacing: -0.5rpx; }
.tr.now { background: rgba(154,46,31,.06); }
.td { flex: 0.8; text-align: center; padding: 12rpx 2rpx; font-size: 18rpx; color: var(--ink); border-top: 1rpx solid var(--line); min-width: 0; word-break: break-all; line-height: 1.5; }
.td.time { flex: 1.9; font-size: 15rpx; letter-spacing: -0.5rpx; white-space: nowrap; }
.td.bu { color: #3F6B37; font-weight: 700; }
.td.xie { color: #9A2E1F; font-weight: 700; }
.tr.now .td { font-weight: 700; }
.tr.now .td:first-child::before { content: '▶'; color: var(--brand); font-size: 13rpx; margin-right: 3rpx; }
.st-open { color: #3F6B37; font-weight: 700; font-size: 18rpx; background: #E8F0E4; border-radius: 6rpx; padding: 2rpx 10rpx; }
.st-close { color: #A2651B; font-size: 18rpx; background: #FCF3DC; border-radius: 6rpx; padding: 2rpx 10rpx; }

/* 依据 */
.basis { margin: 20rpx 32rpx; padding: 22rpx 28rpx; background: var(--quote-bg); }
.bs-t { font-size: 24rpx; font-weight: 800; color: var(--brand); margin-bottom: 10rpx; }
.bs-li { font-size: 19rpx; color: var(--ink2); line-height: 2; }
.bs-k { font-weight: 700; color: var(--ink); }
</style>
