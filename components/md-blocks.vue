<template>
  <view class="mdv" :class="{ serifbody: fam === 'serif' }" :style="{ fontSize: fs + 'rpx' }">
    <view v-for="(b, bi) in blocks" :key="bi" class="blk">
      <!-- 标题 -->
      <view v-if="b.ty === 'h1'" class="h1 serif"><seg :segs="b.segs" /></view>
      <view v-else-if="b.ty === 'h2'" class="h2"><seg :segs="b.segs" /></view>
      <view v-else-if="b.ty === 'h3'" class="h3 serif"><seg :segs="b.segs" /></view>
      <view v-else-if="b.ty === 'h4'" class="h4"><seg :segs="b.segs" /></view>
      <!-- 段落 -->
      <view v-else-if="b.ty === 'p'" class="p" :class="{ ind: b.ind }"><seg :segs="b.segs" /></view>
      <!-- key: value -->
      <view v-else-if="b.ty === 'kv'" class="kv">
        <text class="kv-k">{{ b.k }}</text>
        <view class="kv-v"><seg :segs="b.segs" /></view>
      </view>
      <!-- 引用 -->
      <view v-else-if="b.ty === 'quote'" class="quote">
        <view v-for="(ln, li) in b.lines" :key="li" class="q-line"><seg :segs="ln" /></view>
      </view>
      <!-- 列表 -->
      <view v-else-if="b.ty === 'ul'" class="list">
        <view v-for="(it, ii) in b.items" :key="ii" class="li" :style="{ paddingLeft: (it.lvl ? 44 : 8) + 'rpx' }">
          <text class="dot" :style="{ color: it.lvl ? 'var(--gold)' : 'var(--brand)' }">●</text>
          <view class="li-v"><seg :segs="it.segs" /></view>
        </view>
      </view>
      <view v-else-if="b.ty === 'ol'" class="list">
        <view v-for="(it, ii) in b.items" :key="ii" class="li" :style="{ paddingLeft: (it.lvl ? 44 : 8) + 'rpx' }">
          <text class="num">{{ it.n }}.</text>
          <view class="li-v"><seg :segs="it.segs" /></view>
        </view>
      </view>
      <!-- 表格 -->
      <view v-else-if="b.ty === 'table'" class="tblwrap">
        <view class="tblscroll">
          <view class="tbl" :style="{ minWidth: tableMin(b) }">
            <view class="tr th">
              <view v-for="(c, ci) in b.head" :key="'h' + ci" class="td" :style="cellStyle(b, ci, true)"><seg :segs="inlineCache(bi + 'h' + ci, c)" /></view>
            </view>
            <view v-for="(r, ri) in b.rows" :key="'r' + ri" class="tr" :class="{ zebra: ri % 2 === 1 }">
              <view v-for="(c, ci) in r" :key="c + ci" class="td" :style="cellStyle(b, ci, false)"><seg :segs="inlineCache(bi + ri + '-' + ci, c)" /></view>
            </view>
          </view>
        </view>
      </view>
      <!-- 代码 / 流程图 -->
      <view v-else-if="b.ty === 'code'">
        <view class="code" :class="{ fold: codeFold(bi) && !openedCode[bi] }"><seg :segs="codeSegs(b)" /></view>
        <view v-if="codeFold(bi)" class="code-toggle" @tap="toggleCode(bi)">{{ openedCode[bi] ? '▴ 收起' : '▾ 展开全部 ' + b.text.split('\n').length + ' 行' }}</view>
      </view>
      <view v-else-if="b.ty === 'hr'" class="mdhr"><text class="mdhr-orn">❖</text></view>
    </view>
  </view>
</template>

<script>
import { inlineSegs } from '@/utils/md.js'
import { store } from '@/utils/store.js'

export default {
  name: 'md-blocks',
  props: {
    blocks: { type: Array, default: () => [] },
    base: { type: Number, default: 28 }
  },
  data() {
    return { _segCache: {}, openedCode: {} }
  },
  computed: {
    fs() { return Math.round(this.base * (store.fontScale || 1)) },
    fam() { return store.fontFam || 'sans' }
  },
  methods: {
    codeFold(bi) {
      const b = this.blocks[bi]
      return b && b.ty === 'code' && b.text.split('\n').length > 26
    },
    codeText(b) {
      return b.text
    },
    codeSegs(b) {
      return inlineSegs(b && b.text ? b.text : '')
    },
    toggleCode(bi) {
      this.openedCode[bi] = !this.openedCode[bi]
    },
    inlineCache(key, text) {
      if (!this._segCache[key]) this._segCache[key] = inlineSegs(text)
      return this._segCache[key]
    },
    tableMin(b) {
      const n = Math.max((b.head || []).length, 2)
      return Math.max(750, Math.min(3200, 280 * n)) + 'rpx'
    },
    cellStyle(b, ci, isHead) {
      // 首列窄、长文列宽：min-width + 自然换行，表格超宽横向滚动
      const n = (b.head || []).length
      const first = '150rpx'
      const normal = n === 2 ? '460rpx' : n === 3 ? '330rpx' : '260rpx'
      return { minWidth: ci === 0 ? first : normal }
    }
  }
}
</script>

<style scoped>
.mdv { line-height: 1.9; color: var(--ink); letter-spacing: 0.5rpx; }
.serifbody, .serifbody .li-v, .serifbody .kv-v, .serifbody .q-line { font-family: 'Songti SC', 'STSong', 'STZhongsong', 'Noto Serif SC', 'SimSun', serif; }
.h1 { font-size: 1.5em; font-weight: 800; margin: 0.5em 0 0.6em; color: var(--brand); letter-spacing: 3rpx; }
.h2 { font-size: 1.25em; font-weight: 800; margin: 1.1em 0 0.5em; color: var(--ink); letter-spacing: 2rpx; }
.h3 { font-size: 1.12em; font-weight: 700; margin: 1em 0 0.4em; color: var(--brand-deep, #7C3A21); line-height: 1.5; }
.h4 { font-size: 1.02em; font-weight: 700; margin: 0.9em 0 0.3em; color: var(--ink2); line-height: 1.5; }
.p { margin: 0.5em 0; text-align: justify; word-break: break-word; overflow-wrap: anywhere; }
.li-v, .kv-v, .q-line { min-width: 0; word-break: break-word; overflow-wrap: anywhere; }
.p.ind { text-indent: 2em; }
.kv { display: flex; margin: 0.65em 0; align-items: flex-start; background: var(--zebra-bg); border: 1rpx solid var(--line); border-left: 7rpx solid var(--brand); border-radius: 14rpx; padding: 16rpx 20rpx; box-shadow: 0 3rpx 12rpx rgba(60,44,22,.04); }
.kv-k { flex: 0 0 108rpx; font-weight: 800; color: var(--brand); margin-right: 16rpx; line-height: 1.8; }
.kv-v { flex: 1; min-width: 0; line-height: 1.85; }
.quote { background: linear-gradient(135deg, var(--quote-bg), var(--zebra-bg)); border-left: 6rpx solid var(--gold); border-radius: 4rpx 16rpx 16rpx 4rpx; padding: 18rpx 24rpx; margin: 0.65em 0; }
.q-line { color: var(--ink2); margin: 4rpx 0; }
.list { margin: 0.5em 0; }
.li { display: flex; margin: 10rpx 0; align-items: flex-start; }
.dot { font-size: 0.5em; margin: 16rpx 14rpx 0 0; flex-shrink: 0; }
.num { color: var(--brand); font-weight: 700; margin-right: 12rpx; flex-shrink: 0; min-width: 36rpx; }
.li-v { flex: 1; }
.tblwrap { margin: 0.75em 0; }
.tblscroll { width: 100%; overflow-x: auto; -webkit-overflow-scrolling: touch; }
.tbl { border: 1rpx solid var(--line); border-radius: 14rpx; box-shadow: 0 2rpx 10rpx rgba(60,44,22,.04); width: max-content; max-width: none; }
.tr { display: flex; }
.th { background: linear-gradient(135deg, rgba(154,46,31,.92), rgba(124,58,33,.92)); }
.tdark .th { background: linear-gradient(135deg, #5A3128, #452922); }
.th .td { border-top: none; font-weight: 700; color: #FDF8EE; white-space: nowrap; }
.zebra { background: var(--zebra-bg); }
.td { padding: 13rpx 15rpx; font-size: 0.88em; border-top: 1rpx solid var(--line); border-left: 1rpx solid var(--line); flex: 0 0 auto; box-sizing: border-box; white-space: normal; word-break: break-word; overflow: visible; line-height: 1.7; }
.td:first-child { border-left: none; }
.code { background: var(--code-bg); border: 1rpx dashed var(--line); border-radius: 12rpx; padding: 20rpx 24rpx; margin: 0.6em 0; font-family: Menlo, Consolas, monospace; font-size: 0.82em; color: var(--ink2); white-space: pre-wrap; word-break: break-all; }
.code.fold { max-height: 260rpx; overflow: hidden; position: relative; }
.code-toggle { text-align: center; font-size: 21rpx; color: var(--brand); padding: 10rpx 0 16rpx; font-weight: 700; }
.mdhr { display: flex; align-items: center; justify-content: center; margin: 1.1em 0; color: var(--gold); }
.mdhr-orn { font-size: 0.8em; opacity: 0.75; }
.mdhr::before, .mdhr::after { content: ''; width: 90rpx; height: 1rpx; background: linear-gradient(90deg, transparent, var(--gold)); margin: 0 20rpx; }
.mdhr::after { background: linear-gradient(90deg, var(--gold), transparent); }
</style>

<style>
/* 行内片段全局样式（seg 组件在同文件内无法 scoped，用全局） */
.seg-b { font-weight: 700; color: var(--brand); }
.seg-i { font-style: italic; }
.seg-c { font-family: Menlo, Consolas, monospace; background: var(--zebra-bg); padding: 2rpx 8rpx; border-radius: 6rpx; font-size: 0.9em; }
.seg-d { text-decoration: line-through; color: var(--ink2); }
.seg-a { color: var(--brand); text-decoration: underline; }
</style>
