<template>
  <text class="seg-root">
    <text v-for="(s, i) in segs" :key="i" :class="'seg-' + s.t" :user-select="s.t === 'txt'" @tap="s.t === 'fang' && tapFang(s.v)">{{ s.v }}</text>
  </text>
</template>

<script>
import { store } from '@/utils/store.js'
import { loadData } from '@/utils/data.js'

export default {
  name: 'seg',
  props: { segs: { type: Array, default: () => [{ t: 'txt', v: '' }] } },
  methods: {
    async tapFang(name) {
      const clean = String(name || '').replace(/[「」“”\s]/g, '')
      const find = list => { const all = list || []; const exact = all.find(x => x.n === name || x.n === clean); if (exact) return exact; return all.filter(x => clean.includes(x.n) || x.n.includes(clean)).sort((a, b) => b.n.length - a.n.length)[0] }
      // 阅读器进入时已预加载方剂索引，命中时同步跳转，避免点击后出现等待页。
      let item = find(globalThis.__NX_FORMULA_ITEMS__)
      try {
        if (!item) { const d = await loadData('formulas'); item = find(d.items) }
        if (!item) { uni.showToast({ title: '未找到方剂详情', icon: 'none' }); return }
        if (store.readerItem && store.readerItem.kind === 'md') store.readerReturn = store.readerItem
        store.readerItem = { kind: 'formula', item }
        uni.navigateTo({ url: '/pkgFormula/pages/detail' })
      } catch (e) { uni.showToast({ title: '方剂库加载失败', icon: 'none' }) }
    }
  }
}
</script>

<style>
.seg-root { line-height: inherit; }
.seg-txt { color: inherit; }
.seg-b { font-weight: 700; color: var(--brand); }
.seg-i { font-style: italic; }
.seg-c { font-family: Menlo, Consolas, monospace; background: var(--zebra-bg); padding: 2rpx 8rpx; border-radius: 6rpx; font-size: 0.9em; }
.seg-d { text-decoration: line-through; color: var(--ink2); }
.seg-a { color: var(--brand); text-decoration: underline; }
.seg-fang { color: var(--brand); border-bottom: 2rpx solid var(--brand); font-weight: 600; }
</style>
