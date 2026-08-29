<template>
  <view class="page" :class="theme === 'dark' ? 'tdark' : 'tlight'">
    <view class="prog" v-if="!result"><view class="prog-in" :style="{ width: progress + '%' }" /></view>

    <!-- 问诊进行中 -->
    <view class="ask card fade-in" v-if="!result">
      <view class="a-step">第 {{ stepNo }} 问 · 本路径最多 {{ totalSteps }} 问</view>
      <view class="a-q serif">{{ node.q }}</view>
      <view class="a-sub" v-if="node.sub">{{ node.sub }}</view>
      <view class="a-opts">
        <view class="a-opt" v-for="(o, i) in node.opts" :key="i" @tap="answer(o)">{{ o.t }}</view>
      </view>
      <view class="a-back" v-if="path.length" @tap="goBack">‹ 上一步</view>
    </view>

    <!-- 结果 -->
    <view class="res fade-in" v-if="result">
      <view class="r-hero">
        <view class="r-mer serif">{{ result.mer }}病方向</view>
        <view class="r-name serif">{{ result.fang }}</view>
        <view class="r-sub">本路径已完成，共回答 {{ path.length + 1 }} 个问题；根据你的回答推断的经方方向（仅供学习参考）</view>
      </view>
      <view class="r-card card" v-if="result.detail">
        <view class="rc-row" v-if="result.detail.zhizhi"><text class="rc-k">主症</text><text class="rc-v">{{ result.detail.zhizhi }}</text></view>
        <view class="rc-row" v-if="result.detail.origin"><text class="rc-k">原方</text><text class="rc-v">{{ result.detail.origin }}</text></view>
        <view class="rc-row hl" v-if="result.detail.clinical"><text class="rc-k">临床</text><text class="rc-v">{{ result.detail.clinical }}</text></view>
        <view class="rc-row" v-if="result.detail.composition"><text class="rc-k">组成</text><text class="rc-v">{{ result.detail.composition }}</text></view>
        <view class="rc-note" v-if="result.note">{{ result.note }}</view>
      </view>
      <view class="r-acts">
        <view class="r-btn main" @tap="openDetail" v-if="result.detail">查看方剂详解</view>
        <view class="r-btn" @tap="restart">↺ 重新问诊</view>
      </view>
      <view class="r-warn">⚠ 本向导按倪师六经辨证主证设计，临床需四诊合参；峻药方剂务必遵执业医师指导；急重症请立即就医。</view>
    </view>
  </view>
</template>

<script>
import { store, applyTheme } from '@/utils/store.js'
import { loadData } from '@/utils/data.js'

/* 问诊决策树：源自 SKILL 快速诊断流程图 + 六经速查表 + 感冒六经方 */
const TREE = {
  start: {
    q: '目前最突出的感觉是？', sub: '先定六经大方向',
    opts: [
      { t: '怕冷 · 发烧 · 头身痛', to: 'cold' },
      { t: '大热大渴大汗 · 不怕冷', to: 'yangming' },
      { t: '忽冷忽热 · 口苦咽干', to: 'shaoyang' },
      { t: '腹满 · 下利 · 没胃口', to: 'taiyin' },
      { t: '极度倦怠嗜睡 · 手脚冰凉', to: 'shaoyin' },
      { t: '渴不止 · 心中疼热 · 饥不欲食', to: 'jueyin' }
    ]
  },
  cold: {
    q: '出汗情况？', sub: '太阳病：有汗桂枝、无汗麻黄',
    opts: [
      { t: '有汗 · 微恶风 · 肌肉酸痛', res: { mer: '太阳', fang: '桂枝汤', note: '桂枝白芍等量；阳虚加桂、阴虚加芍（倪师口诀）。' } },
      { t: '无汗 · 骨节疼痛 · 恶寒重', to: 'mahuang' },
      { t: '后项强痛 · 喉咙痛', res: { mer: '太阳', fang: '葛根汤', note: '项强喉痛用葛根；面部中风葛根加倍（源669）。' } }
    ]
  },
  mahuang: {
    q: '咳嗽有痰吗？',
    opts: [
      { t: '不咳 · 纯表寒', res: { mer: '太阳', fang: '麻黄汤', note: '麻黄必高于桂枝；心脏病者禁用（源765）。' } },
      { t: '痰清稀 · 泡沫 · 怕冷', res: { mer: '太阳', fang: '小青龙汤', note: '外寒内饮；细辛起手1钱、重症3-5钱。' } },
      { t: '痰黄稠 · 烦躁口渴 · 外寒里热', res: { mer: '太阳', fang: '大青龙汤', note: '麻黄六两为峻剂，分三次服；体弱者慎。' } }
    ]
  },
  yangming: {
    q: '大便与腹胀情况？',
    opts: [
      { t: '便秘 · 腹胀硬痛拒按', res: { mer: '阳明', fang: '承气汤类（大/小/调胃）', note: '痞满燥实大承气、仅痞满小承气、仅燥实调胃承气。' } },
      { t: '大便尚可 · 大热大汗大渴脉洪大', res: { mer: '阳明', fang: '白虎汤（加人参）', note: '阳明经证四大数据：大热大汗大渴脉洪大。' } }
    ]
  },
  shaoyang: {
    q: '还有哪些兼症？', sub: '但见一证便是，不必悉具',
    opts: [
      { t: '胸胁苦满 · 呕心 · 目眩', res: { mer: '少阳', fang: '小柴胡汤', note: '重用柴胡为君；口苦咽干目眩往来寒热，见一证即可用。' } },
      { t: '兼便秘 · 胸胁满痛（少阳阳明并病）', res: { mer: '少阳', fang: '大柴胡汤', note: '少阳兼阳明腑实；大肠癌案例常用方。' } }
    ]
  },
  taiyin: {
    q: '下利与腹痛情况？',
    opts: [
      { t: '腹满时痛 · 下利 · 食不下', res: { mer: '太阴', fang: '理中汤', note: '脾虚寒湿主方；手足自温、脉沉缓。' } },
      { t: '下利清谷 · 完谷不化（重）', res: { mer: '太阴/少阴', fang: '四逆汤（四逆辈）', note: '里寒重症，急温之；不可再攻下。' } }
    ]
  },
  shaoyin: {
    q: '兼有水肿或心悸吗？',
    opts: [
      { t: '水肿 · 心悸 · 头眩 · 身瞤动', res: { mer: '少阴', fang: '真武汤', note: '少阴水饮主方；治肾必治心（倪师）。' } },
      { t: '无 · 但欲寐 · 脉微细 · 四肢厥逆', res: { mer: '少阴', fang: '四逆汤', note: '心肾阳虚急温之；生附子棉布包先煎。' } }
    ]
  },
  jueyin: {
    q: '手脚温度与脉象？',
    opts: [
      { t: '手足厥寒 · 脉细欲绝', res: { mer: '厥阴', fang: '当归四逆汤', note: '脚冷身温用此方；身冷才用四逆汤（倪师鉴别）。' } },
      { t: '上热下寒 · 消渴 · 气上撞心', res: { mer: '厥阴', fang: '乌梅丸', note: '寒热错杂、蛔厥久利；必须丸剂，汤剂无效（药缓力专）。' } }
    ]
  }
}

export default {
  data() {
    return { nodeKey: 'start', path: [], result: null, detail: null }
  },
  computed: {
    theme() { return store.theme },
    node() { return TREE[this.nodeKey] || TREE.start },
    stepNo() { return this.path.length + 1 },
    totalSteps() { return 3 },
    progress() { return Math.round(this.stepNo / (this.totalSteps + 1) * 100) }
  },
  onShow() { applyTheme() },
  methods: {
    answer(o) {
      if (o.to) {
        this.path.push(this.nodeKey)
        this.nodeKey = o.to
      } else if (o.res) {
        this.result = { ...o.res }
        this.loadDetail(o.res.fang)
        uni.pageScrollTo({ scrollTop: 0, duration: 200 })
      }
    },
    goBack() {
      const k = this.path.pop()
      this.nodeKey = k || 'start'
    },
    restart() {
      this.nodeKey = 'start'
      this.path = []
      this.result = null
      this.detail = null
    },
    async loadDetail(name) {
      try {
        const d = await loadData('formulas')
        const clean = name.replace(/（.*?）/g, '').replace(/类.*/, '')
        const it = (d.items || []).find(x => x.n === clean || x.n.includes(clean))
        if (it) {
          this.detail = it
          this.result.detail = it
        }
      } catch (e) { /* 无则不显示 */ }
    },
    openDetail() {
      const d = this.result.detail
      if (!d) return
      const store2 = store
      store2.readerItem = { kind: 'formula', item: d }
      uni.navigateTo({ url: '/pkgFormula/pages/detail' })
    }
  }
}
</script>

<style scoped>
.page { min-height: 100vh; background: var(--bg); padding: 0 32rpx 80rpx; }
.prog { position: fixed; top: 0; left: 0; right: 0; height: 6rpx; background: var(--zebra-bg); z-index: 50; }
.prog-in { height: 100%; background: linear-gradient(90deg, var(--gold), var(--brand)); transition: width .25s; }
.ask { margin-top: 40rpx; padding: 40rpx 36rpx; }
.a-step { font-size: 20rpx; color: var(--gold); font-weight: 700; letter-spacing: 2rpx; }
.a-q { font-size: 42rpx; font-weight: 800; color: var(--ink); margin-top: 14rpx; line-height: 1.5; }
.a-sub { font-size: 23rpx; color: var(--ink2); margin-top: 10rpx; }
.a-opts { margin-top: 36rpx; }
.a-opt { background: var(--zebra-bg); border: 2rpx solid var(--line); border-radius: 18rpx; padding: 26rpx 28rpx; font-size: 28rpx; color: var(--ink); margin-bottom: 18rpx; transition: all .15s; }
.a-opt:active { border-color: var(--brand); background: rgba(154,46,31,.06); }
.a-back { text-align: center; font-size: 24rpx; color: var(--ink2); padding: 16rpx 0 6rpx; }
.res { margin-top: 30rpx; }
.r-hero { background: linear-gradient(140deg, var(--hero1), var(--hero2)); border-radius: 24rpx; padding: 40rpx 36rpx; text-align: center; }
.r-mer { font-size: 26rpx; color: #F6E7C9; letter-spacing: 4rpx; }
.r-name { font-size: 56rpx; font-weight: 800; color: #FDF8EE; margin-top: 12rpx; letter-spacing: 4rpx; }
.r-sub { font-size: 20rpx; color: rgba(253,248,238,.8); margin-top: 14rpx; }
.r-card { margin-top: 24rpx; padding: 26rpx 30rpx; }
.rc-row { display: flex; padding: 14rpx 0; border-bottom: 1rpx dashed var(--line); font-size: 24rpx; }
.rc-row:last-of-type { border-bottom: none; }
.rc-k { width: 90rpx; color: #fff; background: var(--gold); border-radius: 8rpx; height: 40rpx; line-height: 40rpx; text-align: center; font-size: 20rpx; margin-right: 18rpx; flex-shrink: 0; align-self: flex-start; }
.rc-row.hl .rc-k { background: var(--brand); }
.rc-row.hl .rc-v { color: var(--brand); font-weight: 700; }
.rc-v { flex: 1; color: var(--ink); line-height: 1.7; }
.rc-note { font-size: 21rpx; color: var(--ink2); background: var(--quote-bg); border-radius: 12rpx; padding: 16rpx 20rpx; margin-top: 16rpx; line-height: 1.75; }
.r-acts { display: flex; gap: 18rpx; margin-top: 26rpx; }
.r-btn { flex: 1; text-align: center; border-radius: 44rpx; padding: 22rpx 0; font-size: 26rpx; font-weight: 700; border: 2rpx solid var(--brand); color: var(--brand); }
.r-btn.main { background: linear-gradient(135deg, var(--brand), var(--brand-deep)); color: #FDF8EE; border-color: transparent; }
.r-warn { margin-top: 24rpx; font-size: 20rpx; color: #A2651B; background: #FCF3DC; border-radius: 12rpx; padding: 16rpx 22rpx; line-height: 1.7; }
</style>
