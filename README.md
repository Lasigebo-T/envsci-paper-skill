<div align="center">

# 🌍 envsci-paper-skill

**Turn an environmental-science field-sampling dataset into a submission-ready paper.**

A single, self-contained Agent Skill for **Claude Code** and **Codex** that walks an
environmental-science *monitoring / sampling* study from raw data → QA/QC → statistics &
pollution-risk indices → publication figures → IMRaD writing → citation integrity →
peer-review simulation → reviewer-response letter → target-journal fit.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Version](https://img.shields.io/badge/Version-1.0.0-blue.svg)](CHANGELOG.md)
[![Works with](https://img.shields.io/badge/Works_with-Claude_Code_%7C_Codex-1F7A4D.svg)](#installation)
[![Standard](https://img.shields.io/badge/Standard-Agent_Skills-blueviolet.svg)](https://agentskills.io/)
[![Scripts](https://img.shields.io/badge/Scripts-tested-brightgreen.svg)](#scripts)

</div>

> **Why this exists.** Generic "write my paper" tools don't know what an environmental-science
> paper actually needs: non-detect handling, dry-vs-wet-weight units, recovery/blank QA/QC,
> the right statistical test for skewed concentration data, and the pollution & risk indices
> (Igeo, EF, PLI, Hakanson, WQI, EPA HQ/HI/CR) reviewers expect — with the *correct* formulas.
> `enviro-paper` bakes all of that in, then adds an anti-fabrication citation gate and a
> pre-submission reviewer simulation on top.

---

## What's included

One router-style skill — **`enviro-paper`** — = a lean `SKILL.md` + 7 on-demand references + 2 runnable scripts:

| File | Purpose |
|------|---------|
| `SKILL.md` | Lean router: the 10-stage pipeline, the mode-dispatch table, and the quality gates. |
| `references/research-and-literature.md` | Literature search (Crossref/OpenAlex/Semantic Scholar/PubMed) + anti-hallucination sourcing. |
| `references/data-analysis.md` | **The env-sci core**: QA/QC, non-detects, statistics, and every pollution/risk index with formula + reference + worked example. |
| `references/figures.md` | Publication-figure rules + how to drive `envsci_style.py`. |
| `references/writing.md` | Section-aware IMRaD drafting + Nature-style polishing + Chinese-author workflow. |
| `references/citations-and-integrity.md` | Journal citation styles + two **blocking** integrity gates. |
| `references/review-and-response.md` | 3-reviewer simulation + point-by-point response letters. |
| `references/journals.md` | Scope/format guide for the major environmental journals. |
| `scripts/envsci_style.py` | `matplotlib` publication style + env-sci plotters (site map, boxplot, heatmap, PCA biplot, spatial scatter, stacked composition). |
| `scripts/check_references.py` | Offline, stdlib-only reference-integrity linter (exit 1 on any HIGH issue). |

---

## Installation

`enviro-paper` is a reusable instruction bundle centred on `SKILL.md`. **Copy the whole
`skills/enviro-paper/` folder**, not just `SKILL.md` — the workflow depends on `references/`
and `scripts/`.

### 1. Codex

**Plugin marketplace (bundle install):**

```bash
codex plugin marketplace add https://github.com/Lasigebo-T/envsci-paper-skill --ref main
codex plugin add enviro-paper@envsci-paper-skill
```

**Manual local-skill install (always works):**

```bash
git clone https://github.com/Lasigebo-T/envsci-paper-skill.git
cd envsci-paper-skill
mkdir -p ~/.codex/skills
cp -R skills/enviro-paper ~/.codex/skills/
```

Restart Codex, then ask naturally, e.g. `Analyze my sampling data and compute pollution indices.`

### 2. Claude Code

**Plugin marketplace (bundle install):**

```bash
claude plugin marketplace add Lasigebo-T/envsci-paper-skill
claude plugin install enviro-paper@envsci-paper-skill
```

**Manual user-skill install (always works):**

```bash
git clone https://github.com/Lasigebo-T/envsci-paper-skill.git
mkdir -p ~/.claude/skills
cp -R envsci-paper-skill/skills/enviro-paper ~/.claude/skills/
```

Start a new Claude Code session; the skill auto-triggers on environmental-science requests
(or invoke it explicitly with `/enviro-paper`).

> **Windows (PowerShell)** — use `Copy-Item` and the `py` launcher:
> ```powershell
> git clone https://github.com/Lasigebo-T/envsci-paper-skill.git
> New-Item -ItemType Directory -Force "$HOME\.claude\skills" | Out-Null
> Copy-Item -Recurse -Force ".\envsci-paper-skill\skills\enviro-paper" "$HOME\.claude\skills\"
> # run scripts with:  py skills\enviro-paper\scripts\envsci_style.py --demo all
> ```

### 3. Other agents / manual

The portable unit is the `skills/enviro-paper/` directory. Copy it into your prompt
library, keep `SKILL.md` + `references/` + `scripts/` together, and adapt the frontmatter
to your agent's native format if needed.

---

## Quick start

Just describe what you need — in English or Chinese. The skill detects intent and loads the
right reference.

| You want… | Try saying |
|-----------|-----------|
| End-to-end paper | "take my sampling data to a manuscript" · 「把这批数据写成论文」 |
| Data analysis + indices | "analyze my data, QA/QC, pollution indices, health risk" · 「分析采样数据、质控、污染指数、健康风险」 |
| A figure | "make a PCA biplot / site map / boxplot by site" · 「画 PCA 双标图 / 点位图 / 箱线图」 |
| Write a section | "write the introduction / methods / discussion" · 「写引言 / 方法 / 讨论」 |
| Polish English | "polish this paragraph, fix translationese" · 「润色这段、去翻译腔」 |
| Citation integrity | "check my references for fabricated DOIs" · 「核对参考文献有没有编造」 |
| Peer review | "simulate reviewers on my manuscript" · 「模拟审稿」 |
| Response letter | "draft a point-by-point rebuttal" · 「逐条回复审稿意见」 |
| Journal choice | "which journal fits / format for STOTEN" · 「投哪个期刊 / 按 STOTEN 格式」 |

---

## The pipeline & quality gates

The full state machine runs end-to-end only in `full-pipeline` mode; every other mode is a
single-stage entry point.

```
SCOPE → DATA/QAQC → STATS/INDICES → FIGURES → WRITE → POLISH → CITATIONS
   → ⟦I-1 integrity gate⟧ → REVIEW → REVISE → RE-REVIEW → ⟦I-2 integrity gate⟧ → RESPONSE/FINALIZE
```

Non-negotiable gates: **D** (data validity) · **S** (stats/formula correctness) · **F** (figure QA) ·
**I-1 / I-2** (two *blocking* anti-fabrication integrity gates, run before review and again, fresh,
after all revision). Plus iron rules: no fabricated citations/DOIs, every value traces to the data,
units + dry/wet basis always stated, declared non-detect handling, colorblind-safe figures, and a
mandatory comparison to environmental quality standards.

---

## Scripts

Both scripts run standalone (tested on Python 3.14, matplotlib 3.10, numpy 2.3, pandas 2.3).

```bash
python scripts/envsci_style.py --demo all      # 12 demo figures (smoke-test the API)
python scripts/check_references.py refs.bib    # structural integrity lint; exit 1 on HIGH issues
```

- `envsci_style.py` requires **matplotlib + numpy + pandas** (scipy / geo backends optional, lazily imported). See `scripts/requirements.txt`.
- `check_references.py` is **stdlib-only** (no install). It lints *structure*; live existence checks are done by the agent via web fetch + literature MCP tools.
- **Windows:** if `python` opens the Microsoft Store, use the `py` launcher.

---

## Design & attribution

`enviro-paper` was built by studying and fusing two excellent open-source skill collections,
then adding an environmental-science analytical layer neither provides:

- **[academic-research-skills](https://github.com/imbad0202/academic-research-skills)** (MIT) —
  the *rigor backbone*: multi-stage pipeline, two blocking integrity gates, anti-fabrication
  citation verification, human-in-the-loop checkpoints, anti-sycophancy peer review.
- **[nature-skills](https://github.com/Yuan1z0825/nature-skills)** (MIT) — the *concrete-output
  backbone*: publication-grade figures, section-aware writing, quantified polishing rules,
  3-referee simulation, reviewer-response letters, Chinese-author dual-output.
- **Environmental-science layer (new in this repo):** QA/QC + non-detect handling, the correct
  statistical tests for environmental data, and the full pollution/ecological/health-risk index
  suite (Igeo · EF · CF/PLI · Hakanson Er/RI · Nemerow · WQI · EPA HQ/HI/CR) with canonical
  references, threshold tables, and worked examples.

Index formulas and thresholds were cross-checked against their canonical sources (Müller 1969,
Tomlinson 1980, Hakanson 1980, US-EPA RAGS), and both scripts were executed to confirm they run.

---

## Contributing

Issues and PRs welcome — new index/figure types, journal profiles, and language fixes especially.
Keep `SKILL.md` lean (it routes; deep how-to lives in `references/`), and keep both scripts
dependency-light and runnable.

## License

[MIT](LICENSE) © 2026 Lasigebo-T. The two upstream skill collections it draws from are likewise MIT-licensed.
