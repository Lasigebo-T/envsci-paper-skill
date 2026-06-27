# envsci-paper-skill v2.1.0 — 三方对比(刷新版)

日期:2026-06-28 · 对比对象:[academic-research-skills](https://github.com/imbad0202/academic-research-skills)(ARS,全学科通用)、[nature-skills](https://github.com/Yuan1z0825/nature-skills)(Nature/CNS 风格通用)。

## 本次 v2.1.0 闭合的差距

| 能力 | v2.0.0 | v2.1.0 | 此前归谁独有 |
|---|---|---|---|
| 引文页/段/句锚点 | ❌ | ✅ envsci-writing 发出 + envsci-citations 核验(`ANCHOR_VERIFIED/UNRESOLVED/MISMATCH/MISSING`) | ARS(Three-Layer Citation Emission) |
| 时间一致性/时代错置审计 | ❌ | ✅ Phase C5(前向引用 / 过时标准版本 / 时态错配)+ `check_references.py --manuscript-year` | ARS(Temporal Integrity Audit) |
| 论文→可视化产物 | ❌ | ✅ 新 sibling envsci-slides(GA/TOC + 汇报 deck) | nature-skills(paper2ppt) |

## 三方对比表(v2.1.0)

| 维度 | **envsci-paper-skill v2.1.0** | Academic Research Skills | nature-skills |
|---|---|---|---|
| 目标领域 | ✅ **环境野外采样/监测专精** | 全学科通用 | Nature/CNS 风格,跨学科 |
| 架构 | 总伞 + **9** 功能 skill | Pipeline + 4 skill | 11 个并列 skill |
| 数据统计+质控 | ✅✅ LOD/非检出/检验选择/PCA-PERMANOVA | ❌ | ❌ 仅 FAIR |
| 污染/风险指数 | ✅✅ Igeo/EF/CF/PLI/Er-RI/内梅罗/WQI/HQ-HI-CR | ❌ | ❌ |
| 源解析 | ✅ APCS-MLR / EPA PMF | ❌ | ❌ |
| 科研出图 | ✅✅ 点位图(CRS+比例尺+指北针)/显著性字母/Piper 等 | 通用图 + VLM 核验 | 通用 Python/R |
| **图文摘要 GA / TOC** | ✅ **新增 envsci-slides:ga_canvas.py 按刊 px/dpi 出 SVG+PNG** | ❌(只做正文图) | 部分(figure skill) |
| **汇报 deck** | ✅ **新增 deck_build.py:.pptx + 备注,会议/组会/答辩模板** | ❌ | ✅ paper2ppt |
| 论文→专利 | ❌(未做) | ❌ | ✅ paper-to-patent |
| 写作 | ✅ IMRaD + 单位/dw-ww + 知识隔离 + **高危声明锚点** | 强(12-agent) | 强 |
| 选刊 | ✅ 12 本环境刊 范围/字数/GA/IF | ⚠️ 偏 IS/医疗 | ❌(锁 Nature) |
| 引文格式 | ✅ Elsevier/ACS/Springer | APA/Chicago/MLA/IEEE/Vancouver | DOI 核验 |
| 反杜撰门禁 | ✅ 2 道 BLOCKING + 三角核验 + **锚点核验** + **时间审计** + 领域公式/限值核验 | ✅✅ 最齐全(存在性闸/三层锚点/忠实度审计/时间审计/失败模式清单) | ⚠️ 基础(DOI + Nature 内容) |
| 模拟审稿 | ✅ 3 审 + 魔鬼代言 + 综合 + 反谄媚 | ✅ EIC+3审+魔鬼+跨模型 | ✅ 3 审 + 综合 |
| 回复信 | ✅ 逐条、不编造 | ✅ rebuttal-audit | ✅ nature-response |
| 双语 | ✅ 中英(中文作者优化) | 英 + 繁中摘要 | ✅ 中英对照 |

## 结论

- **决定性优势仍在领域纵深**:污染/风险指数、源解析、领域出图+地图要素、领域选刊、领域级诚信核查——两个通才包在这些格仍是空的。
- **v2.1.0 把两处"对手独有"补平**:引文锚点 + 时间一致性审计(原 ARS 独有),论文→GA/汇报(原 nature-skills 独有)。
- **诚实保留的落后处**:① ARS 的诚信子项仍更"全谱"(如 claim-faithfulness 定位、material passport、跨模型审稿 agent)——我们补了锚点+时间审计,缩小了差距但未完全追平;② nature-skills 仍有 **论文→专利**,我们未做(当初 YAGNI 砍掉);③ ARS/nature 是通才,换领域即用,我们是垂直专精(刻意取舍)。

**一句话**:通才包帮你"把论文写出来",envsci-paper-skill 帮你"把环境采样论文写对、写到能投 STOTEN",且 v2.1.0 后在引文诚信细粒度与投稿可视化产物上不再落后一档。
