<template>
  <view class="page" :class="theme === 'dark' ? 'tdark' : 'tlight'">
    <view class="banner">
      <view class="avatar serif">倪</view>
      <view class="u-main">
        <view class="u-name serif">岐黄学子</view>
        <view class="u-sub">读经典 · 辨六经 · 用经方</view>
      </view>
      <view class="seal2 serif">人紀</view>
    </view>

    <!-- 统计 -->
    <view class="statbar card fade-in">
      <view class="st" @tap="tab='fav'"><view class="st-n serif">{{ favorites.length }}</view><view class="st-k">收藏</view></view>
      <view class="st" @tap="tab='hist'"><view class="st-n serif">{{ history.length }}</view><view class="st-k">足迹</view></view>
      <view class="st"><view class="st-n serif">{{ readCount }}</view><view class="st-k">累计阅读</view></view>
      <view class="st"><view class="st-n serif">{{ meta ? meta.version : '—' }}</view><view class="st-k">知识库</view></view>
    </view>

    <!-- tabs -->
    <view class="tabs">
      <view class="tab" :class="{ on: tab === 'fav' }" @tap="tab = 'fav'">我的收藏</view>
      <view class="tab" :class="{ on: tab === 'hist' }" @tap="tab = 'hist'">阅读足迹</view>
    </view>

    <view class="list card fade-in">
      <view v-if="!(tab === 'fav' ? favorites : history).length" class="empty">
        <text class="e-orn">❈</text>
        <text>{{ tab === 'fav' ? '暂无收藏，阅读时点右上角 ☆ 收藏' : '暂无阅读记录' }}</text>
      </view>
      <view v-for="h in (tab === 'fav' ? favorites : history)" :key="h.f + h.i" class="l-item" @tap="reopen(h)">
        <view class="l-main">
          <view class="l-t">{{ h.t }}</view>
          <view class="l-s" v-if="h.s">{{ h.s }}</view>
        </view>
        <text class="l-x" v-if="tab === 'fav'" @tap.stop="unfav(h)">✕</text>
        <text class="l-time" v-else>{{ fmtTime(h.ts) }}</text>
      </view>
    </view>

    <!-- 设置 -->
    <view class="sec-title serif"><image class="ico" src="/static/icons/settings-brand.png" style="vertical-align:-6rpx;margin-right:10rpx" />偏好设置</view>
    <view class="set card">
      <view class="s-row">
        <view class="s-k">深夜模式<text class="s-d">宣纸 ⇢ 玄墨</text></view>
        <switch :checked="theme === 'dark'" color="#9A2E1F" @change="toggleTheme" style="transform:scale(.75)" />
      </view>
      <view class="s-row col">
        <view class="s-k">正文字号</view>
        <view class="fonts">
          <view v-for="f in fontOpts" :key="f.v" class="f-chip" :class="{ on: fontScale === f.v }" @tap="setFont(f.v)">{{ f.label }}</view>
        </view>
      </view>
      <view class="s-row col">
        <view class="s-k">正文字体<text class="s-d">黑体（默认）或宋体（古籍风）</text></view>
        <view class="fonts">
          <view class="f-chip" :class="{ on: fontFam === 'sans' }" @tap="setFont2('sans')">黑体</view>
          <view class="f-chip serif" :class="{ on: fontFam === 'serif' }" @tap="setFont2('serif')">宋体</view>
        </view>
      </view>
      <view class="s-row col">
        <view class="s-k">数据管理</view>
        <view class="fonts">
          <view class="f-chip warn" @tap="clearData('hist')">清空足迹</view>
          <view class="f-chip warn" @tap="clearData('fav')">清空收藏</view>
          <view class="f-chip warn" @tap="clearData('chat')">清空会话</view>
        </view>
      </view>
    </view>

    <!-- 关于 -->
    <view class="sec-title serif">关于</view>
    <view class="about card">
      <view class="a-item" @tap="showAbout('readme')"><text>项目说明（README）</text><text class="a-arrow">›</text></view>
      <view class="a-item" @tap="showAbout('changelog')"><text>知识库更新日志</text><text class="a-arrow">›</text></view>
      <view class="a-item" @tap="showAbout('license')"><text>内容来源与免责声明</text><text class="a-arrow">›</text></view>
      <view class="a-item" @tap="goStudy"><text>学习中心（闪卡背诵 · 条文 · 报告）</text><text class="a-arrow">›</text></view>
      <view class="a-item" @tap="goUpdate"><text>内容更新（检查源库 · 数据包）</text><text class="a-arrow">›</text></view>
      <view class="a-item" @tap="goBackup"><text>备份与恢复（收藏/笔记/打卡）</text><text class="a-arrow">›</text></view>
      <view class="a-item" @tap="goHealth"><text>健康自测（六大标准打卡）</text><text class="a-arrow">›</text></view>
      <view class="a-item" @tap="goAi"><text>AI 问诊配置</text><text class="a-arrow">›</text></view>
    </view>
    <view class="foot">倪师经方 · 离线知识库 v1.0（数据蒸馏自开源项目 nihaixia）</view>
  </view>
</template>

<script>
import { store, setTheme, setFontScale, setFontFam, toggleFav, initSettings, applyTheme } from '@/utils/store.js'
import { loadData } from '@/utils/data.js'
import { openEntry, openMd } from '@/utils/routes.js'

export default {
  data() {
    return {
      tab: 'fav',
      meta: null,
      fontOpts: [
        { v: 0.85, label: '小' }, { v: 1, label: '标准' }, { v: 1.15, label: '大' }, { v: 1.3, label: '特大' }
      ]
    }
  },
  computed: {
    theme() { return store.theme },
    favorites() { return store.favorites },
    history() { return store.history },
    fontScale() { return store.fontScale },
    fontFam() { return store.fontFam },
    readCount() {
      const k = 'nx_readcount_' + new Date().getFullYear()
      return uni.getStorageSync(k) || store.history.length || 0
    }
  },
  onShow() {
    if (!store.ready) initSettings()
    loadData('meta').then(m => { this.meta = m; store.meta = m }).catch(() => {})
    applyTheme()
  },
  methods: {
    toggleTheme(e) { setTheme(e.detail.value ? 'dark' : 'light') },
    setFont(v) { setFontScale(v); uni.showToast({ title: '已应用', icon: 'none' }) },
    setFont2(v) { setFontFam(v); uni.showToast({ title: v === 'serif' ? '已切换宋体' : '已切换黑体', icon: 'none' }) },
    clearData(k) {
      const names = { hist: '阅读足迹', fav: '收藏', chat: 'AI会话' }
      uni.showModal({
        title: '清空' + names[k],
        content: '确定清空全部' + names[k] + '吗？此操作不可恢复。',
        success: r => {
          if (!r.confirm) return
          if (k === 'hist') store.history = []
          if (k === 'fav') store.favorites = []
          if (k === 'chat') store.chats = []
          uni.setStorageSync(k === 'hist' ? 'nx_hist' : k === 'fav' ? 'nx_fav' : 'nx_chats', [])
          uni.showToast({ title: '已清空', icon: 'none' })
        }
      })
    },
    unfav(h) { toggleFav(h); uni.showToast({ title: '已取消收藏', icon: 'none' }) },
    reopen(h) { openEntry({ f: h.f, i: h.i, t: h.t }) },
    goAi() { uni.switchTab({ url: '/pages/ai/chat' }) },
    goHealth() { uni.navigateTo({ url: '/pages/health/health' }) },
    goStudy() { uni.navigateTo({ url: '/pages/study/study' }) },
    goUpdate() { uni.navigateTo({ url: '/pages/mine/update' }) },
    goBackup() { uni.navigateTo({ url: '/pages/mine/backup' }) },
    fmtTime(ts) {
      const d = new Date(ts)
      const p = n => (n < 10 ? '0' + n : n)
      return `${p(d.getMonth() + 1)}/${p(d.getDate())} ${p(d.getHours())}:${p(d.getMinutes())}`
    },
    async showAbout(which) {
      if (!this.meta) { try { this.meta = await loadData('meta') } catch (e) { return } }
      const m = this.meta
      if (which === 'readme') {
        openMd({ f: 'misc', id: 'readme', t: '项目说明 README', b: m.readme || '' })
      } else if (which === 'changelog') {
        openMd({ f: 'misc', id: 'changelog', t: '知识库更新日志', b: m.changelog || '' })
      } else {
        uni.showModal({
          title: '内容来源与免责声明',
          content: '本应用全部内容蒸馏自开源知识库 jangviktor-web/nihaixia（倪海厦人纪教学资料整理），仅用于中医学习与文化传播。应用内容不构成医疗建议，处方用药请务必遵执业医师指导。 respectfully © 人纪/天纪著作权归原权利人。',
          showCancel: false,
          confirmText: '知道了'
        })
      }
    }
  }
}
</script>

<style scoped>
.page { min-height: 100vh; background: var(--bg); padding-bottom: 60rpx; }
.banner { background: linear-gradient(140deg, var(--hero1), var(--hero2)); display: flex; align-items: center; padding: 56rpx 36rpx 64rpx; }
.avatar { width: 110rpx; height: 110rpx; border-radius: 30rpx; background: rgba(253,248,238,.18); border: 3rpx solid rgba(253,248,238,.8); color: #FDF8EE; font-size: 52rpx; font-weight: 800; display: flex; align-items: center; justify-content: center; }
.u-main { flex: 1; margin-left: 26rpx; }
.u-name { font-size: 38rpx; font-weight: 800; color: #FDF8EE; letter-spacing: 3rpx; }
.u-sub { font-size: 22rpx; color: rgba(253,248,238,.85); margin-top: 8rpx; }
.seal2 { width: 88rpx; height: 88rpx; border: 4rpx solid rgba(253,248,238,.85); border-radius: 16rpx; color: #FDF8EE; font-size: 32rpx; font-weight: 800; display: flex; align-items: center; justify-content: center; transform: rotate(7deg); }
.statbar { margin: -34rpx 32rpx 0; position: relative; display: flex; padding: 28rpx 0; }
.st { flex: 1; text-align: center; }
.st-n { font-size: 34rpx; font-weight: 800; color: var(--brand); }
.st-k { font-size: 21rpx; color: var(--ink2); margin-top: 4rpx; }
.tabs { display: flex; margin: 30rpx 32rpx 0; }
.tab { padding: 16rpx 34rpx; font-size: 27rpx; color: var(--ink2); background: var(--zebra-bg); border-radius: 32rpx 32rpx 0 0; margin-right: 8rpx; }
.tab.on { background: var(--card); color: var(--brand); font-weight: 700; }
.list { margin: 0 32rpx; padding: 8rpx 28rpx; }
.empty { padding: 60rpx 0; text-align: center; color: var(--ink2); font-size: 24rpx; display: flex; flex-direction: column; align-items: center; }
.e-orn { font-size: 60rpx; margin-bottom: 16rpx; }
.l-item { display: flex; align-items: center; padding: 24rpx 0; border-bottom: 1rpx solid var(--line); }
.l-item:last-child { border-bottom: none; }
.l-main { flex: 1; min-width: 0; }
.l-t { font-size: 27rpx; color: var(--ink); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.l-s { font-size: 21rpx; color: var(--ink2); margin-top: 4rpx; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.l-x, .l-time { font-size: 22rpx; color: var(--ink2); margin-left: 16rpx; }
.sec-title { margin: 40rpx 36rpx 18rpx; font-size: 29rpx; font-weight: 800; color: var(--ink); }
.set { margin: 0 32rpx; padding: 6rpx 28rpx; }
.s-row { display: flex; align-items: center; justify-content: space-between; padding: 24rpx 0; border-bottom: 1rpx solid var(--line); }
.s-row.col { flex-direction: column; align-items: stretch; border-bottom: none; }
.s-row:last-child { border-bottom: none; }
.s-k { font-size: 27rpx; color: var(--ink); }
.s-d { display: block; font-size: 20rpx; color: var(--ink2); margin-top: 4rpx; }
.fonts { display: flex; margin-top: 18rpx; }
.f-chip { flex: 1; text-align: center; padding: 14rpx 0; background: var(--zebra-bg); color: var(--ink2); border-radius: 12rpx; margin-right: 14rpx; font-size: 24rpx; }
.f-chip.on { background: var(--brand); color: #fff; }
.about { margin: 0 32rpx; padding: 6rpx 28rpx; }
.a-item { display: flex; justify-content: space-between; align-items: center; padding: 26rpx 0; border-bottom: 1rpx solid var(--line); font-size: 27rpx; color: var(--ink); }
.a-item:last-child { border-bottom: none; }
.a-arrow { color: var(--ink2); font-size: 30rpx; }
.foot { margin-top: 46rpx; text-align: center; font-size: 20rpx; color: var(--ink2); opacity: .8; }
</style>
