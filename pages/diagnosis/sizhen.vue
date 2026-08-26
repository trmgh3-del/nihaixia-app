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
        <view class="basic-row"><input v-model="basic.age" type="number" placeholder="年龄" class="basic-input" /></view>
        <view class="sub-lab">病程</view>
        <view class="opts"><view v-for="o in durationOptions" :key="o" class="opt sm" :class="{ on: basic.duration === o }" @tap="basic.duration = o">{{ o }}</view></view>
        <view class="sub-lab">问诊类型</view>
        <view class="opts"><view v-for="o in caseTypes" :key="o" class="opt sm" :class="{ on: basic.caseType === o }" @tap="basic.caseType = o">{{ o }}</view></view>
        <view class="sub-lab">症状明显时段（可选）</view>
        <view class="opts"><view v-for="o in symptomTimeOptions" :key="o" class="opt sm" :class="{ on: basic.symptomTime === o }" @tap="basic.symptomTime = o">{{ o }}</view></view>
        <view class="sub-lab">已知误治情况（可选）</view>
        <view class="opts"><view v-for="o in misTreatmentOptions" :key="o" class="opt sm" :class="{ on: basic.misTreatment === o }" @tap="basic.misTreatment = o">{{ o }}</view></view>
        <view class="sub-lab">金匮杂病类型（可选）</view>
        <view class="opts"><view v-for="o in miscDiseaseOptions" :key="o" class="opt sm" :class="{ on: basic.miscDisease === o }" @tap="basic.miscDisease = o">{{ o }}</view></view>
        <view class="sub-lab">性别</view>
        <view class="opts"><view v-for="o in ['未说明', '男', '女']" :key="o" class="opt sm" :class="{ on: basic.sex === o }" @tap="basic.sex = o">{{ o }}</view></view>
        <view class="sub-lab">特殊情况</view>
        <view class="opts"><view class="opt sm" :class="{ on: basic.pregnant }" @tap="basic.pregnant = !basic.pregnant">孕期/备孕</view><view class="opt sm" :class="{ on: basic.chronic }" @tap="basic.chronic = !basic.chronic">有慢性病或正在用药</view></view>
        <view class="sub-lab">红旗症状（如有请立即就医）</view>
        <view class="opts"><view v-for="o in redFlagOptions" :key="o" class="opt sm danger-opt" :class="{ on: redFlags.includes(o) }" @tap="toggleRedFlag(o)">{{ o }}</view></view>
        <view class="basic-hint">基本信息仅用于风险提示，不会替代四诊判断；涉及孕期、儿童、高龄、慢性病或正在用药，请优先咨询执业医师。</view>
        <view class="snapshot-row"><view class="snapshot-btn" @tap="saveSnapshot">保存快照</view><view class="snapshot-btn" v-if="snapshots.length" @tap="restoreSnapshot">恢复最近快照</view></view>
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
      <view class="ten-tip card">倪师诊病十问扩展——寒热、汗、头身、二便、饮食、胸腹、耳、口渴及妇女情况，均需结合整体辨证</view>
      <view class="grp card" v-for="q in tenQ" :key="q.k">
        <view class="g-t serif">{{ q.k }}</view>
        <view class="opts">
          <view class="opt sm" v-for="o in q.opts" :key="o" :class="{ on: isPicked(q.k, o) }" @tap="toggleOption(q.k, o)">{{ o }}</view>
        </view>
      </view>
      <view class="grp card">
        <view class="g-t serif">⟡ 厥热胜复（厥阴动态，可选）</view>
        <view class="opts"><view v-for="o in jueReversalOptions" :key="o" class="opt sm" :class="{ on: pick['厥热胜复'] === o }" @tap="setPick('厥热胜复', o)">{{ o }}</view></view>
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
      <view class="grp card">
        <view class="g-t serif">⟡ 切诊来源</view>
        <view class="opts"><view v-for="o in pulseSources" :key="o" class="opt sm" :class="{ on: pulseSource === o }" @tap="pulseSource = o">{{ o }}</view></view>
        <view class="basic-hint">非医师自行触摸的脉象仅供参考，不能作为处方依据。</view>
      </view>
      <view class="grp card">
        <view class="g-t serif">⟡ 复合脉象（可选）</view>
        <view class="opts"><view v-for="o in complexPulses" :key="o.k" class="opt sm" :class="{ on: pick['复合脉'] === o.k }" @tap="setPick('复合脉', o.k)">{{ o.k }}</view></view>
        <view class="basic-hint">复合脉象必须结合症状、舌象判断，不能单凭脉象定方。</view>
      </view>
      <view class="nav-row">
        <view class="nav-btn" @tap="step = 2">‹ 上一步</view>
        <view class="nav-btn main" :class="{ disabled: analyzing }" @tap="analyze">{{ analyzing ? '正在读取知识库…' : '⟡ 生成辨证报告' }}</view>
      </view>
    </view>

    <!-- ===== 辨证报告 ===== -->
    <view v-if="step === 4" class="tab-body fade-in">
      <view class="report card">
        <view class="r-t serif">⟡ 四诊合参 · 辨证报告</view>
        <view class="report-meta">
          <text>规则版本：{{ result.kbVersion || '本地规则' }}</text><text>规则命中：{{ result.kbCoverage }}%</text><text>参考置信度：{{ result.kbConfidence || '不足' }}</text><text>采集完整度：{{ result.completeness }}%</text>
          <text :class="'risk-' + result.risk.level">风险：{{ result.risk.label }}</text>
        </view>
        <view class="r-risk" v-if="result.risk.reasons.length">⚠ {{ result.risk.reasons.join('；') }}</view>
        <view class="r-sec">
          <view class="rs-t">七步辨证摘要</view>
          <view class="r-line" v-for="x in result.sevenSteps" :key="x.k"><text class="step-label">{{ x.k }}</text>{{ x.v }}</view>
        </view>
        <view class="r-sec" v-if="result.combination">
          <view class="rs-t">脉舌/合病鉴别</view><view class="r-line">{{ result.combination }}</view>
        </view>
        <view class="r-sec" v-if="result.sources.length">
          <view class="rs-t">知识库依据</view>
          <view class="r-line source-link" v-for="s in result.sources" :key="s.id" @tap="openSource(s)">● {{ s.source }}：{{ s.title }} ›</view>
          <view class="r-line" v-for="e in result.kbEvidence" :key="e.name">● 匹配规则：{{ e.name }}（{{ e.source }}）</view>
          <view class="r-line">知识库匹配条目：{{ result.kbMatches }} 条（仅作为学习证据，不等同于诊断）</view>
        </view>
        <view class="r-sec" v-if="result.cases.length">
          <view class="rs-t">相似医案（仅供学习）</view>
          <view class="case-item" v-for="c in result.cases" :key="c.id" @tap="openCase(c)"><view><text class="case-title">{{ c.title }}</text><text class="case-date">{{ c.date }}</text></view><view class="case-excerpt">{{ c.excerpt || '医案未载病机摘要' }}</view></view>
        </view>
        <view class="r-sec">
          <view class="rs-t">基本信息</view>
          <view class="r-line">{{ basicSummary }}</view>
        </view>
        <view class="r-sec" v-if="result.scores.length">
          <view class="rs-t">六经倾向（按证据排序）</view>
          <view class="r-score" v-for="m in result.scores" :key="m.name"><text class="r-tag mer">{{ m.role }}：{{ m.name }} {{ m.score }}分</text><text class="score-reason">{{ m.reason }}</text></view>
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
        <view class="r-sec" v-if="result.formulas.length && result.risk.level !== 'high'">
          <view class="rs-t">参考方剂方向</view>
          <view class="r-fang serif" v-for="f in result.formulas" :key="f">「{{ f }}」</view>
          <view class="basic-hint">仅为学习用方证提示，不构成购药、煎服或处方依据。</view>
          <view class="formula-detail" v-for="f in result.formulaDetails" :key="f.name">
            <text class="formula-name">{{ f.name }}</text><text v-if="f.clinical">主治/依据：{{ f.clinical }}</text><text v-if="f.composition">组成：{{ f.composition }}</text><text v-if="f.caution">禁忌：{{ f.caution }}</text>
          </view>
        </view>
        <view class="r-sec" v-if="result.risk.level === 'high'">
          <view class="rs-t">紧急处理</view><view class="r-risk">检测到高风险表现，已停止方剂推荐。请立即就医，不要依据本工具自行用药。</view>
        </view>
        <view class="r-warn">⚠ 四诊合参仅供学习参考，非诊断结论。临床请由执业医师面诊；急重症立即就医。涉及附子、麻黄、细辛等峻药，严禁据此自行购药服用。</view>
        <view class="r-actions"><view class="nav-btn" @tap="copyReport">复制报告</view><view class="nav-btn main" @tap="saveReport">保存报告</view></view>
      </view>
      <view class="nav-row"><view class="nav-btn" @tap="step = 0">‹ 返回修改</view><view class="nav-btn" @tap="reset">↺ 重新采集</view></view>
      <view class="saved-reports card" v-if="savedReports.length">
        <view class="rs-t">历史报告（最近 {{ savedReports.length }} 份）</view>
        <view class="saved-item" v-for="(item, i) in savedReports" :key="item.ts" @tap="viewReport(item)"><text>{{ formatReportTime(item.ts) }} · {{ item.result && item.result.meridians ? (item.result.meridians[0] || '未明确') : '未明确' }}</text><text class="saved-del" @tap.stop="removeReport(i)">查看/删除</text></view>
      </view>
    </view>
  </view>
</template>

<script>
import { store, applyTheme } from '@/utils/store.js'
import { analyzeSizhen } from '@/utils/sizhen-engine.js'
import { loadData } from '@/utils/data.js'
import { openMd, openEntry } from '@/utils/routes.js'
import { loadData } from '@/utils/data.js'
import { openMd, openEntry } from '@/utils/routes.js'

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
  { k: '胃口', opts: ['正常', '亢进', '差/食少', '毫无胃口', '食入即吐', '饥而不欲食'] },
  { k: '疼痛', opts: ['无', '胸痛彻背', '胸胁苦满', '气上撞心/心中疼热', '刺痛', '隐痛', '冷痛', '灼痛'] },
  { k: '胸腹', opts: ['无明显异常', '腹满', '心悸', '胸腹胀满', '心中疼热'] },
  { k: '耳', opts: ['无明显异常', '耳鸣', '耳聋', '耳胀痛'] },
  { k: '妇女', opts: ['不适用/未说明', '经期正常', '经量异常', '带下异常', '孕期出血或腹痛'] },
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
  ['脉位', '脉率', '脉形', '脉力', '复合脉']
]
const EMPTY_RESULT = () => ({ bagang: [], meridians: [], patterns: [], formulas: [], formulaDetails: [], scores: [], selected: [], completeness: 0, risk: { level: 'low', label: '一般', reasons: [] }, sevenSteps: [], combination: '', sources: [], kbEvidence: [], kbVersion: '', kbCoverage: 0, kbConfidence: '不足', kbMatches: 0, cases: [] })
const RED_FLAGS = ['胸痛/胸闷', '呼吸困难', '意识异常/抽搐', '呕血/便血', '持续高热不退', '严重脱水']
const DURATIONS = ['当天', '2-3天', '4-7天', '1-2周', '超过2周', '反复发作']
const PULSE_SOURCES = ['医师诊察', '自己触摸估计', '不确定']
const CASE_TYPES = ['急性外感/感冒', '慢性内伤', '妇科问题', '消化问题', '心肺症状', '不确定']
const MISTREATMENTS = ['无/不确定', '表证误下·利不止', '无汗误用桂枝·烦躁胸闷', '少阴误汗·亡阳', '厥阴误下·利不止']
const MISC_DISEASES = ['不适用/未说明', '痉病', '湿病', '中风', '历节', '血痹', '虚劳', '肺痿', '肺痈', '胸痹', '腹满寒疝', '痰饮咳嗽', '消渴']
const JUE_REVERSALS = ['厥多热少（病进）', '热多厥少（病退）', '厥热相等（病稳）']
const SYMPTOM_TIMES = ['未说明', '清晨（寅至辰）', '中午（巳至未）', '黄昏（申至戌）', '半夜（亥至丑）', '深夜（子至寅）', '凌晨（丑至卯）']
const COMPLEX_PULSES = [
  { k: '浮缓', mer: '太阳', reason: '太阳中风，体虚有汗' }, { k: '浮紧', mer: '太阳', reason: '太阳伤寒，体实无汗' },
  { k: '沉迟', mer: '太阴', reason: '里寒湿、脾阳不足' }, { k: '沉微', mer: '少阴', reason: '阳虚、病由太阴入少阴' },
  { k: '弦数', mer: '少阳', reason: '少阳郁热，需防阳明化热' }, { k: '弦缓', mer: '少阳', reason: '少阳兼太阴虚' },
  { k: '微细欲绝', mer: '少阴', reason: '阳气衰微，属于高风险脉象' }, { k: '结代', mer: '少阴', reason: '心动悸、脉结代，需医师复核' }
]
const MULTI_FIELDS = ['寒热', '疼痛', '胸腹']
const MERIDIANS = ['太阳', '阳明', '少阳', '太阴', '少阴', '厥阴']

export default {
  data() {
    return {
      step: 0,
      stepNames: ['望诊', '闻诊', '问诊', '切诊', '报告'],
      pick: {},
      basic: { age: '', sex: '未说明', duration: '', caseType: '不确定', symptomTime: '未说明', misTreatment: '无/不确定', miscDisease: '不适用/未说明', pregnant: false, chronic: false },
      caseTypes: CASE_TYPES,
      symptomTimeOptions: SYMPTOM_TIMES,
      misTreatmentOptions: MISTREATMENTS,
      miscDiseaseOptions: MISC_DISEASES,
      jueReversalOptions: JUE_REVERSALS,
      complexPulses: COMPLEX_PULSES,
      redFlags: [],
      redFlagOptions: RED_FLAGS,
      durationOptions: DURATIONS,
      pulseSources: PULSE_SOURCES,
      pulseSource: '不确定',
      savedReports: [],
      snapshots: [],
      analyzing: false,
      result: EMPTY_RESULT(),
      wangSe: WANG_SE, wangShe: WANG_SHE, wangTai: WANG_TAI, wangShen: WANG_SHEN,
      wenVoice: WEN_VOICE, wenBreath: WEN_BREATH,
      tenQ: TEN_Q,
      qieWei: QIE_WEI, qieShuai: QIE_SHUAI, qieXing: QIE_XING, qieLi: QIE_LI
    }
  },
  computed: {
    theme() { return store.theme },
    stepCount() { return i => { const fields = STEP_FIELDS[i] || []; return fields.filter(k => this.pick[k]).length + '/' + fields.length } },
    basicSummary() {
      const b = this.basic
      return [b.age ? b.age + '岁' : '年龄未说明', b.sex || '性别未说明', b.duration || '病程未说明', '类型：' + (b.caseType || '不确定'), b.symptomTime && b.symptomTime !== '未说明' ? '时段：' + b.symptomTime : '', b.miscDisease && b.miscDisease !== '不适用/未说明' ? '杂病：' + b.miscDisease : '', b.misTreatment && b.misTreatment !== '无/不确定' ? '误治：' + b.misTreatment : '', '切诊来源：' + this.pulseSource, b.pregnant ? '孕期/备孕' : '', b.chronic ? '慢性病/用药' : '', this.redFlags.length ? '红旗：' + this.redFlags.join('、') : '无红旗症状'].filter(Boolean).join(' · ')
    }
  },
  onLoad() {
    try {
      const draft = uni.getStorageSync('nx_sizhen_draft')
      if (draft && draft.ts && Date.now() - draft.ts < 24 * 60 * 60 * 1000) {
        this.pick = draft.pick || {}; this.basic = Object.assign(this.basic, draft.basic || {}); this.redFlags = draft.redFlags || []; this.pulseSource = draft.pulseSource || '不确定'; this.step = Math.min(draft.step || 0, 3)
        uni.showToast({ title: '已恢复上次问诊', icon: 'none' })
      }
    } catch (e) {}
  },
    onShow() {
    applyTheme()
    try { this.savedReports = uni.getStorageSync('nx_sizhen_reports') || []; this.snapshots = uni.getStorageSync('nx_sizhen_snapshots') || [] } catch (e) { this.savedReports = []; this.snapshots = [] }
  },
  onHide() { if (this.step < 4) this.saveDraft() },
  methods: {
    saveSnapshot() {
      try {
        const next = [{ ts: Date.now(), pick: JSON.parse(JSON.stringify(this.pick)), basic: { ...this.basic }, redFlags: [...this.redFlags], pulseSource: this.pulseSource }, ...(this.snapshots || [])].slice(0, 5)
        this.snapshots = next; uni.setStorageSync('nx_sizhen_snapshots', next); uni.showToast({ title: '快照已保存', icon: 'success' })
      } catch (e) { uni.showToast({ title: '快照保存失败', icon: 'none' }) }
    },
    restoreSnapshot() {
      const s = this.snapshots && this.snapshots[0]
      if (!s) return
      this.pick = JSON.parse(JSON.stringify(s.pick || {})); this.basic = Object.assign(this.basic, s.basic || {}); this.redFlags = s.redFlags || []; this.pulseSource = s.pulseSource || '不确定'; this.step = 0
      uni.showToast({ title: '已恢复最近快照', icon: 'none' })
    },
    setPick(k, v) { this.pick[k] = this.pick[k] === v ? '' : v },
    isPicked(k, v) { return MULTI_FIELDS.includes(k) ? (Array.isArray(this.pick[k]) && this.pick[k].includes(v)) : this.pick[k] === v },
    toggleOption(k, v) {
      if (!MULTI_FIELDS.includes(k)) { this.setPick(k, v); return }
      const current = Array.isArray(this.pick[k]) ? this.pick[k].slice() : []
      const neutral = ['无', '无寒热', '无明显异常', '不适用/未说明']
      const i = current.indexOf(v)
      if (i >= 0) current.splice(i, 1)
      else {
        if (neutral.includes(v)) current.splice(0, current.length)
        else neutral.forEach(x => { const j = current.indexOf(x); if (j >= 0) current.splice(j, 1) })
        current.push(v)
      }
      this.pick[k] = current
    },
    hasPick(k, v) { return Array.isArray(this.pick[k]) ? this.pick[k].includes(v) : this.pick[k] === v },
    saveDraft() {
      try { uni.setStorageSync('nx_sizhen_draft', { ts: Date.now(), pick: this.pick, basic: this.basic, redFlags: this.redFlags, pulseSource: this.pulseSource, step: this.step }) } catch (e) {}
    },
    clearDraft() { try { uni.removeStorageSync('nx_sizhen_draft') } catch (e) {} },
    jumpStep(i) {
      // 只允许返回已走过的步骤；报告必须先完成辨证，避免出现空白报告。
      if (i <= this.step) this.step = i
    },
    reset() { this.pick = {}; this.basic = { age: '', sex: '未说明', duration: '', caseType: '不确定', symptomTime: '未说明', misTreatment: '无/不确定', miscDisease: '不适用/未说明', pregnant: false, chronic: false }; this.redFlags = []; this.pulseSource = '不确定'; this.result = EMPTY_RESULT(); this.step = 0; this.clearDraft() },
    toggleRedFlag(v) { const i = this.redFlags.indexOf(v); if (i >= 0) this.redFlags.splice(i, 1); else this.redFlags.push(v) },
    async analyze() {
      if (this.analyzing) return
      if (!Object.keys(this.pick).some(k => Array.isArray(this.pick[k]) ? this.pick[k].length : this.pick[k])) {
        uni.showToast({ title: '请至少选择一项体征', icon: 'none' }); return
      }
      this.analyzing = true
      try {
        this.result = await analyzeSizhen(this.pick, this.basic, this.redFlags, this.pulseSource)
        this.clearDraft(); this.step = 4
      } catch (e) {
        console.error('四诊分析失败', e)
        uni.showToast({ title: '辨证引擎加载失败，请重试', icon: 'none' })
      } finally { this.analyzing = false }
    },
    reportText() {
      const r = this.result
      return ['《四诊合参辨证报告》', '生成时间：' + new Date().toLocaleString(), '基本信息：' + this.basicSummary, '采集完整度：' + r.completeness + '%', '风险：' + r.risk.label, r.risk.reasons.length ? '风险提示：' + r.risk.reasons.join('；') : '', '采集记录：' + r.selected.join('；'), '八纲：' + (r.bagang.join('、') || '信息不足'), '六经：' + (r.meridians.join('、') || '暂不明确'), '病机：' + (r.patterns.join('；') || '暂无'), '参考方剂：' + (r.risk.level === 'high' ? '高风险，已停止推荐' : (r.formulas.join('、') || '暂无')), '仅供学习参考，不能替代执业医师面诊。'].filter(Boolean).join('\\n')
    },
    copyReport() {
      uni.setClipboardData({ data: this.reportText(), success: () => uni.showToast({ title: '报告已复制', icon: 'none' }) })
    },
    openCase(c) { openEntry({ f: 'casesTable', i: c.id, c: 'case' }) },
    async openSource(source) {
      try {
        const d = await loadData('diagnosis')
        for (const g of d.groups || []) {
          const item = (g.items || []).find(x => x.id === source.id)
          if (item) { openMd({ ...item, f: 'diag' }, item.t, { items: g.items }); return }
        }
      } catch (e) { uni.showToast({ title: '知识库加载失败', icon: 'none' }) }
    },
    saveReport() {
      try {
        const list = uni.getStorageSync('nx_sizhen_reports') || []
        list.unshift({ ts: Date.now(), text: this.reportText(), result: this.result, basic: this.basic, redFlags: this.redFlags })
        uni.setStorageSync('nx_sizhen_reports', list.slice(0, 20))
        this.savedReports = list.slice(0, 20)
        uni.showToast({ title: '报告已保存', icon: 'success' })
      } catch (e) { uni.showToast({ title: '保存失败', icon: 'none' }) }
    },
    formatReportTime(ts) { return new Date(ts).toLocaleString() },
    viewReport(item) {
      if (!item || !item.text) return
      uni.showModal({ title: '历史辨证报告', content: item.text.slice(0, 1800), showCancel: false, confirmText: '关闭' })
    },
    removeReport(i) {
      const list = this.savedReports.slice(); list.splice(i, 1); this.savedReports = list
      try { uni.setStorageSync('nx_sizhen_reports', list) } catch (e) {}
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
.snapshot-row { display: flex; gap: 12rpx; margin-top: 14rpx; }
.snapshot-btn { flex: 1; text-align: center; border: 1rpx solid var(--line); border-radius: 24rpx; padding: 9rpx 0; color: var(--brand); font-size: 20rpx; }
.danger-opt { color: #9A2E1F; border-color: rgba(154,46,31,.2); }
.danger-opt.on { background: #9A2E1F; color: #fff; }
.basic-row .basic-input { margin-bottom: 2rpx; }
.risk-high + .r-sec { border-color: #9A2E1F; }
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
.nav-btn.disabled { opacity: .55; pointer-events: none; }

/* 报告 */
.report { padding: 32rpx 30rpx; }
.r-t { font-size: 32rpx; font-weight: 800; color: var(--brand); margin-bottom: 18rpx; text-align: center; }
.report-meta { display: flex; justify-content: space-between; font-size: 21rpx; color: var(--ink2); margin-bottom: 16rpx; }
.risk-low { color: #3F6B37; }.risk-medium { color: #A2651B; }.risk-high { color: #9A2E1F; font-weight: 800; }
.r-risk { color: #9A2E1F; background: #F5E8E8; padding: 14rpx 18rpx; border-radius: 10rpx; font-size: 21rpx; line-height: 1.7; margin-bottom: 20rpx; }
.r-score { display: flex; align-items: center; gap: 14rpx; margin-bottom: 10rpx; }
.score-reason { font-size: 20rpx; color: var(--ink2); }
.step-label { display: inline-block; min-width: 120rpx; color: var(--brand); font-weight: 700; }
.source-link { color: var(--brand); text-decoration: underline; }
.case-item { border-top: 1rpx solid var(--line); padding: 14rpx 0; }
.case-title { color: var(--brand); font-weight: 700; font-size: 22rpx; }
.case-date { color: var(--ink2); font-size: 18rpx; margin-left: 12rpx; }
.case-excerpt { color: var(--ink2); font-size: 19rpx; line-height: 1.6; margin-top: 6rpx; }
.formula-detail { margin-top: 14rpx; padding: 14rpx 18rpx; border-radius: 10rpx; background: var(--zebra-bg); display: flex; flex-direction: column; gap: 6rpx; font-size: 19rpx; color: var(--ink2); line-height: 1.6; }
.formula-name { color: var(--brand); font-weight: 800; font-size: 22rpx; }
.r-actions { display: flex; gap: 16rpx; margin-top: 20rpx; }
.saved-reports { margin-top: 22rpx; padding: 24rpx 28rpx; }
.saved-item { display: flex; justify-content: space-between; border-top: 1rpx solid var(--line); padding: 14rpx 0; font-size: 20rpx; color: var(--ink2); }
.saved-del { color: var(--brand); padding-left: 24rpx; }
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
