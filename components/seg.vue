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
      try {
        const d = await loadData('formulas')
        const clean = String(name || '').replace(/[「」“”\s]/g, '')
        const item = (d.items || []).find(x => x.n === name || x.n === clean || clean.includes(x.n) || x.n.includes(clean))
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
