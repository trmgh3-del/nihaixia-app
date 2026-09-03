/* App 启动版本检查：每次进程启动只检查一次，避免重复请求、重复弹窗和重复下载。 */
const REPO = 'trmgh3-del/nihaixia-app'
const API = `https://api.github.com/repos/${REPO}`
// 使用 jsdelivr CDN 避免 GitHub API 限流
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

function request(url, success, fail) {
  uni.request({ url, method: 'GET', timeout: 20000, header: { Accept: 'application/vnd.github+json', 'User-Agent': 'nihaixia-app' }, success, fail })
}

// 从 version.json 获取版本信息（优先使用 CDN）
function checkByVersionJson(callback) {
  const url = `${CDN}/releases/version.json`
  uni.request({
    url, method: 'GET', timeout: 15000,
    success: res => {
      if (res.statusCode === 200 && res.data && res.data.version && res.data.apk) {
        const { version, apk } = res.data
        const apkUrl = `${CDN}/releases/${encodeURIComponent(apk)}`
        callback({ name: apk, url: apkUrl }, version)
      } else {
        callback(null, null)
      }
    },
    fail: () => callback(null, null)
  })
}

// 从 GitHub API 扫描目录获取最新 APK
function checkByScanDir(callback) {
  const dirs = ['releases', 'release']
  const scan = i => {
    if (i >= dirs.length) { callback(null, null); return }
    const dir = dirs[i]
    request(`${API}/contents/${dir}?ref=main`, result => {
      const files = Array.isArray(result.data) ? result.data : []
      // 优先找 latest.apk，否则找版本号最大的
      let file = files.find(x => x && x.type === 'file' && x.name === 'latest.apk')
      if (!file) {
        const apks = files.filter(x => x && x.type === 'file' && /\.apk$/i.test(x.name || ''))
        file = apks.sort((a, b) => (b.name || '').localeCompare(a.name || ''))[0]
      }
      if (file) {
        const version = (file.name.match(/v?\d+(?:\.\d+)+/i) || [])[0] || '未知'
        callback({ name: file.name, url: `https://raw.githubusercontent.com/${REPO}/main/${dir}/${encodeURIComponent(file.name)}` }, version)
      } else scan(i + 1)
    }, () => scan(i + 1))
  }
  scan(0)
}

export function checkAppUpdate(silent = false) {
  if (typeof globalThis !== 'undefined' && globalThis.__NX_UPDATE_CHECKED__) return
  if (typeof globalThis !== 'undefined') globalThis.__NX_UPDATE_CHECKED__ = true
  const current = (uni.getSystemInfoSync && uni.getSystemInfoSync().appVersion) || '1.0.0'
  const finish = (asset, version) => {
    if (asset && version && newer(version, current)) promptUpdate(asset, version)
    else if (!silent) uni.showToast({ title: '当前已是最新版本', icon: 'none', duration: 2200 })
  }

  // 优先从 version.json 获取（CDN，无限流）
  checkByVersionJson((asset, version) => {
    if (asset && version) { finish(asset, version); return }
    // version.json 失败，尝试扫描目录
    checkByScanDir(finish)
  })
}
