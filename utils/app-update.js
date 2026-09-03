/* App 启动版本检查：每次进程启动只检查一次 */
const REPO = 'trmgh3-del/nihaixia-app'
const GITHUB_RAW = `https://raw.githubusercontent.com/${REPO}/main`
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

export function checkAppUpdate(silent = false) {
  if (typeof globalThis !== 'undefined' && globalThis.__NX_UPDATE_CHECKED__) return
  if (typeof globalThis !== 'undefined') globalThis.__NX_UPDATE_CHECKED__ = true
  
  const current = (uni.getSystemInfoSync && uni.getSystemInfoSync().appVersion) || '1.0.0'
  let knownVersion = ''
  try { knownVersion = uni.getStorageSync(KNOWN_VERSION_KEY) || '' } catch (e) {}
  
  console.log('[更新检查] 当前版本:', current, '已知版本:', knownVersion)
  
  uni.request({
    url: `${GITHUB_RAW}/releases/version.json`,
    method: 'GET', timeout: 15000,
    success: res => {
      console.log('[更新检查] version.json 响应:', res.statusCode, res.data)
      if (res.statusCode === 200 && res.data && res.data.version) {
        const version = res.data.version
        const isNewer = newer(version, current)
        const isNewerThanKnown = newer(version, knownVersion)
        console.log('[更新检查] 最新版本:', version, '是否更新:', isNewer, '是否新于已知:', isNewerThanKnown)
        
        if (isNewer && isNewerThanKnown) {
          console.log('[更新检查] 显示更新弹窗')
          uni.showModal({
            title: '发现新版本',
            content: `${version} 已发布，是否下载？`,
            confirmText: '下载更新',
            cancelText: '暂不更新',
            success: r => {
              console.log('[更新检查] 用户选择:', r.confirm ? '下载' : '暂不')
              if (r.confirm) {
                // 开始下载
                uni.showLoading({ title: '下载中...' })
                const apkUrl = `${GITHUB_RAW}/releases/latest.apk`
                console.log('[更新检查] 下载地址:', apkUrl)
                const task = uni.downloadFile({
                  url: apkUrl,
                  success: res => {
                    uni.hideLoading()
                    console.log('[更新检查] 下载结果:', res.statusCode, res.tempFilePath)
                    if (res.statusCode === 200 && res.tempFilePath) {
                      uni.showModal({
                        title: '下载完成',
                        content: '是否立即安装？',
                        confirmText: '安装',
                        cancelText: '稍后',
                        success: r2 => {
                          if (r2.confirm && typeof plus !== 'undefined' && plus.runtime) {
                            plus.runtime.install(res.tempFilePath, {}, 
                              () => uni.showToast({ title: '安装成功', icon: 'success' }),
                              (e) => { console.log('[更新检查] 安装失败:', e); uni.showToast({ title: '安装失败', icon: 'none' }) }
                            )
                          }
                        }
                      })
                    } else {
                      uni.showModal({ title: '下载失败', content: '请检查网络后重试', showCancel: false })
                    }
                  },
                  fail: (e) => {
                    uni.hideLoading()
                    console.log('[更新检查] 下载失败:', e)
                    uni.showModal({ title: '下载失败', content: '请检查网络后重试', showCancel: false })
                  }
                })
                // 监听下载进度
                if (task && task.onProgressUpdate) {
                  task.onProgressUpdate(res => {
                    console.log('[更新检查] 下载进度:', res.progress + '%')
                  })
                }
              } else {
                try { uni.setStorageSync(KNOWN_VERSION_KEY, version) } catch (e) {}
              }
            }
          })
        } else if (!silent) {
          console.log('[更新检查] 已是最新版本')
          uni.showToast({ title: '当前已是最新版本', icon: 'none', duration: 2200 })
        }
      } else if (!silent) {
        uni.showToast({ title: '当前已是最新版本', icon: 'none', duration: 2200 })
      }
    },
    fail: (e) => { 
      console.log('[更新检查] 请求失败:', e)
      if (!silent) uni.showToast({ title: '当前已是最新版本', icon: 'none', duration: 2200 }) 
    }
  })
}
