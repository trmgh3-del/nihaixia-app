<template>
  <view class="page" :class="theme === 'dark' ? 'tdark' : 'tlight'">
    <view class="wrap">
      <view class="hero">
        <view class="hero-t serif">接口配置</view>
        <view class="hero-s">OpenAI 兼容 · DeepSeek / Kimi / 通义 / OpenAI / Ollama</view>
      </view>

      <view class="form card fade-in">
        <view class="f-block">
          <view class="f-label">API 地址 <text class="f-tip">自动拼接 /chat/completions</text></view>
          <view class="f-input">
            <input v-model="cfg.baseUrl" placeholder="https://api.deepseek.com" placeholder-class="ph" />
          </view>
        </view>
        <view class="f-block">
          <view class="f-label">API Key <text class="f-tip">仅保存在本机</text></view>
          <view class="f-input">
            <input v-model="cfg.apiKey" password placeholder="sk-..." placeholder-class="ph" />
          </view>
        </view>
        <view class="f-block">
          <view class="f-label">模型</view>
          <view class="f-input">
            <input v-model="cfg.model" placeholder="deepseek-chat" placeholder-class="ph" />
          </view>
          <view class="f-quick">
            <view class="fq-chip" v-for="m in models" :key="m.m" @tap="cfg.baseUrl = m.u; cfg.model = m.m">{{ m.label }}</view>
          </view>
        </view>

        <view class="f-block">
          <view class="f-label">思维内核</view>
          <view class="modes">
            <view class="mode" :class="{ on: cfg.mode === 'lite' }" @tap="cfg.mode = 'lite'">
              <view class="m-t">精简内核</view>
              <view class="m-d">内置蒸馏版倪师思维，任何模型可用</view>
            </view>
            <view class="mode" :class="{ on: cfg.mode === 'rag' }" @tap="cfg.mode = 'rag'">
              <view class="m-t">检索增强</view>
              <view class="m-d">自动检索本地知识库原文作答</view>
            </view>
            <view class="mode" :class="{ on: cfg.mode === 'full' }" @tap="cfg.mode = 'full'">
              <view class="m-t">完整 SKILL</view>
              <view class="m-d">132KB 全量内核（需长上下文模型）</view>
            </view>
          </view>
        </view>

        <view class="f-block row">
          <view class="f-label">流式输出</view>
          <switch :checked="cfg.stream" color="#9A2E1F" @change="cfg.stream = $event.detail.value" style="transform:scale(.8)" />
        </view>
        <view class="f-block">
          <view class="f-label">温度 <text class="f-temp">{{ Number(cfg.temperature).toFixed(1) }}</text></view>
          <slider :value="cfg.temperature" :min="0" :max="1.4" :step="0.1" activeColor="#9A2E1F" block-size="20" @change="cfg.temperature = $event.detail.value" />
        </view>

        <view class="row2">
          <view class="test" @tap="testConn">{{ testing ? '测试中…' : '⚡ 测试连接' }}</view>
          <view class="save2" @tap="save">保存配置</view>
        </view>
        <view class="t-result" v-if="testResult" :class="testResult.ok ? 'ok' : 'fail'">{{ testResult.msg }}</view>
        <view class="note">H5 端调用第三方接口需对方允许跨域（CORS）；App 端无此限制。回答仅供学习参考，用药请遵医嘱。</view>
      </view>
    </view>
  </view>
</template>

<script>
import { store, saveAI } from '@/utils/store.js'

export default {
  data() {
    return {
      cfg: { ...store.ai },
      testing: false,
      testResult: null,
      models: [
        { label: 'DeepSeek', u: 'https://api.deepseek.com', m: 'deepseek-chat' },
        { label: 'Kimi', u: 'https://api.moonshot.cn/v1', m: 'moonshot-v1-8k' },
        { label: '通义', u: 'https://dashscope.aliyuncs.com/compatible-mode/v1', m: 'qwen-plus' },
        { label: 'Ollama', u: 'http://127.0.0.1:11434/v1', m: 'qwen2.5:7b' }
      ]
    }
  },
  computed: {
    theme() { return store.theme }
  },
  methods: {
    testConn() {
      if (this.testing) return
      if (!this.cfg.apiKey) { this.testResult = { ok: false, msg: '请先填写 API Key' }; return }
      this.testing = true
      this.testResult = null
      const t0 = Date.now()
      uni.request({
        url: this.cfg.baseUrl.replace(/\/+$/, '') + '/chat/completions',
        method: 'POST',
        timeout: 30000,
        header: { 'Content-Type': 'application/json', Authorization: 'Bearer ' + this.cfg.apiKey },
        data: { model: this.cfg.model, messages: [{ role: 'user', content: '你好' }], max_tokens: 8, stream: false },
        success: res => {
          const ms = Date.now() - t0
          if (res.statusCode >= 200 && res.statusCode < 300) {
            this.testResult = { ok: true, msg: '✓ 连接成功（' + ms + 'ms，模型 ' + this.cfg.model + '）' }
          } else {
            const em = res.data && res.data.error && res.data.error.message
            this.testResult = { ok: false, msg: '✗ HTTP ' + res.statusCode + (em ? '：' + em : '') }
          }
        },
        fail: err => {
          this.testResult = { ok: false, msg: '✗ ' + (err && err.errMsg === 'request:fail' ? '网络不通或跨域被拦（H5需接口允许CORS）' : (err && err.errMsg) || '请求失败') }
        },
        complete: () => { this.testing = false }
      })
    },
    save() {
      saveAI(this.cfg)
      uni.showToast({ title: '已保存', icon: 'success' })
      setTimeout(() => uni.navigateBack({ fail: () => uni.switchTab({ url: '/pages/ai/chat' }) }), 450)
    }
  }
}
</script>

<style scoped>
.page { min-height: 100vh; background: var(--bg); padding-bottom: 80rpx; }
.wrap { padding: 0 32rpx; }
.hero { padding: 36rpx 8rpx 30rpx; }
.hero-t { font-size: 46rpx; font-weight: 800; color: var(--brand); letter-spacing: 3rpx; }
.hero-s { font-size: 22rpx; color: var(--ink2); margin-top: 12rpx; }
.form { padding: 14rpx 30rpx 30rpx; }
.f-block { padding: 24rpx 0; border-bottom: 1rpx solid var(--line); }
.f-block.row { display: flex; align-items: center; justify-content: space-between; }
.f-block:last-of-type { border-bottom: none; }
.f-label { font-size: 27rpx; font-weight: 700; color: var(--ink); margin-bottom: 16rpx; }
.f-block.row .f-label { margin-bottom: 0; }
.f-tip { font-size: 19rpx; color: var(--ink2); font-weight: 400; margin-left: 12rpx; }
.f-input { background: var(--zebra-bg); border-radius: 14rpx; height: 80rpx; display: flex; align-items: center; padding: 0 24rpx; }
.f-input input { width: 100%; font-size: 26rpx; color: var(--ink); height: 80rpx; line-height: 80rpx; }
.ph { color: var(--ink2); }
.f-quick { display: flex; flex-wrap: wrap; margin-top: 16rpx; }
.fq-chip { font-size: 21rpx; color: var(--brand); background: var(--zebra-bg); border: 1rpx solid var(--line); border-radius: 26rpx; padding: 8rpx 24rpx; margin: 0 14rpx 10rpx 0; }
.modes { display: flex; gap: 14rpx; }
.mode { flex: 1; border: 2rpx solid var(--line); border-radius: 16rpx; padding: 20rpx 16rpx; }
.mode.on { border-color: var(--brand); background: rgba(154,46,31,.05); }
.m-t { font-size: 24rpx; font-weight: 800; color: var(--ink); }
.mode.on .m-t { color: var(--brand); }
.m-d { font-size: 18rpx; color: var(--ink2); margin-top: 8rpx; line-height: 1.5; }
.f-temp { color: var(--brand); margin-left: 10rpx; }
.row2 { display: flex; gap: 16rpx; margin-top: 30rpx; }
.test { flex: 1; text-align: center; border-radius: 44rpx; padding: 24rpx 0; font-size: 27rpx; font-weight: 700; border: 2rpx solid var(--gold); color: var(--gold); }
.save2 { flex: 1.2; text-align: center; border-radius: 44rpx; padding: 24rpx 0; font-size: 28rpx; font-weight: 700; letter-spacing: 2rpx; background: linear-gradient(135deg, var(--brand), var(--brand-deep)); color: #FDF8EE; }
.t-result { margin-top: 20rpx; font-size: 22rpx; border-radius: 12rpx; padding: 14rpx 20rpx; line-height: 1.7; }
.t-result.ok { color: #3F6B37; background: #E8F0E4; }
.t-result.fail { color: #833B3B; background: #F5E8E8; }
.save { margin-top: 30rpx; background: linear-gradient(135deg, var(--brand), var(--brand-deep)); color: #FDF8EE; text-align: center; border-radius: 44rpx; padding: 24rpx 0; font-size: 28rpx; font-weight: 700; letter-spacing: 2rpx; display: none; }
.note { font-size: 20rpx; color: var(--ink2); line-height: 1.7; margin-top: 22rpx; opacity: .85; }
</style>
