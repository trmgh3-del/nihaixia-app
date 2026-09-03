/* App 启动版本检查：每次进程启动只检查一次，避免重复请求、重复弹窗和重复下载。 */
const REPO = 'trmgh3-del/nihaixia-app'
const CDN = `https://cdn.jsdelivr.net/gh/${REPO}@main`
const KNOWN_VERSION_KEY = 'nihaixia_known_version'

function newer(tag, current) {
  const a = String(current || '0.0.0').replace(/^v/i, '').split('.').map(Number)
  const m = String(tag || '').match(/\d+(?:\.\d+)+/)
  if (!m) return false
  const b = m[0].split('.').map(Number)
  for (let i = 0; i < Math.max(a.length, b.length); i++) {
    if ((b[i] || 0) !== (a[i] || 0)) return (b[i] || 0) > (a[i] || 0)
  }
  return false
}

function install(asset) {
  if (!asset || !asset.url) return
  // #ifdef H5
  if (typeof window !== 'undefined') window.open(asset.url, '_blank', 'noopener,noreferrer')
  // #endif
  // #ifndef H5
  uni.showLoading({ title: '下载更新中' })
  uni.downloadFile({
    url: asset.url,
    success: res => {
      if (res.statusCode !== 200 || !res.tempFilePath) {
        uni.showToast({ title: '下载失败', icon: 'none' }); return
      }
      if (typeof plus !== 'undefined' && plus.runtime) {
        plus.runtime.install(res.tempFilePath, {}, () => {}, () => uni.showToast({ title: '安装失败', icon: 'none' }))
      } else uni.showToast({ title: '请手动安装下载文件', icon: 'none' })
    },
    fail: () => uni.showToast({ title: '下载失败，请检查网络', icon: 'none' }),
    complete: () => uni.hideLoading()
  })
  // #endif
}

function promptUpdate(asset, version) {
  uni.showModal({
    title: '发现新版本',
    content: `${version} 已发布，是否下载并安装？`,
    confirmText: '下载更新', cancelText: '暂不更新',
    success: r => {
      if (r.confirm) {
        install(asset)
      } else {
        // 用户选择暂不更新，记录版本号，下次不再提示
        try { uni.setStorageSync(KNOWN_VERSION_KEY, version) } catch (e) {}
      }
    }
  })
}

export function checkAppUpdate(silent = false) {
  if (typeof globalThis !== 'undefined' && globalThis.__NX_UPDATE_CHECKED__) return
  if (typeof globalThis !== 'undefined') globalThis.__NX_UPDATE_CHECKED__ = true
  const current = (uni.getSystemInfoSync && uni.getSystemInfoSync().appVersion) || '1.0.0'
  
  // 获取本地记录的已知版本
  let knownVersion = ''
  try { knownVersion = uni.getStorageSync(KNOWN_VERSION_KEY) || '' } catch (e) {}
  
  // 从 version.json 获取最新版本号
  uni.request({
    url: `${CDN}/releases/version.json`,
    method: 'GET', timeout: 15000,
    success: res => {
      if (res.statusCode === 200 && res.data && res.data.version) {
        const latestVersion = res.data.version
        const apkUrl = `${CDN}/releases/latest.apk`
        const asset = { name: 'latest.apk', url: apkUrl }
        
        // 判断是否需要更新：版本比当前新 且 比已知版本新
        if (newer(latestVersion, current) && newer(latestVersion, knownVersion)) {
          promptUpdate(asset, latestVersion)
        } else if (!silent) {
          uni.showToast({ title: '当前已是最新版本', icon: 'none', duration: 2200 })
        }
      } else if (!silent) {
        uni.showToast({ title: '当前已是最新版本', icon: 'none', duration: 2200 })
      }
    },
    fail: () => {
      if (!silent) uni.showToast({ title: '当前已是最新版本', icon: 'none', duration: 2200 })
    }
  })
}
