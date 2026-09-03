<template>
  <view class="page" :class="theme === 'dark' ? 'tdark' : 'tlight'">
    <!-- 自定义导航 -->
    <view class="nav" :style="{ paddingTop: sb + 'px' }">
      <view class="nav-in">
        <view class="nav-title">
          <text class="nav-name serif">AI 问诊</text>
          <view class="nav-live"><view class="live-dot" />{{ modeLabel }}</view>
        </view>
        <view class="nav-acts">
          <view class="nav-btn" @tap="goCfg"><image class="ico" src="/static/icons/settings-light.png" /></view>
          <view class="nav-btn" @tap="exportChat"><image class="ico" src="/static/icons/share-light.png" /></view>
      <view class="nav-btn" @tap="clearChat"><image class="ico" src="/static/icons/trash-light.png" /></view>
        </view>
      </view>
    </view>

    <!-- 聊天区 -->
    <scroll-view class="chat" scroll-y :scroll-top="scrollTop" :scroll-into-view="scrollInto" scroll-with-animation>
      <view class="notice">
        <text>⟡ 倪师思维内核已内置。回答仅供中医学习参考，不构成医疗建议；急重症请立即就医。</text>
      </view>
      <view v-if="!chats.length" class="welcome card fade-in">
        <view class="w-seal serif">倪</view>
        <view class="w-title serif">倪师思维内核 · 已就绪</view>
        <view class="w-desc">配置任意 OpenAI 兼容接口后，即可以倪海厦的视角与口吻问诊论治：先辨六经、再选方剂、剂量注明体系。</view>
        <view class="w-feats">
          <view class="w-feat"><text class="wf-k">精简内核</text><text>任何模型可用</text></view>
          <view class="w-feat"><text class="wf-k">检索增强</text><text>自动检索本地知识库作答</text></view>
          <view class="w-feat"><text class="wf-k">完整SKILL</text><text>132KB 全量内核（长上下文）</text></view>
        </view>
        <view class="w-cta" @tap="goCfg"><image class="ico-s" src="/static/icons/settings-light.png" />立即配置接口</view>
      </view>
      <template v-for="(m, i) in chats" :key="i">
        <view class="time-divider" v-if="showTimeDivider(i)">{{ fmtTs(m.ts) }}</view>
        <view class="msg" :class="m.role">
          <view class="avatar" v-if="m.role === 'assistant'">倪</view>
          <view class="bubble-wrap">
            <view class="bubble">
              <view v-if="m.role === 'user'" class="b-text">{{ m.content }}</view>
              <md-blocks v-else :blocks="m.blocks || []" :base="26" />
              <view v-if="m.role === 'assistant' && m.loading" class="typing"><view class="t-dot" /><view class="t-dot" /><view class="t-dot" /><text class="cursor">▍</text></view>
              <view v-if="m.refs && m.refs.length" class="b-refs">
                <view class="br-chips">
                  <view class="br-chip" v-for="(rf, ri) in m.refs" :key="ri" @tap="openRef(rf)">{{ rf.t }}</view>
                </view>
              </view>
            </view>
            <view class="b-actions" v-if="m.role === 'assistant' && !m.loading && i === chats.length - 1">
              <text class="b-act" @tap="copyMsg(m)">复制</text>
              <text class="b-act" @tap="regen(i)">重新生成</text>
            </view>
          </view>
          <view class="avatar user" v-if="m.role === 'user'">我</view>
        </view>
      </template>
      <view :id="'end-' + chats.length" style="height: 30rpx" />
    </scroll-view>

    <!-- 快捷提问 -->
    <scroll-view v-if="!chats.length" scroll-x class="quicks">
      <view class="q-row">
        <view v-for="q in quicks" :key="q" class="q-chip" @tap="ask(q)">{{ q }}</view>
      </view>
    </scroll-view>

    <!-- 输入区 -->
    <view class="rec-overlay" v-if="recording" @tap="stopMic">
      <view class="rec-wave">
        <view class="rw-bar" v-for="i in 5" :key="i" :style="{ animationDelay: (i * 0.1) + 's' }" />
      </view>
      <view class="rec-text">{{ interimText || '正在聆听…' }}</view>
      <view class="rec-stop">点击停止录音</view>
    </view>
    <view class="inputbar" :style="{ paddingBottom: (safeBottom + 8) + 'px' }">
      <view class="i-pill">
        <view class="i-mic" :class="{ on: recording }" v-if="micOk" @tap.stop="toggleMic">
          <image class="ico-s" :src="recording ? '/static/icons/sound-light.png' : '/static/icons/sound-brand.png'" />
        </view>
        <textarea v-model="input" class="i-text" :maxlength="2000" placeholder="描述症状 / 提问经方…" :auto-height="true" :adjust-position="true" :show-confirm-bar="false" confirm-type="send" @confirm="send" :disabled="sending" />
        <view class="i-send" :class="{ dis: sending || !input.trim(), on: input.trim() && !sending }" @tap="send">
          <image class="ico" src="/static/icons/send-light.png" />
        </view>
      </view>
    </view>
  </view>
</template>

<script>
import { store, setChats } from '@/utils/store.js'
import { parseMd } from '@/utils/md.js'
import { chatCompletion, QUICK_PROMPTS, lastRagRefs } from '@/utils/ai.js'
import { openEntry } from '@/utils/routes.js'

export default {
  data() {
    return {
      sb: 24,
      safeBottom: 20,
      micOk: false,
      recording: false,
      interimText: '',
      input: '',
      sending: false,
      scrollTop: 0,
      scrollInto: '',
      quicks: QUICK_PROMPTS,
      modes: [
        { k: 'lite', label: '精简内核' },
        { k: 'rag', label: '检索增强' },
        { k: 'full', label: '完整SKILL' }
      ]
    }
  },
  computed: {
    theme() { return store.theme },
    chats() { return store.chats },
    modeLabel() {
      const map = { lite: '精简内核', rag: '检索增强', full: '完整SKILL' }
      return map[store.ai.mode] || '精简内核'
    }
  },
  mounted() {
    const si = uni.getSystemInfoSync()
    this.sb = si.statusBarHeight || 24
    // 语音识别可用性
    // #ifdef APP-PLUS
    this.micOk = !!(plus.speech && typeof plus.speech.startRecognize === 'function')
    // #endif
    // #ifdef H5
    this.micOk = !!(window.SpeechRecognition || window.webkitSpeechRecognition)
    // #endif
    this.safeBottom = si.safeAreaInsets ? si.safeAreaInsets.bottom || 20 : 20
    this.$nextTick(() => this.scrollEnd())
  },
  methods: {
    goCfg() { uni.navigateTo({ url: '/pages/ai/config' }) },
    toggleMic() {
      if (this.recording) { this.stopMic(); return }
      this.interimText = ''
      // #ifdef APP-PLUS
      try {
        plus.speech.startRecognize(
          { lang: 'zh-CN' },
          t => { this.input = (this.input || '') + t; this.interimText = t },
          e => { this.recording = false; this.interimText = '' }
        )
        this.recording = true
      } catch (e) { uni.showToast({ title: '语音识别不可用', icon: 'none' }) }
      // #endif
      // #ifdef H5
      try {
        const SR = window.SpeechRecognition || window.webkitSpeechRecognition
        if (!SR) { uni.showToast({ title: '此浏览器不支持语音识别（推荐Chrome）', icon: 'none' }); return }
        this._rec = new SR()
        this._rec.lang = 'zh-CN'
        this._rec.interimResults = true
        this._rec.continuous = true
        this._rec.maxAlternatives = 1
        this._rec.onresult = ev => {
          let interim = ''
          let final = ''
          for (let i = ev.resultIndex; i < ev.results.length; i++) {
            const r = ev.results[i]
            if (r.isFinal) final += r[0].transcript
            else interim += r[0].transcript
          }
          if (final) {
            this.input = (this.input || '') + final
            this.interimText = ''
          } else if (interim) {
            this.interimText = interim
          }
        }
        this._rec.onend = () => {
          if (this.recording) {
            this.recording = false
            this.interimText = ''
          }
        }
        this._rec.onerror = (ev) => {
          this.recording = false
          this.interimText = ''
          const err = ev.error || ''
          if (err === 'not-allowed') uni.showToast({ title: '请允许麦克风权限', icon: 'none' })
          else if (err === 'no-speech') uni.showToast({ title: '未检测到语音，请靠近麦克风说话', icon: 'none' })
          else if (err === 'network') uni.showToast({ title: '语音服务需要网络连接', icon: 'none' })
        }
        this._rec.start()
        this.recording = true
      } catch (e) {
        this.recording = false
        uni.showToast({ title: '语音识别启动失败', icon: 'none' })
      }
      // #endif
    },
    stopMic() {
      // #ifdef APP-PLUS
      try { plus.speech.stopRecognize() } catch (e) { /* noop */ }
      // #endif
      // #ifdef H5
      try { this._rec && this._rec.stop() } catch (e) { /* noop */ }
      // #endif
      this.recording = false
      this.interimText = ''
    },    exportChat() {
      if (!store.chats.length) { uni.showToast({ title: '暂无对话', icon: 'none' }); return }
      const lines = store.chats.map(c => (c.role === 'user' ? '【问】' : '【倪师经方AI】') + '\n' + c.content)
      uni.setClipboardData({ data: '《倪师经方AI问诊记录》 ' + new Date().toLocaleString() + '\n\n' + lines.join('\n\n———\n\n') + '\n\n（仅供学习参考，用药请遵医嘱）' })
    },
    clearChat() {
      uni.showModal({
        title: '清空对话',
        content: '确定清空当前会话吗？',
        success: r => { if (r.confirm) setChats([]) }
      })
    },
    ask(q) { this.input = q; this.send() },
    send() {
      const q = this.input.trim()
      if (!q || this.sending) return
      if (!store.ai.apiKey) {
        uni.showModal({
          title: '尚未配置接口',
          content: '去配置 API 地址与 Key 后即可开始问诊（支持 DeepSeek / Kimi 等）。',
          confirmText: '去配置',
          success: r => { if (r.confirm) uni.navigateTo({ url: '/pages/ai/config' }) }
        })
        return
      }
      this.input = ''
      store.chats.push({ role: 'user', content: q, ts: Date.now() })
      store.chats.push({ role: 'assistant', content: '', blocks: [], loading: true, ts: Date.now() })
      setChats(store.chats)
      this.scrollEnd()
      this.stream(q)
    },
    async stream(q) {
      this.sending = true
      const reply = store.chats[store.chats.length - 1]
      try {
        await chatCompletion(q, (delta, whole) => {
          if (whole) reply.content = delta
          else reply.content += delta
          reply.blocks = parseMd(reply.content)
          this.scrollEnd()
        })
        // buildMessages 已执行完毕，此时 lastRagRefs 即本次引用
        reply.refs = store.ai.mode === 'rag' ? (lastRagRefs.refs || []).slice(0, 3) : null
        reply.loading = false
      } catch (e) {
        reply.content = (reply.content || '') + '\n\n⚠ ' + (e.message || '请求失败，请检查网络与配置（H5 需接口允许跨域）')
        reply.blocks = parseMd(reply.content)
        reply.loading = false
      }
      setChats(store.chats)
      this.sending = false
    },
    regen() {
      if (this.sending) return
      const lastUser = [...store.chats].reverse().find(c => c.role === 'user')
      if (!lastUser) return
      while (store.chats.length && store.chats[store.chats.length - 1].role !== 'user') store.chats.pop()
      const q = lastUser.content
      store.chats.push({ role: 'assistant', content: '', blocks: [], loading: true, ts: Date.now() })
      setChats(store.chats)
      this.stream(q)
    },
    showTimeDivider(idx) {
      const cur = this.chats[idx]
      if (!cur || !cur.ts) return idx === 0
      if (idx === 0) return true
      const prev = this.chats[idx - 1]
      if (!prev || !prev.ts) return true
      return cur.ts - prev.ts > 5 * 60 * 1000
    },
    fmtTs(ts) {
      const d = new Date(ts)
      const p = n => (n < 10 ? '0' + n : n)
      return p(d.getHours()) + ':' + p(d.getMinutes())
    },
    openRef(rf) {
      openEntry({ f: rf.f, c: rf.c, i: rf.i, t: rf.t })
    },
    copyMsg(m) {
      uni.setClipboardData({ data: m.content })
    },
    scrollEnd() {
      this.$nextTick(() => {
        this.scrollInto = 'end-' + store.chats.length
      })
    }
  }
}
</script>

<style scoped>
.page { height: 100vh; padding-bottom: var(--window-bottom, 0px); box-sizing: border-box; display: flex; flex-direction: column; background: var(--bg); overflow: hidden; }
.nav { background: linear-gradient(140deg, var(--hero1), var(--hero2)); flex-shrink: 0; }
.nav-in { display: flex; align-items: center; padding: 20rpx 32rpx; }
.nav-title { flex: 1; display: flex; align-items: center; }
.nav-name { font-size: 36rpx; font-weight: 800; color: #FDF8EE; letter-spacing: 3rpx; }
.nav-live { margin-left: 18rpx; display: flex; align-items: center; height: 40rpx; font-size: 19rpx; color: #FDF8EE; border: 1rpx solid rgba(253,248,238,.5); border-radius: 22rpx; padding: 0 16rpx; }
.live-dot { width: 12rpx; height: 12rpx; border-radius: 50%; background: #7BD389; margin-right: 10rpx; animation: pulse2 2s infinite; }
@keyframes pulse2 { 50% { opacity: .4; } }
.nav-acts { display: flex; }
.nav-btn { width: 64rpx; height: 64rpx; border-radius: 50%; background: rgba(253,248,238,.16); color: #FDF8EE; display: flex; align-items: center; justify-content: center; font-size: 30rpx; margin-left: 18rpx; }


.chat { flex: 1; min-height: 0; padding: 0 24rpx; box-sizing: border-box; }
.welcome { margin: 20rpx 4rpx 26rpx; padding: 34rpx 30rpx; position: relative; overflow: hidden; }
.w-seal { width: 96rpx; height: 96rpx; border-radius: 22rpx; background: linear-gradient(140deg, #9A2E1F, #7C3A21); color: #FDF8EE; font-size: 52rpx; font-weight: 800; display: flex; align-items: center; justify-content: center; }
.w-title { font-size: 32rpx; font-weight: 800; color: var(--brand); margin-top: 20rpx; letter-spacing: 2rpx; }
.w-desc { font-size: 23rpx; color: var(--ink2); line-height: 1.8; margin-top: 12rpx; }
.w-feats { margin-top: 22rpx; }
.w-feat { display: flex; align-items: center; font-size: 22rpx; color: var(--ink); margin-bottom: 14rpx; }
.wf-k { background: var(--zebra-bg); color: var(--brand); border: 1rpx solid var(--line); border-radius: 8rpx; padding: 2rpx 14rpx; margin-right: 16rpx; font-size: 20rpx; flex-shrink: 0; }
.w-cta { display: flex; align-items: center; justify-content: center; margin-top: 26rpx; background: linear-gradient(135deg, var(--brand), var(--brand-deep)); color: #FDF8EE; border-radius: 40rpx; padding: 20rpx 0; font-size: 26rpx; font-weight: 700; }
.w-cta .ico-s { margin-right: 10rpx; }
.notice { margin: 20rpx 4rpx 26rpx; background: var(--quote-bg); border-left: 5rpx solid var(--gold); border-radius: 0 12rpx 12rpx 0; padding: 16rpx 22rpx; font-size: 21rpx; color: var(--ink2); line-height: 1.7; }
.time-divider { text-align: center; font-size: 18rpx; color: var(--ink2); opacity: .55; padding: 16rpx 0 8rpx; }
.msg { display: flex; margin-bottom: 10rpx; align-items: flex-start; }
.msg.user { justify-content: flex-end; }
.avatar { width: 60rpx; height: 60rpx; border-radius: 16rpx; background: linear-gradient(140deg, #9A2E1F, #7C3A21); color: #FDF8EE; display: flex; align-items: center; justify-content: center; font-size: 28rpx; font-weight: 800; flex-shrink: 0; margin-top: 2rpx; }
.avatar.user { background: linear-gradient(140deg, #356065, #234449); width: 60rpx; height: 60rpx; font-size: 24rpx; }
.bubble-wrap { max-width: 78%; display: flex; flex-direction: column; margin: 0 14rpx; }
.bubble { background: var(--card); border-radius: 4rpx 20rpx 20rpx 20rpx; padding: 14rpx 20rpx; box-shadow: 0 2rpx 8rpx rgba(60,44,22,.04); }
.msg.user .bubble-wrap { align-items: flex-end; }
.msg.user .bubble { background: linear-gradient(140deg, #356065, #2F5D62); border-radius: 20rpx 4rpx 20rpx 20rpx; padding: 12rpx 20rpx; }
.msg.user .b-text { color: #F4F9F9; font-size: 26rpx; line-height: 1.55; margin: 0; }
.bubble :deep(.mdv) { font-size: 25rpx; line-height: 1.62; letter-spacing: 0; margin: 0; }
/* 最后一个子元素不留下方margin，实现紧贴包裹 */
.bubble :deep(.mdv > view:last-child) { margin-bottom: 0 !important; padding-bottom: 0 !important; }
/* 第一个子元素不留上方margin */
.bubble :deep(.mdv > view:first-child) { margin-top: 0 !important; }
.bubble :deep(.mdv .p) { margin: 0.2em 0; }
.bubble :deep(.mdv .p.ind) { text-indent: 2em; }
.bubble :deep(.mdv .h1), .bubble :deep(.mdv .h2), .bubble :deep(.mdv .h3), .bubble :deep(.mdv .h4) { margin: 0.3em 0 0.15em; }
.bubble :deep(.mdv .h1) { font-size: 1.2em; }
.bubble :deep(.mdv .h2) { font-size: 1.1em; }
.bubble :deep(.mdv .h3) { font-size: 1.05em; }
.bubble :deep(.mdv .h4) { font-size: 1em; }
.bubble :deep(.mdv .list) { margin: 0.15em 0; }
.bubble :deep(.mdv .li) { margin: 2rpx 0; }
.bubble :deep(.mdv .quote) { margin: 0.2em 0; padding: 10rpx 16rpx; }
.bubble :deep(.mdv .tblwrap) { margin: 0.4em 0; }
.bubble :deep(.mdv .kv) { margin: 0.2em 0; padding: 8rpx 14rpx; }
.bubble :deep(.mdv .mdhr) { margin: 0.5em 0; }
.bubble :deep(.mdv .code) { margin: 0.35em 0; padding: 12rpx 18rpx; font-size: 0.8em; }
.bubble :deep(.mdv .b-time) { font-size: 16rpx; margin-top: 6rpx; }
.typing { display: flex; align-items: center; margin-top: 2rpx; }
.t-dot { width: 10rpx; height: 10rpx; border-radius: 50%; background: var(--gold); margin-right: 10rpx; animation: bounce 1.2s infinite; }
.t-dot:nth-child(2) { animation-delay: .2s; }
.t-dot:nth-child(3) { animation-delay: .4s; }
@keyframes bounce { 0%, 60%, 100% { transform: translateY(0); opacity: .5; } 30% { transform: translateY(-10rpx); opacity: 1; } }
.cursor { color: var(--brand); animation: blink 1s infinite; }
@keyframes blink { 50% { opacity: 0; } }





 .b-actions { display: flex; gap: 20rpx; margin-top: 6rpx; padding-left: 4rpx; }
.b-act { font-size: 19rpx; color: var(--ink2); opacity: .7; font-weight: 500; }
.b-refs { margin: 4rpx 0 2rpx; }

.br-chips { display: flex; flex-wrap: wrap; }
.br-chip { font-size: 18rpx; color: var(--brand); background: rgba(154,46,31,.05); border: 1rpx solid rgba(154,46,31,.2); border-radius: 8rpx; padding: 3rpx 12rpx; margin: 0 8rpx 4rpx 0; }


.quicks { flex-shrink: 0; padding: 6rpx 0 10rpx; }
.q-row { display: flex; padding: 0 24rpx; }
.q-chip { flex-shrink: 0; background: var(--card); color: var(--brand); border: 1rpx solid var(--line); border-radius: 30rpx; padding: 12rpx 26rpx; font-size: 23rpx; margin-right: 16rpx; }

.inputbar { flex-shrink: 0; background: var(--card); padding: 16rpx 24rpx 0; border-top: 1rpx solid var(--line); }
.i-pill { display: flex; align-items: center; background: var(--zebra-bg); border-radius: 36rpx; padding: 12rpx 12rpx 12rpx 28rpx; }
.i-text { flex: 1; min-height: 48rpx; max-height: 220rpx; font-size: 27rpx; color: var(--ink); line-height: 48rpx; padding: 0; background: transparent; }
.i-mic { flex-shrink: 0; width: 68rpx; height: 68rpx; border-radius: 50%; background: var(--card); border: 2rpx solid var(--brand); display: flex; align-items: center; justify-content: center; margin-right: 14rpx; box-shadow: 0 2rpx 8rpx rgba(154,46,31,.15); }
.i-mic.on { background: var(--brand); border-color: var(--brand); box-shadow: 0 4rpx 16rpx rgba(154,46,31,.35); animation: pulse2 1.2s infinite; }
.rec-overlay { position: fixed; inset: 0; z-index: 997; background: rgba(20,12,6,.88); display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 0 40rpx; }
.rec-wave { display: flex; align-items: center; gap: 10rpx; height: 80rpx; margin-bottom: 30rpx; }
.rw-bar { width: 8rpx; border-radius: 6rpx; background: #F6E7C9; animation: wave 0.8s ease-in-out infinite alternate; }
.rw-bar:nth-child(1) { height: 30rpx; }
.rw-bar:nth-child(2) { height: 50rpx; }
.rw-bar:nth-child(3) { height: 70rpx; }
.rw-bar:nth-child(4) { height: 50rpx; }
.rw-bar:nth-child(5) { height: 30rpx; }
@keyframes wave { from { transform: scaleY(.4); } to { transform: scaleY(1.3); } }
.rec-text { font-size: 30rpx; color: #FDF8EE; line-height: 1.7; text-align: center; min-height: 90rpx; max-width: 600rpx; }
.rec-stop { margin-top: 40rpx; background: rgba(253,248,238,.15); border: 2rpx solid rgba(253,248,238,.5); color: #FDF8EE; border-radius: 44rpx; padding: 16rpx 60rpx; font-size: 26rpx; font-weight: 700; }
.i-send { flex-shrink: 0; width: 76rpx; height: 76rpx; border-radius: 50%; background: linear-gradient(135deg, #C9C0B2, #B4AA98); display: flex; align-items: center; justify-content: center; margin-left: 20rpx; transition: all .2s; }
.i-send.on { background: linear-gradient(135deg, var(--brand), var(--brand-deep)); box-shadow: 0 6rpx 18rpx rgba(154,46,31,.35); transform: scale(1.04); }
.i-send.dis { opacity: .55; }
</style>
