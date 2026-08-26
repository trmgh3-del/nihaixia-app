<template>
  <view class="page" :class="theme === 'dark' ? 'tdark' : 'tlight'">
    <!-- 当前时辰 -->
    <view class="nowcard">
      <view class="nc-time">{{ now.h }}</view>
      <view class="nc-main">
        <view class="nc-mer serif">{{ now.mer }}</view>
        <view class="nc-sub">此刻气血流注 · {{ now.range }} 当令</view>
      </view>
      <view class="nc-side">
        <view class="nc-yuan">原穴 <text class="serif">{{ now.yuan }}</text></view>
        <view class="nc-wx">{{ now.wx }}</view>
      </view>
    </view>

    <!-- 十二时辰流注 -->
    <view class="sec">
      <view class="sec-head"><text class="sec-orn">❖</text><text class="sec-title serif">十二时辰气血流注</text><text class="sec-more" @tap="goNajia">纳甲法开穴 ›</text></view>
      <view class="flow">
        <view v-for="z in ziwu" :key="z.h" class="fz" :class="{ on: z.h === nowKey }">
          <view class="fz-top">
            <text class="fz-h serif">{{ z.h }}</text>
            <view class="fz-dot" :style="{ background: z.color }" />
          </view>
          <view class="fz-mer serif">{{ z.mer }}</view>
          <view class="fz-org">{{ z.merS }}</view>
          <view class="fz-time">{{ z.range }}</view>
          <view class="fz-yuan">原穴·{{ z.yuan }}</view>
        </view>
      </view>
    </view>

    <!-- 歌诀 -->
    <view class="sec">
      <view class="sec-head"><text class="sec-orn">❖</text><text class="sec-title serif">纳支纳甲歌诀（倪师人纪）</text></view>
      <view class="verse card">
        <view class="v-t">地支歌（流注）</view>
        <view class="v-b serif">肺寅大卯胃辰宫，脾巳心午小未中，申胱酉肾心包戌，亥焦子胆丑肝通。</view>
        <view class="hr" />
        <view class="v-t">天干歌（脏腑）</view>
        <view class="v-b serif">甲胆乙肝丙小肠，丁心戊胃己脾乡，庚属大肠辛属肺，壬属膀胱癸肾藏，三焦亦向壬中寄，包络同归入癸水。</view>
        <view class="v-note">倪师：天干地支是中医五行的基础——甲乙木、丙丁火、脾胃土、庚辛金、壬癸水；阴木肝、阳木胆，阴火心、阳火小肠。</view>
      </view>
    </view>

    <!-- 五输穴按时应用 -->
    <view class="sec">
      <view class="sec-head"><text class="sec-orn">❖</text><text class="sec-title serif">按时取穴 · 五输穴应用</text></view>
      <view class="acc card">
        <view class="wu" v-for="w in wushu" :key="w.k">
          <view class="wu-k serif">{{ w.k }}</view>
          <view class="wu-v">{{ w.v }}</view>
        </view>
      </view>
      <view class="note card">子午流注按时开穴有「纳支法」（本文十二时辰流注）与「纳甲法」（按日干开穴）两派；倪师人纪授课以病取五输（井荥俞经合）与十二经流注为纲，临床配合病变性质选穴。</view>
    </view>
  </view>
</template>

<script>
import { store } from '@/utils/store.js'
import { openMd } from '@/utils/routes.js'
import { loadData } from '@/utils/data.js'

const ZIWU = [
  { h: '子', mer: '胆', merS: '足少阳胆经', range: '23:00~01:00', yuan: '丘墟', wx: '阳木', color: '#5B8C5A', hours: [23, 0] },
  { h: '丑', mer: '肝', merS: '足厥阴肝经', range: '01:00~03:00', yuan: '太冲', wx: '阴木', color: '#4F7D4C', hours: [1, 2] },
  { h: '寅', mer: '肺', merS: '手太阴肺经', range: '03:00~05:00', yuan: '太渊', wx: '阴金', color: '#C9A063', hours: [3, 4] },
  { h: '卯', mer: '大肠', merS: '手阳明大肠经', range: '05:00~07:00', yuan: '合谷', wx: '阳金', color: '#B58A4E', hours: [5, 6] },
  { h: '辰', mer: '胃', merS: '足阳明胃经', range: '07:00~09:00', yuan: '冲阳', wx: '阳土', color: '#A2651B', hours: [7, 8] },
  { h: '巳', mer: '脾', merS: '足太阴脾经', range: '09:00~11:00', yuan: '太白', wx: '阴土', color: '#8A6414', hours: [9, 10] },
  { h: '午', mer: '心', merS: '手少阴心经', range: '11:00~13:00', yuan: '神门', wx: '阴火', color: '#9A2E1F', hours: [11, 12] },
  { h: '未', mer: '小肠', merS: '手太阳小肠经', range: '13:00~15:00', yuan: '腕骨', wx: '阳火', color: '#B0452F', hours: [13, 14] },
  { h: '申', mer: '膀胱', merS: '足太阳膀胱经', range: '15:00~17:00', yuan: '京骨', wx: '阳水', color: '#2F5D62', hours: [15, 16] },
  { h: '酉', mer: '肾', merS: '足少阴肾经', range: '17:00~19:00', yuan: '太溪', wx: '阴水', color: '#37506B', hours: [17, 18] },
  { h: '戌', mer: '心包', merS: '手厥阴心包经', range: '19:00~21:00', yuan: '大陵', wx: '相火', color: '#833B3B', hours: [19, 20] },
  { h: '亥', mer: '三焦', merS: '手少阳三焦经', range: '21:00~23:00', yuan: '阳池', wx: '阳火', color: '#54427C', hours: [21, 22] }
]

export default {
  data() {
    return {
      ziwu: ZIWU,
      now: { h: '', mer: '', range: '', yuan: '', wx: '' },
      wushu: [
        { k: '井', v: '病在脏取井穴——指头末梢下针，井主心下满（动脉血管堵塞，针下痛即去）' },
        { k: '荥', v: '病变于色取荥穴——青肝、赤心、黄脾、白肺、黑肾' },
        { k: '俞', v: '病在时间者取俞穴——按时辰发病之症' },
        { k: '经', v: '病变于音者取经穴——声音变化之症' },
        { k: '合', v: '病起于饮食取合穴——饮食所伤之症；五脏不平衡用原穴' }
      ]
    }
  },
  computed: {
    theme() { return store.theme },
    nowKey() { return String(this.now.h || '').replace('时', '') }
  },
  onShow() {
    this.tick()
    this._timer = setInterval(() => this.tick(), 30000)
  },
  onHide() {
    clearInterval(this._timer)
  },
  onUnload() {
    clearInterval(this._timer)
  },
  methods: {
    tick() {
      const h = new Date().getHours()
      const z = ZIWU.find(x => x.hours.includes(h)) || ZIWU[0]
      this.now = { h: z.h + '时', mer: z.mer, range: z.range, yuan: z.yuan, wx: z.wx }
    },
    goNajia() { uni.navigateTo({ url: '/pages/study/najia' }) },
    async openRef() {
      try {
        const d = await loadData('zhenjiu')
        const it = (d.quickref || []).find(x => x.t.includes('十二经络流注'))
        if (it) openMd({ ...it, f: 'zhenjiu' }, it.t)
        else uni.navigateTo({ url: '/pkgZhenjiu/pages/list' })
      } catch (e) {
        uni.navigateTo({ url: '/pkgZhenjiu/pages/list' })
      }
    }
  }
}
</script>

<style scoped>
.page { min-height: 100vh; background: var(--bg); padding: 0 0 60rpx; }
.nowcard { margin: 26rpx 32rpx; background: linear-gradient(140deg, var(--hero1), var(--hero2)); border-radius: 24rpx; padding: 34rpx 32rpx; display: flex; align-items: center; position: relative; overflow: hidden; }
.nowcard::after { content: '子午流注'; position: absolute; right: -10rpx; bottom: -24rpx; font-size: 88rpx; color: #F6E7C9; opacity: .07; font-weight: 800; letter-spacing: 6rpx; }
.nc-time { font-size: 72rpx; font-weight: 800; color: #FDF8EE; font-family: 'Songti SC', 'STSong', serif; margin-right: 30rpx; }
.nc-main { flex: 1; }
.nc-mer { font-size: 40rpx; font-weight: 800; color: #FDF8EE; letter-spacing: 3rpx; }
.nc-sub { font-size: 22rpx; color: rgba(253,248,238,.85); margin-top: 8rpx; }
.nc-side { text-align: right; }
.nc-yuan { font-size: 21rpx; color: rgba(253,248,238,.9); }
.nc-yuan .serif { font-size: 30rpx; font-weight: 800; margin-left: 6rpx; }
.nc-wx { font-size: 20rpx; color: #F6E7C9; margin-top: 6rpx; border: 1rpx solid rgba(246,231,201,.5); border-radius: 10rpx; display: inline-block; padding: 2rpx 14rpx; }
.sec { margin: 30rpx 32rpx 0; }
.sec-head { display: flex; align-items: center; margin-bottom: 18rpx; }
.sec-orn { color: var(--gold); font-size: 22rpx; margin-right: 10rpx; }
.sec-title { font-size: 31rpx; font-weight: 800; color: var(--ink); letter-spacing: 2rpx; }
.sec-more { margin-left: auto; font-size: 23rpx; color: var(--ink2); }
.flow { display: grid; grid-template-columns: repeat(3, 1fr); gap: 14rpx; }
.fz { background: var(--card); border: 1rpx solid var(--line); border-radius: 16rpx; padding: 18rpx 20rpx 16rpx; position: relative; }
.fz.on { border-color: var(--brand); background: linear-gradient(150deg, rgba(154,46,31,.07), var(--card)); box-shadow: 0 6rpx 18rpx rgba(154,46,31,.15); }
.fz-top { display: flex; align-items: center; }
.fz-h { font-size: 30rpx; font-weight: 800; color: var(--ink); }
.fz.on .fz-h { color: var(--brand); }
.fz-dot { width: 14rpx; height: 14rpx; border-radius: 50%; margin-left: auto; }
.fz.on .fz-dot { animation: breathe 1.6s infinite; }
@keyframes breathe { 50% { transform: scale(1.5); opacity: .5; } }
.fz-mer { font-size: 34rpx; font-weight: 800; color: var(--ink); margin-top: 6rpx; letter-spacing: 2rpx; }
.fz-org { font-size: 20rpx; color: var(--ink2); margin-top: 2rpx; }
.fz-time { font-size: 21rpx; color: var(--gold); margin-top: 8rpx; }
.fz-yuan { font-size: 20rpx; color: var(--ink2); margin-top: 2rpx; }
.verse { padding: 26rpx 30rpx; }
.v-t { font-size: 23rpx; font-weight: 800; color: var(--brand); margin-bottom: 10rpx; }
.v-b { font-size: 26rpx; color: var(--ink); line-height: 2; letter-spacing: 2rpx; }
.hr { height: 1rpx; background: var(--line); margin: 22rpx 0; }
.v-note { font-size: 21rpx; color: var(--ink2); line-height: 1.8; margin-top: 16rpx; background: var(--quote-bg); border-radius: 12rpx; padding: 14rpx 20rpx; }
.acc { padding: 8rpx 28rpx; }
.wu { display: flex; padding: 22rpx 0; border-bottom: 1rpx solid var(--line); }
.wu:last-child { border-bottom: none; }
.wu-k { width: 64rpx; height: 64rpx; border-radius: 16rpx; background: var(--zebra-bg); color: var(--brand); font-size: 30rpx; font-weight: 800; display: flex; align-items: center; justify-content: center; margin-right: 22rpx; flex-shrink: 0; }
.wu-v { flex: 1; font-size: 24rpx; color: var(--ink); line-height: 1.75; padding-top: 6rpx; }
.note { margin-top: 18rpx; padding: 20rpx 26rpx; font-size: 21rpx; color: var(--ink2); line-height: 1.8; }
</style>
