# 设计文档:引文锚点+时间审计 与 新 sibling `envsci-slides`

- 日期:2026-06-28
- 状态:已通过 brainstorming,待用户审阅 → 转 writing-plans
- 仓库(单一来源):`envsci-paper-skill/`(git `main`),改完同步到 `~/.claude/skills/`
- 版本:`2.0.0 → 2.1.0`(新增特性、向后兼容,SemVer minor)

---

## 1. 目标与背景

在与 [academic-research-skills](https://github.com/imbad0202/academic-research-skills) 和
[nature-skills](https://github.com/Yuan1z0825/nature-skills) 的对比中,本集群的诚信门禁虽硬,但缺两项 ARS 已具备的细粒度能力:**引文页/段/句锚点** 与 **时间一致性审计**;同时缺少 nature-skills 的 **论文→可视化产物(GA/汇报)** 转换器。本次一次性补齐:

- **Part A**:给 `envsci-citations` 增加(1)页/段/句锚点核验、(2)时间一致性/时代错置审计;并给 `envsci-writing` 加"高危声明发出锚点"的起草规则。
- **Part B**:新建 sibling `envsci-slides`,产出 ①图文摘要 GA/TOC graphic、②学术汇报 deck。
- **Part C**:总伞与插件 manifest 登记、版本与文档更新。

## 2. 范围(YAGNI)

**纳入**:Part A(锚点 c 方案 + 时间审计三检查)、Part B(GA + deck,脚本驱动混合,引入 `python-pptx`)、Part C(注册/版本/文档)、验证、收尾三方对比表。

**不纳入**:海报 poster、科普 lay summary(envsci-slides ③ 扩展,留待将来);把锚点强制到每一句(b 方案,过度);为锚点改 `check_references.py`(锚点需联网读源,属推理门禁)。

## 3. brainstorming 已锁定的决策

| # | 决策 | 选择 |
|---|---|---|
| D1 | 组织方式 | 一份合并 spec,A+B 一起做;收尾重做三方对比 |
| D2 | slides 范围 | ① GA/TOC + ② 汇报 deck(不做 ③) |
| D3 | slides 出活方式 | A 脚本驱动混合;deck 引入 `python-pptx` |
| D4 | 锚点强度 | c:高危声明(数值/直接引语/关键结论)强制发出锚点 + 全量核验;writing 一并改 |
| D5 | 时间审计形态 | 三检查挂现有相位(新 C5 + 扩 §6 + Phase E 备注);脚本仅加 `--manuscript-year` 前向引用筛 |
| D6 | pipeline 挂载 | GA 进 Stage 10 (FINALIZE);汇报 deck 不做阻断阶段,仅 hand-off 注明可单独调用 |
| D7 | deck 模板 | 可切换:会议口头(默认)/组会/答辩 |

---

## Part A — `envsci-citations`(+ `envsci-writing`)增强

### A1. 页/段/句锚点(D4 方案 c)

**锚点语法(新增约定,CSL locator 风格,人读+机读):**

- 页:`[@key, p. 42]` / 页范围 `[@key, pp. 42–45]`
- 节:`[@key, §3.2]`(或 `[@key, sec. 3.2]`)
- 直接引语:`[@key, "≤25 词原句"]`(原句同时出现在正文引号内)

锚点是**起草期标注 + 审计元数据**。格式转换(§7 `citations` 模式)时按目标刊样式渲染:
- 直接引语:多数刊要求给出页码,锚点页码保留进引文。
- 转述声明:Elsevier 编号制 `[n]` 等通常不打印页码 → 锚点仅用于**审计追踪**,不进正文。

**发出端 —— `envsci-writing`(小改):**

- `references/writing.md` 新增一节"**高危声明的来源锚点**":凡属下列三类的句子,起草时**必须**带锚点;其余可选:
  1. 任何来自文献的**数值**(浓度、回收率、指数值、限值/阈值、文献统计量);
  2. 任何**直接引语**;
  3. 任何具体的、可争议的**结论性断言**(归因于某来源)。
- `SKILL.md` 在写作纪律处加一行指针,并在"When NOT to use / hand off"提示锚点的**核验**归 `envsci-citations`。
- 触发词补充(中/英):`source anchor / 锚点 / 页码定位`。

**核验端 —— `envsci-citations`(主改):**

- `references/citations-and-integrity.md` 扩 **Phase B(Citation context → + anchor verification)**:对每条带锚点的高危声明,在联网取源时核对:
  1. 锚点位置可解析(页在该文献页码范围内;节/章存在);
  2. 直接引语确在该处(或邻近);
  3. 该处确实支持声明(沿用 Phase B 既有"source supports claim?")。
- 新判据:`ANCHOR_VERIFIED` / `ANCHOR_UNRESOLVED`(取不到源/无法定位,记 NOTE)/ `ANCHOR_MISMATCH`(引语未找到 / 页超范围 → FAIL)/ `ANCHOR_MISSING`(高危声明缺必需锚点 → I-2 FAIL,I-1 记 SERIOUS)。
- §2 deception 列表交叉引用(锚点缺失/伪造与 PH/SH、DOI Misdirection 联动)。
- §9 pre-finalize 清单:新增"每条高危声明带**已核验**锚点(无 ANCHOR_MISSING/MISMATCH)"。
- §10 输出报告 summary 表新增一行 **Anchor verification**;Issues 区按 location 列出。
- §11 一行提醒新增:"高危声明=数字/引语/关键结论必须钉锚点;锚点页码对不上=造假信号"。
- **脚本不动**(锚点核验需联网读源,属 Claude 推理门禁,符合"脚本只做离线结构"分工)。

### A2. 时间一致性 / 时代错置审计(D5)

三类检查,挂到现有相位(不另起大相位):

| 检查 | 内容 | 落点 | 执行者 |
|---|---|---|---|
| T1 前向引用/时序不可能 | 引了发表晚于本文写作年的文献当先验依据;或时序自相矛盾 | 新增 **Phase C5 Temporal integrity** | 脚本预筛 + 推理 |
| T2 过时/被取代的标准版本 | 引旧版 WHO/EPA/GB 限值、已更新的 IRIS RfD/SF、被取代的 SQG | 扩 **§6**(每类标准加"版本时效"核查列/备注) | 推理 + §6 既有标准原文查证 |
| T3 时代/时态错配 | "迄今/最新/首次报道"却引陈旧来源或被更早文献推翻(联动 `envsci-ideate` 抢发检查) | **Phase E** 备注 | 推理 |

- 新判据:`TEMPORAL_OK` / `TEMPORAL_FORWARD_REF`(T1)/ `TEMPORAL_SUPERSEDED`(T2)/ `TEMPORAL_EPOCH_MISMATCH`(T3)。
- 严重度:T1 前向引用 = HIGH/SERIOUS;T2 过时标准 = MEDIUM~SERIOUS(取决于是否影响结论,如限值变化导致超标判断翻转→SERIOUS);T3 = NOTE~MEDIUM。
- §9 清单新增"时间一致性:无前向引用 / 关键限值取现行版本 / '最新/首次'类断言经时间核验"。
- §10 输出 summary 表新增一行 **Temporal integrity**。
- §2 已有的 "Temporal Masking" compound-deception 加交叉引用,统一口径。

**脚本唯一新增 —— `scripts/check_references.py`:**

- 新增可选参数 `--manuscript-year N`:启用后,任何 `引文年 > N` 标记 `TEMPORAL_FORWARD_REF`(HIGH;并入 exit 1 判定)。复用已有年份解析与 `--max-year` 逻辑。
- 更新 `--selftest`:内置一条 `引文年 > manuscript-year` 的样例,断言被捕获;无网络、无新依赖(保持 stdlib-only)。
- §8 文档同步更新 CLI 用法与示例。

---

## Part B — 新 sibling `envsci-slides`

### B1. 目录结构(贴 cluster 模板)

```text
skills/envsci-slides/
├── SKILL.md                 # 路由(50–80 行):EN+中文触发词 + "Not for X use Y" 边界
├── references/
│   └── slides.md            # 深文档:心智模型/硬规格/GA档案库/deck档案库/工具/Gate-S/交接
└── scripts/
    ├── ga_canvas.py         # GA/TOC 画布→按刊 px/dpi 导出(SVG + PNG);复用色盲安全配色
    ├── deck_build.py        # deck:python-pptx 从结构化大纲→.pptx + speaker notes
    └── requirements.txt     # python-pptx;(matplotlib/numpy 复用,GA 可选)
```

### B2. `SKILL.md`(描述与边界)

- `name: envsci-slides`
- 描述开头:"Use when the user wants to BUILD the visual submission/dissemination artifacts for an environmental-science field-sampling paper: a **graphical abstract / TOC graphic**, or a **presentation deck**(conference / group meeting / defense)."
- **EN 触发**:graphical abstract, GA, TOC graphic / table-of-contents art, paper-to-slides, paper-to-PPT, presentation deck, conference slides, defense slides, group-meeting slides, speaker notes。
- **中文触发**:图文摘要(成图/做图)、做 GA、TOC 图、论文转 PPT、汇报幻灯、会议幻灯、组会汇报、答辩 PPT、讲者备注、把论文做成汇报。
- **边界(Not for X — use Y),防与现有 skill 打架**:
  - GA/highlights 的**文字、摘要措辞** → `envsci-writing`(已管 "写 highlights/图文摘要");
  - 各刊 GA/TOC **尺寸与规格** → `envsci-journals`(slides **消费**其规格,不重复维护);
  - **正文出版图 / 新数据图** → `envsci-figures`(slides 只**重组已有图**,**绝不新画/新数**);
  - 通用图型选择 / 视觉-QA 闭环 / 中文字体 → 配合 `scipilot-figure-skill`。
- **诚信继承(关键)**:幻灯与 GA 上的**每个数字、每条结论必须已存在于经 I-1/I-2 门禁核验的正文**;`envsci-slides` 自身**绝不引入新数字/新声明**——只做"已核验内容"的视觉重组。

### B3. `references/slides.md`(七节)

1. **§1 心智模型(契约先行)**:先定**唯一核心信息**(one-message)→ 选 archetype → 拉取**已核验素材**(图来自 `envsci-figures`,数字来自 Data Ledger/已核验正文,文字来自 `envsci-writing`,规格来自 `envsci-journals`)。
2. **§2 硬规格**:GA = Elsevier ~531×1328 px(或矢量,短边 ≥531 px);ES&T TOC = 3.25×1.75 in、≥300 dpi、+ 50–60 词 synopsis。字体内嵌、色盲安全、缩略图可读(最小字号阈值)、SVG-first→PNG。附"各刊 GA 规格"指针(指向 `envsci-journals`,不复制)。
3. **§3 GA archetype 库**(环境采样导向):机理/过程示意、前→后对比、空间梯度小图、**"输入→系统→输出"通量图**(契合 SWI 孔隙水/peeper 营养盐通量)、概念剖面图。每型给 do/don't 与"信息密度上限"。
4. **§4 deck archetype + 三种节奏模板**:会议口头(~10–12 min:hook→gap→methods 轻→key results→take-home)/组会(方法与排障更深)/答辩(完整 methods+QA/QC、预设问答)。附 slide-type 目录 + speaker-notes 写法。
5. **§5 工具与大纲 schema**:`ga_canvas.py` / `deck_build.py` 用法;结构化大纲(JSON/MD)字段定义;导出与命名。
6. **§6 Gate-S(Slides-QA 自检契约)**:逐项 pass/fail——GA:缩略图可读、词数/信息密度达标、色盲安全、单位齐、尺寸/dpi 合刊、synopsis 词数、**无新增/未核验数字**;deck:一页一信息、字号阈值、图均可溯源(注明源 figure)、**无杜撰内容**。仿 `envsci-figures` 的 Gate-F。
7. **§7 交接**:GA → `envsci-journals` 投稿包;deck 独立;诚信指针 → `envsci-citations`(数字须已核验)。

### B4. 脚本契约

- `ga_canvas.py`:输入结构化版式(标题/要素/配色/目标刊预设),输出 `SVG + PNG`(按刊 px/dpi)。预设至少:`elsevier-ga`(531×1328)、`est-toc`(3.25×1.75 in @300 dpi)。色盲安全配色**与 `envsci-figures` 一致,但调色板拷贝进本脚本**——不在运行时 `import` envsci-figures,以保持 envsci-slides 可独立安装(install.md 允许单装)。带 `--selftest`:生成一张样例 GA 并断言尺寸/dpi/文件存在。
- `deck_build.py`:输入结构化大纲(标题/分节/每页 bullet/figure 路径/备注/模板名),用 `python-pptx` 输出 `.pptx`(含 speaker notes)。模板:`conference`(默认)/`group`/`defense`。带 `--selftest`:生成一份 3–4 页样例 deck 并断言文件/页数/notes 存在。
- `requirements.txt`:`python-pptx`(deck);GA 若用 matplotlib 则复用 figures 的 `matplotlib numpy`。Windows 用 `py`(见用户环境约定)。

---

## Part C — 集成、注册与文档

### C1. 总伞 `skills/enviro-paper/SKILL.md`(D6)

- frontmatter:`8 envsci-*` → `9 envsci-*`,并在描述中加入 envsci-slides。
- bullet sibling 列表:加 `envsci-slides (图文摘要/汇报幻灯)`。
- hand-off 段:加 `- graphical abstract / TOC graphic / presentation deck → **envsci-slides**`。
- 10 阶段 pipeline 表:**Stage 10 (RESPONSE/FINALIZE)** owner 增加 `envsci-slides`(GA 作为投稿包一部分);并加一句注:汇报 deck 为可单独调用的传播产物,不是阻断阶段;slides 只消费 I 门禁已核验内容。

> **计数口径(避免改错)**:manifest 描述串里的 "1 umbrella + **8** function skills" → "**9** function skills"(功能 skill 数,加了 envsci-slides);install.md 的 "collection of **9** Agent Skills" → "**10**"(含 umbrella 的总数),其内部 "+ 8 envsci-* function skills" → "+ 9"。两个数指代不同,别混。

### C2. 插件 manifest(描述串里都写着"8 ... function skills (...)",需改为 9 并加 envsci-slides,且 version → 2.1.0)

- `.claude-plugin/marketplace.json`:顶层 `version` + `plugins[0].version` → `2.1.0`;两处 `description` 串("8"→"9",列表加 envsci-slides);`plugins[0].keywords` 视情加 `graphical-abstract`/`slides`。
- `.claude-plugin/plugin.json`:`version` → `2.1.0`;`description` 串同改;keywords 视情补。
- `.codex-plugin/plugin.json`:`version` → `2.1.0`;`description` 串同改;`interface.longDescription` 可加"generate a graphical abstract and a presentation deck";`interface.capabilities` 已含 Write。

### C3. 文档

- `install.md`:"collection of **9**"→"**10**";目录树加 `envsci-slides/` 行;§4 Verify 加 `py skills/envsci-slides/scripts/ga_canvas.py --selftest` 与 `deck_build.py --selftest`,并提示 `pip install -r skills/envsci-slides/scripts/requirements.txt`。
- `README.md`:技能清单/计数更新,加 envsci-slides 一行(及其在表/列表里的位置)。
- `CHANGELOG.md`:新增 `## [2.1.0] — 2026-06-28`,记 Added(envsci-slides;citations 锚点+时间审计;writing 锚点规则;check_references.py `--manuscript-year`)。

### C4. 同步安装

改完 dev 仓库后,把 `skills/*` 同步到 `~/.claude/skills/`(新增 envsci-slides 文件夹 + 覆盖 enviro-paper/envsci-citations/envsci-writing),保证本机即时可用。

---

## 4. 验证(证据先行)

1. `py skills/envsci-citations/scripts/check_references.py --selftest` → OK(含新 `--manuscript-year` 前向引用样例)。
2. `py skills/envsci-slides/scripts/ga_canvas.py --selftest` → 生成样例 GA,断言尺寸/dpi 通过。
3. `py skills/envsci-slides/scripts/deck_build.py --selftest` → 生成样例 .pptx,断言页数/notes 通过(先 `pip install -r .../requirements.txt`)。
4. 路径/命令核对:所有改动 SKILL.md 的指针、references 文件名、脚本路径可达。
5. 人工抽测:用一段含锚点 + 一处前向引用 + 一处过时限值的样例,跑 `envsci-citations` integrity,确认四类新判据触发正确。
6. 实测产出 1 张样例 GA(elsevier-ga 预设)+ 1 份样例 deck(conference 模板)。

## 5. 交付物

- 3 个改动 skill(enviro-paper / envsci-citations / envsci-writing)+ 1 个新 skill(envsci-slides)+ manifests/文档/版本。
- dev 仓库 git 提交(分支:不在 main 直接改 → 新建 feature 分支,见计划阶段);本机 `~/.claude/skills/` 同步。
- **收尾**:用 2.1.0 形态**重做** envsci-paper-skill vs academic-research-skills vs nature-skills 对比表(本轮指定的最后一步)。

## 6. 不纳入 / 可选(默认不做,用户确认再做)

- 版本号 tag、推送 GitHub、发 Release 资产 zip。
- envsci-slides ③ 扩展(poster / lay summary)。

## 7. 受影响文件清单(driving the plan)

**改:**
- `skills/enviro-paper/SKILL.md`
- `skills/envsci-citations/SKILL.md`
- `skills/envsci-citations/references/citations-and-integrity.md`
- `skills/envsci-citations/scripts/check_references.py`
- `skills/envsci-writing/SKILL.md`
- `skills/envsci-writing/references/writing.md`
- `.claude-plugin/marketplace.json`、`.claude-plugin/plugin.json`、`.codex-plugin/plugin.json`
- `install.md`、`README.md`、`CHANGELOG.md`

**新建:**
- `skills/envsci-slides/SKILL.md`
- `skills/envsci-slides/references/slides.md`
- `skills/envsci-slides/scripts/ga_canvas.py`、`deck_build.py`、`requirements.txt`

**同步:** `~/.claude/skills/`(envsci-slides 新增 + enviro-paper/envsci-citations/envsci-writing 覆盖)
