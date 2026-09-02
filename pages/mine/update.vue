<template>
  <view class="page" :class="theme === 'dark' ? 'tdark' : 'tlight'">
    <view class="hero">
      <view class="h-t serif">内容更新</view>
      <view class="h-s">知识库当前版本 · 源仓库检查 · 数据包热更新</view>
    </view>

    <view class="blk card fade-in">
      <view class="b-t serif">当前内置版本</view>
      <view class="kv"><text class="k">构建日期</text><text class="v">{{ meta.builtAt || '—' }}</text></view>
      <view class="kv"><text class="k">知识库版本</text><text class="v">{{ meta.version || '—' }}</text></view>
      <view class="kv"><text class="k">内容规模</text><text class="v">{{ brief }}</text></view>
      <view class="kv" v-if="hotDate"><text class="k">已热更新</text><text class="v hl">{{ hotDate }}</text></view>
    </view>

    <view class="blk card fade-in">
      <view class="b-t serif">检查源仓库更新</view>
      <view class="b-d">对比 GitHub 源仓库最新提交与本地构建日期。</view>
      <view class="b-acts">
        <view class="b-btn" @tap="checkRepo">{{ checking ? '检查中…' : '⟳ 检查源库更新' }}</view>
      </view>
      <view class="b-tip" v-if="repoMsg" :class="repoOk ? 'ok' : 'warn'">{{ repoMsg }}</view>
    </view>

    <view class="blk card fade-in">
      <view class="b-t serif">从 GitHub 获取 App 更新</view>
      <view class="b-d">进入本页会自动检查 GitHub 最新 Release；发现新版 APK 后提示确认，App 端可下载并调用系统安装器，H5 端打开发布页。安装包更新需要系统安装确认，不能静默替换。</view>
      <view class="b-acts">
        <view class="b-btn main" @tap="checkAppRelease">{{ releaseChecking ? '检查中…' : '⟳ 检查并下载安装更新' }}</view>
      </view>
      <view class="b-tip" v-if="releaseMsg" :class="releaseOk ? 'ok' : 'warn'">{{ releaseMsg }}</view>
      <view class="b-acts" v-if="releaseUrl && !releaseAsset">
        <view class="b-btn main" @tap="openExternal(releaseUrl)">打开下载页</view>
      </view>
      <view class="b-acts" v-if="releaseAsset">
        <view class="b-btn main" @tap="downloadRelease(releaseAsset)">下载并安装 APK</view>
      </view>
    </view>

    <view class="blk card fade-in">
      <view class="b-t serif">数据包热更新（App）</view>
      <view class="b-d">输入数据包地址（data-update.json），下载校验后立即生效，无需重装。</view>
      <view class="in-row">
        <input class="in" v-model="packUrl" placeholder="https://…/data-update.json" />
      </view>
      <view class="b-acts">
        <view class="b-btn main" @tap="downloadPack">{{ downloading ? '下载中…' : '⤓ 下载并应用' }}</view>
        <view class="b-btn warn2" v-if="hotDate" @tap="clearPack">恢复内置</view>
      </view>
      <view class="b-tip" v-if="packMsg" :class="packOk ? 'ok' : 'warn'">{{ packMsg }}</view>
      <view class="b-note">H5 端因存储限制仅支持检查更新；App 端完整支持。数据包可用 tools/export_bundle.py 从最新源库生成后部署到任意静态服务器/OSS。</view>
    </view>
  </view>
</template>

<script>
import { store, applyTheme } from '@/utils/store.js'
import { loadData, hotPack } from '@/utils/data.js'

export default {
  data() {
    return { meta: {}, packUrl: '', checking: false, repoMsg: '', repoOk: false,
      downloading: false, packMsg: '', packOk: false, hotDate: '',
      releaseChecking: false, releaseMsg: '', releaseOk: false, releaseUrl: '', releaseAsset: null }
  },
  computed: {
    theme() { return store.theme },
    brief() {
      const c = this.meta.counts || {}
      const arr = [c.herbs + '味本草', c.formulas + '方', c.casesTable + '例结构化医案', (c.shanghanSun + c.shanghanQue) + '节伤寒', c.neijing + '篇内经']
      return arr.filter(x => x[0] !== 'u').join(' · ')
    }
  },
  onShow() {
    applyTheme()
    loadData('meta').then(m => { this.meta = m }).catch(() => {})
    this.hotDate = hotPack.date() || ''
    this.packUrl = hotPack.url() || ''
    // 进入更新页自动检查；避免每次切页都请求，六小时内只检查一次。
    if (!this._autoReleaseCheckedAt || Date.now() - this._autoReleaseCheckedAt > 6 * 3600000) {
      this._autoReleaseCheckedAt = Date.now()
      this.checkAppRelease(true)
    }
  },
  methods: {
    openExternal(url) {
      const target = String(url || '')
      // #ifdef H5
      if (typeof window !== 'undefined') window.open(target, '_blank', 'noopener,noreferrer')
      // #endif
      // #ifndef H5
      if (typeof plus !== 'undefined' && plus.runtime) plus.runtime.openURL(target)
      else uni.setClipboardData({ data: target, success: () => uni.showToast({ title: '链接已复制，请用浏览器打开', icon: 'none' }) })
      // #endif
    },
    checkAppRelease(silent = false) {
      if (this.releaseChecking) return
      this.releaseChecking = true
      this.releaseMsg = ''
      this.releaseUrl = ''
      uni.request({
        url: 'https://api.github.com/repos/trmgh3-del/nihaixia-app/releases/latest',
        method: 'GET', timeout: 20000,
        header: { Accept: 'application/vnd.github+json', 'User-Agent': 'nihaixia-app' },
        success: res => {
          const r = res.data
          if (res.statusCode === 200 && r && r.tag_name) {
            this.releaseUrl = r.html_url || 'https://github.com/trmgh3-del/nihaixia-app/releases'
            const assetsRaw = (r.assets || []).filter(a => a && a.browser_download_url)
            const assets = assetsRaw.map(a => a.name).filter(Boolean)
            this.releaseAsset = assetsRaw.find(a => /\.apk$/i.test(a.name || '')) || null
            this.releaseOk = true
            this.releaseMsg = `最新发布：${r.tag_name}${assets.length ? ' · 可下载：' + assets.join('、') : ' · 请在发布页查看下载文件'}`
            if (silent && this.releaseAsset && this.isNewerApp(r.tag_name)) {
              uni.showModal({ title: '发现 App 新版本', content: `${r.tag_name} 已发布，是否下载并安装？`, confirmText: '下载更新', cancelText: '稍后', success: x => { if (x.confirm) this.downloadRelease(this.releaseAsset) } })
            }
          } else if (res.statusCode === 404) {
            // APK 也可能直接放在仓库 release/ 目录，而不是 GitHub Release 附件。
            this.checkRepositoryApk(silent)
          } else {
            this.releaseOk = false
            this.releaseMsg = 'GitHub 发布接口返回异常（HTTP ' + res.statusCode + '）'
          }
        },
        fail: () => { this.releaseOk = false; this.releaseMsg = '无法访问 GitHub，请检查网络或直接打开仓库' },
        complete: () => { this.releaseChecking = false }
      })
    },
    isNewerApp(tag) {
      const current = String(uni.getSystemInfoSync().appVersion || '1.0.0').replace(/^v/i, '').split('.').map(Number)
      const latest = String(tag || '').match(/\d+(?:\.\d+)+/)
      if (!latest) return false
      const next = latest[0].split('.').map(Number)
      for (let i = 0; i < Math.max(current.length, next.length); i++) {
        if ((next[i] || 0) !== (current[i] || 0)) return (next[i] || 0) > (current[i] || 0)
      }
      return false
    },
    downloadRelease(asset) {
      if (!asset || !asset.browser_download_url) return
      // H5 不能安装 APK；App 端下载后交给系统安装器，仍需用户确认。
      // #ifdef H5
      this.openExternal(asset.browser_download_url)
      // #endif
      // #ifndef H5
      uni.showLoading({ title: '下载更新中' })
      uni.downloadFile({ url: asset.browser_download_url, success: res => {
        if (res.statusCode !== 200 || !res.tempFilePath) { uni.showToast({ title: '下载失败', icon: 'none' }); return }
        if (typeof plus !== 'undefined' && plus.runtime) plus.runtime.install(res.tempFilePath, {}, () => {}, () => uni.showToast({ title: '安装失败', icon: 'none' }))
        else uni.showToast({ title: '请打开发布页安装', icon: 'none' })
      }, fail: () => uni.showToast({ title: '下载失败，请检查网络', icon: 'none' }), complete: () => uni.hideLoading() })
      // #endif
    },
    checkRepositoryApk(silent = false) {
      uni.request({
        url: 'https://api.github.com/repos/trmgh3-del/nihaixia-app/contents/release?ref=main',
        method: 'GET', timeout: 20000,
        header: { Accept: 'application/vnd.github+json', 'User-Agent': 'nihaixia-app' },
        success: res => {
          const files = Array.isArray(res.data) ? res.data : []
          const file = files.find(x => x && x.type === 'file' && /\.apk$/i.test(x.name || ''))
          if (!file) {
            this.releaseOk = false
            this.releaseMsg = '仓库暂未发布 Release，release/ 目录也没有 APK 更新包。'
            return
          }
          const download = `https://raw.githubusercontent.com/trmgh3-del/nihaixia-app/main/release/${encodeURIComponent(file.name)}`
          this.releaseAsset = { name: file.name, browser_download_url: download }
          this.releaseUrl = file.html_url || download
          this.releaseOk = true
          this.releaseMsg = `发现仓库 APK：${file.name} · 来源：release/ 目录`
          const version = (file.name.match(/v?\d+(?:\.\d+)+/i) || [])[0]
          if (silent && version && this.isNewerApp(version)) {
            uni.showModal({ title: '发现 App 新版本', content: `${version} 已放入 GitHub release/ 目录，是否下载并安装？`, confirmText: '下载更新', cancelText: '稍后', success: x => { if (x.confirm) this.downloadRelease(this.releaseAsset) } })
          }
        },
        fail: () => { this.releaseOk = false; this.releaseMsg = '无法检查 GitHub release/ 目录，请检查网络' }
      })
    },
    checkRepo() {
      if (this.checking) return
      this.checking = true
      this.repoMsg = ''
      uni.request({
        url: 'https://api.github.com/repos/jangviktor-web/nihaixia/commits?per_page=1',
        method: 'GET',
        timeout: 20000,
        header: { Accept: 'application/vnd.github+json', 'User-Agent': 'nihaixia-app' },
        success: res => {
          if (res.statusCode === 200 && res.data && res.data[0]) {
            const sha = String(res.data[0].sha || '').slice(0, 7)
            const date = String(res.data[0].commit ? res.data[0].commit.committer ? res.data[0].commit.committer.date : '' : '').slice(0, 10)
            const local = this.meta.builtAt || ''
            if (date > local) {
              this.repoOk = false
              this.repoMsg = `源仓库有更新：最新提交 ${date}（${sha}），本地构建于 ${local}。可下载新数据包应用，或到仓库获取最新内容。`
            } else {
              this.repoOk = true
              this.repoMsg = `✓ 已是最新：本地构建 ${local} ≥ 源仓库最新提交 ${date}（${sha}）`
            }
          } else {
            this.repoOk = false
            this.repoMsg = '接口返回异常（HTTP ' + res.statusCode + '）'
          }
        },
        fail: () => { this.repoOk = false; this.repoMsg = '网络请求失败（GitHub API 需可访问）' },
        complete: () => { this.checking = false }
      })
    },
    downloadPack() {
      const url = this.packUrl.trim()
      if (!url || !(url.startsWith('http://') || url.startsWith('https://'))) {
        this.packOk = false; this.packMsg = '请输入有效的数据包地址'; return
      }
      if (this.downloading) return
      this.downloading = true
      this.packMsg = ''
      uni.request({
        url, method: 'GET', timeout: 120000,
        success: async res => {
          const data = res.data
          if (data && data.meta && data.meta.counts && data.shanghan && data.bencao) {
            const ok = hotPack.save(url, data)
            if (ok) {
              this.packOk = true
              this.hotDate = hotPack.date()
              this.packMsg = '✓ 数据包已应用（' + data.meta.builtAt + ' · ' + data.meta.counts.herbs + '味/' + data.meta.counts.formulas + '方），全部内容已生效'
            } else {
              this.packOk = false; this.packMsg = '保存失败：设备存储不可用'
            }
          } else {
            this.packOk = false; this.packMsg = '✗ 不是有效的数据包（缺少 meta/内容字段）'
          }
        },
        fail: () => { this.packOk = false; this.packMsg = '下载失败，请检查地址与网络' },
        complete: () => { this.downloading = false }
      })
    },
    clearPack() {
      hotPack.clear()
      this.hotDate = ''
      this.packOk = true
      this.packMsg = '已恢复内置数据包（重启应用后完全生效）'
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
.kv { display: flex; padding: 12rpx 0; font-size: 23rpx; border-bottom: 1rpx dashed var(--line); }
.kv:last-child { border-bottom: none; }
.k { width: 170rpx; color: var(--ink2); flex-shrink: 0; }
.v { flex: 1; color: var(--ink); }
.v.hl { color: var(--brand); font-weight: 700; }
.b-acts { display: flex; gap: 16rpx; margin-top: 22rpx; }
.b-btn { flex: 1; text-align: center; border-radius: 40rpx; padding: 18rpx 0; font-size: 24rpx; font-weight: 700; border: 2rpx solid var(--brand); color: var(--brand); }
.b-btn.main { background: linear-gradient(135deg, var(--brand), var(--brand-deep)); color: #FDF8EE; border-color: transparent; }
.b-btn.warn2 { border-color: #833B3B; color: #833B3B; }
.in-row { margin-top: 8rpx; }
.in { width: 100%; background: var(--zebra-bg); border-radius: 14rpx; height: 80rpx; line-height: 80rpx; padding: 0 24rpx; font-size: 23rpx; color: var(--ink); }
.b-tip { margin-top: 16rpx; font-size: 21rpx; border-radius: 10rpx; padding: 12rpx 18rpx; line-height: 1.7; }
.b-tip.ok { color: #3F6B37; background: #E8F0E4; }
.b-tip.warn { color: #A2651B; background: #FCF3DC; }
.b-note { margin-top: 14rpx; font-size: 19rpx; color: var(--ink2); line-height: 1.7; }
</style>
