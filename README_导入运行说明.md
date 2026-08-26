# 倪师经方 · UniApp App 项目

基于 [jangviktor-web/nihaixia](https://github.com/jangviktor-web/nihaixia)（倪海厦经方中医 AI Skill 知识库）**全量内容**打造的离线知识库 App。
**技术栈：HBuilderX + UniApp（Vue3）**，一套代码可发布 Android / iOS / H5。

> ✅ **完整性已通过双审计**：源仓库 50 个文件（约 6MB / 225 万字）逐行比对 + 加强版（阈值降至 2 字，覆盖药名/短行/标题行），内容收录 **0 缺失**（`tools/final_audit.py` / `tools/audit_strict.py` 可复验）。

---

## 一、内容全量收录（50 个源文件 → 3694 结构化条目，全部离线内置）

| 分类 | 内容 | 数量 |
|---|---|---|
| 伤寒论 | 太阳篇导言+条文1-129（含补遗/心智模型）+ 下篇阳明篇补齐138-276（含编号对照说明）+ 五经总结·诊病十问 | 167 节 |
| 金匮要略 | 23 篇完整讲解 + 第5/6/7篇讲课实录 + 上课前言 + 续伤寒篇 + 卷首导言 | 27 章 |
| 黄帝内经 | 72 篇（54 提炼 + 18 完整）+ 篇目总览 | 73 篇 |
| 神农本草经 | 上137/中110/下131，含原文·性味·主治·倪注·容川注·用量·禁忌·倪师口述·补注 九类字段 | 378 味 |
| 经方库 | 原方 vs 倪师临床剂量（〔口述〕/〔换算〕标注）+ 感冒六方 + 六经主方 + 剂量速查卡 + 05/06 剂量全档原文 | 157 方 |
| 针灸 | 教程总览 + 十二经络流注 + 五输穴 + 任督要穴 + 治症精选 + 针灸精髓讲义（含"倪師講解針灸"全卷）+ 穴位补遗 | 30 节 + 301 穴 |
| 医案 | 结构化总表（12字段全保留）+ 叙事医案（六大分类，内嵌病历小节已并回父案）+ 人纪医案集（411→195 例整案） | 1703 例 |
| 辨证 | 六经辨证8大公式 + 开阖枢 + 快速诊断流程图 + 脉诊/舌诊速查 + 真寒假热八维 + 七步走 + 用药铁律 + 误治急救 + 诊断经验汇编 | 完整 |
| SKILL 内核 | 速查卡A-H、倪海厦视角、回答工作流、心智模型、决策启发式、表达DNA、关键词索引、常见问答 + **SKILL.md 完整原文（132KB）** | 130+ 节 |
| 讲义文库 | 梁冬对话/人纪闭门课七大重病/扶阳论坛/仲景心法/斯坦福演讲/易筋经/汉唐文章/汉唐诊疗日志 | 412 篇(含附录) |
| 调研附录 | research 全部9文件 + 审计清单(112方/164穴) + 蒸馏README + 剂量表原文全档 + README/README_EN/CHANGELOG/官网页 | 全部 |
| 天纪 | 天机道(紫微斗数)·人间道(易经64卦)·地脉道(阳宅风水) 含各卷概览 | 15 节 |

## 二、功能特性

**内容与检索**
- 🔍 全局搜索：3694 条目索引秒搜 + 「深度全文」模式（扫描全部正文、带上下文摘录）+ 搜索历史
- 🎲 随机一品 / 📖 继续阅读（首页快捷入口）
- 📑 阅读位置自动记忆（每个条目恢复上次滚动位置）

**临床工具**
- 🧭 六经辨证中心：8大公式速览 + **症状自查**（勾选症状→六经评分+主方建议）+ 脉舌鉴别 + 速查总库
- ⇄ **方剂对比**：任选两方，主症/组成/原方/临床剂量双栏对照
- 📊 **医案统计**：1257例年度诊疗量、高频诊断TOP15、高频方剂TOP15 图表
- 🌡 本草性味筛选（寒/热/温/凉/平/有毒）、穴位经络筛选、医案年度+疗效双重筛选

**AI 问诊**
- 内置蒸馏版「倪师思维内核」；任意可从设备访问的 OpenAI 兼容接口（DeepSeek/Kimi/通义/OpenAI/远程 Ollama）；浏览器端禁止 localhost/127.0.0.1
- 三种模式：精简内核 / **检索增强RAG**（自动检索本地知识库附给AI）/ 完整SKILL(132KB)
- SSE 流式输出、会话本地保存、⇪ 一键导出对话

**阅读与效率（新增）**
- 阅读器**上一篇/下一篇**连续翻阅（带位置指示 n/总数），支持伤寒/金匮/内经/针灸/医案/文库/天纪全部列表
- 收藏/历史记录带分类标记，点击直达对应类型页面（方剂详情/本草药卡/医案详单），旧记录按 id 前缀智能推断
- Markdown 表格：列最小宽度 + 自然换行 + 原生横向滚动（超宽表格右列完整可见）
- 搜索结果**关键词高亮** + 深度扫描实时状态提示（◎ 正在扫描…）
- 首页统计卡**点击直达**对应板块；正文**黑体/宋体**双字体切换（古籍风）
- AI 欢迎引导屏；医案一键复制；我的页数据管理（清空足迹/收藏/会话）

**学习中心（新增）**
- **闪卡背诵**：经方156方/本草378味3D翻卡，"记住了/再复习"队列（本地进度）
- **条文背诵**：22条核心条文遮盖填空自测（点击空格显示答案）+ 原文对照 + 每日计数
- **十八反·十九畏速查**：两味药即查配伍禁忌（含歌诀与明细）
- **煎药指南**：先煎/后下/烊化冲服/布包煎 + 火候用水（依讲义煎服法整理）
- **学习报告**：本周阅读/背诵/闪卡/收藏/打卡六项统计 + 9枚成就徽章墙
- **阅读笔记**：任意条目记录心得（阅读器右下笔记按钮）
- **语音朗读**：TTS 读条文（H5 speechSynthesis / App plus.speech）
- **AI回答溯源**：检索增强模式的回答附引用出处chips，点击直达库内原文
- **倪师语录每日一句**：首页按日轮换15条库内金句

**数据与安全（新增）**
- **备份与恢复**：收藏/笔记/打卡/闪卡进度/配置 一键导出JSON（剪贴板/文件），粘贴恢复（含校验）
- **内容更新**：检查GitHub源仓库最新提交 vs 本地构建日期；支持数据包热更新（App端）
- **AI测试连接**：配置页一键测试API连通性（含延迟显示/CORS提示）
- **语音输入问诊**：AI页麦克风语音转文字（H5 Chrome / App plus.speech）
- **正文方剂名自动互链**：伤寒/金匮正文中方剂名自动变为可点击，直达方剂详解卡（30+处/篇）
- **方剂↔医案互链**：方剂详解页自动展示「相关医案 N 例」（从1257例表反查）

**体验（美化升级）**
- 宣纸⇢玄墨深夜模式、字号调节（阅读器 A-/A+）、收藏/阅读足迹、每日一方（配朱砂印章角标）
- Markdown 精排：中文长段**首行缩进两字**（古典排版）、标题朱砂竖线、表头品牌渐变、引文纸纹卡、分隔线纹饰
- **全套自绘线性图标**（18 枚功能图标 + 5 枚导航图标，等线宽圆头笔画设计语言；工具 `tools/gen_icons2/3.py` 可复现），无 emoji 依赖、多端渲染一致
- 阅读器**顶部进度条**（金→朱渐变）、卷首/卷终装饰、全局卡片按压反馈
- AI 打字三点动画、气泡排版、全部数据离线可用

## 三、HBuilderX 运行步骤

1. 安装 [HBuilderX](https://www.dcloud.io/hbuilderx.html)（最新版，含 App 开发插件）
2. **文件 → 导入 → 从本地目录导入**，选择 `nihaixia-app`
3. **运行 H5**：运行 → 运行到浏览器
4. **真机运行**：运行 → 运行到手机或模拟器（按提示装基座）
5. **打包**：发行 → App-云打包（APK/IPA）；`manifest.json` 可视化配置图标名称
   - Android 权限最小化（仅 INTERNET，供 AI 问诊）

> 标准HBuilderX工程（无 node_modules）。CLI 编译已实测通过：`@dcloudio/*@3.0.0-5020420260813003 + vite@5.2.8 + vue@3.4.21`；浏览器自动化回归 **13/13 + 专项 18 项全部通过、0 运行时错误**。

## 四、AI 问诊配置

「AI问诊」→ 右上 ⚙：API 地址（如 `https://api.deepseek.com`）、API Key（仅存本机）、模型名、内核模式、流式/温度。H5 端需接口允许跨域，App 端无此限制。

## 五、目录结构

```
nihaixia-app/
├── pages/            # 主包：首页/医典/辨证/AI问诊/我的/搜索
├── pkgTexts/         # 伤寒论·金匮·内经·通用阅读器（滚动记忆）
├── pkgBencao/ pkgZhenjiu/ pkgFormula/ pkgCase/ pkgArticle/ pkgTianji/
├── components/       # md-blocks(Markdown渲染) / seg(行内片段)
├── utils/            # data(加载) store(状态) md(解析) ai(问诊引擎) routes(路由/检索)
├── static/data/      # 全部知识库 JSON（7.9MB，离线）
├── static/tabbar/    # 导航图标
├── tools/            # build_data.py(数据构建) final_audit.py(完整性审计) gen_icons.py
├── screenshots/      # 21 张实机截图
└── pages.json manifest.json App.vue main.js uni.scss index.html
```

## 六、数据重建与完整性审计（可选）

```bash
git clone https://github.com/jangviktor-web/nihaixia /tmp/repo
python3 tools/build_data.py /tmp/repo static/data    # 重建全部 JSON
python3 tools/build_sizhen_rules.py                    # 编译四诊可执行规则
python3 tools/test_sizhen_rules.py                     # 规则结构+六经回归样例检查
python3 tools/test_sizhen_architecture.py              # 检查页面是否仍有旧辨证逻辑
node --experimental-default-type=module tools/test_sizhen_safety.mjs # 方剂安全过滤回归检查
node --experimental-default-type=module tools/test_sizhen_runtime.mjs # 编译规则运行时回归检查
python3 tools/check_upstream_sync.py                   # 检查上游 main 是否有新提交
python3 tools/report_sizhen_coverage.py                # 查看知识条目到规则的引用覆盖率
python3 tools/validate_case_dataset.py                 # 验证 1257 条结构化医案字段
python3 tools/test_acupoint_dataset.py                 # 验证穴位库与辨证联动数据
python3 tools/validate_expert_blind.py tools/expert_blind_cases.schema.json # 验证专家盲测数据格式
python3 tools/score_expert_blind.py tools/expert_blind_cases.schema.json # 有真实结果后统计一致率
python3 tools/final_audit.py
# HBuilderX 真机验收请按 tools/HBUILDERX_TEST_CHECKLIST.md 执行                           # 逐行审计（应为 0 缺失）
```

## 七、免责声明

内容为倪海厦人纪/天纪教学资料的开源蒸馏整理，仅用于中医学习与文化传播，不构成医疗建议。处方用药请遵执业医师指导；急重症请立即就医。AI 对话由第三方模型生成，观点不代表本项目立场。人纪/天纪著作权归原权利人。
