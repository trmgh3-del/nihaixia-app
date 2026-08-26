<template>
  <view class="page" :class="theme === 'dark' ? 'tdark' : 'tlight'">
    <view class="banner">
      <view class="b-deco" />
      <view class="b-deco d2" />
      <view class="b-title serif">医典全书</view>
      <view class="b-sub">伤寒 · 金匮 · 内经 · 本草 · 针灸 · 医案 · 讲义 —— 离线全收录</view>
    </view>

    <view v-for="g in catalog" :key="g.title" class="sec fade-in">
      <view class="sec-head">
        <text class="sec-orn">❖</text>
        <text class="sec-title serif">{{ g.title }}</text>
        <text class="sec-desc">{{ g.desc }}</text>
      </view>
      <view class="entries card">
        <view class="e-item" v-for="(e, i) in g.items" :key="e.label" @tap="go(e)" :class="{ 'no-b': i === g.items.length - 1 }">
          <view class="e-icon" :style="{ background: e.bg }">{{ e.icon }}</view>
          <view class="e-main">
            <view class="e-label">{{ e.label }}</view>
            <view class="e-sub">{{ e.sub }}</view>
          </view>
          <view class="e-count" v-if="e.n">{{ e.n }}</view>
          <text class="e-arrow">›</text>
        </view>
      </view>
    </view>

    <view class="foot">
      <text>数据源：jangviktor-web/nihaixia 知识蒸馏库</text>
    </view>
  </view>
</template>

<script>
import { store , applyTheme } from '@/utils/store.js'
import { loadData } from '@/utils/data.js'

export default {
  onShow() { applyTheme() },
  data() {
    return {
      catalog: []
    }
  },
  computed: {
    theme() { return store.theme }
  },
  mounted() {
    this.init()
  },
  methods: {
    async init() {
      let c = {}
      try { c = (await loadData('meta')).counts } catch (e) {}
      this.catalog = [
        {
          title: '四大经典', desc: '人纪正课',
          items: [
            { label: '伤寒论', sub: `太阳篇条文1-129 · 下篇补齐138-276 · 五经篇总结`, n: (c.shanghanSun || 0) + (c.shanghanQue || 0) + (c.wujing || 0) + '篇', icon: '伤', bg: '#FBEAE3', url: '/pkgTexts/pages/shanghan' },
            { label: '金匮要略', sub: '杂病 23 篇完整讲解（含第5/6/7篇讲课实录）', n: (c.jingui || 23) + '篇', icon: '匮', bg: '#FCF3DC', url: '/pkgTexts/pages/jingui' },
            { label: '黄帝内经', sub: '72 篇：54 提炼版 + 18 完整版', n: (c.neijing || 72) + '篇', icon: '内', bg: '#E8F0E4', url: '/pkgTexts/pages/neijing' },
            { label: '神农本草经', sub: `上经${137} · 中经${110} · 下经${131}，原文/性味/主治/倪注/口述`, n: (c.herbs || 378) + '味', icon: '本', bg: '#E9F1F2', url: '/pkgBencao/pages/list' }
          ]
        },
        {
          title: '临床实战', desc: '方 · 穴 · 案',
          items: [
            { label: '经方库', sub: '原方剂量 vs 倪师临床剂量对照（口述/换算标注）', n: (c.formulas || 157) + '方', icon: '方', bg: '#F5E8E8', url: '/pkgFormula/pages/list' },
            { label: '剂量换算与峻药', sub: '汉剂量衡 · 台湾钱制 · 峻药用量谱 · 版本差异对照', icon: '量', bg: '#F1EBE4', url: '/pkgFormula/pages/articles' },
            { label: '针灸大成', sub: '十二经络 · 五输穴 · 任督要穴 · 治症精选 · 穴位补遗', n: (c.points || 0) + '穴', icon: '针', bg: '#EDE9F4', url: '/pkgZhenjiu/pages/list' },
            { label: '医案库', sub: `结构化${c.casesTable || 1257}例 + 叙事${c.casesNarr || 243}例 + 医案集${c.yian || 410}例`, icon: '案', bg: '#FBEEE3', url: '/pkgCase/pages/main' }
          ]
        },
        {
          title: '辨证论治', desc: '诊断公式',
          items: [
            { label: '辨证中心', sub: '六经公式 · 八纲 · 脉舌速查 · 流程图 · 症状自查', icon: '辨', bg: '#EAF0EE', url: '/pages/diagnosis/diagnosis', tab: true },
            { label: '诊断经验汇编', sub: '感冒六经方 · 病机十九条 · 完整条文注解', icon: '验', bg: '#FBEAE3', url: '', diag: 'exp' },
            { label: 'SKILL 速查总库', sub: '速查卡 · 倪师视角 · 工作流 · 启发式 · 表达DNA · 常见问答', icon: '核', bg: '#FCF3DC', url: '/pkgArticle/pages/skill' }
          ]
        },
        {
          title: '讲座与文章', desc: '讲义 · 天纪',
          items: [
            { label: '讲义文库', sub: '梁冬对话 / 闭门课七大重病 / 扶阳论坛 / 仲景心法 / 斯坦福演讲 / 易筋经 / 汉唐文章 / 调研附录', n: (c.articles || 0) + '篇', icon: '文', bg: '#EAF0EE', url: '/pkgArticle/pages/list' },
            { label: '天纪 · 易理', sub: '紫微斗数十四主星 · 十二宫 · 六十四卦人事应用 · 阳宅风水', icon: '天', bg: '#F3EDE4', url: '/pkgTianji/pages/list' },
            { label: 'AI 问诊', sub: '内置倪师思维内核，配置 API 即可用', icon: 'AI', bg: '#EDE9F4', url: '/pages/ai/chat', tab: true }
          ]
        }
      ]
    },
    go(e) {
      if (e.diag) {
        store.pendingDiag = 'exp'
        uni.switchTab({ url: '/pages/diagnosis/diagnosis' })
        return
      }
      if (e.tab) { uni.switchTab({ url: e.url }); return }
      uni.navigateTo({ url: e.url })
    }
  }
}
</script>

<style scoped>
.page { min-height: 100vh; background: var(--bg); padding-bottom: 50rpx; }
.banner { position: relative; background: linear-gradient(140deg, var(--hero1), var(--hero2)); padding: 44rpx 36rpx 56rpx; overflow: hidden; }
.b-deco { position: absolute; width: 360rpx; height: 360rpx; border-radius: 50%; background: #F6E7C9; opacity: .1; top: -140rpx; right: -80rpx; }
.b-deco.d2 { width: 180rpx; height: 180rpx; top: auto; bottom: -70rpx; left: -40rpx; opacity: .07; }
.b-title { position: relative; font-size: 44rpx; font-weight: 800; color: #FDF8EE; letter-spacing: 4rpx; }
.b-sub { position: relative; font-size: 22rpx; color: rgba(253,248,238,.85); margin-top: 12rpx; }
.sec { margin: 30rpx 32rpx 0; }
.sec-head { display: flex; align-items: baseline; margin-bottom: 18rpx; }
.sec-orn { color: var(--gold); font-size: 22rpx; margin-right: 10rpx; }
.sec-title { font-size: 32rpx; font-weight: 800; color: var(--ink); letter-spacing: 2rpx; }
.sec-desc { margin-left: auto; font-size: 21rpx; color: var(--ink2); }
.entries { padding: 6rpx 26rpx; }
.e-item { display: flex; align-items: center; padding: 24rpx 0; border-bottom: 1rpx solid var(--line); }
.no-b { border-bottom: none !important; }
.e-icon { width: 84rpx; height: 84rpx; border-radius: 22rpx; display: flex; align-items: center; justify-content: center; font-size: 34rpx; font-weight: 800; color: var(--ink); flex-shrink: 0; }
.e-main { flex: 1; margin-left: 24rpx; min-width: 0; }
.e-label { font-size: 30rpx; font-weight: 700; color: var(--ink); }
.e-sub { font-size: 22rpx; color: var(--ink2); margin-top: 6rpx; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.e-count { font-size: 22rpx; color: var(--brand); background: var(--zebra-bg); border-radius: 10rpx; padding: 4rpx 14rpx; margin-right: 12rpx; flex-shrink: 0; }
.e-arrow { color: var(--ink2); font-size: 32rpx; }
.foot { margin-top: 50rpx; text-align: center; color: var(--ink2); font-size: 21rpx; opacity: .8; }
</style>
