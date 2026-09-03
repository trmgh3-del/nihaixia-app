#!/usr/bin/env python3
"""统一所有开穴表时间格式为 23:00~01:00 并确保完整显示"""

# ===== 1) najia.vue =====
p = 'pages/study/najia.vue'
s = open(p, encoding='utf-8').read()

# 纳甲法表：恢复完整格式
old = "time: `${a.padStart(2, '0')}~${b.padStart(2, '0')}`,\n          pt: entry"
assert old in s, 'najia time'
s = s.replace(old, "time: `${a.padStart(2, '0')}:00~${b.padStart(2, '0')}:00`,\n          pt: entry")

# 纳支法表：恢复完整格式
old = "time: `${a.padStart(2, '0')}~${b.padStart(2, '0')}`,\n          mer: merName"
assert old in s, 'buxie time'
s = s.replace(old, "time: `${a.padStart(2, '0')}:00~${b.padStart(2, '0')}:00`,\n          mer: merName")

# 时间列宽度加大 + 字号缩小
old = '.td.time { flex: 1.5; font-size: 17rpx; letter-spacing: -0.5rpx; }'
new = '.td.time { flex: 1.9; font-size: 15rpx; letter-spacing: -0.5rpx; }'
assert old in s, 'time css'
s = s.replace(old, new)

# 其他列缩窄
old = '.td { flex: 1; text-align: center; padding: 12rpx 3rpx; font-size: 18rpx; color: var(--ink); border-top: 1rpx solid var(--line); min-width: 0; word-break: break-all; line-height: 1.5; }'
new = '.td { flex: 0.8; text-align: center; padding: 12rpx 2rpx; font-size: 18rpx; color: var(--ink); border-top: 1rpx solid var(--line); min-width: 0; word-break: break-all; line-height: 1.5; }\n.td.time { flex: 1.9; font-size: 15rpx; letter-spacing: -0.5rpx; white-space: nowrap; }'
s = s.replace(old, new)
# 删除旧的 .td.time（已在上面合并）
s = s.replace('.td.time { flex: 1.9; font-size: 15rpx; letter-spacing: -0.5rpx; }\n.td.time', '.td.time')

open(p, 'w', encoding='utf-8').write(s)
print('1) najia.vue 时间格式修复 ok')

# ===== 2) linggui.vue =====
p = 'pages/study/linggui.vue'
s = open(p, encoding='utf-8').read()

# 恢复完整格式（当前是 23:00~01 缺末尾 :00）
old = "time: `${a.padStart(2, '0')}:00~${b.padStart(2, '0')}`"
assert old in s, 'linggui time'
s = s.replace(old, "time: `${a.padStart(2, '0')}:00~${b.padStart(2, '0')}:00`")

# 时间列加宽
old = '.td { flex: 1; text-align: center; padding: 13rpx 6rpx; font-size: 19rpx; color: var(--ink); border-top: 1rpx solid var(--line); white-space: nowrap; }'
new = '.td { flex: 0.8; text-align: center; padding: 13rpx 3rpx; font-size: 18rpx; color: var(--ink); border-top: 1rpx solid var(--line); white-space: nowrap; }\n.td.time { flex: 1.9; font-size: 15rpx; letter-spacing: -0.5rpx; }'
assert old in s, 'linggui td'
s = s.replace(old, new)

# 表头和数据行时间列加class
old = '<view class="td">时间</view>'
s = s.replace(old, '<view class="td time">时间</view>')
old = '<view class="td">{{ r.time }}</view>'
s = s.replace(old, '<view class="td time">{{ r.time }}</view>')

open(p, 'w', encoding='utf-8').write(s)
print('2) linggui.vue 时间格式修复 ok')

# ===== 3) ziwu.vue 也统一 =====
p = 'pkgZhenjiu/pages/ziwu.vue'
s = open(p, encoding='utf-8').read()
# ziwu 用的是 range 字段直接显示 "23-1时"，改为标准格式
old = "range: '23-1时'"
if old in s:
    s = s.replace("range: '23-1时'", "range: '23:00~01:00'")
    # 其他时辰
    for old_r, new_r in [
        ("range: '1-3时'", "range: '01:00~03:00'"), ("range: '3-5时'", "range: '03:00~05:00'"),
        ("range: '5-7时'", "range: '05:00~07:00'"), ("range: '7-9时'", "range: '07:00~09:00'"),
        ("range: '9-11时'", "range: '09:00~11:00'"), ("range: '11-13时'", "range: '11:00~13:00'"),
        ("range: '13-15时'", "range: '13:00~15:00'"), ("range: '15-17时'", "range: '15:00~17:00'"),
        ("range: '17-19时'", "range: '17:00~19:00'"), ("range: '19-21时'", "range: '19:00~21:00'"),
        ("range: '21-23时'", "range: '21:00~23:00'"),
    ]:
        s = s.replace(old_r, new_r)
    open(p, 'w', encoding='utf-8').write(s)
    print('3) ziwu.vue 时间格式统一 ok')

print('\n=== 全部时间格式统一为 23:00~01:00 ===')
