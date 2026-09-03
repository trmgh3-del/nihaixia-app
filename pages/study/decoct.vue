<template>
  <view class="page" :class="theme === 'dark' ? 'tdark' : 'tlight'">
    <view class="hero">
      <view class="h-t serif">煎药指南</view>
      <view class="h-s">先煎 · 后下 · 烊化 · 冲服 —— 依倪师讲义煎服法整理 + 通用煎药常识</view>
    </view>

    <view class="sec" v-for="g in groups" :key="g.k">
      <view class="sec-head"><text class="sec-orn">❖</text><text class="sec-title serif">{{ g.k }}</text><text class="sec-n">{{ g.items.length }}项</text></view>
      <view class="grp card">
        <view class="g-li" v-for="it in g.items" :key="it[0]">
          <text class="g-main">{{ it[0] }}</text>
          <text class="g-sub">{{ it[1] }}</text>
        </view>
      </view>
    </view>

    <view class="fire card">
      <view class="f-t serif">◈ 火候与用水（通用常识）</view>
      <view class="f-li">解表剂（桂枝汤/麻黄汤类）：武火急煎，沸后10-15分钟，不可久煎——气香为度</view>
      <view class="f-li">补益剂（理中/建中/炙甘草汤类）：文火久煎，40-60分钟，使药力尽出</view>
      <view class="f-li">用水：古法以泉水/井水为佳；今用纯净水，一次加足，忌反复添水</view>
      <view class="f-li">倪师常用服法：六碗煮两碗、三餐饭前温服（感冒药每三小时一服）</view>
    </view>
    <view class="warn">⚠ 煎服法以医师处方医嘱为准；生附子等峻药务必先煎久煎并遵医嘱。</view>
  </view>
</template>

<script>
import { store, applyTheme } from '@/utils/store.js'

export default {
  data() {
    return {
      groups: [
        { k: '先煎', items: [
          ['生附子 / 炮附子', '棉布包先煎（倪师：回阳救逆之生附子必布包先煎，去毒）'],
          ['石膏', '打碎先煎（大青龙/白虎类；鸡子大一枚≈40克）'],
          ['龙骨 / 牡蛎 / 鳖甲', '质重难出，先煎 20-30 分钟'],
          ['葛根', '先煎去沫（葛根汤法：先煮葛根减其悍气）']
        ] },
        { k: '后下', items: [
          ['大黄', '汤成前 5 分钟入（柴胡加龙骨牡蛎汤：八碗煮四碗再入大黄煮两碗）'],
          ['薄荷 / 藿香', '气味芳香，最后 3-5 分钟下'],
          ['芒硝', '药汁冲化服（承气类：去渣后纳芒硝微沸）'],
          ['阿胶 / 鸡子黄', '烊化/药汁稍凉后搅入（黄连阿胶汤：小冷后纳胶、鸡子黄搅令相得）']
        ] },
        { k: '冲服', items: [
          ['肉桂粉', '桂枝加桂汤：汤成冲五分肉桂粉（倪师口述）'],
          ['乌梅丸 / 蜜丸', '丸剂温水送服——药缓力专，汤剂无效（乌梅丸铁律）'],
          ['竹茹汁 / 竹沥', '鲜汁冲服'],
          ['朴硝', '药汁冲化']
        ] },
        { k: '布包煎', items: [
          ['生半夏', '配生姜同煎解喉哑（去水化痰）'],
          ['车前子 /旋覆花', '细小有毛，包煎免呛喉'],
          ['灶心土 / 伏龙肝', '布包先煎取汤代水']
        ] }
      ]
    }
  },
  computed: { theme() { return store.theme } },
  onShow() { applyTheme() }
}
</script>

<style scoped>
.page { min-height: 100vh; background: var(--bg); padding-bottom: 70rpx; }
.hero { background: linear-gradient(140deg, #2F5D62, #234449); padding: 40rpx 36rpx 46rpx; }
.h-t { font-size: 38rpx; font-weight: 800; color: #FDF8EE; letter-spacing: 3rpx; }
.h-s { font-size: 21rpx; color: rgba(253,248,238,.85); margin-top: 12rpx; }
.sec { margin: 26rpx 32rpx 0; }
.sec-head { display: flex; align-items: center; margin-bottom: 16rpx; }
.sec-orn { color: var(--gold); font-size: 22rpx; margin-right: 10rpx; }
.sec-title { font-size: 30rpx; font-weight: 800; color: var(--ink); }
.sec-n { margin-left: auto; font-size: 20rpx; color: var(--ink2); }
.grp { padding: 8rpx 28rpx; }
.g-li { display: flex; padding: 18rpx 0; border-bottom: 1rpx dashed var(--line); font-size: 23rpx; }
.g-li:last-child { border-bottom: none; }
.g-main { width: 210rpx; flex-shrink: 0; font-weight: 700; color: var(--brand); }
.g-sub { flex: 1; color: var(--ink); line-height: 1.7; }
.fire { margin: 26rpx 32rpx 0; padding: 24rpx 30rpx; }
.f-t { font-size: 26rpx; font-weight: 800; color: var(--ink); margin-bottom: 14rpx; }
.f-li { font-size: 22rpx; color: var(--ink2); line-height: 2; }
.warn { margin: 26rpx 32rpx 0; font-size: 20rpx; color: #A2651B; background: #FCF3DC; border-radius: 12rpx; padding: 16rpx 22rpx; line-height: 1.7; }
</style>
