<template>
  <view class="page" :class="theme === 'dark' ? 'tdark' : 'tlight'">
    <view class="progress" :style="{ width: progress + '%' }" />
    <view class="wrap" v-if="item">
      <view class="r-head">
        <view class="r-path" v-if="pathLabel">{{ pathLabel }}</view>
        <view class="r-title serif">{{ item.t || item.n || '正文' }}</view>
        <view class="r-orn"><view /><view class="d" /><view /></view>
        <view class="r-meta" v-if="subLine">{{ subLine }}</view>
      </view>
      <view class="r-body card">
        <md-blocks :blocks="blocks" :base="28" />
        <view v-if="!blocks.length" class="empty">该条目为空</view>
      </view>
      <view class="r-foot">
        <text>—— 完 ——</text>
      </view>
      <view class="r-nav" v-if="prev || next">
        <view class="rn-btn" :class="{ dis: !prev }" @tap="goPrev">‹ 上一篇</view>
        <view class="rn-mid">{{ posInfo }}</view>
        <view class="rn-btn" :class="{ dis: !next }" @tap="goNext">下一篇 ›</view>
      </view>
    </view>
    <view class="empty-state" v-else>
      <view class="es-orn serif">空</view>
      <view class="es-t">请从列表选择内容进入阅读</view>
      <view class="es-btn" @tap="goBack">‹ 返回</view>
    </view>

    <!-- 悬浮操作：收纳式（默认单钮，展开子钮，不遮挡正文） -->
    <view class="fab-warp" v-if="item">
      <view class="fab-menu" v-if="fabOpen">
        <view class="f-btn" v-for="(b, i) in fabBtns" :key="i" :style="{ transitionDelay: (fabOpen ? i * 30 : 0) + 'ms' }" @tap="b.fn">
          <image v-if="b.img" class="ico-lg" :src="b.img" />
          <text v-else class="f-txt">{{ b.t }}</text>
        </view>
      </view>
      <view class="fab-main" @tap="fabOpen = !fabOpen">
        <view class="fm-dot" v-for="i in 3" :key="i" />
      </view>
    </view>

    <!-- 笔记弹层 -->
    <view class="note-mask" v-if="noteOpen" @tap="noteOpen = false">
      <view class="note-panel card" @tap.stop>
        <view class="np-t serif">笔记 · {{ (item && (item.t || item.n)) || '' }}</view>
        <textarea class="np-ta" v-model="noteText" :maxlength="500" placeholder="记录心得、疑问或助记口诀…" />
        <view class="np-acts">
          <view class="np-btn" @tap="noteOpen = false">取消</view>
          <view class="np-btn main" @tap="saveNote">保存笔记</view>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
import { store, isFav, toggleFav, pushHistory , applyTheme } from '@/utils/store.js'
import { parseMd, setFangNames } from '@/utils/md.js'
import { FILE_LABEL } from '@/utils/routes.js'

export default {
  onShow() { applyTheme() },
  data() {
    return { blocks: [], favState: false, _scrollTop: 0, _key: '', progress: 0, noteOpen: false, noteText: '', speaking: false, fabOpen: false }
  },
  onUnload() {
    uni.$off('open-fang', this.onOpenFang)
    this.saveScroll()
    this.stopSpeak()
  },
  onHide() {
    this.saveScroll()
  },
  onPageScroll(e) {
    this._scrollTop = e.scrollTop || 0
    try {
      const w = uni.getSystemInfoSync()
      const max = Math.max(1, (uni.getWindowInfo ? uni.getWindowInfo().windowHeight : w.windowHeight) * 0.98)
      this.progress = Math.min(100, Math.round(this._scrollTop / max * 100))
    } catch (e0) { /* noop */ }
  },
  computed: {
    theme() { return store.theme },
    fabBtns() {
      const self = this
      return [
        { img: this.isFav ? '/static/icons/starfill-brand.png' : '/static/icons/star-brand.png', fn: () => self.doFav() },
        { t: 'A-', fn: () => self.fontMinus() },
        { t: 'A+', fn: () => self.fontPlus() },
        { img: '/static/icons/copy-brand.png', fn: () => self.copyAll() },
        { img: '/static/icons/note-brand.png', fn: () => self.openNote() },
        { img: '/static/icons/sound-brand.png', fn: () => { if (self.speaking) self.fabOpen = false; self.toggleSpeak() } }
      ]
    },
    item() { const r = store.readerItem; return r && r.kind === 'md' ? r.item : (store.readerReturn && store.readerReturn.kind === 'md' ? store.readerReturn.item : null) },
    pathLabel() {
      const it = this.item
      if (!it) return ''
      if (it.f && FILE_LABEL[it.f]) return FILE_LABEL[it.f]
      if (it.g) return it.g
      return ''
    },
    subLine() {
      const it = this.item
      if (!it) return ''
      const parts = []
      if (it.date) parts.push(it.date)
      if (it.disease) parts.push(it.disease)
      if (it.meridian) parts.push('六经：' + it.meridian)
      if (it.h2) parts.push(it.h2)
      return parts.join(' · ')
    },
    isFav() {
      const it = this.item
      return it ? isFav(it.f || 'misc', it.id) : false
    },
    prev() { return this.ctxAt(-1) },
    next() { return this.ctxAt(1) },
    posInfo() {
      const rl = store.readList
      if (!rl || !rl.items || !rl.items.length) return ''
      return (rl.idx + 1) + ' / ' + rl.items.length
    }
  },
  async mounted() {
    uni.$on('open-fang', this.onOpenFang)
    await this.ensureFang()
    if (this.item) {
      this.blocks = parseMd(this.item.b || '')
      uni.setNavigationBarTitle({ title: (this.item.t || '阅读').slice(0, 16) , fail: () => {} })
      if (this.item.f && this.item.id) pushHistory({ f: this.item.f, i: this.item.id, t: this.item.t || '文档' })
    }
  },
  methods: {
    goBack() { uni.navigateBack({ fail: () => uni.switchTab({ url: '/pages/index/index' }) }) },
    async ensureFang() {
      // 每次进入阅读器都刷新一次词典，避免旧的 nx_fang_cache 遗漏新增方剂。
      try {
        const d = await loadData('formulas')
        const names = [...new Set((d.items || []).map(x => x.n))]
        globalThis.__NX_FORMULA_ITEMS__ = d.items || []
        setFangNames(names)
        return true
      } catch (e) { return false }
    },
    async onOpenFang(name) {
      try {
        uni.showLoading({ title: '打开方剂' })
        const d = await loadData('formulas')
        uni.hideLoading()
        const clean = String(name || '').replace(/[「」“”\s]/g, '')
        const all = d.items || []
        const it = all.find(x => x.n === name || x.n === clean) || all.filter(x => clean.includes(x.n) || x.n.includes(clean)).sort((a, b) => b.n.length - a.n.length)[0]
        if (!it) { uni.showToast({ title: '未收录该方', icon: 'none' }); return }
        store.readerReturn = { kind: 'md', item: this.item }
        store.readerItem = { kind: 'formula', item: it }
        uni.navigateTo({ url: '/pkgFormula/pages/detail' })
      } catch (e) { uni.hideLoading() }
    },
    ctxAt(off) {
      const rl = store.readList
      if (!rl || !rl.items) return null
      const i = rl.idx + off
      if (i < 0 || i >= rl.items.length) return null
      return { item: rl.items[i], idx: i }
    },
    goPrev() { this.gotoCtx(-1) },
    goNext() { this.gotoCtx(1) },
    gotoCtx(off) {
      const t = this.ctxAt(off)
      if (!t) return
      store.readList.idx = t.idx
      store.readerItem = { kind: 'md', item: t.item }
      this._key = ''
      this._scrollTop = 0
      this.blocks = parseMd(t.item.b || '')
      uni.setNavigationBarTitle({ title: (t.item.t || '阅读').slice(0, 16), fail: () => {} })
      if (t.item.f && t.item.id) pushHistory({ f: t.item.f, i: t.item.id, t: t.item.t || '文档' })
      uni.pageScrollTo({ scrollTop: 0, duration: 0 })
    },
    saveScroll() {
      if (!this._key || this._scrollTop < 200) return
      try {
        const map = uni.getStorageSync('nx_scroll') || {}
        map[this._key] = this._scrollTop
        const keys = Object.keys(map)
        if (keys.length > 120) keys.slice(0, keys.length - 120).forEach(k => delete map[k])
        uni.setStorageSync('nx_scroll', map)
      } catch (e) { /* noop */ }
    },
    doFav() {
      const it = this.item
      if (!it) return
      const added = toggleFav({ f: it.f || 'misc', i: it.id, t: it.t || '文档', s: (it.b || '').slice(0, 80) })
      uni.showToast({ title: added ? '已收藏' : '已取消', icon: 'none' })
      this.favState = !this.favState
    },
    fontMinus() {
      const v = Math.max(0.85, (store.fontScale || 1) - 0.15)
      store.fontScale = Math.round(v * 100) / 100
      uni.setStorageSync('nx_font', store.fontScale)
    },
    fontPlus() {
      const v = Math.min(1.45, (store.fontScale || 1) + 0.15)
      store.fontScale = Math.round(v * 100) / 100
      uni.setStorageSync('nx_font', store.fontScale)
    },
    fabAct(fn) {
      fn()
    },
    openNote() {
      const it = this.item
      if (!it) return
      const key = (it.f || 'misc') + '|' + (it.id || 'x')
      try {
        const notes = uni.getStorageSync('nx_notes') || {}
        this.noteText = (notes[key] && notes[key].note) || ''
      } catch (e) { this.noteText = '' }
      this.noteOpen = true
    },
    saveNote() {
      const it = this.item
      if (!it) return
      const key = (it.f || 'misc') + '|' + (it.id || 'x')
      let notes = {}
      try { notes = uni.getStorageSync('nx_notes') || {} } catch (e) {}
      if (this.noteText.trim()) {
        notes[key] = { t: it.t || it.n || '笔记', note: this.noteText.trim(), ts: Date.now() }
      } else {
        delete notes[key]
      }
      uni.setStorageSync('nx_notes', notes)
      this.noteOpen = false
      uni.showToast({ title: this.noteText.trim() ? '已保存' : '已删除', icon: 'none' })
    },
    speakText() {
      const it = this.item
      if (!it) return ''
      return (it.t || it.n ? String(it.t || it.n) + '。' : '') + String(it.b || '').replace(/[#*>`|\-]/g, '').slice(0, 1200)
    },
    toggleSpeak() {
      if (this.speaking) { this.stopSpeak(); return }
      // #ifdef H5
      try {
        const synth = window.speechSynthesis
        if (!synth || typeof window.SpeechSynthesisUtterance === 'undefined') {
          uni.showToast({ title: '当前浏览器不支持语音合成', icon: 'none' }); return
        }
        if (synth.getVoices && synth.getVoices().length === 0 && !this._voicesWarm) {
          // 部分浏览器 voices 异步加载：先触发一次，给明确提示
          synth.getVoices()
          this._voicesWarm = true
        }
        const u = new window.SpeechSynthesisUtterance(this.speakText())
        u.lang = 'zh-CN'
        u.rate = 0.95
        u.onstart = () => { this.speaking = true }
        u.onend = () => { this.speaking = false }
        u.onerror = () => { this.speaking = false; uni.showToast({ title: '未检测到可用语音引擎（可在系统设置添加中文TTS）', icon: 'none' }) }
        synth.cancel()
        synth.speak(u)
        this.speaking = true
        return
      } catch (e) { uni.showToast({ title: '语音不可用', icon: 'none' }); return }
      // #endif
      // #ifdef APP-PLUS
      try {
        if (!plus.speech || typeof plus.speech.speak !== 'function') {
          uni.showToast({ title: '此基座未包含语音模块', icon: 'none' }); return
        }
        plus.speech.speak(this.speakText(), () => { this.speaking = false }, () => { this.speaking = false })
        this.speaking = true
      } catch (e) { uni.showToast({ title: '语音不可用', icon: 'none' }) }
      // #endif
      // #ifndef H5
      // #ifndef APP-PLUS
      uni.showToast({ title: '当前平台暂不支持', icon: 'none' })
      // #endif
      // #endif
    },
    stopSpeak() {
      // #ifdef H5
      try { window.speechSynthesis.cancel() } catch (e) {}
      // #endif
      // #ifdef APP-PLUS
      try { plus.speech.stop() } catch (e) {}
      // #endif
      this.speaking = false
    },
    copyAll() {
      const it = this.item
      if (!it) return
      uni.setClipboardData({ data: (it.t ? it.t + '\n\n' : '') + (it.b || '') })
    }
  }
}
</script>

<style scoped>
.page { min-height: 100vh; background: var(--bg); padding-bottom: 160rpx; }
.progress { position: fixed; top: 0; left: 0; height: 5rpx; z-index: 99; background: linear-gradient(90deg, var(--gold), var(--brand)); border-radius: 0 4rpx 4rpx 0; transition: width .15s linear; }
.wrap { padding: 30rpx 32rpx 0; }
.r-head { padding: 6rpx 8rpx 26rpx; }
.r-path { display: inline-block; font-size: 20rpx; color: var(--gold); border: 1rpx solid var(--gold); border-radius: 8rpx; padding: 2rpx 14rpx; margin-bottom: 16rpx; }
.r-title { font-size: 44rpx; font-weight: 800; color: var(--ink); line-height: 1.4; letter-spacing: 2rpx; }
.r-orn { display: flex; align-items: center; margin-top: 18rpx; }
.r-orn view { flex: 1; height: 1rpx; background: var(--line); }
.r-orn .d { flex: 0 0 12rpx; height: 12rpx; transform: rotate(45deg); background: var(--gold); margin: 0 16rpx; border-radius: 2rpx; }
.r-meta { font-size: 23rpx; color: var(--ink2); margin-top: 14rpx; }
.r-body { padding: 34rpx 34rpx 40rpx; }
.empty { text-align: center; color: var(--ink2); padding: 60rpx 0; }
.r-foot { display: flex; align-items: center; justify-content: center; color: var(--gold); font-size: 22rpx; margin: 44rpx 0; letter-spacing: 8rpx; }
.r-foot::before, .r-foot::after { content: ''; width: 70rpx; height: 1rpx; background: linear-gradient(90deg, transparent, var(--gold)); margin: 0 22rpx; }
.r-foot::after { background: linear-gradient(90deg, var(--gold), transparent); }
.r-nav { display: flex; align-items: center; margin: 10rpx 0 30rpx; background: var(--card); border-radius: 20rpx; padding: 20rpx 26rpx; box-shadow: 0 4rpx 20rpx rgba(60,44,22,.06); }
.rn-btn { font-size: 26rpx; color: var(--brand); font-weight: 700; padding: 6rpx 10rpx; }
.rn-btn.dis { color: var(--ink2); opacity: .4; }
.rn-mid { flex: 1; text-align: center; font-size: 22rpx; color: var(--ink2); }
.empty-state { display: flex; flex-direction: column; align-items: center; padding: 220rpx 60rpx; }
.es-orn { width: 120rpx; height: 120rpx; border: 4rpx solid var(--line); border-radius: 24rpx; color: var(--gold); opacity: .5; font-size: 52rpx; font-weight: 800; display: flex; align-items: center; justify-content: center; }
.es-t { font-size: 25rpx; color: var(--ink2); margin-top: 30rpx; }
.es-btn { margin-top: 40rpx; font-size: 24rpx; color: var(--brand); border: 2rpx solid var(--brand); border-radius: 40rpx; padding: 12rpx 60rpx; font-weight: 700; }
.fab-warp { position: fixed; right: 24rpx; bottom: 80rpx; z-index: 99; display: flex; flex-direction: column; align-items: flex-end; }
.fab-menu { display: flex; flex-direction: column; box-shadow: 0 8rpx 30rpx rgba(60,44,22,.18); border-radius: 40rpx; background: var(--card); overflow: hidden; margin-bottom: 14rpx; }
.f-btn { width: 96rpx; height: 88rpx; display: flex; align-items: center; justify-content: center; border-bottom: 1rpx solid var(--line); }
.f-btn:last-child { border-bottom: none; }
.f-txt { font-size: 27rpx; font-weight: 700; color: var(--brand); }
.f-btn.on { background: var(--zebra-bg); }
.fab-main { width: 88rpx; height: 88rpx; border-radius: 50%; background: var(--card); box-shadow: 0 8rpx 26rpx rgba(60,44,22,.22); display: flex; align-items: center; justify-content: center; flex-direction: column; }
.fm-dot { width: 8rpx; height: 8rpx; border-radius: 50%; background: var(--brand); margin: 3rpx 0; }
.note-mask { position: fixed; inset: 0; background: rgba(20,12,6,.5); z-index: 998; display: flex; align-items: center; justify-content: center; }
.note-panel { width: 86%; padding: 30rpx 30rpx 24rpx; }
.np-t { font-size: 27rpx; font-weight: 800; color: var(--brand); margin-bottom: 18rpx; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.np-ta { width: 100%; height: 280rpx; background: var(--zebra-bg); border-radius: 14rpx; padding: 20rpx 24rpx; box-sizing: border-box; font-size: 25rpx; color: var(--ink); line-height: 1.7; }
.np-acts { display: flex; gap: 16rpx; margin-top: 22rpx; }
.np-btn { flex: 1; text-align: center; border-radius: 36rpx; padding: 16rpx 0; font-size: 25rpx; font-weight: 700; border: 2rpx solid var(--line); color: var(--ink2); }
.np-btn.main { background: linear-gradient(135deg, var(--brand), var(--brand-deep)); color: #FDF8EE; border-color: transparent; }
</style>
