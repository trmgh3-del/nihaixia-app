/* App 启动版本检查：每次进程启动只检查一次，避免重复请求、重复弹窗和重复下载。 */
// 配置仓库信息（修改这里即可切换存储源）
const CONFIG = {
  // Gitee 配置（国内推荐，速度快）
  gitee: {
    user: 'your-username',  // ← 改成你的 Gitee 用户名
    repo: 'nihaixia-app',   // ← 改成你的 Gitee 仓库名
    branch: 'master'
  },
  // GitHub 备用（国外访问）
  github: {
    user: 'trmgh3-del',
    repo: 'nihaixia-app',
    branch: 'main'
  }
}

// 生成下载链接
function getApkUrls() {
  const urls = []
  
  // Gitee 链接（优先）
  if (CONFIG.gitee.user !== 'your-username') {
    const giteeBase = `https://gitee.com/${CONFIG.gitee.user}/${CONFIG.gitee.repo}/raw/${CONFIG.gitee.branch}`
    urls.push({
      name: 'Gitee',
      versionUrl: `${giteeBase}/releases/version.json`,
      apkUrl: `${giteeBase}/releases/latest.apk`
    })
  }
  
  // GitHub 链接（备用）
  const githubBase = `https://cdn.jsdelivr.net/gh/${CONFIG.github.user}/${CONFIG.github.repo}@${CONFIG.github.branch}`
  urls.push({
    name: 'GitHub',
    versionUrl: `${githubBase}/releases/version.json`,
    apkUrl: `${githubBase}/releases/latest.apk`
  })
  
  return urls
}

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
        try { uni.setStorageSync(KNOWN_VERSION_KEY, version) } catch (e) {}
      }
    }
  })
}

// 尝试从指定源检查更新
function tryCheckUpdate(source, current, knownVersion, callback) {
  uni.request({
    url: source.versionUrl,
    method: 'GET', timeout: 15000,
    success: res => {
      if (res.statusCode === 200 && res.data && res.data.version) {
        const latestVersion = res.data.version
        const asset = { name: 'latest.apk', url: source.apkUrl }
        
        if (newer(latestVersion, current) && newer(latestVersion, knownVersion)) {
          callback(true, asset, latestVersion, source.name)
        } else {
          callback(false, null, null, source.name)
        }
      } else {
        callback(false, null, null, source.name)
      }
    },
    fail: () => callback(false, null, null, source.name)
  })
}

export function checkAppUpdate(silent = false) {
  if (typeof globalThis !== 'undefined' && globalThis.__NX_UPDATE_CHECKED__) return
  if (typeof globalThis !== 'undefined') globalThis.__NX_UPDATE_CHECKED__ = true
  const current = (uni.getSystemInfoSync && uni.getSystemInfoSync().appVersion) || '1.0.0'
  
  let knownVersion = ''
  try { knownVersion = uni.getStorageSync(KNOWN_VERSION_KEY) || '' } catch (e) {}
  
  const sources = getApkUrls()
  let sourceIndex = 0
  
  function tryNextSource() {
    if (sourceIndex >= sources.length) {
      // 所有源都检查完毕，没有更新
      if (!silent) uni.showToast({ title: '当前已是最新版本', icon: 'none', duration: 2200 })
      return
    }
    
    const source = sources[sourceIndex]
    sourceIndex++
    
    tryCheckUpdate(source, current, knownVersion, (hasUpdate, asset, version, sourceName) => {
      if (hasUpdate) {
        promptUpdate(asset, version)
      } else {
        // 当前源没有更新，尝试下一个源
        tryNextSource()
      }
    })
  }
  
  tryNextSource()
}
