#!/usr/bin/env python3
p = 'pages/ai/chat.vue'
s = open(p, encoding='utf-8').read()

# ===== 1) 模板：按钮双态图标 + 录音覆盖层 =====
old = '''        <view class="i-mic" :class="{ on: recording }" v-if="micOk" @tap.stop="toggleMic"><image class="ico-s" src="/static/icons/sound-light.png" /></view>'''
new = '''        <view class="i-mic" :class="{ on: recording }" v-if="micOk" @tap.stop="toggleMic">
          <image class="ico-s" :src="recording ? '/static/icons/sound-light.png' : '/static/icons/sound-brand.png'" />
        </view>'''
assert old in s, 'mic tpl'
s = s.replace(old, new)

# 录音覆盖层（插在 inputbar 之前）
old = '''    <view class="inputbar"'''
new = '''    <view class="rec-overlay" v-if="recording" @tap="stopMic">
      <view class="rec-wave">
        <view class="rw-bar" v-for="i in 5" :key="i" :style="{ animationDelay: (i * 0.1) + 's' }" />
      </view>
      <view class="rec-text">{{ interimText || '正在聆听…' }}</view>
      <view class="rec-stop">点击停止录音</view>
    </view>
    <view class="inputbar"'''
assert old in s, 'overlay pos'
s = s.replace(old, new)

# ===== 2) data：interimText =====
old = """      micOk: false,
      recording: false,"""
new = """      micOk: false,
      recording: false,
      interimText: '',"""
assert old in s, 'data'
s = s.replace(old, new)

# ===== 3) toggleMic 重写 =====
old_start = s.find('    toggleMic() {')
old_end = s.find('    stopMic() {')
if old_start < 0 or old_end < 0:
    raise AssertionError('toggleMic range not found')
old_block = s[old_start:old_end + s[old_end:].find('},') + 3]

new_block = '''    toggleMic() {
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
    },'''

s = s.replace(old_block, new_block)

# ===== 4) CSS =====
old = '.i-mic { flex-shrink: 0; width: 64rpx; height: 64rpx; border-radius: 50%; background: var(--zebra-bg); border: 1rpx solid var(--line); display: flex; align-items: center; justify-content: center; margin-right: 16rpx; }'
new = '.i-mic { flex-shrink: 0; width: 68rpx; height: 68rpx; border-radius: 50%; background: var(--card); border: 2rpx solid var(--brand); display: flex; align-items: center; justify-content: center; margin-right: 14rpx; box-shadow: 0 2rpx 8rpx rgba(154,46,31,.15); }'
assert old in s, 'mic css'
s = s.replace(old, new)

old = '.i-mic.on { background: var(--brand); border-color: var(--brand); animation: pulse2 1.2s infinite; }'
new = '.i-mic.on { background: var(--brand); border-color: var(--brand); box-shadow: 0 4rpx 16rpx rgba(154,46,31,.35); animation: pulse2 1.2s infinite; }'
assert old in s, 'mic on'
s = s.replace(old, new)

# 录音覆盖层样式（在 .i-send 前插入）
old = '.i-send {'
new = '''.rec-overlay { position: fixed; inset: 0; z-index: 997; background: rgba(20,12,6,.88); display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 0 40rpx; }
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
.i-send {'''
assert old in s, 'overlay css'
s = s.replace(old, new)

open(p, 'w', encoding='utf-8').write(s)
print('语音输入全面修复 ok')
