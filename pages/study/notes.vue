<template>
  <view class="page" :class="theme === 'dark' ? 'tdark' : 'tlight'">
    <view class="list" v-if="list.length">
      <view v-for="n in list" :key="n.key" class="n-item card fade-in">
        <view class="n-head">
          <view class="n-t">{{ n.t }}</view>
          <view class="n-time">{{ n.dateStr }}</view>
        </view>
        <view class="n-body">{{ n.note }}</view>
        <view class="n-acts">
          <text class="n-del" @tap="del(n.key)">删除</text>
        </view>
      </view>
    </view>
    <view class="none" v-if="!list.length">暂无笔记 —— 阅读任意内容时，点右下角悬浮按钮中的「笔记」即可记录心得</view>
  </view>
</template>

<script>
import { store, applyTheme } from '@/utils/store.js'

export default {
  data() {
    return { notes: {} }
  },
  computed: {
    theme() { return store.theme },
    list() {
      return Object.keys(this.notes).map(k => {
        const v = this.notes[k]
        const d = new Date(v.ts)
        const p = n => (n < 10 ? '0' + n : n)
        return { key: k, t: v.t, note: v.note, dateStr: `${p(d.getMonth() + 1)}/${p(d.getDate())} ${p(d.getHours())}:${p(d.getMinutes())}`, raw: v }
      }).sort((a, b) => b.raw.ts - a.raw.ts)
    }
  },
  onShow() {
    applyTheme()
    try { this.notes = uni.getStorageSync('nx_notes') || {} } catch (e) { this.notes = {} }
  },
  methods: {
    del(k) {
      uni.showModal({
        title: '删除笔记',
        content: '确定删除这条笔记吗？',
        success: r => {
          if (!r.confirm) return
          const notes = { ...this.notes }
          delete notes[k]
          this.notes = notes
          uni.setStorageSync('nx_notes', notes)
        }
      })
    }
  }
}
</script>

<style scoped>
.page { min-height: 100vh; background: var(--bg); padding: 24rpx 32rpx 70rpx; }
.n-item { padding: 26rpx 30rpx; margin-bottom: 20rpx; }
.n-head { display: flex; align-items: center; }
.n-t { font-size: 27rpx; font-weight: 700; color: var(--brand); flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.n-time { font-size: 20rpx; color: var(--ink2); }
.n-body { font-size: 24rpx; color: var(--ink); line-height: 1.9; margin-top: 12rpx; white-space: pre-wrap; }
.n-acts { margin-top: 14rpx; padding-top: 12rpx; border-top: 1rpx dashed var(--line); }
.n-del { font-size: 21rpx; color: #833B3B; }
</style>
