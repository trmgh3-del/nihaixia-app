/* ================= 本地知识库数据加载器 =================
 * 数据位于 static/data/*.json（随 App 打包，离线可用）
 * H5: fetch 相对路径；App(plus): plus.io 读取 _www/static
 */
const cache = {}

/* ================= 热更新数据包（App 端 _doc/data-update.json 优先） ================= */
const hotPack = {
  _data: null,
  KEY_URL: 'nx_pack_url',
  KEY_DATE: 'nx_pack_date',
  load() {
    if (this._data !== null) return this._data
    this._data = false
    // #ifdef APP-PLUS
    try {
      const txt = uni.getStorageSync('nx_pack_data')
      if (txt) {
        const d = JSON.parse(txt)
        if (d && d.meta && d.shanghan) this._data = d
      }
    } catch (e) { /* noop */ }
    // #endif
    return this._data
  },
  save(url, data) {
    // #ifdef APP-PLUS
    try {
      uni.setStorageSync('nx_pack_data', JSON.stringify(data))
      uni.setStorageSync(this.KEY_URL, url)
      uni.setStorageSync(this.KEY_DATE, data.meta && data.meta.builtAt ? data.meta.builtAt : new Date().toISOString().slice(0, 10))
      this._data = data
      Object.keys(cache).forEach(k => delete cache[k]) // 清缓存，立即生效
      return true
    } catch (e) { return false }
    // #endif
    // #ifndef APP-PLUS
    return false
    // #endif
  },
  clear() {
    try {
      uni.removeStorageSync('nx_pack_data')
      uni.removeStorageSync(this.KEY_URL)
      uni.removeStorageSync(this.KEY_DATE)
    } catch (e) { /* noop */ }
    this._data = false
    Object.keys(cache).forEach(k => delete cache[k])
  },
  date() { try { return uni.getStorageSync(this.KEY_DATE) || '' } catch (e) { return '' } },
  url() { try { return uni.getStorageSync(this.KEY_URL) || '' } catch (e) { return '' } }
}

function fromH5(name) {
  return new Promise((resolve, reject) => {
    fetch('/static/data/' + name + '.json')
      .then(r => {
        if (!r.ok) throw new Error('HTTP ' + r.status)
        return r.json()
      })
      .then(resolve)
      .catch(reject)
  })
}

function fromPlus(name) {
  return new Promise((resolve, reject) => {
    // eslint-disable-next-line no-undef
    plus.io.resolveLocalFileSystemURL('_www/static/data/' + name + '.json', entry => {
      entry.file(file => {
        // eslint-disable-next-line no-undef
        const reader = new plus.io.FileReader()
        reader.onloadend = e => {
          try { resolve(JSON.parse(e.target.result)) } catch (err) { reject(err) }
        }
        reader.onerror = () => reject(new Error('read fail'))
        reader.readAsText(file, 'utf-8')
      }, reject)
    }, reject)
  })
}

export function loadData(name) {
  if (!cache[name]) {
    const hot = hotPack.load()
    if (hot && hot[name] !== undefined) {
      cache[name] = Promise.resolve(hot[name])
      return cache[name]
    }
    // #ifdef H5
    cache[name] = fromH5(name)
    // #endif
    // #ifdef APP-PLUS
    cache[name] = fromPlus(name)
    // #endif
    // #ifndef H5
    // #ifndef APP-PLUS
    cache[name] = new Promise((resolve, reject) => reject(new Error('平台暂不支持本地数据包')))
    // #endif
    // #endif
  }
  return cache[name]
}

export { hotPack }

/* 小程序兜底：部分平台不支持上述读取时，可把 json 转为 js 模块后 import */
export async function mustData(name) {
  try {
    return await loadData(name)
  } catch (e) {
    console.error('数据加载失败:', name, e)
    uni.showToast({ title: '数据包加载失败', icon: 'none' })
    throw e
  }
}
