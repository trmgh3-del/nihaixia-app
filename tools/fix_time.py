#!/usr/bin/env python3
p = 'pages/study/najia.vue'
s = open(p, encoding='utf-8').read()

# ===== 1) 去掉nowrap，允许换行 =====
old = '.td { flex: 1; text-align: center; padding: 13rpx 4rpx; font-size: 19rpx; color: var(--ink); border-top: 1rpx solid var(--line); white-space: nowrap; }'
new = '.td { flex: 1; text-align: center; padding: 12rpx 3rpx; font-size: 18rpx; color: var(--ink); border-top: 1rpx solid var(--line); min-width: 0; word-break: break-all; line-height: 1.5; }'
assert old in s, 'td base'
s = s.replace(old, new)

# ===== 2) 时间列更宽（第2列） =====
old = '.th .td { color: #FDF8EE; font-weight: 700; font-size: 20rpx; }'
new = '''.th .td { color: #FDF8EE; font-weight: 700; font-size: 19rpx; }
.td.time { flex: 1.5; font-size: 17rpx; letter-spacing: -0.5rpx; }'''
assert old in s, 'th td'
s = s.replace(old, new)

# ===== 3) 纳甲法表：时间列加class =====
# 纳甲法表头
old = '<view class="td">时间</view>\n          <view class="td">开穴</view>'
assert old in s, 'najia th'
s = s.replace(old, '<view class="td time">时间</view>\n          <view class="td">开穴</view>')

# 纳甲法数据行
old = '<view class="td">{{ r.time }}</view>\n          <view class="td hl serif">{{ r.pt }}</view>'
assert old in s, 'najia row'
s = s.replace(old, '<view class="td time">{{ r.time }}</view>\n          <view class="td hl serif">{{ r.pt }}</view>')

# ===== 4) 纳支法表：时间列加class =====
old = '<view class="td">{{ row.time }}</view>\n          <view class="td">{{ row.mer }}</view>'
assert old in s, 'buxie row'
s = s.replace(old, '<view class="td time">{{ row.time }}</view>\n          <view class="td">{{ row.mer }}</view>')

# 纳支法表头
old = '<view class="td">时间</view>\n          <view class="td">当令经</view>'
assert old in s, 'buxie th'
s = s.replace(old, '<view class="td time">时间</view>\n          <view class="td">当令经</view>')

# ===== 5) 时间格式简化：去掉秒位冒号后的00，改为短格式 =====
old = """        rows.push({
          hour: h.h,
          time: `${a.padStart(2, '0')}:00~${b.padStart(2, '0')}`,
          pt: entry ? entry.p : '—',
          shu: entry ? entry.s : '—',
          open: !!entry,
          isNow: i === this.hourIdx
        })"""
new = """        rows.push({
          hour: h.h,
          time: `${a.padStart(2, '0')}~${b.padStart(2, '0')}`,
          pt: entry ? entry.p : '—',
          shu: entry ? entry.s : '—',
          open: !!entry,
          isNow: i === this.hourIdx
        })"""
assert old in s, 'najia time fmt'
s = s.replace(old, new)

# 纳支法时间也简化
old = """        rows.push({
          hour: h.h,
          time: `${a.padStart(2, '0')}:00~${b.padStart(2, '0')}`,
          mer: merName,
          mu: bx.mu,
          zi: bx.zi,
          isNow: i === this.hourIdx
        })"""
new = """        rows.push({
          hour: h.h,
          time: `${a.padStart(2, '0')}~${b.padStart(2, '0')}`,
          mer: merName,
          mu: bx.mu,
          zi: bx.zi,
          isNow: i === this.hourIdx
        })"""
assert old in s, 'buxie time fmt'
s = s.replace(old, new)

# ===== 6) 顶部时间范围也简化 =====
old = "return `${a.padStart(2, '0')}:00~${b.padStart(2, '0')}:00`"
new = "return `${a.padStart(2, '0')}:00 ~ ${b.padStart(2, '0')}:00`"
if old in s:
    s = s.replace(old, new)

open(p, 'w', encoding='utf-8').write(s)
print('时间列显示修复 ok')
