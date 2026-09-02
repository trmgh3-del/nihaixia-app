<template>
  <view class="page" :class="theme === 'dark' ? 'tdark' : 'tlight'">
    <view class="banner">
      <image class="b-taiji" src="/static/tabbar/yinyang-on.png" mode="aspectFit" />
      <view class="b-title serif">辨证中心</view>
      <view class="b-sub">先辨六经，再选方剂 —— 八公式 · 流程图 · 脉舌速查 · 症状自查</view>
      <view class="b-cb" @tap="goChuanbian">⟐ 传变规律</view>
    </view>

    <!-- tabs -->
    <view class="tabs">
      <view v-for="(t, i) in tabs" :key="t.k" class="tab" :class="{ on: tab === t.k }" @tap="tab = t.k">{{ t.label }}</view>
    </view>

    <!-- ============ Tab 公式 ============ -->
    <view v-if="tab === 'gongshi'" class="tab-body fade-in">
      <view class="seg-nav">
        <view v-for="sg in segs" :key="sg.k" class="seg-cell" :class="{ on: seg === sg.k }" @tap="switchSeg(sg.k)">
          <text class="seg-name serif">{{ sg.k }}</text>
          <text class="seg-n">{{ sg.n }}</text>
        </view>
      </view>

      <view class="grp">
        <view class="grp-title serif">
          <text class="grp-orn">❖</text>{{ segTitle }}<text class="grp-n">{{ gongshiItems.length }}节</text>
        </view>
        <view class="acc card">
          <view v-for="(it, i) in gongshiItems" :key="it.id" class="acc-item" :class="{ 'no-b': i === gongshiItems.length - 1, open: opened['L' + it.id] }" :id="'acc-' + it.id">
            <view class="acc-head" @tap="toggle('L' + it.id)">
              <text class="acc-t">{{ it.t }}</text>
              <text class="acc-a" :class="{ open: opened['L' + it.id] }">›</text>
            </view>
            <view v-if="opened['L' + it.id]" class="acc-body">
              <md-blocks :blocks="blocksOf(it)" :base="26" />
            </view>
          </view>
        </view>
      </view>

      <view class="grp" v-if="seg === '' || seg === '速查'">
        <view class="grp-title serif">
          <text class="grp-orn">❖</text>诊断经验汇编<text class="grp-n">感冒六方 · 病机十九条</text>
        </view>
        <view class="acc card">
          <view v-for="(it, i) in expItems" :key="it.id" class="acc-item" :class="{ 'no-b': i === expItems.length - 1, open: opened['E' + it.id] }" :id="'acc-' + it.id">
            <view class="acc-head" @tap="toggle('E' + it.id)">
              <text class="acc-t">{{ it.t }}</text>
              <text class="acc-a" :class="{ open: opened['E' + it.id] }">›</text>
            </view>
            <view v-if="opened['E' + it.id]" class="acc-body">
              <md-blocks :blocks="blocksOf(it)" :base="26" />
            </view>
          </view>
        </view>
      </view>
    </view>

    <!-- ============ Tab 自查 ============ -->
    <view v-if="tab === 'zicha'" class="tab-body fade-in">
      <view class="sz-entry card" @tap="goSizhen">
        <view class="sze-ico serif">诊</view>
        <view class="sze-main"><view class="sze-t serif">四诊合参工作台</view><view class="sze-s">望闻问切 → 八纲判定 → 六经倾向 → 参考方剂</view></view>
        <text class="sze-a">›</text>
      </view>
      <view class="wz-entry card" @tap="goWizard">
        <view class="we-ico serif">问</view>
        <view class="we-main"><view class="we-t serif">感冒六经问诊向导</view><view class="we-s">一问一答 · 步进式循证 → 推荐方剂与剂量</view></view>
        <text class="we-a">›</text>
      </view>
      <view class="zc-tip card">
        <text class="zc-tip-t">◌ 症状自查（六经定位）</text>
        <text class="zc-tip-d">按倪师「先辨六经」思路：勾选当前症状 → 查看六经评分与主方建议。合病常见，结果仅供学习参考。</text>
      </view>
      <view class="zc-grp card" v-for="g in symptomGroups" :key="g.name">
        <view class="zc-grp-t">{{ g.name }}</view>
        <view class="zc-opts">
          <view v-for="o in g.opts" :key="o.k" class="zc-opt" :class="{ on: picked[o.k] }" @tap="pick(o.k)">{{ o.label }}</view>
        </view>
      </view>
      <view class="zc-btn" :class="{ dis: !pickedCount }" @tap="analyze">{{ pickedCount ? '开始分析（已选 ' + pickedCount + ' 项）' : '请先勾选症状' }}</view>
      <view class="zc-res card fade-in" v-if="result">
        <view class="zc-res-t serif">⟡ 辨证参考</view>
        <view class="zc-mer" v-for="r in result.mers" :key="r.name">
          <view class="zm-head">
            <text class="zm-name serif" :style="{ color: r.color }">{{ r.name }}</text>
            <view class="zm-bar"><view class="zm-in" :style="{ width: r.pct + '%', background: r.color }" /></view>
            <text class="zm-score">{{ r.score }}分</text>
          </view>
          <view class="zm-fang" v-if="r.fang">主方：<text class="hl">{{ r.fang }}</text></view>
          <view class="zm-note">{{ r.note }}</view>
        </view>
        <view class="zc-warn">⚠ 合病/并病临床常见（如太阳伤寒兼里虚）。本工具仅按六经主证计分，不能替代四诊合参与医师面诊；急重症请立即就医。</view>
        <view class="zc-reset" @tap="resetPick">↺ 重新选择症状</view>
      </view>
    </view>

    <!-- ============ Tab 脉舌&流程 ============ -->
    <view v-if="tab === 'maishe'" class="tab-body fade-in">
      <view class="grp">
        <view class="grp-title serif"><text class="grp-orn">❖</text>脉诊 · 舌诊 · 鉴别</view>
        <view class="acc card">
          <view v-for="(it, i) in maisheItems" :key="it.id" class="acc-item" :class="{ 'no-b': i === maisheItems.length - 1, open: opened['ms' + it.id] }" :id="'acc-' + it.id">
            <view class="acc-head" @tap="toggle('ms' + it.id)">
              <text class="acc-t">{{ it.t }}</text><text class="acc-a" :class="{ open: opened['ms' + it.id] }">›</text>
            </view>
            <view v-if="opened['ms' + it.id]" class="acc-body"><md-blocks :blocks="blocksOf(it)" :base="26" /></view>
          </view>
        </view>
      </view>
    </view>

    <!-- ============ Tab 速查总库 ============ -->
    <view v-if="tab === 'cangku'" class="tab-body fade-in">
      <view class="g-filter scroll-x">
        <scroll-view scroll-x class="chips-scroll">
          <view class="chips-row">
            <view class="g-chip" :class="{ 'chip-on': ckFilter === '' }" @tap="ckFilter = ''">全部</view>
            <view v-for="g2 in skillH2s" :key="g2" class="g-chip" :class="{ 'chip-on': ckFilter === g2 }" @tap="ckFilter = g2">{{ g2 }}</view>
          </view>
        </scroll-view>
      </view>
      <view class="acc card">
        <view v-for="(it, i) in skillFiltered" :key="it.id" class="acc-item" :class="{ 'no-b': i === skillFiltered.length - 1 }">
          <view class="acc-head" @tap="openSkill(it)">
            <view class="acc-main">
              <text class="acc-t">{{ it.t }}</text>
              <text class="acc-sub">{{ it.h2 }}</text>
            </view>
            <text class="acc-a">›</text>
          </view>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
import { store , applyTheme } from '@/utils/store.js'
import { loadData } from '@/utils/data.js'
import { parseMd, setFangNames, getFangNames } from '@/utils/md.js'
import { openMd } from '@/utils/routes.js'

const SYMPTOMS = [
  { name: '寒热', opts: [
    { k: '恶寒', label: '怕冷/恶寒', w: { 太阳: 3 } },
    { k: '恶风', label: '怕风', w: { 太阳: 2 } },
    { k: '发烧', label: '发烧', w: { 太阳: 1, 阳明: 1 } },
    { k: '但热不寒', label: '但热不寒', w: { 阳明: 3 } },
    { k: '往来寒热', label: '忽冷忽热', w: { 少阳: 3 } },
    { k: '厥逆', label: '手脚冰凉至肘膝', w: { 少阴: 3 } },
    { k: '上热下寒', label: '上热下寒', w: { 厥阴: 3 } }] },
  { name: '汗', opts: [
    { k: '有汗', label: '有汗', w: { 太阳: 2 } },
    { k: '无汗', label: '无汗', w: { 太阳: 2 } },
    { k: '大汗', label: '大汗不止', w: { 阳明: 2, 少阴: 1 } }] },
  { name: '头身', opts: [
    { k: '头项强痛', label: '头项强痛', w: { 太阳: 3 } },
    { k: '目眩', label: '头晕目眩', w: { 少阳: 2, 少阴: 1 } },
    { k: '肌肉酸痛', label: '肌肉酸痛', w: { 太阳: 1 } },
    { k: '身重水肿', label: '身重/水肿', w: { 少阴: 2, 太阴: 1 } }] },
  { name: '胸腹', opts: [
    { k: '胸胁苦满', label: '胸胁胀满', w: { 少阳: 3 } },
    { k: '心悸', label: '心悸/心跳慢', w: { 少阴: 2 } },
    { k: '气上撞心', label: '气上撞心/心中疼热', w: { 厥阴: 3 } },
    { k: '腹满', label: '腹满/腹胀', w: { 太阴: 3, 阳明: 1 } },
    { k: '胃家实', label: '便秘腹胀硬痛', w: { 阳明: 3 } }] },
  { name: '口渴饮食', opts: [
    { k: '口苦咽干', label: '口苦/咽干', w: { 少阳: 3 } },
    { k: '大渴', label: '大渴喜冷饮', w: { 阳明: 2 } },
    { k: '消渴', label: '渴饮不止(消渴)', w: { 厥阴: 3 } },
    { k: '饥不欲食', label: '饥而不欲食', w: { 厥阴: 3 } },
    { k: '食不下', label: '食不下/没胃口', w: { 太阴: 3 } }] },
  { name: '二便', opts: [
    { k: '便秘', label: '便秘', w: { 阳明: 2 } },
    { k: '下利清谷', label: '下利清谷(寒泻)', w: { 少阴: 2, 太阴: 2 } },
    { k: '小便不利', label: '小便不利', w: { 少阴: 1, 太阴: 1 } }] },
  { name: '睡眠神志', opts: [
    { k: '但欲寐', label: '但欲寐(倦怠嗜睡)', w: { 少阴: 3 } },
    { k: '烦躁谵语', label: '烦躁/谵语', w: { 阳明: 2 } },
    { k: '失眠', label: '失眠心烦', w: { 厥阴: 1, 少阴: 1 } }] },
  { name: '脉舌', opts: [
    { k: '脉浮', label: '脉浮', w: { 太阳: 3 } },
    { k: '脉洪大', label: '脉洪大', w: { 阳明: 3 } },
    { k: '脉微细', label: '脉微细', w: { 少阴: 3 } },
    { k: '脉弦', label: '脉弦', w: { 少阳: 2 } },
    { k: '舌淡苔白', label: '舌淡苔白', w: { 太阴: 1, 少阴: 1 } },
    { k: '舌红苔黄燥', label: '舌红苔黄燥', w: { 阳明: 2 } }] }
]

const MER_INFO = {
  太阳: { color: '#9A2E1F', note: '表证第一关。有汗桂枝汤，无汗麻黄汤；项强喉痛加葛根。' },
  阳明: { color: '#8A6414', note: '但热不寒。经证大热大汗大渴→白虎汤；腑实便秘腹满→承气汤类。' },
  少阳: { color: '#3F6B37', note: '半表半里，但见一证便是（口苦、往来寒热、胸胁苦满）→ 小柴胡汤。' },
  太阴: { color: '#2F5D62', note: '脾虚寒湿：腹满吐利、食不下 → 理中汤；重则四逆汤。' },
  少阴: { color: '#54427C', note: '心肾阳虚，急温之：脉微细但欲寐 → 四逆汤；水饮心悸头眩 → 真武汤。' },
  厥阴: { color: '#833B3B', note: '阴之尽，寒热并结：消渴气上撞心 → 乌梅丸；手足厥寒脉细 → 当归四逆汤。' }
}

export default {
  onShow() {
    applyTheme()
    if (store.pendingDiag) {
      const name = store.pendingDiag
      store.pendingDiag = ''
      this.tab = 'gongshi'
      setTimeout(() => this.jumpMeridian(name), 350)
    }
  },
  data() {
    return {
      tab: 'gongshi',
      tabs: [
        { k: 'gongshi', label: '辨证公式' },
        { k: 'zicha', label: '症状自查' },
        { k: 'maishe', label: '脉舌鉴别' },
        { k: 'cangku', label: '速查总库' }
      ],
      meridians: [
        { name: '太阳', bg: '#FBEAE3', fg: '#9A2E1F' }, { name: '阳明', bg: '#FCF3DC', fg: '#8A6414' },
        { name: '少阳', bg: '#E8F0E4', fg: '#3F6B37' }, { name: '太阴', bg: '#E9F1F2', fg: '#2F5D62' },
        { name: '少阴', bg: '#EDE9F4', fg: '#54427C' }, { name: '厥阴', bg: '#F5E8E8', fg: '#833B3B' }
      ],
      diagGroups: [],
      maisheItems: [],
      skillUnits: [],
      ckFilter: '',
      opened: {},
      seg: '',
      picked: {},
      result: null,
      _blk: {}
    }
  },
  computed: {
    theme() { return store.theme },
    symptomGroups() { return SYMPTOMS },
    pickedCount() { return Object.keys(this.picked).filter(k => this.picked[k]).length },
    segs() {
      const base = [{ k: '总览' }, { k: '太阳' }, { k: '阳明' }, { k: '少阳' }, { k: '太阴' }, { k: '少阴' }, { k: '厥阴' }, { k: '速查' }]
      base.forEach(sg => { sg.n = this.itemsOfSeg(sg.k).length })
      return base
    },
    gongshiItems() {
      if (this.seg === '') {
        const g = this.diagGroups[0]
        return g ? g.items : []
      }
      return this.itemsOfSeg(this.seg)
    },
    expItems() {
      const g = this.diagGroups[1]
      return g ? g.items : []
    },
    segTitle() {
      return this.seg === '' ? '六经辨证诊断公式 · 全部' : this.seg === '速查' ? '脉舌鉴别与速查' : this.seg + '病 · 诊断公式'
    },
    skillH2s() {
      const seen = []
      for (const u of this.skillUnits) if (u.h2 && !seen.includes(u.h2) && u.h2.length < 14) seen.push(u.h2)
      return seen.slice(0, 14)
    },
    skillFiltered() {
      if (!this.ckFilter) return this.skillUnits.slice(0, 60)
      return this.skillUnits.filter(u => u.h2 === this.ckFilter)
    }
  },
  mounted() {
    this.init()
    this.ensureFang()
    uni.$on('diag-focus', name => { this.jumpMeridian(name) })
    uni.$on('diag-group', gid => {
      this.tab = 'gongshi'
      const g = this.diagGroups.find(x => x.g === gid)
      if (g) this.opened[g.label + g.items[0].id] = true
    })
  },
  beforeUnmount() {
    uni.$off('diag-focus')
    uni.$off('diag-group')
  },
  methods: {
    async init() {
      try {
        const diag = await loadData('diagnosis')
        this.diagGroups = (diag.groups || []).map(g => ({ g: g.g, label: g.label, items: g.items }))
        this._diagLoaded = true
        if (this.diagGroups.length) {
          const g0 = this.diagGroups[0]
          const first = g0.items.find(x => x.t.includes('总览') || x.t.includes('总纲')) || g0.items[0]
          this.opened['L' + first.id] = true
        }
      } catch (e) { console.error(e) }
      try {
        const su = await loadData('skill_units')
        this.skillUnits = su.units || []
        this.maisheItems = this.skillUnits.filter(u =>
          /脉诊速查|舌诊速查|真寒假热|太阴与少阴交界|快速诊断流程图|七步走/.test(u.t))
      } catch (e) { console.error(e) }
    },
    blocksOf(it) {
      const k = 'd' + it.id
      if (!this._blk[k]) this._blk[k] = parseMd(it.b)
      return this._blk[k]
    },
    goChuanbian() { uni.navigateTo({ url: '/pages/diagnosis/chuanbian' }) },
    goSizhen() { uni.navigateTo({ url: '/pages/diagnosis/sizhen' }) },
    goWizard() { uni.navigateTo({ url: '/pages/diagnosis/wizard' }) },
    itemsOfSeg(k) {
      const g = this.diagGroups[0]
      if (!g) return []
      const items = g.items
      if (k === '总览') return items.filter(x => ['总纲', '六经开阖枢总览', '伤寒论经方两大补虚方', '六经表里关系与气血特征', '传变规律'].some(p => x.t === p || x.t.startsWith(p)))
      if (k === '速查') return items.filter(x => ['快速诊断流程图', '脉诊速查', '舌诊速查', '真寒假热', '真热假寒', '脉舌矛盾', '脉象组合', '舌象组合', '太阴与少阴交界', '七步走', '金匮杂病', '金匮特有方剂', '倪海厦临床心法', '诚实边界'].some(p => x.t.startsWith(p)))
      return items.filter(x => x.t.startsWith('诊断公式') && x.t.includes('：' + k))
    },
    switchSeg(k) {
      this.seg = this.seg === k ? '' : k
      this.opened = {}
      const list = this.gongshiItems
      if (list.length) this.opened['L' + list[0].id] = true
      uni.pageScrollTo({ scrollTop: 0, duration: 200 })
    },
    toggle(k) { this.opened[k] = !this.opened[k] },
    openSkill(it) { openMd({ ...it, f: 'skill' }, it.t) },
    async ensureFang() {
      if (getFangNames().length) return
      try {
        const d = await loadData('formulas')
        globalThis.__NX_FORMULA_ITEMS__ = d.items || []
        setFangNames([...new Set((d.items || []).map(x => x.n))])
      } catch (e) { /* noop */ }
    },
    jumpMeridian(name) {
      this.tab = 'gongshi'
      const tryJump = () => {
        if (!this._diagLoaded) return false
        const k = ['太阳', '阳明', '少阳', '太阴', '少阴', '厥阴'].includes(name) ? name : ''
        this.seg = k
        this.opened = {}
        const items = k ? this.itemsOfSeg(k) : this.itemsOfSeg('总览')
        if (!items.length) return false
        items.forEach(x => { this.opened['L' + x.id] = true })
        this.$nextTick(() => this.scrollToItem(items[0]))
        return true
      }
      if (!tryJump()) {
        let n = 0
        const timer = setInterval(() => {
          n++
          if (tryJump() || n > 15) clearInterval(timer)
        }, 200)
      }
    },
    scrollToItem(it) {
      const sel = '#acc-' + it.id
      setTimeout(() => {
        try {
          const q = uni.createSelectorQuery().in(this)
          q.select(sel).boundingClientRect()
          q.selectViewport().scrollOffset()
          q.exec(res => {
            const rect = res && res[0]
            const vp = res && res[1]
            if (rect && vp && typeof vp.scrollTop === 'number') {
              uni.pageScrollTo({ scrollTop: Math.max(0, rect.top + vp.scrollTop - 100), duration: 260 })
            } else if (rect) {
              uni.pageScrollTo({ selector: sel, duration: 260 })
            }
          })
        } catch (e) {
          uni.pageScrollTo({ selector: sel, duration: 260 })
        }
      }, 150)
    },
    pick(k) { this.picked[k] = !this.picked[k] },
    resetPick() {
      this.picked = {}
      this.result = null
      uni.pageScrollTo({ scrollTop: 0, duration: 250 })
    },
    analyze() {
      const score = {}
      SYMPTOMS.forEach(g => g.opts.forEach(o => {
        if (this.picked[o.k]) Object.keys(o.w).forEach(m => { score[m] = (score[m] || 0) + o.w[m] })
      }))
      const mers = Object.keys(score).map(m => ({ name: m, score: score[m] })).sort((a, b) => b.score - a.score)
      if (!mers.length) { uni.showToast({ title: '请先勾选症状', icon: 'none' }); return }
      const max = mers[0].score || 1
      const list = mers.slice(0, 3).map((r, i) => {
        const info = MER_INFO[r.name]
        return {
          name: r.name, score: r.score, pct: Math.max(12, Math.round(r.score / max * 100)),
          color: info.color, note: info.note,
          fang: i === 0 ? this.pickFang(r.name) : ''
        }
      })
      this.result = { mers: list }
      uni.pageScrollTo({ selector: '.zc-res', duration: 300 })
    },
    pickFang(m) {
      const p = this.picked
      if (m === '太阳') {
        if (p['头项强痛'] && (p['喉咙痛'] || p['口渴'])) return '葛根汤（项强喉痛）'
        return p['无汗'] ? '麻黄汤（无汗）' : p['有汗'] ? '桂枝汤（有汗）' : '桂枝汤/麻黄汤（辨有汗无汗）'
      }
      if (m === '阳明') return (p['便秘'] || p['胃家实']) ? '承气汤类（腑实）' : '白虎汤（经证大热）'
      if (m === '少阳') return '小柴胡汤'
      if (m === '太阴') return '理中汤'
      if (m === '少阴') return (p['身重水肿'] || p['心悸'] || p['小便不利']) ? '真武汤（水饮）' : '四逆汤'
      if (m === '厥阴') return p['厥逆'] ? '当归四逆汤（手足厥寒）' : '乌梅丸'
      return ''
    }
  }
}
</script>

<style scoped>
.page { min-height: 100vh; background: var(--bg); padding-bottom: 60rpx; }
.banner { position: relative; overflow: hidden; background: linear-gradient(140deg, var(--hero1), var(--hero2)); padding: 42rpx 36rpx 34rpx; }
.b-taiji { position: absolute; right: -30rpx; top: -30rpx; width: 220rpx; height: 220rpx; opacity: .16; transform: rotate(-18deg); pointer-events: none; }
.b-title, .b-sub, .b-cb { position: relative; z-index: 2; }
.b-cb { display: flex; align-items: center; width: max-content; height: 48rpx; margin: 18rpx 0 0 auto; font-size: 20rpx; color: #FDF8EE; background: rgba(253,248,238,.16); border: 1rpx solid rgba(253,248,238,.4); border-radius: 26rpx; padding: 0 22rpx; }
.b-title { font-size: 44rpx; font-weight: 800; color: #FDF8EE; letter-spacing: 4rpx; line-height: 1.3; }
.b-sub { max-width: 92%; font-size: 21rpx; color: rgba(253,248,238,.85); margin-top: 12rpx; line-height: 1.65; }
.tabs { position: sticky; top: 0; z-index: 20; display: flex; background: var(--card); border-radius: 0 0 28rpx 28rpx; margin: 0 0; padding: 0 20rpx; box-shadow: 0 6rpx 20rpx rgba(60,44,22,.05); }
.tab { flex: 1; text-align: center; padding: 26rpx 0 20rpx; font-size: 27rpx; color: var(--ink2); border-bottom: 6rpx solid transparent; position: relative; transition: color .2s, transform .2s; }
.tab:active { transform: scale(.96); }
.tab.on { color: var(--brand); font-weight: 800; border-bottom: 6rpx solid transparent; }
.tab.on::after { content: ''; position: absolute; left: 22%; right: 22%; bottom: 6rpx; height: 8rpx; border-radius: 8rpx; background: linear-gradient(90deg, var(--gold), var(--brand)); }
.tab-body { padding: 26rpx 32rpx 0; }

/* 六经分组导航：4×2 紧凑网格 */
.seg-nav { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12rpx; margin-bottom: 24rpx; }
.seg-cell { background: var(--card); border: 1rpx solid var(--line); border-radius: 14rpx; padding: 12rpx 0 10rpx; display: flex; flex-direction: column; align-items: center; }
.seg-cell.on { background: linear-gradient(135deg, var(--brand), var(--brand-deep)); border-color: var(--brand); box-shadow: 0 4rpx 14rpx rgba(154,46,31,.28); }
.seg-name { font-size: 26rpx; font-weight: 800; letter-spacing: 3rpx; color: var(--ink); }
.seg-cell.on .seg-name { color: #FDF8EE; }
.seg-n { font-size: 17rpx; color: var(--ink2); margin-top: 2rpx; }
.seg-cell.on .seg-n { color: rgba(253,248,238,.8); }
.g-filter { margin-bottom: 22rpx; }
.chips-scroll { width: 100%; }
.chips-row { display: flex; padding: 4rpx 0; }
.g-chip { flex-shrink: 0; padding: 12rpx 30rpx; border-radius: 32rpx; font-size: 25rpx; margin-right: 14rpx; background: var(--zebra-bg); color: var(--ink2); }
.chip-on { background: var(--brand) !important; color: #fff !important; }
.grp { margin-bottom: 34rpx; }
.grp-title { display: flex; align-items: center; font-size: 30rpx; font-weight: 800; color: var(--ink); margin-bottom: 16rpx; }
.grp-orn { color: var(--gold); font-size: 22rpx; margin-right: 10rpx; }
.grp-n { margin-left: auto; font-size: 21rpx; color: var(--ink2); font-weight: 400; }

.acc { padding: 4rpx 28rpx; }
.acc-item { border-bottom: 1rpx solid var(--line); transition: background .2s; }
.acc-item.no-b { border-bottom: none; }
.acc-item.open { background: var(--zebra-bg); }
.acc-item.open .acc-t { color: var(--brand); }
.acc-head { display: flex; align-items: center; padding: 26rpx 4rpx; }
.acc-main { flex: 1; min-width: 0; }
.acc-t { font-size: 28rpx; color: var(--ink); font-weight: 600; }
.acc-sub { display: block; font-size: 21rpx; color: var(--ink2); margin-top: 4rpx; }
.acc-a { color: var(--ink2); font-size: 34rpx; transform: rotate(90deg); transition: transform .2s; }
.acc-a.open { transform: rotate(-90deg); }
.acc-body { padding: 4rpx 0 30rpx; border-top: 1rpx dashed var(--line); margin-top: -6rpx; padding-top: 22rpx; min-width: 0; max-width: 100%; overflow: hidden; box-sizing: border-box; }

/* 自查 */
.sz-entry { display: flex; align-items: center; padding: 22rpx 28rpx; margin-bottom: 16rpx; background: linear-gradient(135deg, #FBEAE3, var(--card)); }
.sze-ico { width: 72rpx; height: 72rpx; border-radius: 18rpx; background: var(--brand); color: #FDF8EE; font-size: 32rpx; font-weight: 800; display: flex; align-items: center; justify-content: center; }
.sze-main { flex: 1; margin-left: 22rpx; }
.sze-t { font-size: 29rpx; font-weight: 800; color: var(--brand); }
.sze-s { font-size: 19rpx; color: var(--ink2); margin-top: 6rpx; }
.sze-a { color: var(--brand); font-size: 32rpx; }
.wz-entry { display: flex; align-items: center; padding: 24rpx 28rpx; margin-bottom: 20rpx; background: linear-gradient(135deg, #EDE9F4, var(--card)); }
.we-ico { width: 72rpx; height: 72rpx; border-radius: 18rpx; background: #54427C; color: #FDF8EE; font-size: 32rpx; font-weight: 800; display: flex; align-items: center; justify-content: center; }
.we-main { flex: 1; margin-left: 22rpx; }
.we-t { font-size: 29rpx; font-weight: 800; color: #54427C; }
.we-s { font-size: 20rpx; color: var(--ink2); margin-top: 6rpx; }
.we-a { color: #54427C; font-size: 32rpx; }
.zc-tip { padding: 26rpx 30rpx; margin-bottom: 24rpx; }
.zc-tip-t { display: block; font-weight: 800; color: var(--brand); font-size: 29rpx; margin-bottom: 10rpx; }
.zc-tip-d { font-size: 23rpx; color: var(--ink2); line-height: 1.7; }
.zc-grp { padding: 24rpx 28rpx; margin-bottom: 20rpx; }
.zc-grp-t { font-size: 26rpx; font-weight: 700; color: var(--ink); margin-bottom: 18rpx; }
.zc-opts { display: flex; flex-wrap: wrap; }
.zc-opt { padding: 12rpx 26rpx; border-radius: 32rpx; background: var(--zebra-bg); color: var(--ink2); font-size: 24rpx; margin: 0 16rpx 16rpx 0; border: 1rpx solid transparent; }
.zc-opt.on { background: var(--brand); color: #fff; border-color: var(--brand); }
.zc-btn { margin: 30rpx 0; background: linear-gradient(135deg, var(--brand), var(--brand-deep)); color: #FDF8EE; text-align: center; padding: 26rpx 0; border-radius: 44rpx; font-size: 29rpx; font-weight: 700; letter-spacing: 2rpx; }
.zc-btn.dis { opacity: .45; }
.zc-res { padding: 30rpx; }
.zc-res-t { font-size: 31rpx; font-weight: 800; color: var(--brand); margin-bottom: 20rpx; }
.zc-mer { margin-bottom: 26rpx; }
.zm-head { display: flex; align-items: center; }
.zm-name { font-size: 31rpx; font-weight: 800; width: 90rpx; }
.zm-bar { flex: 1; height: 16rpx; background: var(--zebra-bg); border-radius: 10rpx; overflow: hidden; margin: 0 18rpx; }
.zm-in { height: 100%; border-radius: 10rpx; }
.zm-score { font-size: 23rpx; color: var(--ink2); width: 76rpx; text-align: right; }
.zm-fang { font-size: 26rpx; margin-top: 12rpx; color: var(--ink); }
.zm-note { font-size: 23rpx; color: var(--ink2); margin-top: 6rpx; line-height: 1.7; }
.hl { color: var(--brand); font-weight: 700; }
.zc-warn { margin-top: 10rpx; font-size: 22rpx; color: #A2651B; background: #FCF3DC; border-radius: 12rpx; padding: 16rpx 20rpx; line-height: 1.7; }
.zc-reset { margin-top: 20rpx; text-align: center; font-size: 24rpx; color: var(--brand); font-weight: 700; padding: 14rpx 0; border: 1rpx dashed var(--brand); border-radius: 36rpx; opacity: .85; }
</style>
