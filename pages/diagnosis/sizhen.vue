<template>
  <view class="page" :class="theme === 'dark' ? 'tdark' : 'tlight'">
    <!-- 进度指示 -->
    <view class="steps">
      <view class="step" v-for="(s, i) in stepNames" :key="i" :class="{ on: step === i, done: step > i }" @tap="jumpStep(i)">
        <view class="sp-num serif">{{ i + 1 }}</view>
        <view class="sp-t">{{ s }}<text class="step-count" v-if="i < 4">{{ stepCount(i) }}</text></view>
      </view>
    </view>

    <!-- ===== 1 望诊 ===== -->
    <view v-if="step === 0" class="tab-body fade-in">
      <view class="grp card basic-card">
        <view class="g-t serif">⟡ 基本信息（可选）</view>
        <view class="basic-row"><input v-model="basic.age" type="number" placeholder="年龄" class="basic-input" /><input v-model="basic.duration" placeholder="症状持续时间" class="basic-input" /></view>
        <view class="sub-lab">性别</view>
        <view class="opts"><view v-for="o in ['未说明', '男', '女']" :key="o" class="opt sm" :class="{ on: basic.sex === o }" @tap="basic.sex = o">{{ o }}</view></view>
        <view class="sub-lab">特殊情况</view>
        <view class="opts"><view class="opt sm" :class="{ on: basic.pregnant }" @tap="basic.pregnant = !basic.pregnant">孕期/备孕</view><view class="opt sm" :class="{ on: basic.chronic }" @tap="basic.chronic = !basic.chronic">有慢性病或正在用药</view></view>
        <view class="basic-hint">基本信息仅用于风险提示，不会替代四诊判断；涉及孕期、儿童、高龄、慢性病或正在用药，请优先咨询执业医师。</view>
      </view>
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
        <view class="report-meta">
          <text>采集完整度：{{ result.completeness }}%</text>
          <text :class="'risk-' + result.risk.level">风险：{{ result.risk.label }}</text>
        </view>
        <view class="r-risk" v-if="result.risk.reasons.length">⚠ {{ result.risk.reasons.join('；') }}</view>
        <view class="r-sec" v-if="result.scores.length">
          <view class="rs-t">六经倾向（按证据排序）</view>
          <view class="r-score" v-for="m in result.scores" :key="m.name"><text class="r-tag mer">{{ m.name }} {{ m.score }}分</text><text class="score-reason">{{ m.reason }}</text></view>
        </view>
        <view class="r-sec">
          <view class="rs-t">本次采集记录</view>
          <view class="r-line" v-for="x in result.selected" :key="x">● {{ x }}</view>
        </view>
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
        <view class="r-warn">⚠ 四诊合参仅供学习参考，非诊断结论。临床请由执业医师面诊；急重症立即就医。涉及附子、麻黄、细辛等峻药，严禁据此自行购药服用。</view>
        <view class="r-actions"><view class="nav-btn" @tap="copyReport">复制报告</view><view class="nav-btn main" @tap="saveReport">保存报告</view></view>
      </view>
      <view class="nav-row"><view class="nav-btn" @tap="step = 0">‹ 返回修改</view><view class="nav-btn" @tap="reset">↺ 重新采集</view></view>
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

const STEP_FIELDS = [
  ['望色', '舌质', '舌苔', '望神'],
  ['声音', '呼吸'],
  TEN_Q.map(q => q.k),
  ['脉位', '脉率', '脉形', '脉力']
]
const EMPTY_RESULT = () => ({ bagang: [], meridians: [], patterns: [], formulas: [], scores: [], selected: [], completeness: 0, risk: { level: 'low', label: '一般', reasons: [] } })
const MERIDIANS = ['太阳', '阳明', '少阳', '太阴', '少阴', '厥阴']

export default {
  data() {
    return {
      step: 0,
      stepNames: ['望诊', '闻诊', '问诊', '切诊', '报告'],
      pick: {},
      basic: { age: '', sex: '未说明', duration: '', pregnant: false, chronic: false },
      result: EMPTY_RESULT(),
      wangSe: WANG_SE, wangShe: WANG_SHE, wangTai: WANG_TAI, wangShen: WANG_SHEN,
      wenVoice: WEN_VOICE, wenBreath: WEN_BREATH,
      tenQ: TEN_Q,
      qieWei: QIE_WEI, qieShuai: QIE_SHUAI, qieXing: QIE_XING, qieLi: QIE_LI
    }
  },
  computed: {
    theme() { return store.theme },
    stepCount() { return i => { const fields = STEP_FIELDS[i] || []; return fields.filter(k => this.pick[k]).length + '/' + fields.length } }
  },
  onLoad() {
    try {
      const draft = uni.getStorageSync('nx_sizhen_draft')
      if (draft && draft.ts && Date.now() - draft.ts < 24 * 60 * 60 * 1000) {
        this.pick = draft.pick || {}; this.basic = Object.assign(this.basic, draft.basic || {}); this.step = draft.step || 0
        uni.showToast({ title: '已恢复上次问诊', icon: 'none' })
      }
    } catch (e) {}
  },
  onShow() { applyTheme() },
  onHide() { this.saveDraft() },
  methods: {
    setPick(k, v) { this.pick[k] = this.pick[k] === v ? '' : v },
    saveDraft() {
      try { uni.setStorageSync('nx_sizhen_draft', { ts: Date.now(), pick: this.pick, basic: this.basic, step: this.step }) } catch (e) {}
    },
    clearDraft() { try { uni.removeStorageSync('nx_sizhen_draft') } catch (e) {} },
    jumpStep(i) {
      // 只允许返回已走过的步骤；报告必须先完成辨证，避免出现空白报告。
      if (i <= this.step) this.step = i
    },
    reset() { this.pick = {}; this.basic = { age: '', sex: '未说明', duration: '', pregnant: false, chronic: false }; this.result = EMPTY_RESULT(); this.step = 0; this.clearDraft() },
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

      // 证据评分：问诊/切诊权重高于一般望闻信息，并保留理由供报告复核。
      const score = {}; const reasons = {}
      MERIDIANS.forEach(m => { score[m] = 0; reasons[m] = [] })
      const addScore = (m, n, why) => { score[m] += n; if (why && !reasons[m].includes(why)) reasons[m].push(why) }
      const rules = {
        '望色': { '面色黄': ['太阴', 1, '面色黄'], '面色黑': ['少阴', 1, '面色黑'], '面色赤': ['阳明', 1, '面色赤'] },
        '舌苔': { '黄': ['阳明', 2, '苔黄'], '黄腻': ['阳明', 1, '苔黄腻'], '白腻': ['太阴', 2, '苔白腻'] },
        '汗': { '无汗': ['太阳', 2, '无汗'], '有汗自汗': ['太阳', 2, '自汗'], '大汗不止': ['少阴', 2, '大汗不止'] },
        '寒热': { '恶寒': ['太阳', 3, '恶寒'], '恶风': ['太阳', 2, '恶风'], '往来寒热': ['少阳', 3, '往来寒热'], '但热不寒': ['阳明', 3, '但热不寒'] },
        '大便': { '便秘': ['阳明', 3, '便秘'], '下利清谷': ['少阴', 3, '下利清谷'], '黏滞不爽': ['太阴', 2, '便黏滞'] },
        '口渴': { '渴喜冷饮': ['阳明', 2, '渴喜冷饮'], '消渴多饮': ['厥阴', 3, '消渴'] },
        '睡眠': { '但欲寐': ['少阴', 3, '但欲寐'] },
        '手足温度': { '手脚冰凉': ['少阴', 3, '手脚冰凉'], '手心热脚凉': ['厥阴', 3, '上热下寒'], '脚凉手温': ['太阴', 2, '脚凉手温'] },
        '头身': { '头痛项强': ['太阳', 2, '头项强痛'], '身痛骨节痛': ['太阳', 2, '身痛骨节痛'], '身重困倦': ['太阴', 2, '身重困倦'], '头晕目眩': ['少阳', 1, '头晕目眩'] },
        '脉位': { '浮': ['太阳', 3, '脉浮'], '沉': ['少阴', 2, '脉沉'] },
        '脉率': { '迟': ['少阴', 2, '脉迟'], '数': ['阳明', 2, '脉数'] },
        '脉形': { '弦': ['少阳', 2, '脉弦'], '细': ['少阴', 2, '脉细'], '滑': ['阳明', 1, '脉滑'], '洪': ['阳明', 2, '脉洪'] },
        '脉力': { '有力': ['阳明', 1, '脉有力'], '无力': ['少阴', 2, '脉无力'], '微': ['少阴', 3, '脉微'] }
      }
      Object.keys(rules).forEach(k => { const rule = rules[k][p[k]]; if (rule) addScore(rule[0], rule[1], rule[2]) })
      mer.forEach(m => { if (!score[m]) addScore(m, 1, '其他四诊信息') })
      const scores = MERIDIANS.map(name => ({ name, score: score[name], reason: reasons[name].slice(0, 3).join('、') })).filter(x => x.score > 0).sort((a, b) => b.score - a.score)
      const selected = Object.keys(p).filter(k => p[k]).map(k => k + '：' + p[k])
      const completedSteps = STEP_FIELDS.filter(fields => fields.some(k => p[k])).length
      const completeness = Math.round(completedSteps / STEP_FIELDS.length * 100)
      const conflicts = []
      if (p['口渴'] === '渴喜冷饮' && ['白腻', '薄白'].includes(p['舌苔'])) conflicts.push('口渴喜冷饮但舌苔偏寒湿，寒热线索并见')
      if (p['脉率'] === '迟' && p['舌苔'] === '黄') conflicts.push('脉迟但苔黄，寒热线索并见')
      if (p['睡眠'] === '但欲寐' && p['脉力'] === '有力') conflicts.push('但欲寐与脉有力需复核')
      const riskReasons = [...conflicts]
      if (['失神', '假神'].includes(p['望神'])) riskReasons.push('神志异常')
      if (['大汗不止', '下利清谷'].includes(p['汗']) || p['大便'] === '下利清谷') riskReasons.push('存在脱液或亡阳风险')
      if (p['手足温度'] === '手脚冰凉' || p['脉力'] === '微') riskReasons.push('阳虚厥逆表现')
      if (this.basic.pregnant) riskReasons.push('孕期/备孕')
      if (this.basic.chronic) riskReasons.push('慢性病或正在用药')
      const risk = { level: riskReasons.length ? (riskReasons.some(x => ['神志异常', '存在脱液或亡阳风险'].includes(x)) ? 'high' : 'medium') : 'low', label: riskReasons.length ? (riskReasons.some(x => ['神志异常', '存在脱液或亡阳风险'].includes(x)) ? '高风险' : '需复核') : '一般', reasons: riskReasons }

      // 阴阳总判
      const hasYang = [...bg].some(b => ['表','热','实'].includes(b))
      const hasYin = [...bg].some(b => ['里','寒','虚'].includes(b))
      if (hasYang && !hasYin) bg.add('阳')
      else if (hasYin && !hasYang) bg.add('阴')
      else if (hasYang && hasYin) bg.add('寒热错杂')

      // 去重
      if (conflicts.length) patterns.unshift('输入复核：' + conflicts.join('；'))
      if (!scores.length) patterns.unshift('当前信息不足，暂不能形成明确六经倾向，请补充寒热、汗、二便、胃口及脉象。')
      this.result = {
        bagang: [...bg],
        meridians: scores.length ? scores.map(x => x.name) : [...mer],
        patterns: patterns.slice(0, 8),
        formulas: [...new Set(formulas)].slice(0, 5),
        scores,
        selected,
        completeness,
        risk
      }
      this.clearDraft()
      this.step = 4
    },
    reportText() {
      const r = this.result
      return ['《四诊合参辨证报告》', '采集完整度：' + r.completeness + '%', '风险：' + r.risk.label, r.risk.reasons.length ? '风险提示：' + r.risk.reasons.join('；') : '', '采集记录：' + r.selected.join('；'), '八纲：' + (r.bagang.join('、') || '信息不足'), '六经：' + (r.meridians.join('、') || '暂不明确'), '病机：' + (r.patterns.join('；') || '暂无'), '参考方剂：' + (r.formulas.join('、') || '暂无'), '仅供学习参考，不能替代执业医师面诊。'].filter(Boolean).join('\\n')
    },
    copyReport() {
      uni.setClipboardData({ data: this.reportText(), success: () => uni.showToast({ title: '报告已复制', icon: 'none' }) })
    },
    saveReport() {
      try {
        const list = uni.getStorageSync('nx_sizhen_reports') || []
        list.unshift({ ts: Date.now(), text: this.reportText(), result: this.result })
        uni.setStorageSync('nx_sizhen_reports', list.slice(0, 20))
        uni.showToast({ title: '报告已保存', icon: 'success' })
      } catch (e) { uni.showToast({ title: '保存失败', icon: 'none' }) }
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
.step-count { display: block; font-size: 16rpx; color: var(--gold); margin-top: 3rpx; }
.basic-row { display: flex; gap: 14rpx; }
.basic-input { flex: 1; height: 68rpx; line-height: 68rpx; padding: 0 18rpx; box-sizing: border-box; border-radius: 12rpx; background: var(--zebra-bg); color: var(--ink); font-size: 22rpx; }
.basic-hint { margin-top: 14rpx; color: var(--ink2); font-size: 19rpx; line-height: 1.6; }
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
.r-t { font-size: 32rpx; font-weight: 800; color: var(--brand); margin-bottom: 18rpx; text-align: center; }
.report-meta { display: flex; justify-content: space-between; font-size: 21rpx; color: var(--ink2); margin-bottom: 16rpx; }
.risk-low { color: #3F6B37; }.risk-medium { color: #A2651B; }.risk-high { color: #9A2E1F; font-weight: 800; }
.r-risk { color: #9A2E1F; background: #F5E8E8; padding: 14rpx 18rpx; border-radius: 10rpx; font-size: 21rpx; line-height: 1.7; margin-bottom: 20rpx; }
.r-score { display: flex; align-items: center; gap: 14rpx; margin-bottom: 10rpx; }
.score-reason { font-size: 20rpx; color: var(--ink2); }
.r-actions { display: flex; gap: 16rpx; margin-top: 20rpx; }
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
