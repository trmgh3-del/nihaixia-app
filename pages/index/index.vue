<template>
  <view class="page" :class="theme === 'dark' ? 'tdark' : 'tlight'">
    <!-- ===== 顶部 Hero ===== -->
    <view class="hero">
      <view class="hero-bg">
        <view class="hero-circle c1" />
        <view class="hero-circle c2" />
        <view class="hero-circle c3" />
      </view>
      <view class="statusbar" :style="{ height: sb + 'px' }" />
      <view class="hero-top">
        <view class="hero-left">
          <view class="hero-title serif">倪师经方</view>
          <view class="hero-sub">人纪 · 经方中医全库 <text class="ver">v1.0</text></view>
        </view>
        <view class="hero-right">
          <view class="date-chip serif">{{ dateStr }}</view>
          <view class="seal serif">經方</view>
        </view>
      </view>
      <view class="searchbar" @tap="goSearch">
        <image class="ico" src="/static/icons/search-gray.png" style="margin-right:14rpx" />
        <text class="s-ph">搜索条文 / 方剂 / 本草 / 医案 / 穴位…</text>
      </view>
      <view class="hero-quick">
        <view class="hq-chip" @tap="randomOne"><image class="ico-s" src="/static/icons/dice-light.png" />随机一品</view>
        <view class="hq-chip" v-if="lastRead" @tap="continueRead"><image class="ico-s" src="/static/icons/book-light.png" />继续阅读</view>
        <view class="hq-chip" @tap="goMine"><image class="ico-s" src="/static/icons/star-light.png" />收藏</view>
      </view>
    </view>

    <!-- ===== 数据总览 ===== -->
    <view class="stats card fade-in">
      <view class="stat" v-for="s in statsList" :key="s.k" @tap="statGo(s.k)">
        <view class="stat-n serif">{{ s.n }}<text class="stat-u">{{ s.u }}</text></view>
        <view class="stat-k">{{ s.k }}</view>
      </view>
    </view>

    <!-- ===== 每日一方 ===== -->
    <view class="sec">
      <view class="sec-head">
        <text class="sec-orn">❖</text>
        <text class="sec-title serif">每日一方</text>
        <text class="sec-more" @tap="goFormulas">进经方库 ›</text>
      </view>
      <view class="daily card fade-in" v-if="daily" @tap="openDaily">
        <view class="daily-seal serif">每日<br>一方</view>
        <view class="daily-head">
          <view class="daily-name serif">{{ daily.n }}</view>
          <view class="daily-tag">{{ srcShort }}</view>
        </view>
        <view class="daily-zz" v-if="daily.zhizhi">「 {{ daily.zhizhi }} 」</view>
        <view class="daily-cols" v-if="daily.origin && daily.clinical">
          <view class="d-col">
            <view class="dc-t">原方 · 汉制<text class="dc-u">1两≈15.6g</text></view>
            <view class="dc-v">{{ daily.origin }}</view>
          </view>
          <view class="d-col hl">
            <view class="dc-t">倪师临床 · 钱制<text class="dc-u">1钱≈3.75g</text></view>
            <view class="dc-v">{{ daily.clinical }}</view>
          </view>
        </view>
        <view class="daily-rows" v-else>
          <view class="daily-row" v-if="daily.zhizhi"><text class="dl">主症</text><text class="dv">{{ daily.zhizhi }}</text></view>
          <view class="daily-row" v-if="daily.origin"><text class="dl">原方</text><text class="dv">{{ daily.origin }}</text></view>
          <view class="daily-row" v-if="daily.clinical"><text class="dl">临床</text><text class="dv hl">{{ daily.clinical }}</text></view>
          <view class="daily-row" v-if="daily.composition"><text class="dl">组成</text><text class="dv">{{ daily.composition }}</text></view>
        </view>
        <view class="daily-foot">
          <view class="df-shuffle" @tap.stop="shuffleDaily"><image class="ico-s" src="/static/icons/dice-light.png" />换一方</view>
          <view class="df-more">方剂详解 ›</view>
        </view>
      </view>
    </view>

    <!-- ===== 倪师语录 ===== -->
    <view class="sec">
      <view class="quote card fade-in">
        <view class="q-mark serif">「</view>
        <view class="q-body serif">{{ dailyQuote }}</view>
        <view class="q-from">—— 倪师语录 · 每日一句</view>
      </view>
    </view>

    <!-- ===== 实用工具 ===== -->
    <view class="sec">
      <view class="sec-head">
        <text class="sec-orn">❖</text>
        <text class="sec-title serif">临证工具</text>
      </view>
      <view class="tools">
        <view class="tool card" @tap="goZiwu">
          <view class="t-ico ziwu serif">子午</view>
          <view class="t-main">
            <view class="t-name serif">子午流注</view>
            <view class="t-desc">当前{{ nowMer }}经当令</view>
          </view>
          <text class="t-arrow">›</text>
        </view>
        <view class="tool card" @tap="goConvert">
          <view class="t-ico conv serif">衡</view>
          <view class="t-main">
            <view class="t-name serif">剂量换算器</view>
            <view class="t-desc">三体系剂量互算</view>
          </view>
          <text class="t-arrow">›</text>
        </view>
        <view class="tool card" @tap="goChuanbian">
          <view class="t-ico cb serif">传</view>
          <view class="t-main">
            <view class="t-name serif">六经传变</view>
            <view class="t-desc">四种传变方式</view>
          </view>
          <text class="t-arrow">›</text>
        </view>
        <view class="tool card" @tap="goWizard">
          <view class="t-ico wz serif">问</view>
          <view class="t-main">
            <view class="t-name serif">问诊向导</view>
            <view class="t-desc">步进式问诊选方</view>
          </view>
          <text class="t-arrow">›</text>
        </view>
        <view class="tool card" @tap="goHealth">
          <view class="t-ico hp serif">健</view>
          <view class="t-main">
            <view class="t-name serif">健康自测</view>
            <view class="t-desc">六大健康标准</view>
          </view>
          <text class="t-arrow">›</text>
        </view>
        <view class="tool card" @tap="goTreat">
          <view class="t-ico tr serif">穴</view>
          <view class="t-main">
            <view class="t-name serif">症状查穴</view>
            <view class="t-desc">按症状查穴位</view>
          </view>
          <text class="t-arrow">›</text>
        </view>
      </view>
    </view>

    <!-- ===== 学习中心 ===== -->
    <view class="sec">
      <view class="study card fade-in" @tap="goStudy">
        <view class="sd-ico serif">學</view>
        <view class="sd-main">
          <view class="sd-t serif">学习中心</view>
          <view class="sd-d">闪卡背诵 · 条文背诵 · 十八反 · 煎药指南 · 学习报告 · 笔记</view>
        </view>
        <text class="sd-a">›</text>
      </view>
    </view>

    <!-- ===== 六经辨证 ===== -->
    <view class="sec">
      <view class="sec-head">
        <text class="sec-orn">❖</text>
        <text class="sec-title serif">六经辨证</text>
        <text class="sec-more" @tap="goDiag">辨证中心 ›</text>
      </view>
      <view class="meridians card fade-in">
        <view class="m-item" v-for="m in meridians" :key="m.name" :style="{ background: m.bg, color: m.fg }" @tap="openDiagGroup(m)">
          <view class="m-top">
            <view class="m-name serif">{{ m.name }}</view>
            <view class="m-kai">{{ m.kai }}</view>
          </view>
          <view class="m-fang">{{ m.f }}</view>
        </view>
      </view>
    </view>

    <!-- ===== 功能宫格 ===== -->
    <view class="sec">
      <view class="sec-head">
        <text class="sec-orn">❖</text>
        <text class="sec-title serif">知识宝库</text>
      </view>
      <view class="grid card fade-in">
        <view class="g-item" v-for="g in grids" :key="g.label" @tap="g.fn()">
          <view class="g-icon" :style="{ background: g.bg }">{{ g.icon }}</view>
          <view class="g-label">{{ g.label }}</view>
        </view>
      </view>
    </view>

    <!-- ===== 最近阅读 ===== -->
    <view class="sec" v-if="histories.length">
      <view class="sec-head">
        <text class="sec-orn">❖</text>
        <text class="sec-title serif">最近阅读</text>
        <text class="sec-more" @tap="goMine">全部 ›</text>
      </view>
      <view class="hist card fade-in">
        <view class="h-item" v-for="h in histories" :key="h.f + h.i" @tap="reopen(h)">
          <text class="h-lib">{{ libName(h.f) }}</text>
          <text class="h-t">{{ h.t }}</text>
          <text class="h-time">{{ fmtTime(h.ts) }}</text>
        </view>
      </view>
    </view>

    <view class="foot">
      <text>内容蒸馏自倪海厦人纪教学体系（开源知识库）</text>
      <text>仅供中医学习参考 · 处方用药请遵医嘱</text>
    </view>
  </view>
</template>

<script>
import { store, applyTheme } from '@/utils/store.js'
import { loadData } from '@/utils/data.js'
import { openEntry, openMd, FILE_LABEL } from '@/utils/routes.js'

export default {
  data() {
    return {
      sb: 24,
      dateStr: '',
      nowMer: '—',
      daily: null,
      histories: [],
      statsList: [],
      meridians: [
        { name: '太阳', kai: '开', f: '桂枝汤·麻黄汤', bg: '#FBEAE3', fg: '#9A2E1F', u: '太阳病' },
        { name: '阳明', kai: '阖', f: '白虎汤·承气汤', bg: '#FCF3DC', fg: '#8A6414', u: '阳明病' },
        { name: '少阳', kai: '枢', f: '小柴胡汤', bg: '#E8F0E4', fg: '#3F6B37', u: '少阳病' },
        { name: '太阴', kai: '开', f: '理中汤·四逆汤', bg: '#E9F1F2', fg: '#2F5D62', u: '太阴病' },
        { name: '少阴', kai: '枢', f: '四逆汤·真武汤', bg: '#EDE9F4', fg: '#54427C', u: '少阴病' },
        { name: '厥阴', kai: '阖', f: '乌梅丸·当归四逆', bg: '#F5E8E8', fg: '#833B3B', u: '厥阴病' }
      ],
      quotes: [
        '经方才是真正能够代表我国的正统医学。',
        '中医不立病名，只看症——同症同治，不受病名限制。',
        '脚是冷的，就定义成寒。寒不然你告诉我怎么讲，只有这个寒字最传神。',
        '上工治未病，有症状就动手，不等病名确立。',
        '胃气为生死关键——人绝水谷则死，脉无胃气亦死。',
        '阳一壮，就把阴拉起来了。',
        '不要被病名吓到。中医看的是证，不是病。',
        '知道使用经方的中医，才配被称为中医。',
        '同症同治，看病不看病名，这是中医的智慧。',
        '小肠是火，大肠是金，最上面的肺也是金——金和金是相通的。',
        '治病以阳药为主，不用补药。',
        '中医是化繁为简，看到就知道做什么。',
        '虚实寒热表里阴阳，八纲辨证一目了然。',
        '遇到脉结代，先用炙甘草汤补足里阴，再治其他。',
        '阳明无死证——但热不寒，清下二法而已。'
      ],
      grids: [
        { label: '伤寒论', icon: '伤寒', bg: '#FBEAE3', fn: () => uni.navigateTo({ url: '/pkgTexts/pages/shanghan' }) },
        { label: '金匮要略', icon: '金匮', bg: '#E9F1F2', fn: () => uni.navigateTo({ url: '/pkgTexts/pages/jingui' }) },
        { label: '黄帝内经', icon: '内经', bg: '#FCF3DC', fn: () => uni.navigateTo({ url: '/pkgTexts/pages/neijing' }) },
        { label: '神农本草', icon: '本草', bg: '#FBEAE3', fn: () => uni.navigateTo({ url: '/pkgBencao/pages/list' }) },
        { label: '经方库', icon: '方剂', bg: '#E9F1F2', fn: () => uni.navigateTo({ url: '/pkgFormula/pages/list' }) },
        { label: '针灸大成', icon: '针灸', bg: '#FCF3DC', fn: () => uni.navigateTo({ url: '/pkgZhenjiu/pages/list' }) },
        { label: '医案库', icon: '医案', bg: '#FBEAE3', fn: () => uni.navigateTo({ url: '/pkgCase/pages/main' }) },
        { label: '讲义文库', icon: '讲义', bg: '#E9F1F2', fn: () => uni.navigateTo({ url: '/pkgArticle/pages/list' }) },
        { label: '天纪易理', icon: '天纪', bg: '#FCF3DC', fn: () => uni.navigateTo({ url: '/pkgTianji/pages/list' }) },
        { label: '全文搜索', icon: '搜索', bg: '#FBEAE3', fn: () => uni.navigateTo({ url: '/pages/search/search' }) }
      ]
    }
  },
  computed: {
    theme() { return store.theme },
    stats() { return store.meta ? store.meta.counts : null },
    lastRead() { return store.history.length ? store.history[0] : null },
    dailyQuote() {
      // 用设备本地日期，不能用 Date.now()/86400000（它按 UTC 过零点，会在本地早上才切换）
      const d = new Date()
      const doy = Math.floor(Date.UTC(d.getFullYear(), d.getMonth(), d.getDate()) / 86400000)
      return this.quotes[doy % this.quotes.length]
    },
    srcShort() {
      const src = this.daily && this.daily.src
      if (!src) return '经方'
      if (src.includes('感冒')) return '感冒六经方'
      if (src.includes('关键方剂')) return '六经主方'
      if (src.includes('速查卡')) return '剂量速查卡'
      if (src.includes('C类')) return '临床勘误'
      return '临床剂量速查'
    }
  },
  onShow() {
    this.histories = store.history.slice(0, 6)
    this.sb = uni.getSystemInfoSync().statusBarHeight || 24
    const d = new Date()
    const wk = ['日', '一', '二', '三', '四', '五', '六'][d.getDay()]
    this.dateStr = `${d.getMonth() + 1}月${d.getDate()}日 · 周${wk}`
    const MERS = { 23: '胆', 0: '胆', 1: '肝', 2: '肝', 3: '肺', 4: '肺', 5: '大肠', 6: '大肠', 7: '胃', 8: '胃', 9: '脾', 10: '脾', 11: '心', 12: '心', 13: '小肠', 14: '小肠', 15: '膀胱', 16: '膀胱', 17: '肾', 18: '肾', 19: '心包', 20: '心包', 21: '三焦', 22: '三焦' }
    const chinaNow = new Date(Date.now() + 8 * 3600000)
    this.nowMer = MERS[chinaNow.getUTCHours()] || '—'
    applyTheme()
    // 首页可能长期驻留，不重新挂载；每次回到首页都检查本地日期是否已变化
    this.refreshDaily()
  },
  mounted() {
    this.init()
    // 页面保持打开跨过本地午夜时，也能自动切换；回到页面时 onShow 还会再次校验
    this._dailyTimer = setInterval(() => this.refreshDaily(), 30000)
  },
  onUnload() {
    if (this._dailyTimer) {
      clearInterval(this._dailyTimer)
      this._dailyTimer = null
    }
  },
  methods: {
    async init() {
      try {
        const meta = await loadData('meta')
        store.meta = meta
        const c = meta.counts
        this.statsList = [
          { n: String(c.shanghanSun + c.shanghanQue + c.wujing), u: '节', k: '伤寒全篇' },
          { n: String(c.jingui), u: '篇', k: '金匮要略' },
          { n: String(c.neijing), u: '篇', k: '黄帝内经' },
          { n: String(c.herbs), u: '味', k: '神农本草' },
          { n: String(c.formulas), u: '方', k: '经方库' },
          { n: String(c.casesTable + c.casesNarr + c.yian), u: '例', k: '医案全集' },
          { n: String(c.points), u: '穴', k: '针灸穴位' },
          { n: String(c.articles), u: '篇', k: '讲义文库' }
        ]
      } catch (e) { console.error(e) }
      try {
        const fm = await loadData('formulas')
        const items = (fm.items || []).filter(x => x.clinical && x.origin)
        this._pool = items
        this.refreshDaily(true)
      } catch (e) { console.error(e) }
    },
    refreshDaily(force = false) {
      if (!this._pool || !this._pool.length) return
      const d = new Date()
      const key = `${d.getFullYear()}-${d.getMonth() + 1}-${d.getDate()}`
      if (!force && this._dailyDayKey === key) return
      // 基于本地年月日计算，保证每天固定一方，并在跨本地午夜后自动更新
      const dayNumber = Math.floor(Date.UTC(d.getFullYear(), d.getMonth(), d.getDate()) / 86400000)
      this.daily = this._pool[dayNumber % this._pool.length]
      this._dailyDayKey = key
    },
    goSearch() { uni.navigateTo({ url: '/pages/search/search' }) },
    goFormulas() { uni.navigateTo({ url: '/pkgFormula/pages/list' }) },
    goDiag() { uni.switchTab({ url: '/pages/diagnosis/diagnosis' }) },
    goMine() { uni.switchTab({ url: '/pages/mine/mine' }) },
    async randomOne() {
      try {
        uni.showLoading({ title: '抽取中' })
        const idx = await loadData('index')
        const pool = idx.filter(e => e.c !== 'case' || e.f === 'casesNarr')
        const e = pool[Math.floor(Math.random() * pool.length)]
        uni.hideLoading()
        if (e) openEntry({ f: e.f, c: e.c, i: e.i, t: e.t })
      } catch (err) {
        uni.hideLoading()
        uni.showToast({ title: '打开失败', icon: 'none' })
      }
    },
    goZiwu() { uni.navigateTo({ url: '/pkgZhenjiu/pages/ziwu' }) },
    goStudy() { uni.navigateTo({ url: '/pages/study/study' }) },
    goChuanbian() { uni.navigateTo({ url: '/pages/diagnosis/chuanbian' }) },
    goWizard() { uni.navigateTo({ url: '/pages/diagnosis/wizard' }) },
    goHealth() { uni.navigateTo({ url: '/pages/health/health' }) },
    goTreat() { uni.navigateTo({ url: '/pkgZhenjiu/pages/treat' }) },
    goConvert() { uni.navigateTo({ url: '/pkgFormula/pages/convert' }) },
    statGo(k) {
      const map = {
        '伤寒全篇': '/pkgTexts/pages/shanghan', '金匮篇': '/pkgTexts/pages/jingui', '内经篇': '/pkgTexts/pages/neijing',
        '本草': '/pkgBencao/pages/list', '方剂': '/pkgFormula/pages/list', '医案': '/pkgCase/pages/main',
        '穴位': '/pkgZhenjiu/pages/list', '讲义': '/pkgArticle/pages/list'
      }
      if (map[k]) uni.navigateTo({ url: map[k] })
    },
    continueRead() {
      const h = store.history[0]
      if (h) openEntry({ f: h.f, i: h.i, t: h.t })
    },
    openDaily() {
      if (!this.daily) return
      openEntry({ f: 'formulas', c: 'formula', i: this.daily.id, t: this.daily.n })
    },
    shuffleDaily() {
      if (!this._pool || !this._pool.length) return
      let next = this.daily
      let guard = 0
      while (next.id === (this.daily && this.daily.id) && guard++ < 20) {
        next = this._pool[Math.floor(Math.random() * this._pool.length)]
      }
      this.daily = next
    },
    openDiagGroup(m) {
      // 先记入全局待处理（页面未创建时事件会丢），再广播
      store.pendingDiag = m.name
      uni.switchTab({ url: '/pages/diagnosis/diagnosis' })
    },
    reopen(h) { openEntry({ f: h.f, i: h.i, t: h.t }) },
    libName(f) {
      const map = { shanghan: '伤寒', jingui: '金匮', neijing: '内经', bencao: '本草', formulas: '方剂', zhenjiu: '针灸', casesTable: '医案', casesNarr: '医案', yian: '医案', articles: '文库', skill: '内核', tianji: '天纪', diag: '辨证', misc: '文档' }
      return map[f] || '文档'
    },
    fmtTime(ts) {
      const d = new Date(ts)
      const p = n => (n < 10 ? '0' + n : n)
      return `${p(d.getMonth() + 1)}/${p(d.getDate())} ${p(d.getHours())}:${p(d.getMinutes())}`
    }
  }
}
</script>

<style scoped>
.page { min-height: 100vh; background: var(--bg); padding-bottom: 40rpx; }

/* Hero */
.hero { position: relative; background: linear-gradient(150deg, var(--hero1), var(--hero2)); padding: 0 32rpx 46rpx; border-radius: 0 0 44rpx 44rpx; overflow: hidden; }
.hero-bg { position: absolute; inset: 0; }
.hero-circle { position: absolute; border-radius: 50%; opacity: .12; background: #F6E7C9; }
.c1 { width: 420rpx; height: 420rpx; top: -160rpx; right: -100rpx; }
.c2 { width: 260rpx; height: 260rpx; bottom: -90rpx; left: -60rpx; opacity: .08; }
.c3 { width: 130rpx; height: 130rpx; top: 90rpx; left: 46%; opacity: .07; }
.hero-top { position: relative; display: flex; justify-content: space-between; align-items: center; padding: 28rpx 8rpx 20rpx; }
.hero-title { font-size: 52rpx; font-weight: 800; color: #FDF8EE; letter-spacing: 6rpx; }
.hero-sub { font-size: 22rpx; color: rgba(253, 248, 238, .85); margin-top: 10rpx; }
.ver { background: rgba(253, 248, 238, .2); border-radius: 8rpx; padding: 2rpx 12rpx; font-size: 20rpx; margin-left: 10rpx; }
.hero-right { display: flex; flex-direction: column; align-items: center; }
.date-chip { font-size: 19rpx; color: rgba(253,248,238,.85); border: 1rpx solid rgba(253,248,238,.35); border-radius: 22rpx; padding: 3rpx 16rpx; margin-bottom: 12rpx; letter-spacing: 2rpx; }
.seal { width: 104rpx; height: 104rpx; border: 5rpx solid rgba(253, 248, 238, .9); border-radius: 18rpx; color: #FDF8EE; display: flex; align-items: center; justify-content: center; font-size: 40rpx; font-weight: 800; letter-spacing: 4rpx; transform: rotate(6deg); box-shadow: inset 0 0 0 3rpx rgba(253, 248, 238, .35); }
.searchbar { position: relative; background: rgba(253, 251, 245, .96); border-radius: 44rpx; height: 84rpx; display: flex; align-items: center; padding: 0 32rpx; box-shadow: 0 8rpx 24rpx rgba(60, 20, 8, .25); }
.s-icon { font-size: 30rpx; margin-right: 16rpx; }
.searchbar .ico { margin-right: 14rpx; }
.s-ph { color: #9C9284; font-size: 26rpx; }
.hero-quick { position: relative; display: flex; margin-top: 20rpx; }
.hq-chip { display: flex; align-items: center; background: rgba(253,248,238,.18); border: 1rpx solid rgba(253,248,238,.4); color: #FDF8EE; border-radius: 30rpx; padding: 8rpx 24rpx; font-size: 22rpx; margin-right: 16rpx; }
.hq-chip .ico-s { margin-right: 10rpx; }

/* 统计 */
.stats { margin: -30rpx 32rpx 0; position: relative; display: flex; flex-wrap: wrap; padding: 26rpx 10rpx 14rpx; }
.stat { width: 25%; text-align: center; margin-bottom: 14rpx; }
.stat-n { font-size: 34rpx; font-weight: 800; color: var(--brand); }
.stat-u { font-size: 19rpx; font-weight: 500; color: var(--gold); margin-left: 4rpx; }
.stat-k { font-size: 21rpx; color: var(--ink2); margin-top: 2rpx; }

/* 区块 */
.sec { margin: 34rpx 32rpx 0; }
.sec-head { display: flex; align-items: center; margin-bottom: 20rpx; }
.sec-orn { color: var(--gold); font-size: 24rpx; margin-right: 12rpx; }
.sec-title { font-size: 34rpx; font-weight: 800; color: var(--ink); letter-spacing: 2rpx; }
.sec-more { margin-left: auto; font-size: 24rpx; color: var(--ink2); }

/* 每日一方 */
.daily { padding: 28rpx 30rpx; position: relative; overflow: hidden; }
.daily::after { content: '經方'; position: absolute; right: -14rpx; bottom: -32rpx; font-size: 120rpx; color: var(--brand); opacity: .045; font-weight: 800; letter-spacing: 8rpx; }
.daily-seal { position: absolute; top: 20rpx; right: 22rpx; width: 84rpx; height: 84rpx; border: 3rpx solid var(--brand); border-radius: 12rpx; color: var(--brand); font-size: 26rpx; font-weight: 800; line-height: 1.3; text-align: center; display: flex; align-items: center; justify-content: center; transform: rotate(6deg); opacity: .75; background: rgba(154,46,31,.04); }
.daily-head { display: flex; align-items: center; margin-bottom: 14rpx; padding-right: 100rpx; }
.daily-name { font-size: 38rpx; font-weight: 800; color: var(--brand); letter-spacing: 2rpx; }
.daily-tag { margin-left: auto; display: flex; align-items: center; height: 44rpx; box-sizing: border-box; font-size: 20rpx; color: var(--gold); border: 1rpx solid var(--gold); border-radius: 8rpx; padding: 0 12rpx; }
.daily-zz { font-size: 24rpx; color: var(--ink2); line-height: 1.7; padding: 2rpx 0 16rpx; border-bottom: 1rpx dashed var(--line); margin-bottom: 18rpx; }
.daily-cols { display: flex; }
.d-col { flex: 1; min-width: 0; background: var(--zebra-bg); border-radius: 16rpx; padding: 16rpx 18rpx; }
.d-col.hl { background: rgba(154,46,31,.06); margin-left: 12rpx; }
.dc-t { font-size: 19rpx; color: var(--ink2); font-weight: 700; margin-bottom: 8rpx; }
.d-col.hl .dc-t { color: var(--brand); }
.dc-u { font-size: 15rpx; font-weight: 400; opacity: .7; margin-left: 8rpx; }
.dc-v { font-size: 21rpx; color: var(--ink); line-height: 1.75; display: -webkit-box; -webkit-box-orient: vertical; -webkit-line-clamp: 4; overflow: hidden; }
.d-col.hl .dc-v { color: var(--brand); font-weight: 600; }
.daily-rows .daily-row { display: flex; margin-top: 10rpx; font-size: 24rpx; }
.dl { flex-shrink: 0; color: #fff; background: var(--gold); border-radius: 8rpx; padding: 2rpx 14rpx; margin-right: 16rpx; font-size: 21rpx; height: 40rpx; line-height: 40rpx; }
.daily-rows .dv { flex: 1; color: var(--ink); }
.hl { color: var(--brand); font-weight: 600; }
.daily-foot { display: flex; align-items: center; margin-top: 20rpx; }
.df-shuffle { display: flex; align-items: center; font-size: 22rpx; color: #FDF8EE; background: linear-gradient(135deg, var(--gold), #B08D45); border-radius: 28rpx; padding: 8rpx 26rpx; }
.df-shuffle .ico-s { margin-right: 8rpx; }
.df-more { margin-left: auto; font-size: 23rpx; color: var(--brand); font-weight: 700; }

/* 倪师语录 */
.quote { position: relative; padding: 30rpx 34rpx; background: linear-gradient(135deg, var(--quote-bg), var(--card)); overflow: hidden; }
.q-mark { position: absolute; left: 18rpx; top: 2rpx; font-size: 80rpx; color: var(--gold); opacity: .35; }
.q-body { font-size: 27rpx; color: var(--ink); line-height: 1.9; letter-spacing: 1rpx; text-align: justify; }
.q-from { text-align: right; font-size: 19rpx; color: var(--gold); margin-top: 12rpx; }
/* 学习中心 */
.study { display: flex; align-items: center; padding: 28rpx 28rpx; background: linear-gradient(135deg, #3A241E, #241713); }
.sd-ico { width: 88rpx; height: 88rpx; border-radius: 22rpx; border: 2rpx solid rgba(246,231,201,.5); color: #F6E7C9; font-size: 40rpx; font-weight: 800; display: flex; align-items: center; justify-content: center; }
.sd-main { flex: 1; margin-left: 24rpx; }
.sd-t { font-size: 32rpx; font-weight: 800; color: #FDF8EE; letter-spacing: 2rpx; }
.sd-d { font-size: 19rpx; color: rgba(253,248,238,.75); margin-top: 8rpx; }
.sd-a { color: rgba(253,248,238,.7); font-size: 34rpx; }

/* 临证工具：3列网格（minmax(0,1fr) 防内容撑破） */
.tools { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 14rpx; }
.tool { display: flex; flex-direction: column; align-items: center; padding: 22rpx 8rpx 16rpx; }
.t-ico { width: 84rpx; height: 84rpx; border-radius: 20rpx; display: flex; align-items: center; justify-content: center; font-size: 30rpx; font-weight: 800; flex-shrink: 0; }
.t-ico.ziwu { background: #E9F1F2; color: #2F5D62; }
.t-ico.conv { background: #FCF3DC; color: #8A6414; }
.t-main { text-align: center; margin-top: 14rpx; }
.t-name { font-size: 24rpx; font-weight: 800; color: var(--ink); white-space: nowrap; }
.t-desc { font-size: 17rpx; color: var(--ink2); margin-top: 6rpx; text-align: center; line-height: 1.4; display: -webkit-box; -webkit-box-orient: vertical; -webkit-line-clamp: 2; overflow: hidden; max-width: 100%; word-break: break-all; }
.tool { min-width: 0; }
.t-arrow { display: none; }
.t-ico.cb { background: #F5E8E8; color: #833B3B; }
.t-ico.wz { background: #EDE9F4; color: #54427C; }
.t-ico.hp { background: #E8F0E4; color: #3F6B37; }
.t-ico.tr { background: #FBEEE3; color: #95541C; }

/* 六经：3×2 栅格 + 开阖枢角标 */
.meridians { display: grid; grid-template-columns: repeat(3, 1fr); gap: 14rpx; padding: 20rpx; }
.m-item { height: 122rpx; border-radius: 18rpx; padding: 18rpx 20rpx 16rpx; box-sizing: border-box; display: flex; flex-direction: column; justify-content: space-between; }
.m-top { display: flex; align-items: center; }
.m-name { font-size: 31rpx; font-weight: 800; letter-spacing: 5rpx; }
.m-kai { margin-left: auto; width: 36rpx; height: 36rpx; display: flex; align-items: center; justify-content: center; font-size: 19rpx; line-height: 1; opacity: .65; border: 1.5rpx solid currentColor; border-radius: 10rpx; }
.m-fang { font-size: 19rpx; opacity: .82; letter-spacing: 1rpx; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

/* 宫格 */
.grid { display: flex; flex-wrap: wrap; padding: 20rpx 0; }
.g-item { width: 20%; display: flex; flex-direction: column; align-items: center; margin-bottom: 26rpx; }
.g-icon { width: 88rpx; height: 88rpx; border-radius: 24rpx; display: flex; align-items: center; justify-content: center; font-size: 28rpx; font-weight: 800; color: var(--ink); position: relative; box-shadow: inset 0 0 0 3rpx rgba(255,255,255,.55); }
.g-icon::after { content: ''; position: absolute; inset: 5rpx; border: 1.5rpx solid rgba(60,44,22,.14); border-radius: 16rpx; }
.g-label { font-size: 23rpx; color: var(--ink2); margin-top: 10rpx; }

/* 最近阅读 */
.hist { padding: 8rpx 26rpx; }
.h-item { display: flex; align-items: center; padding: 22rpx 0; border-bottom: 1rpx solid var(--line); }
.h-item:last-child { border-bottom: none; }
.h-lib { flex-shrink: 0; display: flex; align-items: center; height: 36rpx; font-size: 18rpx; color: var(--gold); border: 1rpx solid var(--gold); border-radius: 8rpx; padding: 0 10rpx; margin-right: 16rpx; opacity: .85; }
.h-t { flex: 1; font-size: 27rpx; color: var(--ink); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.h-time { font-size: 21rpx; color: var(--ink2); }

.foot { margin: 60rpx 32rpx 20rpx; text-align: center; color: var(--ink2); font-size: 21rpx; line-height: 2; opacity: .8; }
</style>
