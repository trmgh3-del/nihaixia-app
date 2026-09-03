#!/usr/bin/env python3
p = 'pkgFormula/pages/list.vue'
s = open(p, encoding='utf-8').read()

# ===== 1) 重构对比弹窗模板：双列卡片 =====
old = '''    <view class="cmp-mask" v-if="cmpView" @tap="cmpView = null">
      <view class="cmp-panel card" @tap.stop>
        <view class="cp-title serif">方剂对比</view>
        <scroll-view scroll-y class="cp-scroll">
          <view class="cp-head">
            <view class="cp-col" v-for="(a, i) in cmpView" :key="i">
              <view class="cp-name serif" :style="{ color: i ? '#2F5D62' : 'var(--brand)' }">{{ a.n }}</view>
              <view class="cp-src">{{ a.src || '经方' }}</view>
            </view>
          </view>
          <view class="cp-row" v-for="f in cmpFields" :key="f.k">
            <view class="cp-lab">{{ f.k }}</view>
            <view class="cp-val" v-for="(a, i) in cmpView" :key="i" :style="{ borderColor: i ? '#2F5D62' : 'var(--brand)' }">{{ a[f.v] || '—' }}</view>
          </view>
          <view class="cp-note">剂量体系：原方为汉朝度量衡（1两≈15.6g）；临床为倪师台湾制（1钱≈3.75g）。仅供学习参考，遵医嘱。</view>
        </scroll-view>
        <view class="cp-close" @tap="cmpView = null">关闭</view>
      </view>
    </view>'''
new = '''    <view class="cmp-mask" v-if="cmpView" @tap="cmpView = null">
      <view class="cmp-panel card" @tap.stop>
        <view class="cp-title serif">⟡ 方剂对比</view>
        <scroll-view scroll-y class="cp-scroll">
          <view class="cp-cols">
            <view class="cp-card" v-for="(a, i) in cmpView" :key="i" :class="{ alt: i === 1 }">
              <view class="cpc-head" :class="{ alt: i === 1 }">
                <view class="cpc-name serif">{{ a.n }}</view>
                <view class="cpc-src">{{ a.src || '经方' }}</view>
              </view>
              <view class="cpc-field" v-for="f in cmpFields" :key="f.k">
                <view class="cpc-lab">{{ f.k }}</view>
                <view class="cpc-val" :class="{ hl: f.v === 'clinical' }">{{ a[f.v] || '—' }}</view>
              </view>
            </view>
          </view>
          <view class="cp-note">剂量体系：原方为汉朝度量衡（1两≈15.6g）；临床为倪师台湾制（1钱≈3.75g）。仅供学习参考，遵医嘱。</view>
        </scroll-view>
        <view class="cp-close" @tap="cmpView = null">关闭</view>
      </view>
    </view>'''
assert old in s, 'cmp tpl'
s = s.replace(old, new)

# ===== 2) 删旧CSS，写新双列卡片样式 =====
import re
for cls in ['.cp-head', '.cp-col', '.cp-name', '.cp-src', '.cp-row', '.cp-lab', '.cp-val']:
    m = re.search(re.escape(cls) + r'\s*\{[^}]+\}', s)
    if m:
        s = s.replace(m.group(0), '')

old = '.cp-scroll { max-height: 60vh; padding: 0 24rpx; }'
new = '''.cp-scroll { max-height: 60vh; padding: 0 20rpx; }
.cp-cols { display: grid; grid-template-columns: 1fr 1fr; gap: 14rpx; }
.cp-card { border-radius: 16rpx; overflow: hidden; border: 2rpx solid var(--brand); min-width: 0; }
.cp-card.alt { border-color: #2F5D62; }
.cpc-head { background: linear-gradient(135deg, rgba(154,46,31,.92), rgba(124,58,33,.92)); padding: 14rpx 12rpx 12rpx; text-align: center; }
.cpc-head.alt { background: linear-gradient(135deg, #2F5D62, #234449); }
.cpc-name { font-size: 25rpx; font-weight: 800; color: #FDF8EE; word-break: break-all; line-height: 1.4; }
.cpc-src { font-size: 16rpx; color: rgba(253,248,238,.75); margin-top: 2rpx; }
.cpc-field { padding: 10rpx 10rpx 8rpx; border-top: 1rpx solid var(--line); min-width: 0; }
.cpc-lab { font-size: 17rpx; color: var(--gold); font-weight: 700; margin-bottom: 2rpx; }
.cpc-val { font-size: 18rpx; color: var(--ink); line-height: 1.55; word-break: break-all; min-height: 34rpx; }
.cpc-val.hl { color: var(--brand); font-weight: 600; }'''
assert old in s, 'cp-scroll css'
s = s.replace(old, new)

open(p, 'w', encoding='utf-8').write(s)
print('双列卡片对比重构 ok')
