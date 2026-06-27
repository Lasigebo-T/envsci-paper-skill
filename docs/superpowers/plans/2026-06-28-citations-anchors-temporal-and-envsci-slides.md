# 引文锚点+时间审计 与 envsci-slides 实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 给 envsci-citations 增加页/段/句锚点核验与时间一致性审计、给 envsci-writing 增加高危声明锚点规则,并新建 envsci-slides(GA + 汇报 deck),作为 envsci-paper-skill v2.1.0 发布。

**Architecture:** 单一来源是 dev 仓库 `envsci-paper-skill/`(已在分支 `feature/v2.1.0-anchors-temporal-slides`)。诚信新能力以 Claude 推理门禁形式写入 `references/citations-and-integrity.md`,脚本只加一项离线结构筛(`--manuscript-year`)。envsci-slides 贴 cluster 模板(SKILL.md + references/slides.md + scripts/),脚本驱动混合(matplotlib 出 GA、python-pptx 出 deck),且**可独立安装**(调色板内嵌,不 import 兄弟 skill)。改完同步到 `~/.claude/skills/`。

**Tech Stack:** Markdown skill docs;Python 3.9+(stdlib)`check_references.py`;`matplotlib`(GA)、`python-pptx`(deck)。Windows 用 `py` 启动器(非 `python`)。

**前置说明(所有任务通用):**
- 工作目录:`D:\Users\SJS\桌面\CC4paper\(第一次采样）2025秋季采样\envsci-paper-skill`
- 已在分支 `feature/v2.1.0-anchors-temporal-slides`;每个任务末尾 commit;不切 main、不 push(除非用户最后要求)。
- Markdown 文档任务没有单元测试,其"测试"= 先 `Grep` 确认目标串不存在 → 编辑 → `Grep` 确认目标串已存在(verification-by-grep)。
- 脚本任务用脚本内置 `--selftest` 作为测试。

---

## File Structure(决策锁定)

**修改:**
- `skills/envsci-citations/scripts/check_references.py` — 加 `--manuscript-year` 前向引用筛 + selftest
- `skills/envsci-citations/references/citations-and-integrity.md` — Phase B 锚点核验、Phase C5 时间审计、§6 版本时效、§9/§10/§11/§2 更新
- `skills/envsci-citations/SKILL.md` — integrity 模式描述 + 触发词
- `skills/envsci-writing/references/writing.md` — 高危声明锚点规则
- `skills/envsci-writing/SKILL.md` — 指针 + 触发词
- `skills/enviro-paper/SKILL.md` — 登记第 9 个 function skill + pipeline Stage 10
- `.claude-plugin/marketplace.json`、`.claude-plugin/plugin.json`、`.codex-plugin/plugin.json` — version 2.1.0 + 描述
- `install.md`、`README.md`、`CHANGELOG.md`

**新建:**
- `skills/envsci-slides/SKILL.md`
- `skills/envsci-slides/references/slides.md`
- `skills/envsci-slides/scripts/ga_canvas.py`、`deck_build.py`、`requirements.txt`

---

## Task 1: check_references.py 加 `--manuscript-year` 前向引用筛(TDD)

**Files:**
- Modify: `skills/envsci-citations/scripts/check_references.py`(`check_references()` ~L481、`_check_year` 后 ~L538、`run_selftest` ~L679、`main` argparse ~L772、调用 ~L825)

- [ ] **Step 1: 先加失败的 selftest 断言(test-first)**

在 `run_selftest()` 中,现有 7 条 refs 的断言块之后、`detect_format` 断言之前,插入:

```python
    # Forward reference (cited year > manuscript year) -> HIGH TEMPORAL_FORWARD_REF.
    fwd_refs = [
        Reference("future", "Ahead, Z.", "Cited from the future", "2027", "STOTEN", "10.1016/j.stoten.2027.1"),
        Reference("okpast", "Past, Y.", "A normal prior", "2019", "Water Res.", "10.1016/j.watres.2019.2"),
    ]
    fwd_issues = check_references(fwd_refs, fmt="bibtex", manuscript_year=2025)
    fwd_codes = Counter(i.code for i in fwd_issues)
    assert fwd_codes["TEMPORAL_FORWARD_REF"] == 1, fwd_codes
    # Without manuscript_year, no temporal check fires.
    none_issues = check_references(fwd_refs, fmt="bibtex")
    assert Counter(i.code for i in none_issues)["TEMPORAL_FORWARD_REF"] == 0, none_issues
```

- [ ] **Step 2: 运行确认失败**

Run: `py skills/envsci-citations/scripts/check_references.py --selftest`
Expected: FAIL —`TypeError: check_references() got an unexpected keyword argument 'manuscript_year'`(功能未实现)。

- [ ] **Step 3: 实现功能**

(a) 改 `check_references` 签名与循环(~L481–501):

```python
def check_references(
    refs: List[Reference],
    fmt: str,
    min_year: int = DEFAULT_MIN_YEAR,
    max_year: int = DEFAULT_MAX_YEAR,
    manuscript_year: Optional[int] = None,
) -> List[Issue]:
    """Run the full structural check suite, returning a flat list of Issues."""
    issues: List[Issue] = []

    # Per-entry checks: DOI validity, year plausibility, required fields.
    for ref in refs:
        issues.extend(_check_doi(ref))
        issues.extend(_check_year(ref, min_year, max_year))
        if manuscript_year is not None:
            issues.extend(_check_forward_reference(ref, manuscript_year))
        if fmt != "md":
            issues.extend(_check_required_fields(ref))

    # List-level checks: duplicate DOIs, duplicate titles.
    issues.extend(_check_duplicate_dois(refs))
    issues.extend(_check_duplicate_titles(refs))

    return issues
```

(b) 在 `_check_year` 函数之后(~L538)新增:

```python
def _check_forward_reference(ref: Reference, manuscript_year: int) -> List[Issue]:
    """Cited source dated after the manuscript's writing year = impossible basis."""
    if not ref.year:
        return []
    m = re.search(r"(\d{4})", ref.year)
    if not m:
        return []  # unparseable year already flagged by _check_year
    y = int(m.group(1))
    if y > manuscript_year:
        return [
            Issue(
                "HIGH",
                "TEMPORAL_FORWARD_REF",
                ref.key,
                f"cited year {y} is after manuscript year {manuscript_year} "
                "(forward reference / impossible citation)",
            )
        ]
    return []
```

(c) `main()` argparse:在 `--max-year` 块之后(~L772)加:

```python
    parser.add_argument(
        "--manuscript-year",
        type=int,
        default=None,
        help="Manuscript writing year; enables forward-reference check "
        "(any cited year > this is flagged TEMPORAL_FORWARD_REF).",
    )
```

(d) `main()` 调用处(~L825)改为传入:

```python
    issues = check_references(
        refs, fmt, min_year=args.min_year, max_year=args.max_year,
        manuscript_year=args.manuscript_year,
    )
```

- [ ] **Step 4: 运行确认通过**

Run: `py skills/envsci-citations/scripts/check_references.py --selftest`
Expected: PASS —打印 `selftest: OK`。

- [ ] **Step 5: 冒烟验证 CLI 退出码**

Run(临时文件,bash):
```bash
printf '@article{f, title={X}, year={2030}, author={A}, journal={J}, doi={10.1/x}}\n' > /tmp/r.bib
py skills/envsci-citations/scripts/check_references.py /tmp/r.bib --manuscript-year 2025; echo "exit=$?"
```
Expected: 报告含 `TEMPORAL_FORWARD_REF`,`exit=1`。

- [ ] **Step 6: Commit**

```bash
git add skills/envsci-citations/scripts/check_references.py
git commit -m "feat(citations): add --manuscript-year forward-reference screen to check_references"
```

---

## Task 2: citations-and-integrity.md — Phase B 锚点核验

**Files:**
- Modify: `skills/envsci-citations/references/citations-and-integrity.md`(Phase B 区,~L82–138 之间)

- [ ] **Step 1: 读文件定位 Phase B**

Read `skills/envsci-citations/references/citations-and-integrity.md`,找到 §4 Phase B(Citation context)小节末尾。

- [ ] **Step 2: 在 Phase B 末尾插入锚点核验子节**

```markdown
#### B-anchor — Source-anchor verification (high-risk claims)

A **high-risk claim** is (i) any value attributed to a source (concentration,
recovery, index value, guideline/threshold, literature statistic), (ii) any
direct quotation, or (iii) any specific contested conclusion attributed to a
source. Per **envsci-writing**, every high-risk claim MUST carry a source anchor:

- page: `[@key, p. 42]` / range `[@key, pp. 42–45]`
- section: `[@key, §3.2]`
- quote: `[@key, "verbatim ≤25 words"]` (the quoted words also appear in prose)

During the online source lookup (§3), for each high-risk claim:
1. Resolve the anchor location — page within the source's page range; the
   section exists; the quoted text is present at/near the anchor.
2. Confirm the anchored location actually supports the claim (Phase B context).

Verdicts:
- `ANCHOR_VERIFIED` — location resolves and supports the claim.
- `ANCHOR_UNRESOLVED` — source full text not accessible; record as NOTE (not a
  fail by itself); flag for manual check.
- `ANCHOR_MISMATCH` — quote not found, or page/section out of range → **FAIL**.
- `ANCHOR_MISSING` — a high-risk claim carries no anchor → **FAIL at I-2**
  (SERIOUS at I-1).

Anchors are authoring/audit metadata. At formatting (§7), keep page numbers for
direct quotations per journal style; for paraphrased claims the anchor stays in
the audit trail and is not printed.
```

- [ ] **Step 3: 验证**

Run: `Grep "ANCHOR_MISMATCH" skills/envsci-citations/references/citations-and-integrity.md`
Expected: 命中(锚点子节已写入)。

- [ ] **Step 4: Commit**

```bash
git add skills/envsci-citations/references/citations-and-integrity.md
git commit -m "feat(citations): add Phase B source-anchor verification for high-risk claims"
```

---

## Task 3: citations-and-integrity.md — Phase C5 时间审计 + §6/§2/§9/§10/§11

**Files:**
- Modify: `skills/envsci-citations/references/citations-and-integrity.md`(§4 Phase C 区、§6、§2、§9、§10、§11)

- [ ] **Step 1: 在 §4 Phase C 之后插入 Phase C5**

```markdown
### Phase C5 — Temporal integrity (anachronism audit)

Run alongside Phase C. Three checks:

- **T1 Forward reference / impossible citation.** A cited source dated after the
  manuscript's writing year, or a logically impossible timeline (a priority
  claim predating its own cited basis). Verdict `TEMPORAL_FORWARD_REF`
  (HIGH/SERIOUS). Offline pre-screen: `check_references.py --manuscript-year YYYY`.
- **T2 Superseded standard / guideline edition.** A claim citing an outdated
  edition of a standard or a value since revised — WHO/EPA/GB guideline values,
  IRIS RfD/SF, SQG TEL–PEL / ERL–ERM. Cross-check the *current* edition (extends
  §6). Verdict `TEMPORAL_SUPERSEDED`; severity scales with impact (SERIOUS if the
  revised value flips an exceedance / risk conclusion).
- **T3 Epoch / tense mismatch.** Claims using "to date / most recent / first to
  report / currently" that cite stale sources or are contradicted by earlier
  literature (link to **envsci-ideate** scooped-check). Verdict
  `TEMPORAL_EPOCH_MISMATCH` (NOTE–MEDIUM); reason in Phase E.

Default verdict when clean: `TEMPORAL_OK`.
```

- [ ] **Step 2: §6 加"版本时效"一行**

在 §6 表格/清单末尾追加:

```markdown
- **Edition currency (T2).** For every guideline / standard value, confirm it is
  the CURRENT edition. A superseded value used in a present-tense claim is
  `TEMPORAL_SUPERSEDED` (see Phase C5) — e.g. an old WHO drinking-water guideline,
  a revised IRIS RfD, or a superseded SQG threshold.
```

- [ ] **Step 3: §2 交叉引用**

在 §2 "Temporal Masking" 描述处追加一句:

```markdown
  (Operationalised in **Phase C5** — forward references `TEMPORAL_FORWARD_REF`,
  superseded standards `TEMPORAL_SUPERSEDED`, epoch/tense mismatch
  `TEMPORAL_EPOCH_MISMATCH`.)
```

- [ ] **Step 4: §9 清单追加**

```markdown
- [ ] **Anchors** — every high-risk claim (number / direct quote / contested
  conclusion) carries a VERIFIED source anchor; no `ANCHOR_MISSING` / `ANCHOR_MISMATCH`.
- [ ] **Temporal integrity** — no `TEMPORAL_FORWARD_REF` (ran
  `check_references.py --manuscript-year`); key guideline values are the current
  edition; every "latest / first-to-report" claim passed the epoch check.
```

- [ ] **Step 5: §10 输出报告 summary 表追加两行**

```markdown
| Anchor verification | … | high-risk claims pinned & verified |
| Temporal integrity | … | forward-ref / superseded-edition / epoch |
```

- [ ] **Step 6: §11 一行提醒追加**

```markdown
- High-risk = number / direct quote / key conclusion → must be anchored; a page
  that does not contain the quote is a fabrication signal.
- Cited year after the manuscript year, or a superseded guideline value, is an
  integrity failure — run `--manuscript-year` and check edition currency.
```

- [ ] **Step 7: 验证**

Run: `Grep "TEMPORAL_SUPERSEDED|Phase C5|Edition currency" skills/envsci-citations/references/citations-and-integrity.md`
Expected: 三个串都命中。

- [ ] **Step 8: Commit**

```bash
git add skills/envsci-citations/references/citations-and-integrity.md
git commit -m "feat(citations): add Phase C5 temporal-integrity audit + edition-currency checks"
```

---

## Task 4: envsci-citations/SKILL.md — 模式描述 + 触发词

**Files:**
- Modify: `skills/envsci-citations/SKILL.md`(frontmatter description + `integrity` 模式段)

- [ ] **Step 1: 读文件**,找到 `integrity` 模式描述与 frontmatter `description:`。

- [ ] **Step 2: frontmatter description 追加触发短语**

在 description 的英文触发串里加入:`page/section anchor verification, temporal / anachronism check, superseded-guideline check`;在简体中文触发串里加入:`页码/章节锚点核验、时间一致性、时代错置、过时标准版本核查`。

- [ ] **Step 3: `integrity` 模式正文追加一句**

```markdown
The integrity gate now also (a) verifies **source anchors** on high-risk claims
(page/section/quote → `ANCHOR_VERIFIED/UNRESOLVED/MISMATCH/MISSING`, see
references §B-anchor) and (b) runs a **temporal-integrity audit** (Phase C5:
forward references, superseded guideline editions, epoch/tense mismatch). Run
`check_references.py --manuscript-year YYYY` for the offline forward-reference screen.
```

- [ ] **Step 4: 验证**

Run: `Grep "ANCHOR_VERIFIED|Phase C5|--manuscript-year" skills/envsci-citations/SKILL.md`
Expected: 命中。

- [ ] **Step 5: Commit**

```bash
git add skills/envsci-citations/SKILL.md
git commit -m "docs(citations): surface anchor + temporal audit in SKILL.md triggers/modes"
```

---

## Task 5: envsci-writing — 高危声明锚点规则

**Files:**
- Modify: `skills/envsci-writing/references/writing.md`、`skills/envsci-writing/SKILL.md`

- [ ] **Step 1: writing.md 新增一节**(放在写作纪律/术语一致性附近)

```markdown
## Source anchors for high-risk claims

A **high-risk claim** is (i) any value taken from a source (concentration,
recovery, index value, guideline/threshold, a literature statistic), (ii) any
direct quotation, or (iii) any specific, contestable conclusion attributed to a
source. When drafting, every high-risk claim MUST carry a source anchor; other
sentences may carry one optionally.

Anchor syntax (CSL-locator style, authoring-time annotation):
- page `[@key, p. 42]` / range `[@key, pp. 42–45]`
- section `[@key, §3.2]`
- quote `[@key, "verbatim ≤25 words"]` (quoted words also appear in the prose)

These anchors are verified at the integrity gate by **envsci-citations**
(`ANCHOR_VERIFIED/UNRESOLVED/MISMATCH/MISSING`). A high-risk claim with no anchor
fails Gate I-2. Anchors are not necessarily printed: keep page numbers for direct
quotations per journal style; for paraphrase the anchor stays in the audit trail.
```

- [ ] **Step 2: SKILL.md 加指针 + 触发词**

在写作纪律处加一行:`- High-risk claims (numbers / direct quotes / key conclusions) must carry a **source anchor** ([@key, p./§/"quote"]); verified later by envsci-citations.`;触发串补 `source anchor / 来源锚点 / 给数字标页码`。

- [ ] **Step 3: 验证**

Run: `Grep "Source anchors for high-risk claims" skills/envsci-writing/references/writing.md` 且 `Grep "source anchor" skills/envsci-writing/SKILL.md`
Expected: 均命中。

- [ ] **Step 4: Commit**

```bash
git add skills/envsci-writing/references/writing.md skills/envsci-writing/SKILL.md
git commit -m "feat(writing): require source anchors on high-risk claims (emission side)"
```

---

## Task 6: 新建 envsci-slides/SKILL.md

**Files:**
- Create: `skills/envsci-slides/SKILL.md`

- [ ] **Step 1: 写 SKILL.md**(贴 cluster 模板:frontmatter + 路由 + 边界)

```markdown
---
name: envsci-slides
description: >-
  Use when the user wants to BUILD the visual submission / dissemination
  artifacts for an environmental-science field-sampling / monitoring paper: a
  graphical abstract / TOC graphic, or a presentation deck. Triggers (English):
  graphical abstract, GA, TOC graphic / table-of-contents art, paper-to-slides,
  paper-to-PPT, presentation deck, conference slides, defense slides,
  group-meeting slides, speaker notes. Triggers (简体中文): 图文摘要(成图/做图)、
  做 GA、TOC 图、论文转 PPT、汇报幻灯、会议幻灯、组会汇报、答辩 PPT、讲者备注、
  把论文做成汇报. Script-backed: ga_canvas.py builds a journal-spec GA/TOC canvas
  (SVG + PNG at the right px/dpi); deck_build.py builds a .pptx with speaker notes
  (templates: conference / group / defense). Composes with scipilot-figure-skill
  for general visual-QA / layout / Chinese fonts. Not for the GA/highlights TEXT
  or abstract wording (use envsci-writing); not for per-journal GA/TOC size specs
  (use envsci-journals — this skill consumes them); not for producing the
  underlying publication figures or any new data plot (use envsci-figures — slides
  only recompose already-verified figures and NEVER introduce new numbers).
---

# envsci-slides — graphical abstract & presentation deck for env-sci papers

## What this is
Turns an already-written, integrity-checked paper into its **visual artifacts**:
a journal-spec **graphical abstract / TOC graphic** and a **presentation deck**
with speaker notes. It recomposes verified content — it never creates new data,
numbers, or claims.

## When to use
- Build a graphical abstract / TOC graphic for submission.
- Build a conference / group-meeting / defense slide deck from the manuscript.

## When NOT to use (hand off)
- GA / highlights **text**, abstract wording → **envsci-writing**
- Per-journal GA / TOC **size & spec** → **envsci-journals** (consumed here)
- The underlying **publication figures** / any new data plot → **envsci-figures**
- General chart choice / visual-QA loop / Chinese-font fixes → **scipilot-figure-skill**

## Integrity (inherited from the umbrella)
Every number and conclusion on a slide or GA MUST already exist in the
I-1/I-2-verified manuscript. This skill introduces **no** new numbers or claims —
it only re-presents verified content.

## How to run
Read `references/slides.md` fully and follow it. Scripts:
- `py scripts/ga_canvas.py --preset elsevier-ga|est-toc --title "…" --out ga`
- `py scripts/deck_build.py outline.json --out talk.pptx`
(Install deps: `pip install -r scripts/requirements.txt`; use `py` on Windows.)

## Language
Bilingual (English / 简体中文). Technical terms and journal specs kept in English.
```

- [ ] **Step 2: 验证**

Run: `Grep "name: envsci-slides" skills/envsci-slides/SKILL.md` 且 `Grep "NEVER introduce new numbers" skills/envsci-slides/SKILL.md`
Expected: 命中。

- [ ] **Step 3: Commit**

```bash
git add skills/envsci-slides/SKILL.md
git commit -m "feat(slides): scaffold envsci-slides SKILL.md (GA + deck, boundaries, integrity)"
```

---

## Task 7: 新建 envsci-slides/references/slides.md(7 节)

**Files:**
- Create: `skills/envsci-slides/references/slides.md`

- [ ] **Step 1: 写 slides.md**——必须包含以下 7 个二级标题与每节列出的要点(prose 自行展开,但要点不可缺):

```markdown
# envsci-slides — deep reference

## §1 Mental model (contract first)
- Define the ONE core message before drawing anything.
- Pick an archetype (see §3 / §4).
- Pull only VERIFIED assets: figures from envsci-figures, numbers from the Data
  Ledger / I-gate-verified manuscript, text from envsci-writing, specs from
  envsci-journals. Never invent or recompute.

## §2 Hard specs
- GA (Elsevier): min 531 × 1328 px (h × w), or vector; readable at 5 × 13 cm.
- TOC (ACS ES&T): ≤ 3.25 × 1.75 in (8.255 × 4.445 cm), ≥ 300 dpi, + a 50–60-word synopsis.
- Colorblind-safe palette; embed fonts; legible at thumbnail (min font-size rule);
  SVG-first → PNG. Per-journal sizes: defer to envsci-journals (do not duplicate).

## §3 GA archetype catalogue (env-sampling oriented)
- mechanism / process schematic; before→after; spatial-gradient mini-map;
  input→system→output FLUX diagram (fits SWI pore-water / peeper nutrient flux);
  conceptual cross-section. Each: do / don't + an information-density ceiling.

## §4 Deck archetypes + rhythm templates
- conference (~10–12 min: hook → gap → light methods → key results → take-home)
- group meeting (deeper methods / troubleshooting)
- defense (full methods + QA/QC, anticipate Q&A)
- slide-type catalogue + how to write speaker notes.

## §5 Tooling & outline schema
- ga_canvas.py usage + presets; deck_build.py usage + outline JSON schema
  (title, subtitle, template, slides[].{heading,bullets,notes,image}); export & naming.

## §6 Gate-S (slides-QA contract)
- GA: legible at thumbnail; word/information-density within ceiling; colorblind-safe;
  units present; size/dpi compliant; synopsis word count; NO new/unverified numbers.
- Deck: one message per slide; font-size threshold; every figure traceable to a
  source figure; NO fabricated content. (Mirror of envsci-figures Gate-F.)

## §7 Handoff
- GA → envsci-journals submission package; deck stands alone; integrity pointer →
  envsci-citations (numbers must already be verified).
```

- [ ] **Step 2: 验证**

Run: `Grep "Gate-S|input→system→output FLUX|50–60-word synopsis" skills/envsci-slides/references/slides.md`
Expected: 命中(关键要点在)。

- [ ] **Step 3: Commit**

```bash
git add skills/envsci-slides/references/slides.md
git commit -m "feat(slides): add references/slides.md (specs, archetypes, Gate-S, handoff)"
```

---

## Task 8: 新建 ga_canvas.py + requirements.txt(GA,自检)

**Files:**
- Create: `skills/envsci-slides/scripts/ga_canvas.py`、`skills/envsci-slides/scripts/requirements.txt`

- [ ] **Step 1: 写 requirements.txt**

```text
python-pptx>=0.6.21
matplotlib>=3.5
```

- [ ] **Step 2: 写 ga_canvas.py(完整)**

```python
#!/usr/bin/env python3
"""
ga_canvas.py — envsci-slides
Build a journal-spec graphical-abstract / TOC canvas and export SVG + PNG at the
right pixel/dpi. The colorblind-safe palette is embedded so this script is
standalone (no runtime dependency on envsci-figures).

Presets:
  elsevier-ga : 1328 x 531 px (w x h) @ 300 dpi   (Elsevier graphical abstract)
  est-toc     :  975 x 525 px (3.25 x 1.75 in) @ 300 dpi  (ACS ES&T TOC graphic)

Usage:
  py ga_canvas.py --preset elsevier-ga --title "..." --subtitle "..." --out ga
  py ga_canvas.py --selftest

Requires: matplotlib.
"""
from __future__ import annotations

import argparse
import os
import struct

# Okabe–Ito colorblind-safe palette, kept consistent with envsci-figures.
PALETTE = {
    "blue": "#0072B2", "orange": "#E69F00", "green": "#009E73",
    "vermillion": "#D55E00", "skyblue": "#56B4E9", "yellow": "#F0E442",
    "purple": "#CC79A7", "black": "#000000", "grey": "#999999",
}

# preset -> (width_in, height_in, dpi, label)
PRESETS = {
    "elsevier-ga": (1328 / 300, 531 / 300, 300, "Elsevier graphical abstract 1328x531 px"),
    "est-toc": (3.25, 1.75, 300, "ACS ES&T TOC 3.25x1.75 in @300 dpi"),
}


def build_canvas(preset: str, title: str = "", subtitle: str = ""):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    if preset not in PRESETS:
        raise ValueError(f"unknown preset {preset!r}; choose from {list(PRESETS)}")
    w_in, h_in, dpi, _ = PRESETS[preset]
    fig = plt.figure(figsize=(w_in, h_in), dpi=dpi)
    fig.patch.set_facecolor("white")
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_axis_off()
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    ax.add_patch(plt.Rectangle((0, 0.82), 1, 0.18, color=PALETTE["blue"]))
    if title:
        ax.text(0.5, 0.91, title, ha="center", va="center",
                color="white", fontsize=11, fontweight="bold", wrap=True)
    if subtitle:
        ax.text(0.5, 0.50, subtitle, ha="center", va="center",
                color=PALETTE["black"], fontsize=8, wrap=True)
    ax.add_patch(plt.Rectangle((0.04, 0.06), 0.92, 0.70, fill=False,
                               edgecolor=PALETTE["grey"], lw=1, linestyle="--"))
    ax.text(0.5, 0.41, "[ place verified figure / schematic here ]",
            ha="center", va="center", color=PALETTE["grey"], fontsize=7)
    return fig, dpi


def export(fig, dpi, out_stem: str):
    png, svg = f"{out_stem}.png", f"{out_stem}.svg"
    fig.savefig(png, dpi=dpi)
    fig.savefig(svg)
    return png, svg


def _png_size(png_path: str):
    with open(png_path, "rb") as f:
        head = f.read(24)
    if head[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("not a PNG")
    return struct.unpack(">II", head[16:24])


def run_selftest() -> int:
    import tempfile
    import matplotlib.pyplot as plt

    expected = {"elsevier-ga": (1328, 531), "est-toc": (975, 525)}
    failures = []
    with tempfile.TemporaryDirectory() as d:
        for preset, (ew, eh) in expected.items():
            fig, dpi = build_canvas(preset, title="Self-test", subtitle="demo")
            stem = os.path.join(d, preset)
            png, svg = export(fig, dpi, stem)
            plt.close(fig)
            assert os.path.isfile(png) and os.path.isfile(svg), preset
            w, h = _png_size(png)
            if abs(w - ew) > 2 or abs(h - eh) > 2:
                failures.append(f"{preset}: got {w}x{h}, want {ew}x{eh}")
    if failures:
        print("selftest: FAIL\n" + "\n".join(failures))
        return 1
    print("selftest: OK")
    return 0


def main(argv=None) -> int:
    p = argparse.ArgumentParser(
        prog="ga_canvas.py",
        description="Build a journal-spec graphical-abstract / TOC canvas (SVG + PNG).",
    )
    p.add_argument("--preset", choices=list(PRESETS), default="elsevier-ga")
    p.add_argument("--title", default="")
    p.add_argument("--subtitle", default="")
    p.add_argument("--out", default="ga", help="output file stem (.png and .svg)")
    p.add_argument("--selftest", action="store_true")
    args = p.parse_args(argv)
    if args.selftest:
        return run_selftest()
    fig, dpi = build_canvas(args.preset, args.title, args.subtitle)
    png, svg = export(fig, dpi, args.out)
    print(f"wrote {png} and {svg} ({PRESETS[args.preset][3]})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 3: 安装依赖并运行自检**

Run: `pip install -r skills/envsci-slides/scripts/requirements.txt`
Run: `py skills/envsci-slides/scripts/ga_canvas.py --selftest`
Expected: `selftest: OK`(两预设像素尺寸都对)。

- [ ] **Step 4: Commit**

```bash
git add skills/envsci-slides/scripts/ga_canvas.py skills/envsci-slides/scripts/requirements.txt
git commit -m "feat(slides): add ga_canvas.py (journal-spec GA/TOC, SVG+PNG, selftest)"
```

---

## Task 9: 新建 deck_build.py(deck,自检)

**Files:**
- Create: `skills/envsci-slides/scripts/deck_build.py`

- [ ] **Step 1: 写 deck_build.py(完整)**

```python
#!/usr/bin/env python3
"""
deck_build.py — envsci-slides
Build a presentation deck (.pptx) with speaker notes from a structured outline.
Templates: conference (default) / group / defense.

Outline JSON:
{
  "title": "Talk title",
  "subtitle": "Author, affiliation",
  "template": "conference",
  "slides": [
    {"heading": "Background", "bullets": ["...", "..."],
     "notes": "speaker notes", "image": "path/to/verified_fig.png"}
  ]
}

Usage:
  py deck_build.py outline.json --out talk.pptx
  py deck_build.py --selftest

Requires: python-pptx.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

TEMPLATES = {
    "conference": {"accent": "1F7A4D"},
    "group": {"accent": "0072B2"},
    "defense": {"accent": "CC79A7"},
}


def build_deck(outline: dict):
    from pptx import Presentation
    from pptx.util import Inches

    template = outline.get("template", "conference")
    if template not in TEMPLATES:
        raise ValueError(f"unknown template {template!r}; choose {list(TEMPLATES)}")

    prs = Presentation()

    # Title slide
    s = prs.slides.add_slide(prs.slide_layouts[0])
    s.shapes.title.text = outline.get("title", "Untitled")
    if len(s.placeholders) > 1:
        s.placeholders[1].text = outline.get("subtitle", "")

    # Content slides
    for sl in outline.get("slides", []):
        slide = prs.slides.add_slide(prs.slide_layouts[1])
        slide.shapes.title.text = sl.get("heading", "")
        tf = slide.placeholders[1].text_frame
        tf.clear()
        bullets = sl.get("bullets", []) or [""]
        for i, b in enumerate(bullets):
            para = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
            para.text = b
        img = sl.get("image")
        if img and os.path.isfile(img):
            slide.shapes.add_picture(img, Inches(5.2), Inches(1.8), height=Inches(3.5))
        notes = sl.get("notes", "")
        if notes:
            slide.notes_slide.notes_text_frame.text = notes
    return prs


def run_selftest() -> int:
    import tempfile
    from pptx import Presentation

    outline = {
        "title": "Self-test talk", "subtitle": "envsci-slides",
        "template": "conference",
        "slides": [
            {"heading": "Background", "bullets": ["point a", "point b"], "notes": "intro"},
            {"heading": "Methods", "bullets": ["sampling", "QA/QC"], "notes": "explain"},
            {"heading": "Results", "bullets": ["finding 1"], "notes": "key result"},
        ],
    }
    prs = build_deck(outline)
    with tempfile.TemporaryDirectory() as d:
        out = os.path.join(d, "selftest.pptx")
        prs.save(out)
        assert os.path.isfile(out), "pptx not written"
        chk = Presentation(out)
        assert len(chk.slides) == 4, len(chk.slides)  # 1 title + 3 content
        notes_found = sum(
            1 for sl in chk.slides
            if sl.has_notes_slide and sl.notes_slide.notes_text_frame.text.strip()
        )
        assert notes_found >= 3, notes_found
    print("selftest: OK")
    return 0


def main(argv=None) -> int:
    p = argparse.ArgumentParser(
        prog="deck_build.py",
        description="Build a .pptx deck with speaker notes from a structured outline.",
    )
    p.add_argument("outline", nargs="?", help="Path to outline JSON.")
    p.add_argument("--out", default="deck.pptx")
    p.add_argument("--selftest", action="store_true")
    args = p.parse_args(argv)
    if args.selftest:
        return run_selftest()
    if not args.outline:
        p.error("an outline JSON path is required (or use --selftest)")
    outline = json.loads(Path(args.outline).read_text(encoding="utf-8"))
    prs = build_deck(outline)
    prs.save(args.out)
    print(f"wrote {args.out} ({len(prs.slides)} slides)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 2: 运行自检**(依赖已在 Task 8 装)

Run: `py skills/envsci-slides/scripts/deck_build.py --selftest`
Expected: `selftest: OK`(4 张幻灯、≥3 条备注)。

- [ ] **Step 3: Commit**

```bash
git add skills/envsci-slides/scripts/deck_build.py
git commit -m "feat(slides): add deck_build.py (pptx + speaker notes, templates, selftest)"
```

---

## Task 10: 总伞 enviro-paper/SKILL.md 登记

**Files:**
- Modify: `skills/enviro-paper/SKILL.md`(frontmatter ~L6、bullet 列表 ~L14–17、hand-off ~L34–42、pipeline 表 ~L47–67)

- [ ] **Step 1: 读文件**确认四处位置。

- [ ] **Step 2: 编辑四处**
- frontmatter:`8 envsci-* function skills` → `9 envsci-* function skills`,并在括号里补 `+ envsci-slides`。
- bullet 列表:加 `envsci-slides (图文摘要/汇报幻灯)`。
- hand-off 段:加 `- graphical abstract / TOC graphic / presentation deck → **envsci-slides**`。
- pipeline 表 Stage 10 (RESPONSE/FINALIZE) 的 Owner 列加 `+ **envsci-slides**`,并在表下注一句:`The graphical abstract is part of the submission package (Stage 10); the presentation deck is a post-acceptance dissemination artifact — invoke envsci-slides on its own, not a blocking stage. Slides consume only I-gate-verified content.`

- [ ] **Step 3: 验证**

Run: `Grep "envsci-slides" skills/enviro-paper/SKILL.md` 且 `Grep "9 envsci-\* function skills" skills/enviro-paper/SKILL.md`
Expected: 均命中。

- [ ] **Step 4: Commit**

```bash
git add skills/enviro-paper/SKILL.md
git commit -m "feat(umbrella): register envsci-slides (9th function skill; GA in Stage 10)"
```

---

## Task 11: 插件 manifest 版本与描述

**Files:**
- Modify: `.claude-plugin/marketplace.json`、`.claude-plugin/plugin.json`、`.codex-plugin/plugin.json`

> 计数口径:描述串 "8 ... function skills (…envsci-journals)" → "9 ... function skills (…envsci-journals, envsci-slides)";version 全部 `2.0.0` → `2.1.0`。

- [ ] **Step 1: marketplace.json**
- 顶层 `"version": "2.0.0"` → `"2.1.0"`;`plugins[0].version` 同改。
- 两处 `description`:把 `8 independently selectable function skills (envsci-ideate, envsci-litsearch, envsci-data, envsci-figures, envsci-writing, envsci-citations, envsci-review, envsci-journals)` 改为 `9 independently selectable function skills (envsci-ideate, envsci-litsearch, envsci-data, envsci-figures, envsci-writing, envsci-citations, envsci-review, envsci-journals, envsci-slides)`。
- `plugins[0].keywords` 末尾加 `"graphical-abstract"`, `"slides"`。

- [ ] **Step 2: plugin.json**
- `"version": "2.0.0"` → `"2.1.0"`;`description` 同上 8→9 改;`keywords` 末尾加 `"graphical-abstract"`, `"presentation"`。

- [ ] **Step 3: .codex-plugin/plugin.json**
- `"version"` → `"2.1.0"`;`description` 同上 8→9 改;`interface.longDescription` 末尾加一句:` Also generate a journal-spec graphical abstract and a presentation deck.`。

- [ ] **Step 4: 验证(JSON 合法 + 串生效)**

Run: `py -c "import json,glob; [json.load(open(f,encoding='utf-8')) for f in ['.claude-plugin/marketplace.json','.claude-plugin/plugin.json','.codex-plugin/plugin.json']]; print('json ok')"`
Run: `Grep "envsci-slides" .claude-plugin/marketplace.json .claude-plugin/plugin.json .codex-plugin/plugin.json`
Expected: `json ok`;三个文件都命中 `envsci-slides`,version 均为 2.1.0。

- [ ] **Step 5: Commit**

```bash
git add .claude-plugin/marketplace.json .claude-plugin/plugin.json .codex-plugin/plugin.json
git commit -m "chore: bump to 2.1.0 and register envsci-slides in plugin manifests"
```

---

## Task 12: 文档 install.md / README.md / CHANGELOG.md

**Files:**
- Modify: `install.md`、`README.md`、`CHANGELOG.md`

- [ ] **Step 1: install.md**
- `collection of **9** Agent Skills (1 umbrella ... + 8 envsci-* function skills)` → `**10** ... + 9 envsci-* function skills`。
- 目录树加一行:`└── envsci-slides/      # graphical abstract + presentation deck (+ scripts/)`(并把上一行的 `└──` 调成 `├──`)。
- §4 Verify 追加:
```bash
py skills/envsci-slides/scripts/ga_canvas.py --selftest      # selftest: OK
py skills/envsci-slides/scripts/deck_build.py --selftest     # selftest: OK
pip install -r skills/envsci-slides/scripts/requirements.txt  # python-pptx, matplotlib
```

- [ ] **Step 2: README.md**
- 读 README,定位技能清单/计数处;把 function-skill 计数 8→9、总数 9→10;按现有格式加一行 `envsci-slides — graphical abstract + presentation deck`。

- [ ] **Step 3: CHANGELOG.md 顶部新增**

```markdown
## [2.1.0] — 2026-06-28

### Added
- **`envsci-slides`** — new sibling skill: builds a journal-spec **graphical
  abstract / TOC graphic** (`ga_canvas.py`, SVG + PNG at correct px/dpi) and a
  **presentation deck** with speaker notes (`deck_build.py`, python-pptx;
  templates conference / group / defense). Standalone palette; composes with
  scipilot-figure-skill; introduces no new numbers/claims.
- **envsci-citations** — **source-anchor verification** for high-risk claims
  (page/section/quote → `ANCHOR_VERIFIED/UNRESOLVED/MISMATCH/MISSING`, Phase B)
  and a **temporal-integrity audit** (Phase C5: forward references, superseded
  guideline editions, epoch/tense mismatch). `check_references.py` gains
  `--manuscript-year` for an offline forward-reference screen.
- **envsci-writing** — high-risk claims (numbers / direct quotes / key
  conclusions) must emit a source anchor, verified later by envsci-citations.

### Changed
- Umbrella `enviro-paper` registers the 9th function skill; the graphical
  abstract is produced in Stage 10 (FINALIZE).
```

- [ ] **Step 4: 验证**

Run: `Grep "2.1.0" CHANGELOG.md` 且 `Grep "envsci-slides" install.md README.md`
Expected: 命中。

- [ ] **Step 5: Commit**

```bash
git add install.md README.md CHANGELOG.md
git commit -m "docs: register envsci-slides + v2.1.0 notes in install/README/CHANGELOG"
```

---

## Task 13: 全量验证 + 集成抽测 + 同步到 ~/.claude/skills/

**Files:** 无新增;运行与同步。

- [ ] **Step 1: 跑全部脚本自检**

```bash
py skills/envsci-citations/scripts/check_references.py --selftest
py skills/envsci-slides/scripts/ga_canvas.py --selftest
py skills/envsci-slides/scripts/deck_build.py --selftest
```
Expected: 三个都 `selftest: OK`。

- [ ] **Step 2: 集成抽测(锚点+前向引用+过时限值的样例)**

构造一段含:一处带 `[@key, p.12]` 锚点的数值声明、一条 2030 年的前向引用、一处"current WHO guideline"引用旧版的限值;按 `envsci-citations` integrity 模式人工走查,确认能分别触发 `ANCHOR_*`、`TEMPORAL_FORWARD_REF`、`TEMPORAL_SUPERSEDED`。把样例与结论记到 `docs/superpowers/plans/` 旁的临时验证笔记(不提交)。

- [ ] **Step 3: 实测产出 1 GA + 1 deck**

```bash
py skills/envsci-slides/scripts/ga_canvas.py --preset elsevier-ga --title "Demo" --out /tmp/demo_ga
printf '{"title":"Demo","template":"conference","slides":[{"heading":"Results","bullets":["a"],"notes":"n"}]}' > /tmp/o.json
py skills/envsci-slides/scripts/deck_build.py /tmp/o.json --out /tmp/demo.pptx
```
Expected: 生成 `demo_ga.png/.svg` 与 `demo.pptx`。

- [ ] **Step 4: 同步到本机 skills 目录(PowerShell)**

```powershell
Copy-Item -Recurse -Force ".\skills\envsci-slides" "$HOME\.claude\skills\"
Copy-Item -Force ".\skills\enviro-paper\SKILL.md" "$HOME\.claude\skills\enviro-paper\SKILL.md"
Copy-Item -Recurse -Force ".\skills\envsci-citations\*" "$HOME\.claude\skills\envsci-citations\"
Copy-Item -Recurse -Force ".\skills\envsci-writing\*" "$HOME\.claude\skills\envsci-writing\"
```
Expected: `~/.claude/skills/envsci-slides` 存在;另三个 skill 已更新。

- [ ] **Step 5: Commit(若集成抽测发现并修了内容)**

```bash
git add -A
git commit -m "test: verify selftests + integration dry-run for v2.1.0" || echo "nothing to commit"
```

---

## Task 14: 重做三方对比表(交付物)

**Files:**
- Create: `docs/comparison-2026-06-28-v2.1.0.md`(并在回复里呈现给用户)

- [ ] **Step 1: 写对比文档**——以 2.1.0 形态重做 envsci-paper-skill vs academic-research-skills vs nature-skills,重点标出本次新闭合的差距:
  - 引文页/段锚点:之前 ARS 独有 → 现 ✅(本集群已具备)。
  - 时间一致性审计:之前 ARS 独有 → 现 ✅。
  - 论文→GA/PPT:之前 nature-skills 独有 → 现 ✅(GA + deck;但仍**不做** paper→patent,如实标注)。
  - 保留既有领域优势(污染/风险指数、源解析、领域出图、领域选刊、领域诚信)。
  诚实标注仍落后处(如 ARS 诚信子项更细的部分、nature-skills 的 patent/paper2ppt 的 patent 端)。

- [ ] **Step 2: Commit**

```bash
git add docs/comparison-2026-06-28-v2.1.0.md
git commit -m "docs: refreshed 3-way comparison after v2.1.0"
```

- [ ] **Step 3: 呈现**:在回复中给出更新后的对比表,并说明哪些差距已闭合、哪些仍保留。

---

## Self-Review(计划自审记录)

- **Spec 覆盖**:Part A(锚点=Task2/4/5,时间审计=Task1/3)、Part B(slides=Task6–9)、Part C(umbrella=Task10,manifest=Task11,docs=Task12)、验证+同步=Task13、收尾对比=Task14。全部 spec 小节均有对应任务。
- **占位扫描**:脚本任务均含完整可运行代码;markdown 任务给出必含串 + grep 验证;无 TBD/TODO。
- **类型/命名一致**:判据码 `ANCHOR_VERIFIED/UNRESOLVED/MISMATCH/MISSING`、`TEMPORAL_FORWARD_REF/SUPERSEDED/EPOCH_MISMATCH` 在 Task1/3/4/5/12 用法一致;`check_references(..., manuscript_year=...)` 与 `_check_forward_reference` 签名一致;preset 名 `elsevier-ga`/`est-toc` 在 ga_canvas 与文档一致。
- **版本一致**:`2.0.0→2.1.0` 在 Task11/12 统一;计数 function 8→9、总数 9→10 已注明区分。
