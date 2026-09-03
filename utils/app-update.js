/* App 启动版本检查：每次进程启动只检查一次 */
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

function install(url) {
  // #ifdef H5
  if (typeof window !== 'undefined') window.open(url, '_blank', 'noopener,noreferrer')
  // #endif
  // #ifndef H5
  // 显示下载进度弹窗
  let progress = 0
  const modal = uni.showModal({
    title: '下载更新中',
    content: '准备下载...',
    showCancel: false,
    confirmText: '后台下载'
  })
  
  const task = uni.downloadFile({
    url,
    success: res => {
      if (res.statusCode !== 200 || !res.tempFilePath) {
        uni.showModal({ title: '下载失败', content: '请检查网络后重试', showCancel: false })
        return
      }
      uni.showModal({
        title: '下载完成',
        content: '是否立即安装？',
        confirmText: '安装',
        cancelText: '稍后',
        success: r => {
          if (r.confirm) {
            if (typeof plus !== 'undefined' && plus.runtime) {
              plus.runtime.install(res.tempFilePath, {}, 
                () => uni.showToast({ title: '安装成功', icon: 'success' }),
                () => uni.showToast({ title: '安装失败', icon: 'none' })
              )
            } else {
              uni.showToast({ title: '请手动安装', icon: 'none' })
            }
          }
        }
      })
    },
    fail: () => uni.showModal({ title: '下载失败', content: '请检查网络后重试', showCancel: false })
  })
  
  // 监听下载进度
  if (task && task.onProgressUpdate) {
    task.onProgressUpdate(res => {
      progress = res.progress
      // 更新进度显示
      uni.showModal({
        title: '下载更新中',
        content: `下载进度：${progress}%`,
        showCancel: false,
        confirmText: '后台下载'
      })
    })
  }
  // #endif
}

export function checkAppUpdate(silent = false) {
  if (typeof globalThis !== 'undefined' && globalThis.__NX_UPDATE_CHECKED__) return
  if (typeof globalThis !== 'undefined') globalThis.__NX_UPDATE_CHECKED__ = true
  
  const current = (uni.getSystemInfoSync && uni.getSystemInfoSync().appVersion) || '1.0.0'
  let knownVersion = ''
  try { knownVersion = uni.getStorageSync(KNOWN_VERSION_KEY) || '' } catch (e) {}
  
  uni.request({
    url: `${CDN}/releases/version.json`,
    method: 'GET', timeout: 15000,
    success: res => {
      if (res.statusCode === 200 && res.data && res.data.version) {
        const version = res.data.version
        if (newer(version, current) && newer(version, knownVersion)) {
          uni.showModal({
            title: '发现新版本',
            content: `${version} 已发布，是否下载？`,
            confirmText: '下载更新', cancelText: '暂不更新',
            success: r => {
              if (r.confirm) install(`${CDN}/releases/latest.apk`)
              else try { uni.setStorageSync(KNOWN_VERSION_KEY, version) } catch (e) {}
            }
          })
        } else if (!silent) {
          uni.showToast({ title: '当前已是最新版本', icon: 'none', duration: 2200 })
        }
      } else if (!silent) {
        uni.showToast({ title: '当前已是最新版本', icon: 'none', duration: 2200 })
      }
    },
    fail: () => { if (!silent) uni.showToast({ title: '当前已是最新版本', icon: 'none', duration: 2200 }) }
  })
}
