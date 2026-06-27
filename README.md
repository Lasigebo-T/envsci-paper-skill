<div align="center">

# 🌍 envsci-paper-skill — environmental-science paper skill collection

**A family of independently-selectable Agent Skills** for environmental-science field-sampling /
monitoring papers — pick one for a single task, or run the umbrella for the whole
data → manuscript → reviewer-response pipeline. For **Claude Code** and **Codex**.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Version](https://img.shields.io/badge/Version-2.1.0-blue.svg)](CHANGELOG.md)
[![Skills](https://img.shields.io/badge/Skills-10-brightgreen.svg)](#the-collection)
[![Works with](https://img.shields.io/badge/Works_with-Claude_Code_%7C_Codex-1F7A4D.svg)](#installation)
[![Standard](https://img.shields.io/badge/Standard-Agent_Skills-blueviolet.svg)](https://agentskills.io/)

</div>

> **v2.1.0 — now a collection of 10.** The former single `enviro-paper` skill is split into **9 standalone
> function skills + 1 umbrella orchestrator**, so you can invoke exactly the capability you need
> (e.g. just `envsci-figures`, just `envsci-ideate`) without loading the whole pipeline. It also
> composes with the separate **[scipilot-figure-skill](https://github.com/Haojae/scipilot-figure-skill)**
> for general figure methodology. v2.1.0 adds **`envsci-slides`** for graphical abstracts and
> presentation decks, and extends **`envsci-citations`** with source-anchor verification and
> temporal-integrity auditing.

---

## The collection

| Skill | What it does | Say something like… |
|-------|--------------|---------------------|
| **`enviro-paper`** (umbrella) | Orchestrates the full 10-stage pipeline with 2 blocking integrity gates; routes each stage to the right function skill. **Use only for end-to-end.** | "把这批采样数据写成论文" · "take my data all the way to a manuscript" |
| **`envsci-ideate`** | Seed papers + your data → recent **verified** literature → ranked, grounded innovation points + prior-art "scooped" check + honest novelty rating | "找创新点 / 研究空白" · "what's novel here, has it been done" |
| **`envsci-litsearch`** | Literature discovery + anti-hallucination sourcing; databases/MCP routing; log every source with a verified DOI before use | "查文献 / 文献综述" · "find evidence for this claim" |
| **`envsci-data`** | QA/QC, non-detects, the right statistical test, multivariate, and pollution/risk indices (Igeo/EF/PLI/Hakanson/WQI/HQ-HI-CR) with formulas + worked examples | "分析采样数据 / 质控 / 污染指数 / 健康风险" |
| **`envsci-figures`** | Env-sci publication figures (site maps, boxplots, heatmaps, PCA biplots, spatial scatter, stacked bars) + `envsci_style.py`; **composes with scipilot** | "画箱线图 / PCA / 点位图 / 期刊配图" |
| **`envsci-writing`** | Section-aware IMRaD drafting + Nature-style polishing + Chinese-author → English | "写引言/方法/讨论 / 润色 / 去翻译腔" |
| **`envsci-citations`** | Citation formatting to journal style + **blocking anti-fabrication integrity gate** + `check_references.py` | "核对参考文献 / 查 DOI / 查有没有编造的文献" |
| **`envsci-review`** | 3-reviewer pre-submission simulation + point-by-point reviewer-response letters | "模拟审稿 / 逐条回复审稿意见" |
| **`envsci-journals`** | Target-journal scope/format guide + journal-fit decision | "投哪个期刊 / 按 STOTEN 格式" |
| **`envsci-slides`** | Graphical abstract + presentation deck (GA/TOC + .pptx with speaker notes) | "做图摘 / 做汇报幻灯片 / conference deck" |

➕ **Separate companion (install on its own):**
**[scipilot-figure-skill](https://github.com/Haojae/scipilot-figure-skill)** — a general scientific-figure
advisor (data profiling, chart selection, visual-QA closed loop, journal specs, Chinese-font fixes).
`envsci-figures` composes with it for the general figure methodology and adds the env-sci specifics.

---

## Installation

Each skill is one folder centred on `SKILL.md` (+ `references/` and, where relevant, `scripts/`).
Installing the whole repo gives you **all 10 skills**, each independently selectable.

### 1. Claude Code

**Plugin marketplace (whole collection):**
```bash
claude plugin marketplace add Lasigebo-T/envsci-paper-skill
claude plugin install enviro-paper@envsci-paper-skill
```

**Manual (all 10, always works):**
```bash
git clone https://github.com/Lasigebo-T/envsci-paper-skill.git
mkdir -p ~/.claude/skills
cp -R envsci-paper-skill/skills/* ~/.claude/skills/
# install one skill only? copy just that folder, e.g.:
cp -R envsci-paper-skill/skills/envsci-figures ~/.claude/skills/
```

**Windows (PowerShell):**
```powershell
git clone https://github.com/Lasigebo-T/envsci-paper-skill.git
New-Item -ItemType Directory -Force "$HOME\.claude\skills" | Out-Null
Copy-Item -Recurse -Force ".\envsci-paper-skill\skills\*" "$HOME\.claude\skills\"
```

### 2. Codex

```bash
codex plugin marketplace add https://github.com/Lasigebo-T/envsci-paper-skill --ref main
codex plugin add enviro-paper@envsci-paper-skill
# or manual:
git clone https://github.com/Lasigebo-T/envsci-paper-skill.git
mkdir -p ~/.codex/skills && cp -R envsci-paper-skill/skills/* ~/.codex/skills/
```

### 3. The figure companion (recommended)
```bash
git clone https://github.com/Haojae/scipilot-figure-skill.git
cp -R scipilot-figure-skill ~/.claude/skills/      # or ~/.codex/skills/
```

> **Windows Python note:** if `python` opens the Microsoft Store, use the `py` launcher to run the scripts.

---

## How to use

- **Single task** → just describe it; the right skill auto-triggers, or invoke it explicitly
  (`/envsci-figures`, `/envsci-ideate`, …). Each has a distinct, non-colliding trigger description.
- **Whole paper** → ask for the full pipeline; the **`enviro-paper`** umbrella walks the 10 stages and
  hands each to the right function skill, enforcing the two blocking anti-fabrication integrity gates.

```
SCOPE(ideate+litsearch) → DATA/STATS(data) → FIGURES(figures+scipilot) → WRITE/POLISH(writing)
  → CITATIONS → ⟦I-1 gate⟧ → REVIEW → REVISE → ⟦I-2 gate⟧ → RESPONSE/JOURNAL-FIT
```

---

## Scripts (run standalone; tested on Python 3.14 / matplotlib 3.10 / numpy 2.3 / pandas 2.3)

```bash
python skills/envsci-figures/scripts/envsci_style.py --demo all       # 12 demo figures
python skills/envsci-citations/scripts/check_references.py refs.bib   # integrity lint; exit 1 on HIGH
```
`envsci_style.py` needs matplotlib+numpy+pandas (see `skills/envsci-figures/scripts/requirements.txt`);
`check_references.py` is stdlib-only.

---

## Design & attribution

Fuses two open-source skill collections, plus an environmental-science analytical layer, plus the
scipilot figure methodology:
- **[academic-research-skills](https://github.com/imbad0202/academic-research-skills)** (MIT) — rigor backbone: integrity gates, anti-fabrication citations, HITL.
- **[nature-skills](https://github.com/Yuan1z0825/nature-skills)** (MIT) — concrete-output backbone: publication figures, section-aware writing, response letters.
- **[scipilot-figure-skill](https://github.com/Haojae/scipilot-figure-skill)** — general scientific-figure advisor that `envsci-figures` composes with.
- **Environmental-science layer (this repo):** QA/QC + non-detects, correct env stats, and the full pollution/ecological/health-risk index suite (Igeo · EF · CF/PLI · Hakanson Er/RI · Nemerow · WQI · EPA HQ/HI/CR) with canonical references and worked examples.

## License

[MIT](LICENSE) © 2026 Lasigebo-T. Upstream collections are likewise MIT-licensed; scipilot-figure-skill is a separate project under its own license.
