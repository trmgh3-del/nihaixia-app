<template>
  <text class="seg-root">
    <text v-for="(s, i) in segs" :key="i" :class="'seg-' + s.t" :user-select="s.t === 'txt'" @tap="s.t === 'fang' && tapFang(s.v)">{{ s.v }}</text>
  </text>
</template>

<script>
export default {
  name: 'seg',
  props: {
    segs: { type: Array, default: () => [{ t: 'txt', v: '' }] }
  },
  methods: {
    tapFang(name) {
      uni.$emit('open-fang', name)
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
