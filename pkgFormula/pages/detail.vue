<template>
  <view class="page" :class="theme === 'dark' ? 'tdark' : 'tlight'">
    <view class="hero" v-if="f">
      <view class="f-name serif">{{ f.n }}</view>
      <view class="f-alias" v-if="f.alias">别名：{{ Array.isArray(f.alias) ? f.alias.join('、') : f.alias }}</view>
      <view class="f-flags">
        <view class="f-tag" v-if="f.meridian">{{ f.meridian }}</view>
        <view class="f-tag" v-if="f.category">{{ f.category }}</view>
        <view class="f-tag review" v-if="f.expertStatus">资料审核：{{ f.expertStatus === 'approved' ? '已审核' : '待审核' }}</view>
        <view class="f-tag" v-if="f.src">{{ f.src }}</view>
        <view class="f-fav" @tap="doFav">{{ fav ? '★' : '☆' }}</view>
      </view>
    </view>

    <view class="body" v-if="f">
      <view class="sec card fade-in" v-if="f.zhizhi">
        <view class="s-t serif"><text class="s-orn">▍</text>主症关键</view>
        <view class="s-v" :style="{ fontSize: fs }">{{ f.zhizhi }}</view>
      </view>
      <view class="sec card fade-in" v-if="f.composition">
        <view class="s-t serif"><text class="s-orn">▍</text>组成</view>
        <view class="s-v" :style="{ fontSize: fs }">{{ f.composition }}</view>
      </view>
      <view class="sec card fade-in" v-if="f.components && f.components.length">
        <view class="s-t serif"><text class="s-orn">▍</text>逐味组成（点击药名查看本草）</view>
        <view class="component-list"><view class="component-chip" v-for="c in f.components" :key="c.name" @tap="openHerb(c.name)">{{ c.name }}<text v-if="c.dosage"> {{ c.dosage }}</text></view></view>
      </view>
      <view class="sec card fade-in" v-if="f.origin">
        <view class="s-t serif"><text class="s-orn">▍</text>古代原方 <text class="s-unit">汉朝度量衡 · 1两≈15.6g</text></view>
        <view class="s-v" :style="{ fontSize: fs }">{{ f.origin }}</view>
      </view>
      <view class="sec card fade-in hl-card" v-if="f.clinical">
        <view class="s-t serif"><text class="s-orn">▍</text>倪师临床剂量 <text class="s-unit">台湾制 · 1钱≈3.75g</text></view>
        <view class="s-v clinical" :style="{ fontSize: fs }">{{ f.clinical }}</view>
      </view>
      <view class="sec card fade-in" v-if="f.preparation">
        <view class="s-t serif"><text class="s-orn">▍</text>煎服法</view>
        <view class="s-v" :style="{ fontSize: fs }">{{ f.preparation }}</view>
      </view>
      <view class="sec card fade-in danger-card" v-if="f.contraindication">
        <view class="s-t serif"><text class="s-orn">▍</text>禁忌与风险</view>
        <view class="s-v caution" :style="{ fontSize: fs }">{{ f.contraindication }}</view>
      </view>
      <view class="sec card fade-in" v-if="f.doses">
        <view class="s-t serif"><text class="s-orn">▍</text>逐味剂量（原文）</view>
        <view class="s-v" :style="{ fontSize: fs }">{{ f.doses }}</view>
      </view>
      <view class="sec card fade-in" v-if="f.note">
        <view class="s-t serif"><text class="s-orn">▍</text>备注 · 核对点</view>
        <view class="s-v note" :style="{ fontSize: fs }">{{ f.note }}</view>
      </view>

      <view class="others card fade-in" v-if="others.length">
        <view class="o-t">同名方剂其他来源记录</view>
        <view v-for="(o, i) in others" :key="i" class="o-item" @tap="switchTo(o)">
          <text class="o-src">{{ o.src }}</text>
          <text class="o-v">{{ (o.clinical || o.doses || o.composition || o.zhizhi || '').slice(0, 40) }}</text>
          <text class="o-a">›</text>
        </view>
      </view>

      <view class="related card fade-in" v-if="cases.length">
        <view class="rl-t serif">相关医案 · {{ cases.length }} 例（1257例总表反查）</view>
        <view class="rl-item" v-for="c in cases" :key="c.n" @tap="openCase(c)">
          <view class="rl-no serif">#{{ c.n }}</view>
          <view class="rl-main">
            <view class="rl-top">
              <text class="rl-diag serif">{{ c.diag || '未记诊断' }}</text>
              <text class="rl-mark" v-if="c.result">{{ /✅|👍|痊愈|恢复/.test(c.result) ? '✓效' : /❓|未知/.test(c.result) ? '观察' : '' }}</text>
            </view>
            <view class="rl-bingji" v-if="c.bingji">{{ c.bingji.slice(0, 30) }}</view>
            <view class="rl-fang" v-if="c.fangji">「{{ c.fangji.slice(0, 40) }}」</view>
          </view>
          <text class="rl-a">›</text>
        </view>
      </view>

      <view class="acts">
        <view class="act copy" @tap="copyAll"><image class="ico-s" src="/static/icons/copy-light.png" />复制完整方卡</view>
      </view>
      <view class="warn">剂量引自倪师讲课文稿（口述/换算标注）。用药请遵执业医嘱，峻药（附子/半夏/麻黄等）尤须谨慎。</view>
    </view>
    <view class="empty-state" v-if="!f">
    <view class="es-orn serif">空</view>
    <view class="es-t">请从「经方库」选择方剂进入</view>
    <view class="es-btn" @tap="goBack">‹ 返回</view>
  </view>
</view>
</template>

<script>
import { store, isFav, toggleFav, pushHistory , applyTheme } from '@/utils/store.js'
import { loadData } from '@/utils/data.js'

export default {
  onShow() { applyTheme() },
  data() {
    return { all: [], current: null, cases: [] }
  },
  computed: {
    theme() { return store.theme },
    f() { return this.current },
    fav() { return this.current ? isFav('formulas', this.current.id) : false },
    others() { return this.all.filter(x => x.n === (this.current && this.current.n) && x.id !== this.current.id) },
    fs() { return Math.round(26 * (store.fontScale || 1)) + 'rpx' }
  },
  mounted() {
    const r = store.readerItem
    if (r && r.kind === 'formula') {
      this.current = r.item
      uni.setNavigationBarTitle({ title: r.item.n.slice(0, 14) , fail: () => {} })
      pushHistory({ f: 'formulas', i: r.item.id, t: r.item.n, c: 'formula' })
      loadData('formulas').then(d => { this.all = d.items || [] }).catch(() => {})
      this.loadCases()
    }
  },
  methods: {
    goBack() { uni.navigateBack({ fail: () => uni.switchTab({ url: '/pages/index/index' }) }) },
    loadCases() {
      const cur = () => this.current
      loadData('cases_table').then(d => {
        const f = cur()
        if (!f) return
        const name = f.n
        const rows = (d.rows || []).filter(r => r.fangji && String(r.fangji).includes(name)).slice(0, 8)
        this.cases = rows
      }).catch(() => {})
    },
    openCase(c) {
      store.readerItem = { kind: 'row', item: c }
      uni.navigateTo({ url: '/pkgCase/pages/row' })
    },
    switchSegGuard() {},
    async openHerb(name) {
      try {
        const d = await loadData('bencao')
        const herb = (d.herbs || []).find(h => h.n === name || h.canonicalName === name || (h.aliases || []).includes(name))
        if (herb) { store.readerItem = { kind: 'herb', item: herb }; uni.navigateTo({ url: '/pkgBencao/pages/herb' }) }
        else uni.showToast({ title: '未找到本草条目', icon: 'none' })
      } catch (e) { uni.showToast({ title: '本草库加载失败', icon: 'none' }) }
    },
    switchTo(o) {
      this.current = o
      uni.pageScrollTo({ scrollTop: 0 })
    },
    doFav() {
      const c = this.current
      const added = toggleFav({ f: 'formulas', i: c.id, t: c.n, s: (c.clinical || c.zhizhi || '').slice(0, 60), c: 'formula' })
      uni.showToast({ title: added ? '已收藏' : '已取消', icon: 'none' })
    },
    copyAll() {
      const f = this.current
      const lines = [`【${f.n}】`]
      if (f.zhizhi) lines.push('主症：' + f.zhizhi)
      if (f.composition) lines.push('组成：' + f.composition)
      if (f.origin) lines.push('原方：' + f.origin)
      if (f.clinical) lines.push('倪师临床：' + f.clinical)
      if (f.doses) lines.push('逐味剂量：' + f.doses)
      if (f.note) lines.push('备注：' + f.note)
      lines.push('（倪师经方App · 仅供学习参考，遵医嘱）')
      uni.setClipboardData({ data: lines.join('\n') })
    }
  }
}
</script>

<style scoped>
.empty-state { display: flex; flex-direction: column; align-items: center; padding: 220rpx 60rpx; }
.es-orn { width: 120rpx; height: 120rpx; border: 4rpx solid var(--line); border-radius: 24rpx; color: var(--gold); opacity: .5; font-size: 52rpx; font-weight: 800; display: flex; align-items: center; justify-content: center; }
.es-t { font-size: 25rpx; color: var(--ink2); margin-top: 30rpx; }
.es-btn { margin-top: 40rpx; font-size: 24rpx; color: var(--brand); border: 2rpx solid var(--brand); border-radius: 40rpx; padding: 12rpx 60rpx; font-weight: 700; }
.page { min-height: 100vh; background: var(--bg); padding-bottom: 60rpx; }
.hero { background: linear-gradient(140deg, var(--hero1), var(--hero2)); padding: 44rpx 36rpx 52rpx; display: flex; align-items: center; }
.f-name { font-size: 46rpx; font-weight: 800; color: #FDF8EE; letter-spacing: 3rpx; }
.f-alias { margin-top: 8rpx; color: rgba(253,248,238,.78); font-size: 19rpx; }
.f-flags { margin-left: auto; display: flex; align-items: center; }
.f-tag { font-size: 19rpx; color: #FDF8EE; background: rgba(253,248,238,.18); border: 1rpx solid rgba(253,248,238,.45); border-radius: 10rpx; padding: 6rpx 16rpx; }
.f-tag.review { color: #F6E7C9; }
.f-fav { margin-left: 20rpx; font-size: 44rpx; color: #F6E7C9; }
.body { margin-top: -26rpx; padding: 0 32rpx; }
.sec { padding: 28rpx 30rpx; margin-bottom: 22rpx; }
.hl-card { border: 2rpx solid var(--gold); }
.s-t { font-size: 28rpx; font-weight: 800; color: var(--ink); margin-bottom: 14rpx; display: flex; align-items: baseline; flex-wrap: wrap; }
.s-orn { color: var(--brand); }
.s-unit { font-size: 19rpx; color: var(--ink2); font-weight: 400; margin-left: 12rpx; }
.s-v { font-size: 26rpx; color: var(--ink); line-height: 1.9; text-align: justify; }
.component-list { display: flex; flex-wrap: wrap; gap: 12rpx; }
.component-chip { color: var(--brand); background: var(--zebra-bg); border: 1rpx solid var(--line); border-radius: 12rpx; padding: 9rpx 16rpx; font-size: 22rpx; }
.clinical { color: var(--brand); font-weight: 600; }
.danger-card { border: 2rpx solid rgba(154,46,31,.35); }
.caution { color: #9A2E1F; }
.note { color: var(--ink2); }
.others { padding: 24rpx 28rpx; margin-bottom: 22rpx; }
.o-t { font-size: 24rpx; font-weight: 700; color: var(--ink2); margin-bottom: 14rpx; }
.o-item { display: flex; align-items: center; padding: 16rpx 0; border-top: 1rpx dashed var(--line); }
.o-src { font-size: 20rpx; color: var(--gold); margin-right: 16rpx; flex-shrink: 0; }
.o-v { flex: 1; font-size: 22rpx; color: var(--ink); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.o-a { color: var(--ink2); }
.related { padding: 26rpx 28rpx; margin-bottom: 22rpx; }
.rl-t { font-size: 28rpx; font-weight: 800; color: var(--brand); margin-bottom: 16rpx; display: flex; align-items: center; }
.rl-t::before { content: '◈'; margin-right: 10rpx; font-size: 22rpx; }
.rl-item { display: flex; align-items: flex-start; padding: 16rpx 0; border-bottom: 1rpx dashed var(--line); }
.rl-item:last-child { border-bottom: none; }
.rl-no { font-size: 19rpx; color: var(--gold); font-weight: 700; margin-right: 16rpx; flex-shrink: 0; padding-top: 4rpx; }
.rl-main { flex: 1; min-width: 0; }
.rl-top { display: flex; align-items: center; }
.rl-diag { font-size: 26rpx; font-weight: 800; color: var(--ink); flex: 1; }
.rl-mark { font-size: 17rpx; color: #3F6B37; background: #E8F0E4; border-radius: 6rpx; padding: 2rpx 10rpx; margin-left: 12rpx; flex-shrink: 0; }
.rl-bingji { font-size: 20rpx; color: var(--ink2); margin-top: 4rpx; line-height: 1.6; }
.rl-fang { font-size: 19rpx; color: var(--brand); margin-top: 6rpx; line-height: 1.6; opacity: .85; }
.rl-a { color: var(--ink2); font-size: 30rpx; margin-left: 12rpx; flex-shrink: 0; }
.acts { margin: 10rpx 0 20rpx; }
.act { text-align: center; border-radius: 44rpx; padding: 24rpx 0; font-size: 27rpx; font-weight: 700; }
.copy { display: flex; align-items: center; justify-content: center; background: linear-gradient(135deg, var(--brand), var(--brand-deep)); color: #FDF8EE; }
.copy .ico-s { margin-right: 10rpx; }
.warn { font-size: 20rpx; color: #A2651B; background: #FCF3DC; border-radius: 12rpx; padding: 16rpx 22rpx; line-height: 1.7; }
</style>
