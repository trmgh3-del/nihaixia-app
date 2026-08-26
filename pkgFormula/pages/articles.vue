<template>
  <view class="page" :class="theme === 'dark' ? 'tdark' : 'tlight'">
    <view class="list">
      <view v-for="a in articles" :key="a.id" class="a-item card fade-in" @tap="open(a)">
        <view class="a-t serif">{{ a.t }}</view>
        <view class="a-s">{{ snippet(a) }}</view>
        <text class="a-arrow">›</text>
      </view>
    </view>
  </view>
</template>

<script>
import { store , applyTheme } from '@/utils/store.js'
import { loadData } from '@/utils/data.js'
import { openMd } from '@/utils/routes.js'

export default {
  onShow() { applyTheme() },
  data() {
    return { articles: [] }
  },
  computed: {
    theme() { return store.theme }
  },
  mounted() {
    loadData('formulas').then(d => {
      // 附加上剂量换算标准等 SKILL 相关文章
      this.articles = d.articles || []
    }).catch(() => {})
  },
  methods: {
    snippet(a) { return (a.b || '').replace(/[#>*`|]/g, '').replace(/\s+/g, ' ').slice(0, 70) },
    open(a) { openMd({ ...a, f: 'formulas' }, a.t) }
  }
}
</script>

<style scoped>
.page { min-height: 100vh; background: var(--bg); padding: 24rpx 32rpx 60rpx; }
.a-item { position: relative; padding: 28rpx 30rpx; margin-bottom: 22rpx; }
.a-t { font-size: 30rpx; font-weight: 800; color: var(--ink); }
.a-s { font-size: 22rpx; color: var(--ink2); margin-top: 12rpx; line-height: 1.6; }
.a-arrow { position: absolute; right: 30rpx; top: 34rpx; color: var(--ink2); font-size: 30rpx; }
</style>
