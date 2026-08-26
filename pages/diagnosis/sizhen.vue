<template>
  <view class="page" :class="theme === 'dark' ? 'tdark' : 'tlight'">
    <!-- 进度指示 -->
    <view class="steps">
      <view class="step" v-for="(s, i) in stepNames" :key="i" :class="{ on: step === i, done: step > i }" @tap="jumpStep(i)">
        <view class="sp-num serif">{{ i + 1 }}</view>
        <view class="sp-t">{{ s }}</view>
      </view>
    </view>

    <!-- ===== 1 望诊 ===== -->
    <view v-if="step === 0" class="tab-body fade-in">
      <view class="grp card">
        <view class="g-t serif">⟡ 望色（面色）</view>
        <view class="opts">
          <view class="opt" v-for="o in wangSe" :key="o.k" :class="{ on: pick['望色'] === o.k }" @tap="setPick('望色', o.k)">
            <text class="opt-dot" :style="{ background: o.color }" />
            <text>{{ o.k }}</text>
          </view>
        </view>
        <view class="opt-note" v-if="pick['望色']">{{ wangSe.find(x => x.k === pick['望色']).note }}</view>
      </view>
      <view class="grp card">
        <view class="g-t serif">⟡ 望舌（舌质舌苔）</view>
        <view class="opts">
          <view class="opt sm" v-for="o in wangShe" :key="o.k" :class="{ on: pick['舌质'] === o.k }" @tap="setPick('舌质', o.k)">{{ o.k }}</view>
        </view>
        <view class="sub-lab">舌苔</view>
        <view class="opts">
          <view class="opt sm" v-for="o in wangTai" :key="o.k" :class="{ on: pick['舌苔'] === o.k }" @tap="setPick('舌苔', o.k)">{{ o.k }}</view>
        </view>
        <view class="opt-note" v-if="pick['舌质'] || pick['舌苔']">
          {{ (wangShe.find(x => x.k === pick['舌质']) || {}).note || '' }}
          {{ (wangTai.find(x => x.k === pick['舌苔']) || {}).note || '' }}
        </view>
      </view>
      <view class="grp card">
        <view class="g-t serif">⟡ 望神</view>
        <view class="opts">
          <view class="opt" v-for="o in wangShen" :key="o.k" :class="{ on: pick['望神'] === o.k }" @tap="setPick('望神', o.k)">{{ o.k }}</view>
        </view>
        <view class="opt-note" v-if="pick['望神']">{{ wangShen.find(x => x.k === pick['望神']).note }}</view>
      </view>
      <view class="next-btn" @tap="step = 1">下一步 · 闻诊 ›</view>
    </view>

    <!-- ===== 2 闻诊 ===== -->
    <view v-if="step === 1" class="tab-body fade-in">
      <view class="grp card">
        <view class="g-t serif">⟡ 听声音</view>
        <view class="opts">
          <view class="opt" v-for="o in wenVoice" :key="o.k" :class="{ on: pick['声音'] === o.k }" @tap="setPick('声音', o.k)">{{ o.k }}</view>
        </view>
        <view class="opt-note" v-if="pick['声音']">{{ wenVoice.find(x => x.k === pick['声音']).note }}</view>
      </view>
      <view class="grp card">
        <view class="g-t serif">⟡ 呼吸</view>
        <view class="opts">
          <view class="opt" v-for="o in wenBreath" :key="o.k" :class="{ on: pick['呼吸'] === o.k }" @tap="setPick('呼吸', o.k)">{{ o.k }}</view>
        </view>
        <view class="opt-note" v-if="pick['呼吸']">{{ wenBreath.find(x => x.k === pick['呼吸']).note }}</view>
      </view>
      <view class="nav-row">
        <view class="nav-btn" @tap="step = 0">‹ 上一步</view>
        <view class="nav-btn main" @tap="step = 2">下一步 · 问诊 ›</view>
      </view>
    </view>

    <!-- ===== 3 问诊（倪师十问） ===== -->
    <view v-if="step === 2" class="tab-body fade-in">
      <view class="ten-tip card">倪师诊病十问——按倪海厦人纪教学法：每一问都直指阴阳表里寒热虚实</view>
      <view class="grp card" v-for="q in tenQ" :key="q.k">
        <view class="g-t serif">{{ q.k }}</view>
        <view class="opts">
          <view class="opt sm" v-for="o in q.opts" :key="o" :class="{ on: pick[q.k] === o }" @tap="setPick(q.k, o)">{{ o }}</view>
        </view>
      </view>
      <view class="nav-row">
        <view class="nav-btn" @tap="step = 1">‹ 上一步</view>
        <view class="nav-btn main" @tap="step = 3">下一步 · 切诊 ›</view>
      </view>
    </view>

    <!-- ===== 4 切诊 ===== -->
    <view v-if="step === 3" class="tab-body fade-in">
      <view class="grp card">
        <view class="g-t serif">⟡ 脉位</view>
        <view class="opts">
          <view class="opt" v-for="o in qieWei" :key="o.k" :class="{ on: pick['脉位'] === o.k }" @tap="setPick('脉位', o.k)">{{ o.k }}</view>
        </view>
      </view>
      <view class="grp card">
        <view class="g-t serif">⟡ 脉率</view>
        <view class="opts">
          <view class="opt" v-for="o in qieShuai" :key="o.k" :class="{ on: pick['脉率'] === o.k }" @tap="setPick('脉率', o.k)">{{ o.k }}</view>
        </view>
      </view>
      <view class="grp card">
        <view class="g-t serif">⟡ 脉形</view>
        <view class="opts">
          <view class="opt sm" v-for="o in qieXing" :key="o.k" :class="{ on: pick['脉形'] === o.k }" @tap="setPick('脉形', o.k)">{{ o.k }}</view>
        </view>
      </view>
      <view class="grp card">
        <view class="g-t serif">⟡ 脉力</view>
        <view class="opts">
          <view class="opt" v-for="o in qieLi" :key="o.k" :class="{ on: pick['脉力'] === o.k }" @tap="setPick('脉力', o.k)">{{ o.k }}</view>
        </view>
      </view>
      <view class="nav-row">
        <view class="nav-btn" @tap="step = 2">‹ 上一步</view>
        <view class="nav-btn main" @tap="analyze">⟡ 生成辨证报告</view>
      </view>
    </view>

    <!-- ===== 辨证报告 ===== -->
    <view v-if="step === 4" class="tab-body fade-in">
      <view class="report card">
        <view class="r-t serif">⟡ 四诊合参 · 辨证报告</view>
        <view class="r-sec">
          <view class="rs-t">八纲判定</view>
          <view class="r-tags">
            <view class="r-tag" v-for="b in result.bagang" :key="b" :class="b.includes('阳') || b.includes('表') || b.includes('热') || b.includes('实') ? 'yang' : 'yin'">{{ b }}</view>
          </view>
        </view>
        <view class="r-sec" v-if="result.meridians.length">
          <view class="rs-t">六经倾向</view>
          <view class="r-tags">
            <view class="r-tag mer" v-for="m in result.meridians" :key="m">{{ m }}</view>
          </view>
        </view>
        <view class="r-sec" v-if="result.patterns.length">
          <view class="rs-t">病机分析</view>
          <view class="r-line" v-for="p in result.patterns" :key="p">● {{ p }}</view>
        </view>
        <view class="r-sec" v-if="result.formulas.length">
          <view class="rs-t">参考方剂方向</view>
          <view class="r-fang serif" v-for="f in result.formulas" :key="f">「{{ f }}」</view>
        </view>
        <view class="r-warn">⚠ 四诊合参仅供学习参考，非诊断结论。临床请由执业医师面诊；急重症立即就医。</view>
      </view>
      <view class="nav-row">
        <view class="nav-btn" @tap="reset">↺ 重新采集</view>
      </view>
    </view>
  </view>
</template>

<script>
import { store, applyTheme } from '@/utils/store.js'

/* ===== 望诊数据 ===== */
const WANG_SE = [
  { k: '面色青', color: '#5B8C5A', note: '青主肝、主寒、主痛、主瘀' },
  { k: '面色赤', color: '#C0392B', note: '赤主热（实热满面通红/虚热颧红娇嫩）' },
  { k: '面色黄', color: '#D4A017', note: '黄主脾虚、主湿（萎黄=气血虚/黄胖=湿虚）' },
  { k: '面色白', color: '#E8E8E8', note: '白主虚、主寒、主失血（㿠白=阳虚）' },
  { k: '面色黑', color: '#2C3E50', note: '黑主肾虚、主水饮、主瘀血（黑而暗淡=肾阳虚）' }
]
const WANG_SHE = [
  { k: '淡白', note: '气血两虚或阳虚' }, { k: '红', note: '热证（尖红=心火/全红=实热）' },
  { k: '绛', note: '热入营血' }, { k: '紫暗', note: '瘀血或寒凝' }, { k: '胖大有齿痕', note: '脾虚湿盛' }, { k: '瘦薄', note: '阴虚或气血不足' }
]
const WANG_TAI = [
  { k: '薄白', note: '正常或表证初起' }, { k: '白腻', note: '寒湿或痰饮' }, { k: '黄', note: '里热证' },
  { k: '黄腻', note: '湿热' }, { k: '燥裂', note: '热盛伤津' }, { k: '剥落', note: '胃气不足/胃阴伤' }, { k: '黑', note: '热极或寒极（危重）' }
]
const WANG_SHEN = [
  { k: '得神', note: '神志清楚、目光明亮、面色荣润——预后良好' },
  { k: '失神', note: '精神萎靡、目光呆滞、面色晦暗——预后不良' },
  { k: '假神', note: '久病突然精神好转、颧红如妆——回光返照（危候）' }
]

/* ===== 闻诊数据 ===== */
const WEN_VOICE = [
  { k: '语声高亢', note: '实证、热证' }, { k: '语声低微', note: '虚证、寒证' },
  { k: '少气懒言', note: '气虚' }, { k: '谵语', note: '热扰心神（实证）' },
  { k: '郑声', note: '心气大伤（虚证）' }, { k: '呼吸气粗', note: '实证' }, { k: '呼吸微弱', note: '虚证、元气不足' }
]
const WEN_BREATH = [
  { k: '喘', note: '实喘声高息涌/虚喘声低息短' }, { k: '哮', note: '呼吸急促伴喉中痰鸣' },
  { k: '短气', note: '气不足用（虚）' }, { k: '太息', note: '肝气郁结' }
]

/* ===== 问诊（倪师十问） ===== */
const TEN_Q = [
  { k: '汗', opts: ['无汗', '有汗自汗', '盗汗', '大汗不止', '头汗'] },
  { k: '头身', opts: ['无明显不适', '头痛项强', '身痛骨节痛', '身重困倦', '头晕目眩'] },
  { k: '大便', opts: ['正常', '便秘', '溏泄', '下利清谷', '黏滞不爽'] },
  { k: '小便', opts: ['正常', '短赤', '清长', '不利/癃闭', '频数'] },
  { k: '口渴', opts: ['不渴', '渴喜冷饮', '渴喜热饮', '渴不欲饮', '消渴多饮'] },
  { k: '睡眠', opts: ['正常', '入睡难', '易醒', '彻夜不眠', '但欲寐'] },
  { k: '手足温度', opts: ['手脚温热', '脚凉手温', '手脚冰凉', '手心热脚凉'] },
  { k: '胃口', opts: ['正常', '亢进', '差/食少', '毫无胃口', '食入即吐'] },
  { k: '疼痛', opts: ['无', '胀痛', '刺痛', '隐痛', '冷痛', '灼痛'] },
  { k: '寒热', opts: ['恶寒', '恶风', '发热', '往来寒热', '但热不寒', '无寒热'] }
]

/* ===== 切诊数据 ===== */
const QIE_WEI = [
  { k: '浮', bagang: '表' }, { k: '沉', bagang: '里' }
]
const QIE_SHUAI = [
  { k: '迟', bagang: '寒' }, { k: '数', bagang: '热' }, { k: '平' }
]
const QIE_XING = [
  { k: '弦', bagang: '肝胆病' }, { k: '滑', bagang: '痰饮/实热' }, { k: '细', bagang: '气血虚' },
  { k: '洪', bagang: '热盛' }, { k: '紧', bagang: '寒/痛' }, { k: '濡', bagang: '湿' },
  { k: '涩', bagang: '瘀血/精伤' }, { k: '结代', bagang: '脏气衰微' }
]
const QIE_LI = [
  { k: '有力', bagang: '实证' }, { k: '无力', bagang: '虚证' }, { k: '微', bagang: '阳虚' }
]

export default {
  data() {
    return {
      step: 0,
      stepNames: ['望诊', '闻诊', '问诊', '切诊', '报告'],
      pick: {},
      result: { bagang: [], meridians: [], patterns: [], formulas: [] },
      wangSe: WANG_SE, wangShe: WANG_SHE, wangTai: WANG_TAI, wangShen: WANG_SHEN,
      wenVoice: WEN_VOICE, wenBreath: WEN_BREATH,
      tenQ: TEN_Q,
      qieWei: QIE_WEI, qieShuai: QIE_SHUAI, qieXing: QIE_XING, qieLi: QIE_LI
    }
  },
  computed: { theme() { return store.theme } },
  onShow() { applyTheme() },
  methods: {
    setPick(k, v) { this.pick[k] = this.pick[k] === v ? '' : v },
    jumpStep(i) {
      // 只允许返回已走过的步骤；报告必须先完成辨证，避免出现空白报告。
      if (i <= this.step) this.step = i
    },
    reset() { this.pick = {}; this.result = { bagang: [], meridians: [], patterns: [], formulas: [] }; this.step = 0 },
    analyze() {
      if (!Object.keys(this.pick).some(k => this.pick[k])) {
        uni.showToast({ title: '请至少选择一项体征', icon: 'none' })
        return
      }
      const p = this.pick
      const bg = new Set()
      const mer = new Set()
      const patterns = []
      const formulas = []

      // 望色
      if (p['望色']) {
        if (p['望色'].includes('白')) { bg.add('虚'); bg.add('寒'); patterns.push('面色白主虚寒') }
        if (p['望色'].includes('赤')) { bg.add('热'); patterns.push('面色赤主热证') }
        if (p['望色'].includes('黄')) { bg.add('虚'); mer.add('太阴'); patterns.push('面色黄主脾虚湿盛') }
        if (p['望色'].includes('青')) { bg.add('寒'); patterns.push('面色青主寒主痛主瘀') }
        if (p['望色'].includes('黑')) { bg.add('肾虚'); mer.add('少阴'); patterns.push('面色黑主肾虚水饮') }
      }
      // 舌
      if (p['舌质'] === '淡白') bg.add('虚')
      if (p['舌质'] === '红' || p['舌质'] === '绛') bg.add('热')
      if (p['舌质'] === '紫暗') patterns.push('舌紫暗主瘀血')
      if (p['舌质'] === '胖大有齿痕') { mer.add('太阴'); patterns.push('舌胖大齿痕主脾虚湿盛') }
      if (p['舌苔'] === '白腻') { bg.add('寒'); patterns.push('苔白腻主寒湿') }
      if (p['舌苔'] === '黄' || p['舌苔'] === '黄腻') { bg.add('热'); patterns.push('苔黄主里热') }
      // 望神
      if (p['望神'] === '失神' || p['望神'] === '假神') patterns.push('⚠ 神志异常：' + (p['望神'] === '假神' ? '假神为危候' : '失神预后不良'))
      // 闻诊
      if (p['声音'] === '语声高亢') bg.add('实')
      if (p['声音'] === '语声低微' || p['声音'] === '少气懒言') bg.add('虚')
      if (p['声音'] === '谵语') { bg.add('热'); bg.add('实'); patterns.push('谵语主热扰心神') }
      if (p['呼吸'] === '短气') bg.add('虚')
      // 问诊十问
      if (p['头身'] === '头痛项强' || p['头身'] === '身痛骨节痛') {
        mer.add('太阳')
        if (p['头身'] === '头痛项强') patterns.push('头项强痛属太阳表证')
      }
      if (p['头身'] === '身重困倦') { mer.add('太阴'); patterns.push('身重困倦多见脾虚湿盛') }
      if (p['头身'] === '头晕目眩') { mer.add('少阳'); patterns.push('头晕目眩可见少阳或水饮') }
      if (p['汗'] === '无汗') { mer.add('太阳'); formulas.push('麻黄汤') }
      if (p['汗'] === '有汗自汗') { mer.add('太阳'); bg.add('表虚'); formulas.push('桂枝汤') }
      if (p['汗'] === '盗汗') bg.add('阴虚')
      if (p['汗'] === '大汗不止') { bg.add('阳虚'); patterns.push('大汗不止防亡阳') }
      if (p['大便'] === '便秘') { bg.add('里'); bg.add('实'); mer.add('阳明'); formulas.push('承气汤类') }
      if (p['大便'] === '下利清谷') { bg.add('里'); bg.add('寒'); mer.add('少阴'); formulas.push('四逆汤') }
      if (p['大便'] === '黏滞不爽') { mer.add('太阴'); patterns.push('大便黏滞主湿') }
      if (p['小便'] === '短赤') bg.add('热')
      if (p['小便'] === '清长') bg.add('寒')
      if (p['口渴'] === '渴喜冷饮') { bg.add('热'); formulas.push('白虎汤') }
      if (p['口渴'] === '渴不欲饮') patterns.push('渴不欲饮主湿或瘀')
      if (p['口渴'] === '消渴多饮') { mer.add('厥阴'); patterns.push('消渴属厥阴') }
      if (p['睡眠'] === '但欲寐') { mer.add('少阴'); patterns.push('但欲寐为少阴主证') }
      if (p['睡眠'] === '彻夜不眠') bg.add('阴虚')
      if (p['手足温度'] === '手脚冰凉') { bg.add('寒'); mer.add('少阴'); formulas.push('四逆汤') }
      if (p['手足温度'] === '手心热脚凉') { patterns.push('上热下寒（厥阴）'); mer.add('厥阴'); formulas.push('乌梅丸') }
      if (p['手足温度'] === '脚凉手温') { patterns.push('脚冷=里寒之兆'); mer.add('太阴') }
      if (p['胃口'] === '毫无胃口') patterns.push('胃气将绝，亟需重视')
      if (p['寒热'] === '恶寒') { mer.add('太阳'); bg.add('表') }
      if (p['寒热'] === '往来寒热') { mer.add('少阳'); formulas.push('小柴胡汤') }
      if (p['寒热'] === '但热不寒') { mer.add('阳明'); bg.add('热') }
      // 切诊
      if (p['脉位'] === '浮') bg.add('表')
      if (p['脉位'] === '沉') bg.add('里')
      if (p['脉率'] === '迟') bg.add('寒')
      if (p['脉率'] === '数') bg.add('热')
      if (p['脉形'] === '弦') mer.add('少阳')
      if (p['脉形'] === '细') bg.add('虚')
      if (p['脉形'] === '滑') bg.add('实')
      if (p['脉形'] === '洪') bg.add('热')
      if (p['脉力'] === '有力') bg.add('实')
      if (p['脉力'] === '无力') bg.add('虚')

      // 阴阳总判
      const hasYang = [...bg].some(b => ['表','热','实'].includes(b))
      const hasYin = [...bg].some(b => ['里','寒','虚'].includes(b))
      if (hasYang && !hasYin) bg.add('阳')
      else if (hasYin && !hasYang) bg.add('阴')
      else if (hasYang && hasYin) bg.add('寒热错杂')

      // 去重
      this.result = {
        bagang: [...bg],
        meridians: [...mer],
        patterns: patterns.slice(0, 8),
        formulas: [...new Set(formulas)].slice(0, 5)
      }
      this.step = 4
    }
  }
}
</script>

<style scoped>
.page { min-height: 100vh; background: var(--bg); padding-bottom: 80rpx; }

/* 步骤条 */
.steps { display: flex; padding: 22rpx 20rpx 16rpx; }
.step { flex: 1; display: flex; flex-direction: column; align-items: center; }
.sp-num { width: 52rpx; height: 52rpx; border-radius: 50%; border: 3rpx solid var(--line); color: var(--ink2); font-size: 24rpx; font-weight: 800; display: flex; align-items: center; justify-content: center; }
.step.on .sp-num { border-color: var(--brand); background: var(--brand); color: #FDF8EE; }
.step.done .sp-num { border-color: var(--gold); background: var(--gold); color: #fff; }
.sp-t { font-size: 18rpx; color: var(--ink2); margin-top: 6rpx; }
.step.on .sp-t { color: var(--brand); font-weight: 700; }

.tab-body { padding: 10rpx 32rpx 0; }
.grp { padding: 24rpx 28rpx; margin-bottom: 18rpx; }
.g-t { font-size: 27rpx; font-weight: 800; color: var(--brand); margin-bottom: 16rpx; }
.opts { display: flex; flex-wrap: wrap; gap: 10rpx; }
.opt { display: flex; align-items: center; padding: 12rpx 26rpx; border-radius: 30rpx; background: var(--zebra-bg); color: var(--ink2); font-size: 23rpx; border: 2rpx solid transparent; }
.opt.sm { padding: 8rpx 20rpx; font-size: 21rpx; }
.opt.on { background: var(--brand); color: #fff; border-color: var(--brand); }
.opt-dot { width: 20rpx; height: 20rpx; border-radius: 50%; margin-right: 10rpx; border: 1rpx solid rgba(0,0,0,.1); }
.opt-note { margin-top: 14rpx; font-size: 21rpx; color: var(--ink2); background: var(--quote-bg); border-radius: 10rpx; padding: 10rpx 16rpx; line-height: 1.7; }
.sub-lab { font-size: 21rpx; color: var(--gold); margin: 14rpx 0 8rpx; font-weight: 700; }

.ten-tip { padding: 20rpx 26rpx; margin-bottom: 16rpx; font-size: 21rpx; color: var(--ink2); line-height: 1.7; background: var(--quote-bg); }

.next-btn { text-align: center; background: linear-gradient(135deg, var(--brand), var(--brand-deep)); color: #FDF8EE; border-radius: 44rpx; padding: 22rpx 0; font-size: 27rpx; font-weight: 700; margin: 20rpx 0; }
.nav-row { display: flex; gap: 16rpx; margin: 20rpx 0; }
.nav-btn { flex: 1; text-align: center; border-radius: 44rpx; padding: 20rpx 0; font-size: 25rpx; font-weight: 700; border: 2rpx solid var(--line); color: var(--ink2); }
.nav-btn.main { background: linear-gradient(135deg, var(--brand), var(--brand-deep)); color: #FDF8EE; border-color: transparent; }

/* 报告 */
.report { padding: 32rpx 30rpx; }
.r-t { font-size: 32rpx; font-weight: 800; color: var(--brand); margin-bottom: 24rpx; text-align: center; }
.r-sec { margin-bottom: 24rpx; }
.rs-t { font-size: 24rpx; font-weight: 800; color: var(--ink); margin-bottom: 12rpx; border-left: 5rpx solid var(--gold); padding-left: 14rpx; }
.r-tags { display: flex; flex-wrap: wrap; gap: 10rpx; }
.r-tag { font-size: 22rpx; padding: 8rpx 22rpx; border-radius: 10rpx; font-weight: 700; }
.r-tag.yang { background: #FBEAE3; color: #9A2E1F; }
.r-tag.yin { background: #E9F1F2; color: #2F5D62; }
.r-tag.mer { background: #EDE9F4; color: #54427C; }
.r-line { font-size: 22rpx; color: var(--ink); line-height: 2; }
.r-fang { font-size: 28rpx; color: var(--brand); font-weight: 800; margin: 8rpx 0; }
.r-warn { margin-top: 20rpx; font-size: 19rpx; color: #A2651B; background: #FCF3DC; border-radius: 12rpx; padding: 14rpx 18rpx; line-height: 1.7; }
</style>
