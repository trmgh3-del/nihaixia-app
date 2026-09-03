/* App 启动版本检查：每次进程启动只检查一次，避免重复请求、重复弹窗和重复下载。 */
const REPO = 'trmgh3-del/nihaixia-app'
const CDN = `https://cdn.jsdelivr.net/gh/${REPO}@main`

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
    success: r => { if (r.confirm) install(asset) }
  })
}

// 从 version.json 获取版本号
function getVersionFromJson(callback) {
  uni.request({
    url: `${CDN}/releases/version.json`,
    method: 'GET', timeout: 15000,
    success: res => {
      if (res.statusCode === 200 && res.data && res.data.version) {
        callback(res.data.version)
      } else {
        callback(null)
      }
    },
    fail: () => callback(null)
  })
}

export function checkAppUpdate(silent = false) {
  if (typeof globalThis !== 'undefined' && globalThis.__NX_UPDATE_CHECKED__) return
  if (typeof globalThis !== 'undefined') globalThis.__NX_UPDATE_CHECKED__ = true
  const current = (uni.getSystemInfoSync && uni.getSystemInfoSync().appVersion) || '1.0.0'
  
  const apkUrl = `${CDN}/releases/latest.apk`
  
  // 先从 version.json 获取版本号，获取不到则用文件检查
  getVersionFromJson(version => {
    if (version) {
      // 有版本号，直接判断
      const asset = { name: 'latest.apk', url: apkUrl }
      if (newer(version, current)) {
        promptUpdate(asset, version)
      } else if (!silent) {
        uni.showToast({ title: '当前已是最新版本', icon: 'none', duration: 2200 })
      }
    } else {
      // 没有 version.json，尝试直接下载 APK 检查是否存在
      uni.request({
        url: apkUrl,
        method: 'HEAD',
        timeout: 10000,
        success: res => {
          if (res.statusCode === 200) {
            // APK 存在，但不知道版本号，提示用户有新版本
            const asset = { name: 'latest.apk', url: apkUrl }
            promptUpdate(asset, '最新版')
          } else if (!silent) {
            uni.showToast({ title: '当前已是最新版本', icon: 'none', duration: 2200 })
          }
        },
        fail: () => {
          if (!silent) uni.showToast({ title: '当前已是最新版本', icon: 'none', duration: 2200 })
        }
      })
    }
  })
}
