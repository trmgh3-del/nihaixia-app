<template>
  <view class="page" :class="theme === 'dark' ? 'tdark' : 'tlight'">
    <view class="hero">
      <view class="h-t serif">备份与恢复</view>
      <view class="h-s">收藏 · 笔记 · 打卡 · 闪卡进度 · 配置 —— 一份JSON全带走</view>
    </view>

    <view class="blk card fade-in">
      <view class="b-t serif">① 导出备份</view>
      <view class="b-d">包含：收藏 {{ stats.fav }} 条 · 笔记 {{ stats.note }} 条 · 足迹 {{ stats.hist }} 条 · 健康打卡 {{ stats.health }} 天 · 闪卡进度 {{ stats.flash }} 张 · 背诵/主题/字号设置（不含 API Key）</view>
      <view class="b-acts">
        <view class="b-btn" @tap="copyBackup">复制到剪贴板</view>
        <view class="b-btn gold" @tap="saveFile" v-if="isApp">保存为文件</view>
      </view>
      <view class="b-tip" v-if="savedPath">已保存：{{ savedPath }}（可通过系统分享/文件管理器取出）</view>
    </view>

    <view class="blk card fade-in">
      <view class="b-t serif">② 从备份恢复</view>
      <textarea class="b-ta" v-model="importText" placeholder="粘贴之前导出的备份JSON…" />
      <view class="b-acts">
        <view class="b-btn main" @tap="doImport">恢复数据</view>
      </view>
      <view class="b-warn" v-if="importMsg">{{ importMsg }}</view>
      <view class="b-note">恢复会覆盖当前同名数据；AI对话记录与健康趋势也会一并恢复。恢复后建议重启应用。</view>
    </view>
  </view>
</template>

<script>
import { store, applyTheme, initSettings } from '@/utils/store.js'

const KEYS = ['nx_fav', 'nx_hist', 'nx_notes', 'nx_flash', 'nx_recite', 'nx_health', 'nx_shist', 'nx_sizhen_reports', 'nx_sizhen_draft', 'nx_sizhen_snapshots', 'nx_theme', 'nx_font', 'nx_fontfam']

export default {
  data() {
    return { importText: '', importMsg: '', savedPath: '', isApp: false,
      stats: { fav: 0, note: 0, hist: 0, health: 0, flash: 0 } }
  },
  computed: { theme() { return store.theme } },
  onShow() {
    applyTheme()
    // #ifdef APP-PLUS
    this.isApp = true
    // #endif
    this.gather()
  },
  methods: {
    gather() {
      const g = (k, d) => { try { return uni.getStorageSync(k) || d } catch (e) { return d } }
      this.stats = {
        fav: (g('nx_fav', [])).length,
        note: Object.keys(g('nx_notes', {})).length,
        hist: (g('nx_hist', [])).length,
        health: (g('nx_health', [])).length,
        flash: Object.keys(g('nx_flash', {})).length
      }
    },
    buildBackup() {
      const data = { app: 'nihaixia', ver: 1, exportedAt: new Date().toISOString() }
      KEYS.forEach(k => { data[k] = uni.getStorageSync(k) })
      data.nx_chats = uni.getStorageSync('nx_chats')
      return JSON.stringify(data)
    },
    copyBackup() {
      uni.setClipboardData({ data: this.buildBackup() })
    },
    saveFile() {
      // #ifdef APP-PLUS
      try {
        const txt = this.buildBackup()
        const d = new Date()
        const p = n => (n < 10 ? '0' + n : n)
        const name = `nx-backup-${d.getFullYear()}${p(d.getMonth() + 1)}${p(d.getDate())}.json`
        plus.io.resolveLocalFileSystemURL('_doc/', dir => {
          dir.getFile(name, { create: true }, f => {
            f.createWriter(w => {
              w.onwrite = () => { this.savedPath = '_doc/' + name }
              w.write(txt)
            })
          })
        })
      } catch (e) { uni.showToast({ title: '保存失败', icon: 'none' }) }
      // #endif
    },
    doImport() {
      const t = this.importText.trim()
      if (!t) { this.importMsg = '请先粘贴备份内容'; return }
      let data
      try { data = JSON.parse(t) } catch (e) { this.importMsg = '❌ 不是有效的JSON（请确认完整复制）'; return }
      if (!data || data.app !== 'nihaixia') { this.importMsg = '❌ 不是本应用的备份文件'; return }
      let n = 0
      KEYS.concat(['nx_chats']).forEach(k => {
        if (data[k] !== undefined && data[k] !== '') { uni.setStorageSync(k, data[k]); n++ }
      })
      this.importMsg = '✓ 已恢复 ' + n + ' 项数据'
      initSettings()
      this.gather()
      uni.showToast({ title: '恢复成功', icon: 'success' })
    }
  }
}
</script>

<style scoped>
.page { min-height: 100vh; background: var(--bg); padding-bottom: 80rpx; }
.hero { background: linear-gradient(140deg, var(--hero1), var(--hero2)); padding: 42rpx 36rpx 48rpx; }
.h-t { font-size: 40rpx; font-weight: 800; color: #FDF8EE; letter-spacing: 3rpx; }
.h-s { font-size: 21rpx; color: rgba(253,248,238,.85); margin-top: 12rpx; }
.blk { margin: 24rpx 32rpx 24rpx; padding: 28rpx 30rpx; }
.blk:first-of-type { margin-top: 28rpx; }

.b-t { font-size: 28rpx; font-weight: 800; color: var(--brand); margin-bottom: 14rpx; }
.b-d { font-size: 21rpx; color: var(--ink2); line-height: 1.8; }
.b-acts { display: flex; gap: 16rpx; margin-top: 22rpx; }
.b-btn { flex: 1; text-align: center; border-radius: 40rpx; padding: 18rpx 0; font-size: 24rpx; font-weight: 700; border: 2rpx solid var(--brand); color: var(--brand); }
.b-btn.gold { border-color: var(--gold); color: var(--gold); }
.b-btn.main { background: linear-gradient(135deg, var(--brand), var(--brand-deep)); color: #FDF8EE; border-color: transparent; }
.b-tip { margin-top: 16rpx; font-size: 19rpx; color: #3F6B37; background: #E8F0E4; border-radius: 10rpx; padding: 10rpx 16rpx; word-break: break-all; }
.b-ta { width: 100%; height: 220rpx; background: var(--zebra-bg); border-radius: 14rpx; padding: 20rpx 24rpx; box-sizing: border-box; font-size: 22rpx; color: var(--ink); margin-top: 6rpx; }
.b-warn { margin-top: 16rpx; font-size: 22rpx; border-radius: 10rpx; padding: 12rpx 18rpx; }
.b-note { margin-top: 14rpx; font-size: 19rpx; color: var(--ink2); line-height: 1.7; }
</style>
