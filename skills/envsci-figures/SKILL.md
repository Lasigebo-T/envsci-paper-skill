---
name: envsci-figures
description: >-
  Use when the user wants to MAKE a publication figure for an environmental-science field-sampling / monitoring paper and already knows (roughly) what the figure should show. Specific triggers — English: site/sampling-location map, boxplot by site or season with significance letters, correlation heatmap (Spearman), PCA biplot, HCA dendrogram/clustered heatmap, spatial interpolation (IDW/kriging) map, stacked composition / congener-fingerprint bars, time series with detection-limit line, pollution-index or risk bars with threshold lines (Igeo/EF/CF/PLI/Er/RI/Nemerow/WQI/HQ/HI/CR), hydrochemistry Piper/Stiff/Gibbs/Durov, journal-final sizing (89 mm / 183 mm), SVG-first export. Simplified-Chinese: 环境出图、采样点位图/站位图、按点位或季节的箱线图、显著性字母标注、相关热图、PCA双标图、聚类热图、空间插值图、堆叠组成图/指纹图、污染指数图、风险指数图、期刊配图、出版级矢量图、色盲安全配色. This skill adds the env-sci-specific chart catalogue, the env conventions (units + dw/ww basis, error bars with n, colorblind-safe, map furniture: CRS+scale bar+north arrow), the Gate-F figure-QA contract, and the ready-to-run plotters in scripts/envsci_style.py. IMPORTANT integration: for GENERAL chart-type SELECTION ("不知道用什么图"/"how should I plot this?"), data profiling, the visual-QA closed loop, journal specs across many journals, and Chinese-font fixes, COMPOSE WITH the scipilot-figure-skill (general figure methodology) — this skill supplies the env-sci chart choices, conventions, and plotters on top. Not for statistics / indices / non-detect handling / source apportionment (use envsci-data — figures never introduce new numbers); not for citation or caption-fidelity integrity gates (use envsci-citations); not for choosing the target journal (use envsci-journals).
---

# envsci-figures — Publication figures for environmental science

## What this is
The figure stage for env-sci field-sampling / monitoring papers. It takes data that has
**already** been QA/QC'd and analysed (by `envsci-data`) and turns a defensible claim into a
journal-ready figure: site maps, boxplots by site/season with post-hoc significance letters,
correlation heatmaps, PCA biplots, HCA cluster heatmaps, spatial interpolation, time series,
stacked composition/fingerprint bars, hydrochemistry diagrams, and pollution/risk-index bars.
It ships `scripts/envsci_style.py` — colorblind-safe, rainbow-banned, editable-SVG plotters that
return `(fig, ax)` and never call `plt.show()`. **Figures never introduce new numbers**; every
plotted value must trace to a Data-Ledger cell or script output.

## When to use
- The user wants to **draw a specific env-sci figure** and knows roughly what it should show.
- A figure carries a spatial, statistical, or risk claim and must pass a publication-QA gate.
- A figure needs env conventions enforced: units + dw/ww basis, error bars with n, map furniture,
  log-axis labeling, threshold reference lines, journal-final sizing, SVG-first export.

## When NOT to use (hand off)
- **"Which chart type fits this data?" / data profiling / visual-QA closed loop / Chinese-font
  fixes / many-journal specs** → **compose with `scipilot-figure-skill`** for the general figure
  methodology; come back here for the env-sci chart choice, conventions, and plotters.
- **Computing the values** — statistics, normality/ANOVA/Kruskal–Wallis/Spearman, PCA/HCA inputs,
  indices (Igeo/EF/CF/PLI/Er/RI/Nemerow/WQI), health risk (HQ/HI/CR), non-detect handling,
  source apportionment → **`envsci-data`** (Gate S supplies the numbers + their citations).
- **Citation formatting / caption-fidelity integrity gate** → **`envsci-citations`**.
- **Picking the target journal / its scope & format** → **`envsci-journals`**.

## How to run
1. **Read `references/figures.md` fully and follow it** — the deep how-to lives there: the Figure
   Contract (§1), the env-sci chart catalogue with when-to-use → gotchas → plotter (§3), the
   mandated style numbers (§2), the cross-cutting conventions (§5), the full plotter API (§4), and
   the **FIGURE-QA CONTRACT / Gate F** (§6). Do not start template-first — write the one-sentence
   claim and panel map first.
2. **Plot via `scripts/envsci_style.py`** (import, never read into context):
   `set_envsci_style()` once → `fig_size("single"|"double")` → a plotter
   (`boxplot_by_group`, `correlation_heatmap`, `pca_biplot`, `time_series`,
   `spatial_scatter_map`, `stacked_composition`) → **override the placeholder axis label** with the
   real quantity + unit + dw/ww basis → `save_figure(...)` (SVG first, then PNG 300/600 dpi).
   Smoke-test the API with `py scripts/envsci_style.py --demo all` (on Windows use the `py`
   launcher, not `python`). Install core deps via `scripts/requirements.txt`.
3. **Run Gate F before delivering.** Every HARD row must pass; a failing HARD row is a
   `[FIGURE GAP]`, not "good enough". If a needed backend/library is missing, **stop and report the
   missing runtime** — do not silently substitute another tool.
4. **Hand off** the Figure Contract, Gate-F verdict, caption draft (units/basis, n, error
   definition, test + correction, CRS for maps), and source-data trace to the writing and integrity
   stages.

## Integrity ethos (keep on every figure)
No invented values, significance letters, or DOIs. Index values, background Bn, and toxic-response
factors come from `envsci-data` with their canonical citations — figures only display them. Every
quantitative axis carries units and, for solids, **dw/ww**. Error bars are defined (SD/SE/95% CI)
with n. Non-detect handling is declared upstream and reflected (e.g. detection-limit reference
lines). Colorblind-safe only — rainbow/jet banned, red–green never the sole encoding, figure must
read in grayscale.

## Language
Respond in the user's language (the user works in Simplified Chinese): deliver the figure with an
English caption, then add brief Chinese structural notes (what each panel shows, what is still
missing). Keep variable names, units, Latin binomials, DOIs, and journal terms in English.
