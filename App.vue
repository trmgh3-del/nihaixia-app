<script>
import { initSettings } from '@/utils/store.js'
import { setFangNames } from '@/utils/md.js'
import { loadData } from '@/utils/data.js'
export default {
  onLaunch() {
    initSettings()
    // 预载方名词典（正文方剂名互链）
    loadData('formulas').then(d => {
      if (d && d.items) setFangNames([...new Set(d.items.map(x => x.n))])
    }).catch(() => {})
  }
}
</script>

<style>
/* ================= 全局主题变量 ================= */
.tlight {
  --bg: #F6F1E7; --card: #FFFFFF; --ink: #2E2A24; --ink2: #6B6357; --line: #E8E0D0;
  --brand: #9A2E1F; --brand-deep: #7C3A21; --gold: #C8A45C; --accent: #2F5D62;
  --quote-bg: #F9F4E9; --thead-bg: #F3ECDD; --zebra-bg: #FAF7F0; --code-bg: #F3EFE5;
  --hero1: #9A2E1F; --hero2: #7C3A21;
}
.tdark {
  --bg: #151312; --card: #211E1B; --ink: #EAE3D4; --ink2: #A69C8B; --line: #37322B;
  --brand: #D06A4E; --brand-deep: #E0906E; --gold: #D9B87A; --accent: #7FB0AE;
  --quote-bg: #262220; --thead-bg: #2B2723; --zebra-bg: #262220; --code-bg: #1D1A18;
  --hero1: #3A241E; --hero2: #241713;
}
page {
  background-color: #F6F1E7;
  font-size: 28rpx;
  color: #2E2A24;
  font-family: -apple-system, BlinkMacSystemFont, 'Helvetica Neue', 'PingFang SC',
    'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
}
page.theme-dark, .theme-dark { background-color: #151312; color: #EAE3D4; }

/* 宽屏适配：桌面浏览器/平板 内容限宽居中 */
@media (min-width: 900px) {
  uni-page-body, page { max-width: 880px; margin: 0 auto; }
  .uni-tabbar { max-width: 880px; left: 50% !important; transform: translateX(-50%) !important; width: 100%; }
  .progress, .fab-warp, .fab { right: calc(50% - 440px + 24rpx) !important; }
}
/* 通用工具类 */
.serif { font-family: 'Songti SC', 'STSong', 'STZhongsong', 'Noto Serif SC', 'SimSun', serif; }
.card { background: var(--card); border-radius: 20rpx; box-shadow: 0 4rpx 20rpx rgba(60,44,22,.06); }
.hr { height: 1rpx; background: var(--line); }
.fade-in { animation: fadeIn .35s ease both; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(14rpx); } to { opacity: 1; transform: translateY(0); } }
button::after { border: none; }
.none { display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 110rpx 0; color: var(--ink2); font-size: 25rpx; }
.none::before { content: '❈'; display: block; font-size: 56rpx; color: var(--gold); opacity: .55; margin-bottom: 20rpx; }
.uni-input-input:focus { outline: none; }
.ico { width: 34rpx; height: 34rpx; flex-shrink: 0; }
.ico-s { width: 28rpx; height: 28rpx; flex-shrink: 0; }
.ico-lg { width: 44rpx; height: 44rpx; flex-shrink: 0; }
.card { transition: transform .12s ease, box-shadow .12s ease; }
.card:active, .press:active { transform: scale(.985); box-shadow: 0 2rpx 10rpx rgba(60,44,22,.1); }
/* 行内片段 */
.seg-b { font-weight: 700; color: var(--brand); white-space: nowrap; display: inline-block; }
.seg-i { font-style: italic; }
.seg-c { font-family: Menlo, Consolas, monospace; background: var(--zebra-bg); padding: 2rpx 8rpx; border-radius: 6rpx; font-size: .9em; }
.seg-d { text-decoration: line-through; color: var(--ink2); }
.seg-a { color: var(--brand); text-decoration: underline; }
/* 标题统一单行收纳：短标题不再无故换行，过长标题用省略号保持布局稳定 */
.sec-head { min-width: 0; }
.sec-head .sec-title, .sec-title { white-space: nowrap; overflow: hidden; text-overflow: ellipsis; min-width: 0; }
</style>
