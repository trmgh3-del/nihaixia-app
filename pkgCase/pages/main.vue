<template>
  <view class="page" :class="theme === 'dark' ? 'tdark' : 'tlight'">
    <view class="sbar">
      <view class="s-box">
        <image class="ico" src="/static/icons/search-gray.png" />
        <input class="s-input" v-model="q" :placeholder="tab === 'tbl' ? '搜诊断 / 方剂 / 病机 / 结果…' : '搜疾病 / 方剂 / 六经…'" />
      </view>
    </view>
    <view class="tabs">
      <view class="tab" :class="{ on: tab === 'tbl' }" @tap="tab = 'tbl'">结构化 {{ rows.length }}</view>
      <view class="tab" :class="{ on: tab === 'narr' }" @tap="tab = 'narr'">叙事分类 {{ narrCount }}</view>
      <view class="tab" :class="{ on: tab === 'yian' }" @tap="tab = 'yian'">医案集 {{ yian.length }}</view>
      <view class="tab" :class="{ on: tab === 'stats' }" @tap="tab = 'stats'">统计</view>
    </view>

    <!-- 结构化 1257 -->
    <scroll-view v-if="tab === 'tbl'" scroll-y class="scroll">
      <view class="filters">
        <view class="ft" :class="{ on: yearF === '' }" @tap="yearF = ''">全年</view>
        <view v-for="y in years" :key="y" class="ft" :class="{ on: yearF === y }" @tap="yearF = y">{{ y }} <text class="ft-n">{{ yearCount(y) }}</text></view>
      </view>
      <view class="filters" style="padding-top:0">
        <view class="ft" :class="{ on: resF === '' }" @tap="resF = ''">疗效不限</view>
        <view class="ft" :class="{ on: resF === 'good' }" @tap="resF = resF === 'good' ? '' : 'good'">✅ 有效/恢复</view>
        <view class="ft" :class="{ on: resF === 'unk' }" @tap="resF = resF === 'unk' ? '' : 'unk'">❓ 待观察</view>
      </view>
      <view class="list">
        <view v-for="r in shownRows" :key="r.n" class="c-item card fade-in" @tap="openRow(r)">
          <view class="c-head">
            <view class="c-no">#{{ r.n }}</view>
            <view class="c-diag">{{ r.diag || '未记诊断' }}</view>
            <view class="c-date">{{ shortDate(r.date) }}</view>
          </view>
          <view class="c-row" v-if="r.patient"><text class="c-k">患者</text><text class="c-v">{{ r.patient }}</text></view>
          <view class="c-row" v-if="r.bingji"><text class="c-k">病机</text><text class="c-v">{{ r.bingji }}</text></view>
          <view class="c-row" v-if="r.fangji"><text class="c-k">方剂</text><text class="c-v hl">{{ r.fangji }}</text></view>
          <view class="c-mark" v-if="r.result">{{ mark(r.result) }}</view>
        </view>
        <view v-if="loaded && !shownRows.length" class="none">无匹配医案</view>
      </view>
    </scroll-view>

    <!-- 叙事 243 -->
    <scroll-view v-else-if="tab === 'narr'" scroll-y class="scroll">
      <view class="filters">
        <view class="ft" :class="{ on: grpF === '' }" @tap="grpF = ''">全部</view>
        <view v-for="g in groups" :key="g.g" class="ft" :class="{ on: grpF === g.g }" @tap="grpF = g.g">{{ g.g }} {{ g.items.length }}</view>
      </view>
      <view class="list">
        <view v-for="it in shownNarr" :key="it.id" class="c-item card fade-in" @tap="openNarr(it)">
          <view class="c-head">
            <view class="c-no2 serif">{{ it.t }}</view>
            <view class="c-date">{{ it.date }}</view>
          </view>
          <view class="c-tags">
            <text class="c-tag" v-if="it.disease">{{ it.disease }}</text>
            <text class="c-tag mer" v-if="it.meridian">六经·{{ it.meridian }}</text>
            <text class="c-tag cat">{{ it.g }}</text>
          </view>
          <view class="c-s">{{ (it.b || '').replace(/[#>*`|-]/g, '').replace(/\s+/g, ' ').slice(0, 90) }}</view>
        </view>
        <view v-if="loaded && !shownNarr.length" class="none">无匹配医案</view>
      </view>
    </scroll-view>

    <!-- 医案集 410 -->
    <scroll-view v-else scroll-y class="scroll">
      <view class="list">
        <view v-for="it in shownYian" :key="it.id" class="c-item card fade-in" @tap="openYian(it)">
          <view class="c-head">
            <view class="c-no2 serif">{{ it.t }}</view>
            <view class="c-date">{{ it.date }}</view>
          </view>
          <view class="c-tags">
            <text class="c-tag" v-if="it.disease">{{ it.disease }}</text>
            <text class="c-tag mer" v-if="it.meridian">六经·{{ it.meridian }}</text>
          </view>
          <view class="c-s">{{ (it.b || '').replace(/[#>*`|-]/g, '').replace(/\s+/g, ' ').slice(0, 90) }}</view>
        </view>
        <view v-if="loaded && !shownYian.length" class="none">无匹配医案</view>
      </view>
    </scroll-view>

    <!-- 统计 -->
    <scroll-view v-if="tab === 'stats'" scroll-y class="scroll">
      <view class="st-wrap">
        <view class="st-card card fade-in">
          <view class="st-t serif">⟡ 年度诊疗量（{{ rows.length }} 例）</view>
          <view class="st-row" v-for="y in statYears" :key="y.k">
            <text class="st-k">{{ y.k }}</text>
            <view class="st-bar"><view class="st-in" :style="{ width: y.pct + '%' }" /></view>
            <text class="st-n">{{ y.n }}</text>
          </view>
        </view>
        <view class="st-card card fade-in" v-if="merStats.length">
          <view class="st-t serif">⟡ 叙事医案六经分布（{{ merTotal }} 例标注）</view>
          <view class="st-row" v-for="d in merStats" :key="d.k">
            <text class="st-k wide">{{ d.k }}</text>
            <view class="st-bar"><view class="st-in c4" :style="{ width: d.pct + '%' }" /></view>
            <text class="st-n">{{ d.n }}</text>
          </view>
        </view>
        <view class="st-card card fade-in">
          <view class="st-t serif">⟡ 高频诊断 TOP15</view>
          <view class="st-row" v-for="d in statDiags" :key="d.k">
            <text class="st-k wide">{{ d.k }}</text>
            <view class="st-bar"><view class="st-in c2" :style="{ width: d.pct + '%' }" /></view>
            <text class="st-n">{{ d.n }}</text>
          </view>
        </view>
        <view class="st-card card fade-in">
          <view class="st-t serif">⟡ 高频方剂 TOP15</view>
          <view class="st-row" v-for="d in statFangs" :key="d.k">
            <text class="st-k wide">{{ d.k }}</text>
            <view class="st-bar"><view class="st-in c3" :style="{ width: d.pct + '%' }" /></view>
            <text class="st-n">{{ d.n }}</text>
          </view>
        </view>
        <view class="st-note">统计口径：1257 例结构化医案总表（2005-2009，汉唐中医）。诊断/方剂按关键词计数，一例可含多词。</view>
      </view>
    </scroll-view>
  </view>
</template>

<script>
import { store , applyTheme } from '@/utils/store.js'
import { loadData } from '@/utils/data.js'
import { openMd } from '@/utils/routes.js'

export default {
  onShow() { applyTheme() },
  data() {
    return { loaded: false,
      q: '', tab: 'tbl', yearF: '', grpF: '', resF: '',
      rows: [], groups: [], yian: []
    }
  },
  computed: {
    theme() { return store.theme },
    years() {
      const ys = {}
      this.rows.forEach(r => {
        const m = String(r.date || '').match(/(20\d\d)/)
        if (m) ys[m[1]] = (ys[m[1]] || 0) + 1
      })
      return Object.keys(ys).sort()
    },
    narrCount() { return this.groups.reduce((s, g) => s + g.items.length, 0) },
    shownRows() {
      // 过滤源表空占位行（序号存在但全部字段为空，如首行）
      let list = this.rows.filter(r => r.diag || r.fangji || r.bingji || r.patient || r.result)
      if (this.yearF) list = list.filter(r => String(r.date || '').includes(this.yearF))
      if (this.resF === 'good') list = list.filter(r => /✅|👍|痊愈|恢复/.test(r.result || ''))
      if (this.resF === 'unk') list = list.filter(r => /❓|未知/.test(r.result || '') || !r.result)
      const q = this.q.trim()
      if (q) list = list.filter(r => (r.diag + r.bingji + r.fangji + r.result + r.patient + r.guandian).includes(q))
      return list.slice(0, 300)
    },
    statYears() {
      const m = {}
      this.rows.forEach(r => {
        const y = String(r.date || '').match(/(20\d\d)/)
        const k = y ? y[1] : '未记'
        m[k] = (m[k] || 0) + 1
      })
      const arr = Object.keys(m).map(k => ({ k, n: m[k] })).sort((a, b) => a.k.localeCompare(b.k))
      const max = Math.max(...arr.map(x => x.n), 1)
      return arr.map(x => ({ ...x, pct: Math.max(6, Math.round(x.n / max * 100)) }))
    },
    statDiags() { return this.topWords('diag', 15) },
    merStats() {
      const m = {}
      let total = 0
      this.groups.forEach(g => (g.items || []).forEach(it => {
        const mer = String(it.meridian || '').trim().split(/[、,，\s]/)[0]
        if (mer && mer.length <= 4) { m[mer] = (m[mer] || 0) + 1; total++ }
      }))
      const order = ['太阳', '阳明', '少阳', '太阴', '少阴', '厥阴', '太阳少阳并病', '厥阴', '少阴']
      const arr = Object.keys(m).map(k => ({ k, n: m[k] }))
        .sort((a, b) => order.indexOf(a.k) === -1 ? 99 : order.indexOf(a.k) - (order.indexOf(b.k) === -1 ? 99 : order.indexOf(b.k)))
        .sort((a, b) => (order.indexOf(a.k) === -1 ? 1 : 0) - (order.indexOf(b.k) === -1 ? 1 : 0) || order.indexOf(a.k) - order.indexOf(b.k))
        .slice(0, 8)
      const max = Math.max(...arr.map(x => x.n), 1)
      return arr.map(x => ({ ...x, pct: Math.max(6, Math.round(x.n / max * 100)) }))
    },
    merTotal() { return this.groups.reduce((s, g) => s + (g.items || []).filter(it => it.meridian).length, 0) },
    statFangs() { return this.topWords('fangji', 15) },
    shownNarr() {
      let items = []
      if (this.grpF) {
        const g = this.groups.find(x => x.g === this.grpF)
        items = g ? g.items : []
      } else items = this.groups.flatMap(g => g.items)
      const q = this.q.trim()
      if (q) items = items.filter(it => (it.t + (it.b || '') + it.disease + (it.meridian || '')).includes(q))
      return items.slice(0, 300)
    },
    shownYian() {
      const q = this.q.trim()
      if (!q) return this.yian.slice(0, 300)
      return this.yian.filter(it => (it.t + (it.b || '') + it.disease + (it.meridian || '')).includes(q)).slice(0, 300)
    }
  },
  mounted() {
    Promise.all([
      loadData('cases_table').then(d => { this.rows = d.rows || [] }),
      loadData('cases_narr').then(d => { this.groups = d.groups || [] }),
      loadData('yian').then(d => { this.yian = d.items || [] })
    ]).catch(() => {}).finally(() => { this.loaded = true })
  },
  methods: {
    yearCount(y) { return this.rows.filter(r => String(r.date || '').includes(y)).length },
    topWords(field, topN) {
      const m = {}
      const DICT = field === 'diag'
        ? ['肝癌', '乳癌', '肺癌', '脑瘤', '血癌', '淋巴癌', '大肠癌', '胰脏癌', '骨癌', '舌癌', '摄护腺癌', '肝硬化', '糖尿病', '心脏病', '高血压', '失眠', '尿毒症', '红斑狼疮', '中风', '癫痫', '忧郁症', '帕金森', '自闭症', '哮喘', 'C型肝炎', '艾滋病', '肾病', '不孕', '痛风', '关节炎', '便秘', '感冒', '水肿', '黄疸', '偏头痛']
        : ['大柴胡汤', '小柴胡汤', '葛根汤', '桂枝汤', '麻黄汤', '五苓散', '真武汤', '四逆汤', '黄连阿胶汤', '炙甘草汤', '小建中汤', '乌梅丸', '承气汤', '十枣汤', '半夏泻心汤', '柴胡桂枝汤', '桂枝茯苓丸', '肾气丸', '射干麻黄汤', '吴茱萸汤', '附子泻心汤', '旋覆代赭汤', '己椒苈黄丸', '木防己汤', '泽泻汤', '奔豚汤', '酸枣仁汤', '抵当汤', '桃核承气汤', '茵陈蒿汤', '栀子柏皮汤', '麻黄附子细辛汤', '大黄蟅虫丸', '排脓汤', '薏仁附子败酱散', '大黄牡丹皮汤', '当归四逆汤', '四物汤', '生化汤', '桂枝加桂汤', '苓桂术甘汤', '甘草泻心汤', '生姜泻心汤', '石膏', '生附子', '炮附子', '生半夏']
      this.rows.forEach(r => {
        const txt = r[field] || ''
        DICT.forEach(w => { if (txt.includes(w)) m[w] = (m[w] || 0) + 1 })
      })
      const arr = Object.keys(m).map(k => ({ k, n: m[k] })).sort((a, b) => b.n - a.n).slice(0, topN)
      const max = Math.max.apply(null, arr.map(x => x.n).concat([1]))
      return arr.map(x => ({ ...x, pct: Math.max(6, Math.round(x.n / max * 100)) }))
    },
    shortDate(d) {
      const m = String(d || '').match(/(\d{4}-\d{2}-\d{2})/)
      return m ? m[1] : String(d || '').slice(0, 12)
    },
    mark(res) {
      if (/✅|👍|痊愈|恢复/.test(res)) return '✅ 有效/恢复'
      if (/❓|未知/.test(res)) return '❓ 待观察'
      return '📊 ' + res.slice(0, 16)
    },
    openRow(r) {
      store.readerItem = { kind: 'row', item: r }
      uni.navigateTo({ url: '/pkgCase/pages/row' })
    },
    openNarr(it) {
      const list = this.shownNarr
      const idx = list.findIndex(x => x.id === it.id)
      openMd({ ...it, f: 'casesNarr', b: it.b }, it.t, { items: list.map(x => ({ ...x, f: 'casesNarr' })), idx })
    },
    openYian(it) {
      const list = this.shownYian
      const idx = list.findIndex(x => x.id === it.id)
      openMd({ ...it, f: 'yian' }, it.t, { items: list.map(x => ({ ...x, f: 'yian' })), idx })
    }
  }
}
</script>

<style scoped>
.page { height: 100vh; display: flex; flex-direction: column; background: var(--bg); }
.sbar { padding: 22rpx 32rpx; background: var(--card); flex-shrink: 0; }
.s-box { display: flex; align-items: center; background: var(--zebra-bg); border-radius: 38rpx; padding: 0 28rpx; height: 74rpx; }
.s-ico { margin-right: 14rpx; font-size: 26rpx; }
.s-input { flex: 1; font-size: 26rpx; color: var(--ink); }
.tabs { display: flex; background: var(--card); padding: 0 20rpx 20rpx; gap: 10rpx; flex-shrink: 0; }
.tab { flex: 1; text-align: center; font-size: 21rpx; padding: 14rpx 0; border-radius: 28rpx; background: var(--zebra-bg); color: var(--ink2); white-space: nowrap; overflow: hidden; }
.tab.on { background: var(--brand); color: #fff; font-weight: 700; }
.scroll { flex: 1; }
.filters { display: flex; flex-wrap: wrap; padding: 20rpx 32rpx 4rpx; }
.ft { font-size: 21rpx; color: var(--ink2); background: var(--zebra-bg); border-radius: 24rpx; padding: 8rpx 22rpx; margin: 0 12rpx 12rpx 0; }
.ft.on { background: var(--brand); color: #fff; }
.ft-n { font-size: 18rpx; opacity: .7; }
.list { padding: 12rpx 32rpx 60rpx; }
.c-item { padding: 24rpx 28rpx; margin-bottom: 20rpx; }
.c-head { display: flex; align-items: center; margin-bottom: 8rpx; }
.c-no { font-size: 21rpx; color: var(--gold); margin-right: 16rpx; font-weight: 700; }
.c-no2 { font-size: 27rpx; color: var(--ink); font-weight: 800; flex: 1; }
.c-diag { font-size: 29rpx; font-weight: 800; color: var(--brand); flex: 1; }
.c-date { font-size: 20rpx; color: var(--ink2); }
.c-row { display: flex; font-size: 22rpx; margin-top: 8rpx; }
.c-k { width: 76rpx; color: var(--ink2); flex-shrink: 0; }
.c-v { flex: 1; color: var(--ink); line-height: 1.6; }
.hl { color: var(--brand); }
.c-mark { margin-top: 10rpx; font-size: 21rpx; color: #3F6B37; background: #E8F0E4; border-radius: 8rpx; padding: 6rpx 16rpx; display: inline-block; }
.c-tags { display: flex; flex-wrap: wrap; margin-top: 8rpx; }
.c-tag { display: flex; align-items: center; height: 36rpx; font-size: 19rpx; color: #95541C; background: #FBEEE3; border-radius: 8rpx; padding: 0 14rpx; margin: 0 10rpx 8rpx 0; }
.c-tag.mer { color: #54427C; background: #EDE9F4; }
.c-tag.cat { color: #2F5D62; background: #E9F1F2; }
.c-s { font-size: 22rpx; color: var(--ink2); margin-top: 8rpx; line-height: 1.6; }
.none { text-align: center; color: var(--ink2); padding: 100rpx 0; }
.st-wrap { padding: 24rpx 32rpx 80rpx; }
.st-card { padding: 28rpx 30rpx; margin-bottom: 24rpx; }
.st-t { font-size: 29rpx; font-weight: 800; color: var(--brand); margin-bottom: 22rpx; }
.st-row { display: flex; align-items: center; margin-bottom: 16rpx; }
.st-k { width: 110rpx; font-size: 22rpx; color: var(--ink); text-align: right; margin-right: 16rpx; flex-shrink: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.st-k.wide { width: 200rpx; }
.st-bar { flex: 1; height: 22rpx; background: var(--zebra-bg); border-radius: 12rpx; overflow: hidden; }
.st-in { height: 100%; border-radius: 12rpx; background: linear-gradient(90deg, #9A2E1F, #C05A44); }
.st-in.c2 { background: linear-gradient(90deg, #8A6414, #C8A45C); }
.st-in.c3 { background: linear-gradient(90deg, #2F5D62, #5E9EA3); }
.st-in.c4 { background: linear-gradient(90deg, #54427C, #8B7BB0); }
.st-n { width: 70rpx; font-size: 21rpx; color: var(--ink2); margin-left: 14rpx; flex-shrink: 0; }
.st-note { font-size: 20rpx; color: var(--ink2); line-height: 1.7; opacity: .8; }
</style>
