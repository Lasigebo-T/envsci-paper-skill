# enviro-paper

**End-to-end authoring skill for environmental-science field-sampling and monitoring papers** —
from raw sampling data to a submission-ready manuscript with reviewer-response letters.

This is a single router-style skill: a lean `SKILL.md` dispatches to one of seven on-demand
reference files plus two runnable scripts. It fuses the **rigor** of
[academic-research-skills](https://github.com/imbad0202/academic-research-skills) (integrity gates,
anti-fabrication citation checking) with the **concrete outputs** of
[nature-skills](https://github.com/Yuan1z0825/nature-skills) (publication figures, section-aware
writing, response letters), tailored to environmental science.

## What it does

| Stage | Capability |
|-------|------------|
| Data / QA-QC | LOD/LOQ, recoveries, blanks, RSD; **non-detect handling** (substitution / KM / ROS / MLE); units & dry/wet basis |
| Statistics | normality + transforms, ANOVA/Tukey vs Kruskal–Wallis/Dunn, Spearman/Pearson, PCA/HCA/PERMANOVA, source apportionment (PMF, APCS-MLR) |
| Indices & risk | **Igeo, EF, CF/PLI, Hakanson Er/RI, Nemerow, WQI**, and **US-EPA health risk HQ/HI/CR** — each with formula, canonical reference, threshold table, and a worked example |
| Figures | publication-quality `matplotlib` figures (site maps, boxplots, correlation heatmaps, PCA biplots, spatial scatter, stacked composition) via `scripts/envsci_style.py` |
| Writing | section-aware IMRaD drafting + Nature-style polishing + Chinese-author dual-output |
| Citations | journal citation styles + **anti-fabrication integrity gates** (no invented DOIs) backed by `scripts/check_references.py` |
| Review | 3-reviewer pre-submission simulation + point-by-point reviewer-response letters |
| Journal-fit | scope/format guide for STOTEN, Water Research, ES&T, Environmental Pollution, JHM, ESPR, and more |

## Modes

Triggered by natural language (English **or** Chinese). Examples:

| Mode | Say something like… |
|------|---------------------|
| `full-pipeline` | "take my sampling data to a manuscript" · 「把这批数据写成论文」 |
| `plan` | "help me scope this study / find the gap" · 「帮我规划 / 研究缺口」 |
| `data-analysis` | "analyze my sampling data, QA/QC, pollution indices" · 「分析采样数据、质控、污染指数、健康风险」 |
| `figures` | "make a PCA biplot / site map / boxplot" · 「画图 / 期刊配图」 |
| `write <section>` | "write the introduction / methods / discussion" · 「写引言 / 方法 / 讨论」 |
| `polish` | "polish my English / fix translationese" · 「润色 / 去翻译腔」 |
| `citations` | "check references / verify DOIs" · 「核对参考文献」 |
| `integrity` | "check for fabricated citations" · 「查有没有编造的文献」 |
| `review` | "peer-review simulation" · 「模拟审稿」 |
| `response` | "point-by-point rebuttal letter" · 「逐条回复审稿意见」 |
| `journal-fit` | "which journal / format for STOTEN" · 「投哪个期刊 / 按STOTEN格式」 |

## Layout

```text
enviro-paper/
├── SKILL.md                           # lean router: pipeline, mode dispatch, quality gates
├── references/
│   ├── research-and-literature.md     # literature search + anti-hallucination sourcing
│   ├── data-analysis.md               # QA/QC, non-detects, stats, indices, risk (env-sci core)
│   ├── figures.md                     # publication-figure rules + how to use envsci_style.py
│   ├── writing.md                     # section-aware IMRaD writing + polishing
│   ├── citations-and-integrity.md     # citation styles + blocking integrity gates
│   ├── review-and-response.md         # reviewer simulation + response letters
│   └── journals.md                    # target-journal scope/format guide
└── scripts/
    ├── envsci_style.py                # matplotlib publication style + env-sci plotters
    ├── check_references.py            # offline reference-integrity linter (stdlib only)
    └── requirements.txt               # matplotlib, numpy, pandas (scipy/geo optional)
```

## Scripts

Both scripts are runnable on their own. **On Windows, if `python` opens the Microsoft Store, use `py`.**

```bash
# Generate one demo of every figure type (smoke test the install/API)
python scripts/envsci_style.py --demo all

# Lint a reference list for structural fabrication signatures (exit 1 on any HIGH issue)
python scripts/check_references.py refs.bib
```

`check_references.py` is **offline and stdlib-only** — it flags malformed/duplicate DOIs, missing
fields, and impossible years. Online existence/triangulation of every reference is done by the agent
(via web fetch + literature MCP tools), per `references/citations-and-integrity.md`.

## License

MIT — see [LICENSE](../../LICENSE).
