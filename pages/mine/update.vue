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

    <view class="blk card fade-in update-note">
      <view class="b-t serif">App 版本更新</view>
      <view class="b-d">App 每次启动时自动检查一次版本。发现新版本后会弹窗确认，并在确认后下载、安装；手动检查时版本相同会提示“已是最新版”。</view>
      <view class="download-box" v-if="apkDownloading">
        <view class="download-line"><text>正在下载 APK</text><text>{{ downloadProgress }}%</text></view>
        <view class="download-track"><view class="download-fill" :style="{ width: downloadProgress + '%' }"></view></view>
        <view class="download-note">请保持网络连接，下载完成后将弹出系统安装确认。</view>
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
      releaseChecking: false, releaseMsg: '', releaseOk: false, releaseUrl: '', releaseAsset: null,
      apkDownloading: false, downloadProgress: 0 }
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
      
      const REPO = 'trmgh3-del/nihaixia-app'
      const CDN = `https://cdn.jsdelivr.net/gh/${REPO}@main`
      
      let knownVersion = ''
      try { knownVersion = uni.getStorageSync('nihaixia_known_version') || '' } catch (e) {}
      
      uni.request({
        url: `${CDN}/releases/version.json`,
        method: 'GET', timeout: 15000,
        success: res => {
          if (res.statusCode === 200 && res.data && res.data.version) {
            const version = res.data.version
            const apkUrl = `${CDN}/releases/latest.apk`
            
            this.releaseAsset = { name: 'latest.apk', browser_download_url: apkUrl }
            this.releaseOk = true
            this.releaseMsg = `最新版本：${version}`
            
            if (this.isNewerApp(version) && this.isNewerThan(version, knownVersion)) {
              this.offerInstall(this.releaseAsset, version)
            } else if (!silent) {
              uni.showToast({ title: '已是最新版', icon: 'none', duration: 2200 })
            }
          } else {
            this.releaseOk = false
            this.releaseMsg = '暂无可用更新'
          }
          this.releaseChecking = false
        },
        fail: () => {
          this.releaseOk = false
          this.releaseMsg = '检查失败，请稍后重试'
          this.releaseChecking = false
        }
      })
    },
    isNewerThan(tag, base) {    isNewerThan(tag, base) {
      if (!base) return true
      const a = String(base || '0.0.0').replace(/^v/i, '').split('.').map(Number)
      const m = String(tag || '').match(/\d+(?:\.\d+)+/)
      if (!m) return false
      const b = m[0].split('.').map(Number)
      for (let i = 0; i < Math.max(a.length, b.length); i++) {
        if ((b[i] || 0) !== (a[i] || 0)) return (b[i] || 0) > (a[i] || 0)
      }
      return false
    },
    offerInstall(asset, version) {
      const KNOWN_VERSION_KEY = 'nihaixia_known_version'
      uni.showModal({ 
        title: '发现 App 新版本', 
        content: `${version} 已发布，是否下载并安装？`, 
        confirmText: '下载更新', 
        cancelText: '稍后', 
        success: x => { 
          if (x.confirm) {
            this.downloadRelease(asset, true)
          } else {
            // 用户选择稍后，记录版本号
            try { uni.setStorageSync(KNOWN_VERSION_KEY, version) } catch (e) {}
          }
        } 
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

    downloadRelease(asset, confirmed = false) {
      if (!asset || !asset.browser_download_url || this.apkDownloading) return
      if (!confirmed) { this.offerInstall(asset, asset.name || '新版本'); return }
      // H5 不能安装 APK；App 端下载后交给系统安装器，仍需用户确认。
      // #ifdef H5
      this.openExternal(asset.browser_download_url)
      // #endif
      // #ifndef H5
      this.apkDownloading = true
      this.downloadProgress = 0
      const task = uni.downloadFile({ url: asset.browser_download_url, success: res => {
        if (res.statusCode !== 200 || !res.tempFilePath) { uni.showToast({ title: '下载失败', icon: 'none' }); return }
        if (typeof plus !== 'undefined' && plus.runtime) plus.runtime.install(res.tempFilePath, {}, () => {}, () => uni.showToast({ title: '安装失败', icon: 'none' }))
        else uni.showToast({ title: '请打开下载页安装', icon: 'none' })
      }, fail: () => uni.showToast({ title: '下载失败，请检查网络', icon: 'none' }), complete: () => { this.apkDownloading = false } })
      if (task && task.onProgressUpdate) task.onProgressUpdate(e => { this.downloadProgress = Math.max(0, Math.min(100, e.progress || 0)) })
      // #endif
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
.download-box { margin-top: 18rpx; padding: 18rpx 20rpx; border: 1rpx solid var(--line); border-radius: 14rpx; background: var(--zebra-bg); }
.download-line { display: flex; justify-content: space-between; color: var(--brand); font-size: 23rpx; font-weight: 700; }
.download-track { height: 14rpx; margin-top: 12rpx; background: var(--line); border-radius: 10rpx; overflow: hidden; }
.download-fill { height: 100%; border-radius: 10rpx; background: linear-gradient(90deg, var(--gold), var(--brand)); transition: width .2s ease; }
.download-note { margin-top: 10rpx; color: var(--ink2); font-size: 19rpx; }
.b-note { margin-top: 14rpx; font-size: 19rpx; color: var(--ink2); line-height: 1.7; }
</style>
