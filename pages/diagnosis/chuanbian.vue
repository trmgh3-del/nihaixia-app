<template>
  <view class="page" :class="theme === 'dark' ? 'tdark' : 'tlight'">
    <!-- 传变路径图 -->
    <view class="chain card">
      <view class="c-title serif">⟡ 六经传变路径（主线与阳明分支）</view>
      <view class="nodes">
        <view class="node-wrap" v-for="(n, i) in chain" :key="n.k">
          <view class="node" :style="{ background: n.bg, color: n.fg }">
            <view class="n-k serif">{{ n.k }}</view>
            <view class="n-s">{{ n.s }}</view>
          </view>
          <view class="arr" v-if="i < chain.length - 1">▼</view>
        </view>
      </view>
      <view class="zhijie">
        <view class="zj-line" />
        <view class="zj-tag">直中：体虚者邪不经三阳，直接中三阴（起病即见四逆、下利、但欲寐）</view>
      </view>
    </view>

    <!-- 四种传变 -->
    <view class="sec">
      <view class="sec-head"><text class="sec-orn">❖</text><text class="sec-title serif">传变四式（倪师·伤寒论条文4-8）</text></view>
      <view class="ways">
        <view class="way card" v-for="w in ways" :key="w.k">
          <view class="w-head" :style="{ color: w.color }">
            <text class="w-k serif">{{ w.k }}</text>
            <text class="w-p">{{ w.p }}</text>
          </view>
          <view class="w-d">{{ w.d }}</view>
        </view>
      </view>
      <view class="no-chuan card">辨传与不传：伤寒一日太阳受之——「脉若静者，为不传；颇欲吐、若躁烦、脉数急者，为传也。」脉静症静则守方，脉数急、烦躁、欲吐即是传经之兆。</view>
    </view>

    <!-- 传变规律原文（数据驱动） -->
    <view class="sec" v-if="items.length">
      <view class="sec-head"><text class="sec-orn">❖</text><text class="sec-title serif">正传 · 误治 · 预警 · 欲解时</text><text class="sec-n">{{ items.length }}节</text></view>
      <view class="acc card">
        <view v-for="(it, i) in items" :key="it.id" class="acc-item" :class="{ 'no-b': i === items.length - 1, open: opened[it.id] }">
          <view class="acc-head" @tap="opened[it.id] = !opened[it.id]">
            <text class="acc-t">{{ it.t.replace('传变规律 · ', '') }}</text>
            <text class="acc-a" :class="{ open: opened[it.id] }">›</text>
          </view>
          <view v-if="opened[it.id]" class="acc-body"><md-blocks :blocks="blocksOf(it)" :base="26" /></view>
        </view>
      </view>
    </view>

    <view class="warn">⚠ 传变判断须四诊合参：脉象由静转数急、神志由静转烦、症状由表入里皆是传经之兆；本页仅供学习参考，急重症请立即就医。</view>
  </view>
</template>

<script>
import { store, applyTheme } from '@/utils/store.js'
import { loadData } from '@/utils/data.js'
import { parseMd } from '@/utils/md.js'

const CHAIN = [
  { k: '太阳', s: '表 · 一关', bg: '#FBEAE3', fg: '#9A2E1F' },
  { k: '少阳', s: '枢 · 半表半里', bg: '#E8F0E4', fg: '#3F6B37' },
  { k: '阳明', s: '阖 · 里热（病位可停）', bg: '#FCF3DC', fg: '#8A6414' }
  { k: '太阴', s: '脾虚寒湿', bg: '#E9F1F2', fg: '#2F5D62' },
  { k: '少阴', s: '心肾阳虚', bg: '#EDE9F4', fg: '#54427C' },
  { k: '厥阴', s: '寒热错杂', bg: '#F5E8E8', fg: '#833B3B' }
]

export default {
  data() {
    return {
      chain: CHAIN,
      items: [],
      opened: {},
      ways: [
        { k: '循经传', p: '依次传递', color: '#9A2E1F', d: '常见主线为太阳→少阳→太阴→少阴→厥阴；太阳进入阳明后病位可停，具体仍须以四诊和条文证据判断，不是机械必经顺序。' },
        { k: '越经传', p: '隔经而传', color: '#8A6414', d: '不按次序，隔一经或隔二经而传（如太阳直入少阳、太阳越传太阴），多因误治伤正或邪气亢盛。' },
        { k: '表里传', p: '表里相注', color: '#2F5D62', d: '相表里的经直接互传，如太阳传入少阴（表寒直入里虚）——最凶险，医者当先察「有表证兼见里虚」者先温里。' },
        { k: '直中', p: '不经三阳', color: '#54427C', d: '体素虚弱或阳衰之人，邪气不经三阳径中三阴：一起病即见但欲寐、下利清谷、四肢厥逆，急温之（四逆辈）。' }
      ],
      _blk: {}
    }
  },
  computed: {
    theme() { return store.theme }
  },
  onShow() { applyTheme(); this.initOnce() },
  methods: {
    async initOnce() {
      if (this._inited) return
      this._inited = true
      try {
        const d = await loadData('diagnosis')
        const g = d.groups[0]
        this.items = (g.items || []).filter(x => x.t.startsWith('传变规律'))
        if (this.items.length) this.opened[this.items[0].id] = true
      } catch (e) { console.error(e) }
    },
    blocksOf(it) {
      if (!this._blk[it.id]) this._blk[it.id] = parseMd(it.b)
      return this._blk[it.id]
    }
  }
}
</script>

<style scoped>
.page { min-height: 100vh; background: var(--bg); padding-bottom: 60rpx; }
.chain { margin: 26rpx 32rpx 0; padding: 30rpx; }
.c-title { font-size: 30rpx; font-weight: 800; color: var(--brand); margin-bottom: 24rpx; }
.nodes { display: flex; flex-direction: column; align-items: center; }
.node-wrap { display: flex; flex-direction: column; align-items: center; width: 100%; }
.node { width: 86%; border-radius: 18rpx; padding: 18rpx 30rpx; display: flex; align-items: center; justify-content: space-between; }
.n-k { font-size: 32rpx; font-weight: 800; letter-spacing: 4rpx; }
.n-s { font-size: 21rpx; opacity: .85; }
.arr { color: var(--gold); font-size: 22rpx; margin: 6rpx 0; }
.zhijie { margin-top: 20rpx; display: flex; align-items: center; }
.zj-line { width: 6rpx; align-self: stretch; background: linear-gradient(180deg, var(--gold), #54427C); border-radius: 4rpx; margin-right: 20rpx; }
.zj-tag { flex: 1; font-size: 21rpx; color: var(--ink2); line-height: 1.8; background: var(--zebra-bg); border-radius: 0 14rpx 14rpx 0; padding: 14rpx 20rpx; }
.sec { margin: 30rpx 32rpx 0; }
.sec-head { display: flex; align-items: center; margin-bottom: 18rpx; }
.sec-orn { color: var(--gold); font-size: 22rpx; margin-right: 10rpx; }
.sec-title { font-size: 30rpx; font-weight: 800; color: var(--ink); letter-spacing: 2rpx; }
.sec-n { margin-left: auto; font-size: 21rpx; color: var(--ink2); }
.ways { display: flex; flex-wrap: wrap; gap: 16rpx; }
.way { width: 48.5%; padding: 22rpx 24rpx; box-sizing: border-box; }
.w-head { display: flex; align-items: baseline; flex-wrap: wrap; }
.w-k { font-size: 29rpx; font-weight: 800; margin-right: 12rpx; }
.w-p { font-size: 19rpx; opacity: .7; }
.w-d { font-size: 21rpx; color: var(--ink2); line-height: 1.75; margin-top: 10rpx; text-align: justify; }
.no-chuan { margin-top: 16rpx; padding: 22rpx 26rpx; font-size: 22rpx; color: var(--ink); line-height: 1.9; background: var(--quote-bg); }
.acc { padding: 4rpx 28rpx; }
.acc-item { border-bottom: 1rpx solid var(--line); transition: background .2s; }
.acc-item.no-b { border-bottom: none; }
.acc-item.open { background: var(--zebra-bg); }
.acc-item.open .acc-t { color: var(--brand); }
.acc-head { display: flex; align-items: center; padding: 26rpx 4rpx; }
.acc-t { font-size: 28rpx; color: var(--ink); font-weight: 600; flex: 1; }
.acc-a { color: var(--ink2); font-size: 34rpx; transform: rotate(90deg); transition: transform .2s; }
.acc-a.open { transform: rotate(-90deg); }
.acc-body { padding: 4rpx 0 30rpx; }
.warn { margin: 30rpx 32rpx 0; font-size: 20rpx; color: #A2651B; background: #FCF3DC; border-radius: 12rpx; padding: 16rpx 22rpx; line-height: 1.7; }
</style>
