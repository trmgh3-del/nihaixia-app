#!/usr/bin/env python3
p = 'pages/study/najia.vue'
s = open(p, encoding='utf-8').read()

# ===== 1) 在"全日补泻速查表"前插入纳甲法开穴表 =====
old = '''    <!-- 全日十二时辰补泻表 -->'''
new = '''    <!-- 纳甲法全日开穴表 -->
    <view class="sec">
      <view class="sec-head"><text class="sec-orn">❖</text><text class="sec-title serif">纳甲法全日开穴 · {{ dayGan }}日（{{ dayMeridian }}）</text></view>
      <view class="tbl card">
        <view class="tr th">
          <view class="td">时辰</view>
          <view class="td">时间</view>
          <view class="td">开穴</view>
          <view class="td">五输</view>
          <view class="td">状态</view>
        </view>
        <view class="tr" v-for="r in najiaTable" :key="r.hour" :class="{ now: r.isNow }">
          <view class="td serif">{{ r.hour }}</view>
          <view class="td">{{ r.time }}</view>
          <view class="td hl serif">{{ r.pt }}</view>
          <view class="td">{{ r.shu }}</view>
          <view class="td">
            <text v-if="r.open" class="st-open">开</text>
            <text v-else class="st-close">阖</text>
          </view>
        </view>
      </view>
    </view>

    <!-- 纳支法全日补泻表 -->'''
assert old in s, '补泻表位置'
s = s.replace(old, new)

# ===== 2) 修改补泻表标题使其更明确 =====
old = '<text class="sec-title serif">全日补泻速查表</text>'
new = '<text class="sec-title serif">纳支法全日补泻 · 母穴/子穴</text>'
assert old in s
s = s.replace(old, new)

# ===== 3) data 加 najiaTable =====
old = "liveClock: '', fullDay: []"
new = "liveClock: '', fullDay: [], najiaTable: []"
assert old in s
s = s.replace(old, new)

# ===== 4) buildNajiaTable 方法 =====
old = '''    buildFullDay() {'''
new = '''    buildNajiaTable() {
      const table = NAJIA[this.dayGanIdx] || {}
      const rows = []
      for (let i = 0; i < 12; i++) {
        const h = HOURS[i]
        const [a, b] = h.range.split('-')
        const entry = table[i]
        rows.push({
          hour: h.h,
          time: `${a.padStart(2, '0')}:00~${b.padStart(2, '0')}`,
          pt: entry ? entry.p : '—',
          shu: entry ? entry.s : '—',
          open: !!entry,
          isNow: i === this.hourIdx
        })
      }
      this.najiaTable = rows
    },
    buildFullDay() {'''
assert old in s, 'buildFullDay'
s = s.replace(old, new)

# ===== 5) tick 中调用 =====
old = '''      this.buildFullDay()'''
new = '''      this.buildNajiaTable()
      this.buildFullDay()'''
assert old in s, 'tick call'
s = s.replace(old, new)

# ===== 6) CSS：开/阖状态标记 =====
old = '.tr.now .td:first-child::before { content: \'▶\'; color: var(--brand); font-size: 13rpx; margin-right: 3rpx; }'
new = '''.tr.now .td:first-child::before { content: '▶'; color: var(--brand); font-size: 13rpx; margin-right: 3rpx; }
.st-open { color: #3F6B37; font-weight: 700; font-size: 18rpx; background: #E8F0E4; border-radius: 6rpx; padding: 2rpx 10rpx; }
.st-close { color: #A2651B; font-size: 18rpx; background: #FCF3DC; border-radius: 6rpx; padding: 2rpx 10rpx; }'''
assert old in s, 'css'
s = s.replace(old, new)

open(p, 'w', encoding='utf-8').write(s)
print('纳甲法全日开穴表恢复 ok')
