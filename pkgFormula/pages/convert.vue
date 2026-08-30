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
      <view class="quick-row"><text class="quick-label">台湾/临床：</text><view v-for="q in [1, 3, 5, 10]" :key="q" class="quick-chip" @tap="setQuick(q)">{{ q }} 钱</view></view>
      <view class="quick-row"><text class="quick-label han">汉制：</text><view class="quick-chip han-chip" @tap="setUnitQuick(1, 0)">1 两</view><view class="quick-chip han-chip" @tap="setUnitQuick(3, 0)">3 两</view><view class="quick-chip han-chip" @tap="setUnitQuick(1, 2)">1 铢</view><view class="quick-chip han-chip" @tap="setUnitQuick(1, 3)">1 分</view></view>
      <view class="quick-row"><text class="quick-label tang">唐制：</text><view class="quick-chip tang-chip" @tap="setUnitQuick(1, 4)">1 斤</view><view class="quick-chip tang-chip" @tap="setUnitQuick(1, 5)">1 两</view><view class="quick-chip tang-chip" @tap="setUnitQuick(1, 6)">1 铢</view><view class="quick-chip tang-chip" @tap="setUnitQuick(1, 7)">1 分</view></view>
      <view class="c-out" v-if="result">
        <view class="o-line">
          <text class="o-k">{{ result.gLabel }}</text>
          <view class="o-v serif">{{ result.g }} <text class="o-u">{{ result.gUnit }}</text></view>
        </view>
        <view class="o-line" v-if="result.mass">
          <text class="o-k">台湾钱制</text>
          <view class="o-v serif">{{ result.qian }} <text class="o-u">钱</text><text class="o-u2">（{{ result.qianG }} 克）</text></view>
        </view>
        <view class="o-line" v-if="result.niQian !== null">
          <text class="o-k">倪师换算</text>
          <view class="o-v serif hl">{{ result.niLabel }} → 临床 {{ result.niQian }}钱（约 {{ result.niQianG }} 克）</view>
        </view>
        <view class="o-note" v-if="cur && cur.note">{{ cur.note }}</view>
        <view class="o-warning" v-if="unit === '钱'">注意：1钱≈3.75克是近现代/台湾钱制；汉代原方通常按1两=24铢、1两≈15.625克考证，不能把“汉制1钱”直接等同3.75克。</view>
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

    <!-- 药物特殊换算：枚数→重量 -->
    <view class="sec">
      <view class="sec-head"><text class="sec-orn">❖</text><text class="sec-title serif">药物特殊换算（枚数→重量）</text></view>
      <view class="tblwrap card"><view class="tbl-caption">以枚/个计的药物重量参考</view><view class="tr th"><view class="td">药物</view><view class="td">数量</view><view class="td">重量</view></view><view class="tr" v-for="(r, i) in countTable" :key="r[0]" :class="{ zebra: i % 2 === 1 }"><view class="td">{{ r[0] }}</view><view class="td">{{ r[1] }}</view><view class="td">{{ r[2] }}</view></view></view>
    </view>

    <!-- 容积换算 -->
    <view class="sec">
      <view class="sec-head"><text class="sec-orn">❖</text><text class="sec-title serif">药物特殊换算（容积→重量）</text></view>
      <view class="tblwrap card"><view class="tbl-caption">同一升的重量因药物密度不同而不同</view><view class="tr th"><view class="td">药物</view><view class="td">容积</view><view class="td">重量</view></view><view class="tr" v-for="(r, i) in volumeTable" :key="r[0]" :class="{ zebra: i % 2 === 1 }"><view class="td">{{ r[0] }}</view><view class="td">{{ r[1] }}</view><view class="td">{{ r[2] }}</view></view></view>
    </view>

    <!-- 倪师临床剂量参考 -->
    <view class="sec">
      <view class="sec-head"><text class="sec-orn">❖</text><text class="sec-title serif">剂量参考（倪海厦）</text></view>
      <view class="dose-ref card"><view v-for="r in doseReference" :key="r[0]" class="dose-line"><text class="dose-k">{{ r[0] }}</text><text>{{ r[1] }}</text></view></view>
    </view>

    <!-- 换算常数参考：完整收录截图中的重量、容量、长度单位 -->
    <view class="sec">
      <view class="sec-head"><text class="sec-orn">❖</text><text class="sec-title serif">换算常数参考</text></view>
      <view class="tblwrap card">
        <view class="tbl-caption">三套度量衡与容量、长度参考；不同体系不可直接混用</view>
        <view class="tr th"><view class="td">类别</view><view class="td">原单位</view><view class="td">参考换算</view></view>
        <view class="tr" v-for="(r, i) in referenceTable" :key="r[0] + r[1]" :class="{ zebra: i % 2 === 1 }">
          <view class="td">{{ r[0] }}</view><view class="td">{{ r[1] }}</view><view class="td">{{ r[2] }}</view>
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
  { k: '两', g: 15.625, out: '克', mass: true, note: '汉朝度量衡：1两=24铢≈15.625克（1斤=16两≈248克）' },
  { k: '斤', g: 248, out: '克', mass: true, note: '汉制约248克（16两）' },
  { k: '铢', g: 0.651, out: '克', mass: true, note: '汉制约0.65克；24铢=1两' },
  { k: '分（汉制）', g: 4.05, out: '克', mass: true, note: '汉制约3.9-4.2克；不要与近现代1钱=10分混用' },
  { k: '唐制斤', g: 220, out: '克', mass: true, note: '唐制参考：1斤约220克；不同考证值可能有差异' },
  { k: '唐制两', g: 13.75, out: '克', mass: true, note: '唐制参考：1两约13.75克' },
  { k: '唐制铢', g: 0.573, out: '克', mass: true, note: '按唐制1两约13.75克、24铢折算，约0.57克' },
  { k: '唐制分', g: 1.375, out: '克', mass: true, note: '按唐制1两约13.75克、10分折算，约1.375克；考证值有差异' },
  { k: '钱', g: 3.75, out: '克', mass: true, note: '近现代/台湾钱制：1钱=10分≈3.75克（1两=10钱）' },
  { k: '升(液体)', g: 200, out: '毫升', mass: false, note: '容量单位：1升≈200毫升，不应标为克' },
  { k: '升(半夏)', g: 130, out: '克', mass: true, note: '半夏一升≈130克；五味子/吴茱萸/蜀椒一升≈50克；葶苈子一升≈60克' },
  { k: '合(液体)', g: 20, out: '毫升', mass: false, note: '容量单位：10合=1升，约20毫升' },
  { k: '合', g: 20, out: '克', mass: true, note: '固体容量/重量需按具体药材和原文核对' },
  { k: '枚(附子大)', g: 25, out: '克', mass: true, range: '20-30', note: '附子大者1枚20-30克（中者约15克；倪师口述约3-4钱）' },
  { k: '枚(杏仁)', g: 0.4, out: '克', mass: true, note: '杏仁10枚≈4克；桃仁比例相近' },
  { k: '枚(枳实)', g: 14.4, out: '克', mass: true, note: '枳实1枚≈14.4克；瓜蒌1枚≈46克' },
  { k: '枚(乌头)', g: 4, out: '克', mass: true, range: '3-6', note: '乌头小者约3克、大者约5-6克，必须严格炮制并遵医嘱' },
  { k: '个(石膏鸡子大)', g: 40, out: '克', mass: true, note: '石膏鸡子大约40克，具体按原文核对' },
  { k: '方寸匕', g: 2, out: '克', mass: true, note: '药末约1-2克，金石类约2.74克，不能一概而论' },
  { k: '钱匕', g: 1.65, out: '克', mass: true, range: '1.5-1.8', note: '约1.5-1.8克' },
  { k: '克', g: 1, out: '克', mass: true, note: '' }
]

export default {
  data() {
    return {
      num: '1',
      unit: '钱',
      unitIdx: 8,
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
        ['1尺', '23.1厘米（长度）'],
        ['1寸', '2.31厘米（长度）']
      ],
      referenceTable: [
        ['汉制重量', '1石', '1石=120斤=29760克'],
        ['汉制重量', '1斤', '1斤=16两=248克'],
        ['汉制重量', '1两', '1两=24铢≈15.625克'],
        ['汉制重量', '1铢', '1铢≈0.65克'],
        ['台制重量', '1斤', '1斤=600克'],
        ['台制重量', '1两', '1两=10钱=37.5克'],
        ['台制重量', '1钱', '1钱=10分=3.75克'],
        ['唐制重量', '1斤', '唐制参考约220克（不同考证值可能有差异）'],
        ['唐制重量', '1两', '唐制参考约13.75克'],
        ['容量', '1升', '约200毫升'],
        ['容量', '1合', '约20毫升'],
        ['容量', '1撮', '约2毫升'],
        ['容量', '1圭', '约0.5毫升'],
        ['长度', '1尺', '23.1厘米'],
        ['长度', '1寸', '2.31厘米']
      ],
      countTable: [
        ['附子（大者）', '1枚', '20～30g'], ['附子（中者）', '1枚', '约15g'],
        ['强乌头（小者）', '1枚', '约3g'], ['强乌头（大者）', '1枚', '约5～6g'],
        ['杏仁（大者）', '10枚', '约4g'], ['枳实', '1枚', '约14.4g'],
        ['瓜蒌', '1枚', '约46g'], ['栀子', '10枚', '约15g'],
        ['石膏（鸡蛋大）', '1枚', '约40g'], ['厚朴', '1斤', '约30g'], ['竹叶', '一握', '约12g']
      ],
      volumeTable: [
        ['半夏', '1升', '约130g'], ['蜀椒', '1升', '约50g'], ['吴茱萸', '1升', '约50g'],
        ['五味子', '1升', '约50g'], ['蛴螬/虫类', '1升', '约16g'], ['葶苈子', '1升', '约60g']
      ],
      doseReference: [
        ['胖子', '五钱起'], ['普通人', '三钱'], ['小孩', '半钱～一钱'], ['甘草·病人', '五钱'], ['甘草·刚得病', '二钱']
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
      const qian = u.mass ? Math.round(g / 3.75 * 100) / 100 : 0
      const qianG = u.mass ? Math.round(qian * 3.75 * 100) / 100 : 0
      const niQian = u.k === '两' ? n : u.k === '钱' ? n : null
      this.result = { g: gR, gUnit: u.out || '克', gLabel: this.metricLabel(u), mass: !!u.mass, qian, qianG, niQian, niQianG: niQian === null ? 0 : Math.round(niQian * 3.75 * 100) / 100, niLabel: n + u.k }
    },
    metricLabel(u) {
      if (u.k === '钱') return '台制公制折算'
      if (u.k.indexOf('唐制') === 0) return '唐制公制折算'
      if (u.k === '升(液体)' || u.k === '合(液体)') return '古制容量折算'
      if (u.k === '升(半夏)' || u.k === '合') return '药材专属折算'
      if (u.k.indexOf('枚') === 0 || u.k.indexOf('个') === 0 || u.k === '方寸匕' || u.k === '钱匕') return '实物参考折算'
      return '汉制公制折算'
    },
    setQuick(q) { this.num = String(q); this.unit = '钱'; this.unitIdx = 8; this.calc() },
    setUnitQuick(n, idx) { this.num = String(n); this.unitIdx = idx; this.unit = UNITS[idx].k; this.calc() },
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
.quick-row { display: flex; align-items: center; flex-wrap: wrap; gap: 10rpx; margin-top: 16rpx; }
.quick-label { font-size: 21rpx; color: var(--ink2); }.quick-label.han { color: #8A6414; }.quick-chip { font-size: 20rpx; color: var(--brand); border: 1rpx solid var(--line); background: var(--zebra-bg); border-radius: 22rpx; padding: 7rpx 16rpx; }.han-chip { color: #8A6414; border-color: #D8BD7A; }
.c-out { margin-top: 26rpx; background: var(--zebra-bg); border-radius: 18rpx; padding: 8rpx 26rpx; }
.o-line { display: flex; align-items: center; padding: 20rpx 0; border-bottom: 1rpx dashed var(--line); }
.o-line:last-of-type { border-bottom: none; }
.o-k { width: 170rpx; font-size: 23rpx; color: var(--ink2); flex-shrink: 0; }
.o-v { font-size: 40rpx; font-weight: 800; color: var(--ink); }
.o-v.hl { font-size: 30rpx; color: var(--brand); }
.o-u { font-size: 22rpx; color: var(--ink2); font-weight: 400; }
.o-u2 { font-size: 20rpx; color: var(--ink2); font-weight: 400; }
.o-note { font-size: 20rpx; color: var(--ink2); line-height: 1.7; padding: 12rpx 0 20rpx; }
.o-warning { font-size: 20rpx; color: #9A2E1F; line-height: 1.7; background: #F5E8E8; border-radius: 10rpx; padding: 12rpx 16rpx; margin: 4rpx 0 16rpx; }
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
.tblwrap { padding: 10rpx 0; overflow: hidden; }
.tbl-caption { padding: 16rpx 22rpx 8rpx; color: var(--ink2); font-size: 20rpx; }
.tr { display: flex; }
.dose-ref { padding: 12rpx 26rpx; }.dose-line { display: flex; padding: 14rpx 0; border-bottom: 1rpx solid var(--line); color: var(--ink); font-size: 23rpx; }.dose-line:last-child { border-bottom: none; }.dose-k { width: 180rpx; color: var(--brand); font-weight: 700; }
.th { background: linear-gradient(135deg, rgba(154,46,31,.92), rgba(124,58,33,.92)); border-radius: 12rpx 12rpx 0 0; }
.th .td { color: #FDF8EE; font-weight: 700; border-top: none; }
.td { flex: 1; padding: 14rpx 22rpx; font-size: 22rpx; color: var(--ink); border-top: 1rpx solid var(--line); line-height: 1.7; }
.zebra .td { background: var(--zebra-bg); }
.warn { margin: 30rpx 32rpx 0; font-size: 20rpx; color: #A2651B; background: #FCF3DC; border-radius: 12rpx; padding: 16rpx 22rpx; line-height: 1.7; }
</style>
