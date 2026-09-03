<template>
  <view class="page" :class="theme === 'dark' ? 'tdark' : 'tlight'">
    <view class="sbar">
      <view class="s-box">
        <image class="ico" src="/static/icons/search-gray.png" />
        <input class="s-input" v-model="q" placeholder="搜症状：腰痛 / 失眠 / 鼻血 / 中风…" />
      </view>
    </view>

    <view class="list">
      <view v-for="t in shown" :key="t.k" class="t-item card fade-in">
        <view class="t-head">
          <view class="t-name serif">{{ t.k }}</view>
          <view class="t-src">{{ t.src }}</view>
        </view>
        <view class="t-desc" v-if="t.d">{{ t.d }}</view>
        <view class="t-pts">
          <view class="t-pt" v-for="p in t.pts" :key="p" @tap="findPoint(p)">{{ p }}</view>
        </view>
      </view>
      <view v-if="!shown.length" class="none">无匹配症状，试试「腰痛」「失眠」「中风」</view>
    </view>

    <view class="src card">内容源自倪师人纪针灸「治症精选 / 针灸速查」；点穴位名可跳转穴位库查看定位与主治。</view>
  </view>
</template>

<script>
import { store, applyTheme } from '@/utils/store.js'
import { loadData } from '@/utils/data.js'

/* 症状→穴位处方（源自 modules/09 治症精选 + distilled/02 速查） */
const TREATS = [
  { k: '腰痛', src: '腰背委中求', pts: ['委中', '肾俞', '腰阳关', '腰痛点', '天宗'], d: '刺法：委中放血效佳；久痛加灸肾俞。' },
  { k: '肩膀抬不起', src: '肩三针+手三阳分工', pts: ['肩髃', '肩髎', '肩贞', '肩三针', '条口'], d: '条口透承山为治肩要穴；抬举不利分三阳经取穴。' },
  { k: '中风（半身不遂）', src: '中风大穴', pts: ['百会', '肩髃', '曲池', '外关', '环跳', '风市', '阳陵泉', '风府', '足三里'], d: '先补健侧、再泻患侧；舌强不语加百会；灸足三里防复中。' },
  { k: '头痛（前额）', src: '阳明头痛', pts: ['头维', '合谷', '阳白'], d: '按部位分经取穴：前额阳明、侧头少阳、后头太阳、巅顶厥阴。' },
  { k: '头痛（侧头）', src: '少阳头痛', pts: ['太阳', '率谷', '外关', '风池'] },
  { k: '偏头痛', src: '少阳', pts: ['风池', '率谷', '外关', '足临泣'] },
  { k: '失眠', src: '心安神宁', pts: ['神门', '三阴交', '安眠', '心俞', '印堂'], d: '心肾不交加太溪；胃不和则卧不安加中脘足三里。' },
  { k: '心悸', src: '心包心经', pts: ['内关', '神门', '厥阴俞', '膻中'] },
  { k: '胃痛 / 呕吐', src: '公孙内关胃心胸', pts: ['公孙', '内关', '中脘', '足三里', '梁丘'], d: '公孙配内关为八脉交会经典配穴，主胃心胸之疾。' },
  { k: '便秘', pts: ['天枢', '支沟', '照海', '足三里', '大肠俞'], d: '支沟通便经验穴；热秘加曲池合谷。' },
  { k: '腹泻', src: '温中止泻', pts: ['天枢', '足三里', '中脘', '关元', '脾俞'], d: '寒泻宜灸；五更泄加命门肾俞。' },
  { k: '感冒', src: '风池祛风', pts: ['风池', '合谷', '肺俞', '大椎', '风门'], d: '大椎为诸阳之会，灸之助阳解表。' },
  { k: '咳嗽 / 气喘', src: '肺系', pts: ['肺俞', '中府', '尺泽', '膻中', '定喘', '天突'] },
  { k: '鼻塞 / 鼻窦炎', pts: ['迎香', '印堂', '合谷', '上星', '风池'] },
  { k: '鼻血', src: '井穴止衄', pts: ['合谷', '上星', '少商', '迎香'] },
  { k: '牙痛', src: '面口合谷收', pts: ['合谷', '下关', '颊车', '内庭'], d: '上牙取下关内庭（足阳明）、下牙取合谷颊车。' },
  { k: '耳鸣 / 耳聋', pts: ['听宫', '耳门', '翳风', '中渚', '外关'], d: '暴聋属实取少阳；久聋属虚加肾俞太溪。' },
  { k: '目赤 / 眼疾', src: '肝开窍于目', pts: ['睛明', '太阳', '太冲', '光明', '肝俞'], d: '眼疾多责肝；光明为络穴治目痛。' },
  { k: '口疮 / 口臭', pts: ['劳宫', '地仓', '合谷', '内庭'] },
  { k: '咽喉痛', pts: ['少商', '商阳', '合谷', '天突'], d: '少商点刺出血为急性咽痛要法。' },
  { k: '痛经 / 月经病', src: '妇科三阴交', pts: ['三阴交', '关元', '气海', '地机', '血海'], d: '三阴交为妇科要穴；实痛加地机，虚寒灸关元。' },
  { k: '水肿', src: '水分利水', pts: ['水分', '水道', '阴陵泉', '三阴交', '复溜'] },
  { k: '尿频 / 夜尿', pts: ['关元', '中极', '肾俞', '太溪', '膀胱俞'] },
  { k: '消渴（糖尿病）', src: '倪师消渴专法', pts: ['消渴穴', '阳池', '关元', '天枢', '脾俞'], d: '第八椎下经外奇穴「消渴穴」可针可灸且可诊断（压之不痛即愈）；阳池透大陵。' },
  { k: '荨麻疹 / 皮肤痒', pts: ['曲池', '血海', '膈俞', '三阴交', '风市'], d: '治风先治血：血海膈俞属血分会。' },
  { k: '落枕', pts: ['悬钟', '后溪', '阿是', '天柱'] },
  { k: '晕眩', pts: ['风池', '百会', '内关', '太冲', '丰隆'], d: '痰饮眩晕加丰隆；血虚加三阴交足三里。' },
  { k: '戒烟 / 咳痰', pts: ['戒烟穴', '尺泽', '丰隆'] }
]

export default {
  data() {
    return { q: '', treats: TREATS }
  },
  computed: {
    theme() { return store.theme },
    shown() {
      const q = this.q.trim()
      if (!q) return this.treats
      return this.treats.filter(t => (t.k + (t.d || '') + t.pts.join() + (t.src || '')).includes(q))
    }
  },
  onShow() { applyTheme() },
  methods: {
    findPoint(name) {
      uni.navigateTo({ url: '/pkgZhenjiu/pages/list?pt=' + encodeURIComponent(name) })
    }
  }
}
</script>

<style scoped>
.page { min-height: 100vh; background: var(--bg); padding-bottom: 60rpx; }
.sbar { padding: 22rpx 32rpx; background: var(--card); display: flex; }
.s-box { flex: 1; display: flex; align-items: center; background: var(--zebra-bg); border-radius: 38rpx; padding: 0 28rpx; height: 74rpx; }
.s-box .ico { margin-right: 14rpx; }
.s-input { flex: 1; font-size: 26rpx; color: var(--ink); }
.list { padding: 24rpx 32rpx 0; }
.t-item { padding: 26rpx 30rpx; margin-bottom: 20rpx; }
.t-head { display: flex; align-items: center; }
.t-name { font-size: 31rpx; font-weight: 800; color: var(--ink); }
.t-src { margin-left: auto; font-size: 22rpx; color: var(--gold); }
.t-desc { font-size: 22rpx; color: var(--ink2); line-height: 1.7; margin-top: 10rpx; }
.t-pts { display: flex; flex-wrap: wrap; margin-top: 16rpx; }
.t-pt { font-size: 23rpx; color: var(--brand); background: rgba(154,46,31,.06); border: 1rpx solid rgba(154,46,31,.25); border-radius: 12rpx; padding: 8rpx 22rpx; margin: 0 14rpx 12rpx 0; }
.src { margin: 26rpx 32rpx 0; padding: 20rpx 26rpx; font-size: 20rpx; color: var(--ink2); line-height: 1.7; }
</style>
