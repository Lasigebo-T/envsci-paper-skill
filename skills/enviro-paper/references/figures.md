# figures.md — Stage 4: Publication Figures for Environmental Science

> **Loaded by:** `figures` mode (and Stage 4 of `full-pipeline`). Read this file once when figure
> work fires; do not preload. **Pairs with `scripts/envsci_style.py`** (imported, never read into
> context).
>
> **Output language follows the user.** Variable names, units, Latin binomials, and journal terms
> stay in English. For a Chinese-speaking user, deliver the figure + English caption, then add brief
> Chinese structural notes (what each panel shows, what is still missing).
>
> **Gate F lives here.** No figure leaves Stage 4 until it passes the **FIGURE-QA CONTRACT** (§6).
> A figure that fails any hard row is `[FIGURE GAP]`, not "good enough".

---

## 0. The one-screen mental model

1. **Contract first** (§1) — one-sentence claim, archetype, panel map. No template-first plotting.
2. **Pick the archetype** from the **env-sci chart catalogue** (§3); read its *when-to-use* and *gotchas*.
3. **Plot via `scripts/envsci_style.py`** (§2 + §4) — never hand-roll rcParams; the script bans
   rainbow/jet and sets editable-SVG text for you.
4. **Apply the cross-cutting conventions** (§5) — units + dw/ww basis, error bars + n, colorblind
   safety, log-axis labeling, map furniture.
5. **Run the FIGURE-QA CONTRACT** (§6) — pass/fail. Gate F.
6. **Export** SVG first, PNG 300/600 dpi second (§2.4 / §4.3).

---

## 1. Figure Contract (pre-work — do this before any plotting code)

Write this short contract into your working notes (and surface the user-facing parts). Start from the
**conclusion**, then choose the *minimum* set of panels that make it clear and defensible — never start
from a favourite chart type.

```text
Core conclusion : one sentence WITH A VERB
                  e.g. "Sediment Cd peaks at the three downstream sites and the geo-accumulation
                  index there reaches the 'moderately-to-heavily polluted' class."
                  NOT "Sediment metal results."
Figure archetype: single-claim panel | multi-panel composite | spatial map-led | composition profile
Target journal  : STOTEN / Water Research / ES&T / Environ. Pollut. / JHM / ESPR / ...
Final size      : single-column ~89 mm  OR  double-column ~183 mm  (height ≤ journal page limit)
Panel map       : a: <unique question> | b: <unique question> | c: <unique question>
Evidence rank   : hero panel = main effect; validation/robustness panels are visually quieter
Stats shown     : test, n, center, spread, correction, significance-annotation method
Source-data     : every plotted value traces to a Data-Ledger cell / script output (CSV/XLSX)
Reviewer risk   : what a skeptical reviewer challenges (n hidden? basis missing? pseudoreplication?)
```

**Hard rules carried from the Figure Contract:**

- **Every panel answers a unique question.** If covering one panel does not weaken the argument,
  *merge or delete it*. Re-displaying panel a's data in another visual form is the #1 redundancy trap
  (e.g. stacked-bar % + heatmap of the same %; replace the heatmap with a z-score deviation view).
- **Separate primary from supporting evidence.** The main effect gets the hero panel / clearest axis;
  controls and robustness panels are smaller and quieter. Equal-sized panels are *not* required.
- **One color vocabulary across the whole figure.** A site, season, or matrix keeps the same color in
  every panel. Never remap the same group to a different hue family between panels.
- **If the user gives data but no claim,** infer a provisional one-sentence claim and confirm it before
  final styling — do not guess silently.
- **Source-data trace is mandatory.** A panel whose numbers cannot be traced to a Data-Ledger cell is a
  `[FIGURE GAP]`; do not fabricate values to fill a plot.

---

## 2. Mandated publication style (the concrete numbers)

These are the enforceable defaults, adapted from the NATURE figure rules to env-sci journals. The
script `set_envsci_style()` applies them; this section is the *specification* the script must satisfy
and the values you cite in captions / methods.

### 2.1 Typography

| Property | Value |
|---|---|
| Font family | `sans-serif`; stack `['Arial', 'Helvetica', 'DejaVu Sans', 'sans-serif']` (DejaVu is the always-present fallback) |
| Base font (dense journal-width figure at final size) | **7 pt** (acceptable 5–7 pt for the densest composites; tick/legend text must stay legible at final printed size) |
| Panel labels | lowercase, **bold**, near top-left, ~8 pt at final size (`a`, `b`, `c`) |
| Axis line width | 0.8–1.2 pt at final size |
| SVG text | `svg.fonttype = 'none'` — text stays as editable `<text>` nodes, **never** outlined to paths |
| PDF text | `pdf.fonttype = 42` — embeds TrueType so text stays selectable |

> The script's default `base_font_pt=7.0` targets the journal-final regime. If you are first drafting
> at slide size, you may set `set_envsci_style(base_font_pt=9.0)` and shrink for the final composite —
> but the **delivered** figure must read at 5–7 pt at its true mm width.

### 2.2 Figure width (the load-bearing mm numbers)

| Column class | Width | `fig_size()` arg |
|---|---|---|
| Single column | **≈ 89 mm** (3.50 in) | `fig_size("single")` |
| Double column | **≈ 183 mm** (7.20 in) | `fig_size("double")` |

- mm → inches via `/ 25.4` (done inside `fig_size`). Height defaults to a sensible ratio; override with
  `fig_size("double", height_mm=120)`.
- Height must not exceed the target journal's page/figure-height limit (verify in the Guide for Authors;
  see `journals.md`).

### 2.3 Resolution & color

| Property | Rule |
|---|---|
| Raster resolution | **≥ 300 dpi** standard; **600 dpi** for dense panels (heatmaps, many-site boxplots, fine maps) |
| Vector | preferred wherever the figure is line/marker art (everything except photos/microscopy/raster basemaps) |
| Spines | top + right **off**; keep left + bottom only |
| Legend | frameless (`frameon=False`); prefer direct labels or one shared legend strip |
| Grid | off by default; sparse y-ticks guide the eye |
| Color maps | **colorblind-safe only** — sequential `viridis` / `cividis`; categorical Okabe–Ito or Tol-bright; diverging `RdBu_r` centered at 0. **Rainbow / `jet` / `hsv` are banned** (`set_envsci_style` removes them from the default cycle). |
| Red–green | never the *only* encoding (≈8% of male readers are red–green colorblind); pair with shape, position, or label. Figure must remain interpretable in grayscale. |

### 2.4 Export policy (SVG-first)

| Order | Format | Settings |
|---|---|---|
| 1 (primary) | **SVG** | `svg.fonttype='none'` → editable text; lossless scaling; the file you hand to a co-author to re-align labels in Illustrator/Inkscape |
| 2 (secondary) | **PNG** | 300 dpi (600 for dense panels) — for submission portals / quick preview |
| 3 (optional) | **PDF / TIFF** | PDF (`pdf.fonttype=42`) or TIFF 600 dpi when the journal requires it |

Always `fig.tight_layout()` before save and `plt.close(fig)` after — both handled by `save_figure`.
**Never** ship a PNG-only figure that contains text needing later adjustment.

---

## 3. Env-sci chart catalogue (when-to-use → gotchas → script function)

Each entry: **what it shows → when to use → gotchas (Gate-F failure modes) → which `envsci_style.py`
function plots it.** Functions are listed in §4; anything without a dedicated function is a recipe over
matplotlib using the shared style.

### 3.1 Sampling-site location map
- **Shows:** where samples were collected; optionally value-coded markers (concentration, index class).
- **When:** *every* field-sampling paper needs one — it is the first Methods/Results figure and the
  visual vocabulary (site IDs, colors) for the whole manuscript.
- **Gotchas:** must carry a **projected CRS stated in the caption**, a **scale bar**, and a **north
  arrow**; add a **regional inset** so a non-local reader can place the study area. Do not plot bare
  lat/lon dots with no geographic context. State the basemap/data source.
- **Function:** `spatial_scatter_map(...)` (pure-matplotlib fallback if no geo backend installed).

### 3.2 Boxplot by site / season (with significance letters)
- **Shows:** concentration distribution per group; spatial pattern across sites or seasonal contrast.
- **When:** the workhorse Results figure for multi-site / multi-season monitoring data. Distribution
  view is honest about spread and outliers (better than bar-of-means for skewed environmental data).
- **Gotchas:** **y-label must carry units + dw/ww basis** (e.g. `Cd (mg kg⁻¹ dw)`); use **log10 y**
  when values span ≥2 orders of magnitude (and label the variable, not "log x"); overlay raw points
  when n is small (n < ~10) so the reader sees the real sample size; annotate **post-hoc significance
  letters** (a, b, c — groups sharing a letter are not significantly different) and **state the test +
  correction in the caption** (e.g. "Kruskal–Wallis + Dunn, Benjamini–Hochberg"). Do not invent letters
  the stats stage did not produce.
- **Function:** `boxplot_by_group(...)`.

### 3.3 Spatial interpolation map (IDW / kriging)
- **Shows:** a continuous concentration surface inferred between sampling points.
- **When:** dense, well-distributed sampling where a continuous gradient is scientifically meaningful
  (e.g. groundwater plume, surface-soil contamination). **Not** for sparse or clustered points.
- **Gotchas:** **report the method and its parameters** — IDW power, or for kriging the **variogram
  model and cross-validation** (RMSE / mean error). Show sample points on top of the surface so the
  reader sees coverage; do not extrapolate far beyond the sampled hull (mask it). Same CRS/scale-bar/
  north-arrow rules as §3.1. State that interpolated values are estimates, not measurements.
- **Function:** recipe over `spatial_scatter_map` + an interpolation library (e.g. `scipy`/`pykrige`);
  overlay sample markers via the same plotter.

### 3.4 Time series
- **Shows:** temporal trend of one or more analytes (across campaigns, months, hydrological events).
- **When:** repeated sampling over time; before/after an intervention; seasonal cycles.
- **Gotchas:** **define error bars in the caption** (SD / SE / 95% CI) **with n**; mark the
  **detection-limit** as a reference line if any points are near/below LOD (and say how non-detects were
  handled — see `data-analysis.md`); do not connect points across a gap that implies data you do not
  have. One season of data cannot support a "trend" claim — flag over-generalization.
- **Function:** `time_series(...)`.

### 3.5 Correlation heatmap
- **Shows:** pairwise associations among analytes / parameters (co-source signal, geochemical control).
- **When:** exploring which variables move together before PCA / source apportionment.
- **Gotchas:** **state which coefficient** — **Spearman is the default for raw environmental
  concentrations** (right-skewed, often censored); Pearson only after a transform that achieves
  normality. Use a **diverging colormap centered at 0** (`RdBu_r`, `vmin=-1, vmax=1`). **Star only
  cells that survive multiple-testing correction** and record the correction in the caption. Correlation
  ≠ causation; do not imply mechanism from the heatmap alone.
- **Function:** `correlation_heatmap(...)`.

### 3.6 PCA biplot
- **Shows:** sample scores + variable loadings in reduced space; grouping by site/season; latent
  source/process structure.
- **When:** multivariate pattern + tentative source grouping after auto-scaling the data.
- **Gotchas:** **axis labels must show the explained variance** — `PC1 (xx.x%)`, `PC2 (xx.x%)`; state
  that data were **auto-scaled (z-scored)** in the caption; color groups with a colorblind-safe
  categorical palette; do not over-interpret components explaining little variance.
- **Function:** `pca_biplot(...)`.

### 3.7 Cluster dendrogram / heatmap (HCA)
- **Shows:** hierarchical grouping of sites or analytes; a clustered heatmap pairs the dendrogram with
  a z-scored value matrix.
- **When:** classifying sampling sites into pollution regimes; grouping co-behaving analytes.
- **Gotchas:** **state the distance metric and linkage** (e.g. Euclidean + Ward) in the caption —
  results change with both; **z-score** rows/columns before heatmapping so one high-magnitude analyte
  does not dominate; use a diverging colormap for the z-scored matrix, sequential for raw. Mask NaN
  cells to white, not to a data color.
- **Function:** recipe over `correlation_heatmap`/`make_heatmap`-style imshow + `scipy.cluster.hierarchy`
  for the dendrogram; share the figure's style via `set_envsci_style`.

### 3.8 Stacked composition bars
- **Shows:** fractional/absolute profiles — PAH ring distributions, PCB/PBDE congener patterns, ionic
  composition, grain-size fractions — per site or sample.
- **When:** comparing *patterns* (fingerprints) across samples, not just totals.
- **Gotchas:** keep the **component order identical** across all bars (so a stack reads left-to-right
  consistently); if showing %, say "normalized to 100%"; use an ordered, colorblind-safe categorical
  palette and consider **direct in-bar labels** for dense profiles instead of a long detached legend;
  if absolute, the y-axis still needs **units + basis**.
- **Function:** `stacked_composition(...)`.

### 3.9 Hydrochemistry diagrams (Piper / Stiff / Gibbs / Durov)
- **Shows:** water-type classification and the processes controlling water chemistry.
  - **Piper** — major-ion water facies (Ca-HCO₃, Na-Cl, …).
  - **Stiff** — per-sample ionic shape signature for quick spatial comparison.
  - **Gibbs** — whether chemistry is rock-, evaporation-, or precipitation-dominated (TDS vs ion ratios).
  - **Durov** — water type + an extra process dimension.
- **When:** groundwater / surface-water hydrochemistry papers with major-ion data (meq L⁻¹).
- **Gotchas:** ions must be converted to **milliequivalents (meq L⁻¹)** and the **cation/anion balance
  checked** (typically within ±5–10%) before plotting — say so. Specialized geometry is best produced
  with a dedicated library (**WQChartPy**); style the surrounding text/labels to match the rest of the
  figure set. State the data source for any reference fields/lines.
- **Function:** external (WQChartPy) recipe; apply `set_envsci_style()` for fonts/export consistency.

### 3.10 Pollution-index / risk bars (with threshold reference lines)
- **Shows:** Igeo / EF / CF / PLI / Er / RI / Nemerow / WQI, or HQ/HI/CR per site, against
  classification thresholds.
- **When:** the summary "how polluted / how risky" figure in Results/Discussion.
- **Gotchas:** **draw the classification thresholds as horizontal reference lines** (e.g. Igeo class
  boundaries 0/1/2/3/4/5; HQ/HI = 1; CR = 1e-6 and 1e-4) and label them; the index values, background
  Bn, and toxic-response factors must come from the **stats stage with their canonical citations** (see
  `data-analysis.md` Gate S) — figures never introduce new numbers. Keep the same site order/colors as
  the other panels.
- **Function:** grouped/horizontal bar recipe over the shared style (use the bar conventions in §5.6);
  add `ax.axhline(threshold, ls='--', color='#767676')` per boundary.

---

## 4. Using `scripts/envsci_style.py` (import → style → plot → save)

> The script is a **tool you run/import**, not prose to read into context. All plotters **return
> `(fig, ax)`**, **never call `plt.show()`**, and saving is **always explicit** via `save_figure`.
> Snippets below match the public API exactly — keep them consistent if you adapt them.

### 4.1 Setup: import + global style (always first)

```python
import matplotlib
matplotlib.use("Agg")                 # headless / batch safe; set BEFORE importing pyplot
import matplotlib.pyplot as plt
import pandas as pd

import sys
sys.path.append("scripts")            # or the absolute path to the skill's scripts/ dir
from envsci_style import (
    set_envsci_style, fig_size, save_figure,
    boxplot_by_group, correlation_heatmap, pca_biplot,
    time_series, spatial_scatter_map, stacked_composition,
)

# Apply publication rcParams ONCE before creating any figure.
# Sets: Arial/DejaVu sans-serif, svg.fonttype='none', pdf.fonttype=42,
# top/right spines off, frameless legends, 7 pt base; registers colorblind-safe
# palettes and bans rainbow/jet from the default cycle.
set_envsci_style(base_font_pt=7.0, palette="okabe_ito", sequential="viridis")
```

`set_envsci_style` arguments:
- `base_font_pt` (default `7.0`) — journal-final text size; bump to ~9 only for slide-size drafts.
- `palette` — categorical cycle: `"okabe_ito"` (default) or `"tol_bright"`.
- `sequential` — sequential colormap default: `"viridis"` (or `"cividis"`).

### 4.2 Sizing a figure

```python
# Single column ≈ 89 mm; double ≈ 183 mm. Returns (w_in, h_in); mm→in handled internally.
w, h = fig_size("double", height_mm=110)
fig, ax = plt.subplots(figsize=(w, h))
```

### 4.3 Saving (SVG first, then PNG; tight_layout + close handled for you)

```python
# Writes name.svg (editable text) then name.png (300 dpi). Use dpi=600 for dense panels.
paths = save_figure(fig, "figures/fig3_sediment_cd", formats=("svg", "png"), dpi=300)
# paths -> ['figures/fig3_sediment_cd.svg', 'figures/fig3_sediment_cd.png']
# save_figure() calls fig.tight_layout() then plt.close(fig) internally — do not re-close.
```

### 4.4 Plotters (each: data + grouping → `(fig, ax)`)

> ⚠️ **Placeholder axis labels are intentional — you MUST override them.** Every plotter sets a
> stand-in label like `Cd  [units, state dw/ww]`. Replace it with the real quantity + unit + dry/wet
> basis (e.g. `ax.set_ylabel(r"Cd (mg kg$^{-1}$ dw)")`) **before** `save_figure()`. A figure shipped
> with the placeholder text still in it **fails Gate-F row 3 (units)**.

**Boxplot by site/season + significance letters (§3.2):**
```python
fig, ax = boxplot_by_group(
    df, value="Cd_mg_kg", group="site",
    log_y=True,                          # values span >2 orders of magnitude
    sig_letters={"S1": "a", "S2": "ab", "S3": "b"},   # from the post-hoc test, NOT invented
    order=["S1", "S2", "S3"],
)
ax.set_ylabel("Cd (mg kg$^{-1}$ dw)")    # units + basis are mandatory
ax.text(0.0, -0.18, "Kruskal–Wallis + Dunn (BH); n=5 per site; box=IQR, whiskers=1.5×IQR",
        transform=ax.transAxes, fontsize=6)   # caption note: test + n + spread definition
save_figure(fig, "figures/fig2_cd_by_site")
```

**Correlation heatmap (§3.5):**
```python
fig, ax = correlation_heatmap(
    df[["Cd", "Pb", "Zn", "Cu", "TOC"]],
    method="spearman",                   # default for raw concentrations
    annot_significant=True,              # star cells passing multiple-testing correction
    cmap="RdBu_r", vmin=-1, vmax=1,      # diverging, centered at 0
)
# caption MUST record: "Spearman ρ; * = p<0.05 after Benjamini–Hochberg correction"
save_figure(fig, "figures/fig4_corr", dpi=600)
```

**PCA biplot (§3.6):**
```python
fig, ax = pca_biplot(
    df, features=["Cd", "Pb", "Zn", "Cu", "TOC"],
    color_by="site",                     # samples colored by a categorical column (optional)
    standardize=True,                    # z-score auto-scaling (mandatory for mixed units)
)
# PCA is computed INSIDE the function (numpy SVD) from df[features] — do NOT pre-compute
# scores/loadings. Axis labels already carry "PC1 (xx.x%)".
# caption: "Variables auto-scaled (z-score) prior to PCA."
save_figure(fig, "figures/fig5_pca")
```

**Time series with error bars + detection limit (§3.4):**
```python
fig, ax = time_series(
    df, time="month", value="NO3_mg_L", group="site",
    error="ci", n=5,                     # error type defined; n recorded for the caption
    detection_limit=0.05,                # draws a reference line; explain non-detect handling
)
ax.set_ylabel("NO$_3^-$ (mg L$^{-1}$)")
save_figure(fig, "figures/fig6_no3_timeseries")
```

**Sampling-site map (§3.1):**
```python
fig, ax = spatial_scatter_map(
    df, lon="lon", lat="lat", value="PLI",
    crs="EPSG:32650",                    # projected CRS — STATE IT in the caption
    scalebar=True, north_arrow=True,
)
# A regional locator INSET is added in your GIS step (QGIS/ArcGIS), not by this function.
# caption: CRS, basemap source, what marker color encodes
save_figure(fig, "figures/fig1_sites", dpi=600)
```

**Stacked composition profiles (§3.8):**
```python
fig, ax = stacked_composition(
    df, sample_col="site", fraction_cols=["2-3 ring", "4 ring", "5-6 ring"],
    normalize=True,                      # -> % composition; say "normalized to 100%"
    order=["S1", "S2", "S3"],            # consistent sample order across all bars
)
save_figure(fig, "figures/fig7_pah_profile")
```

### 4.5 CLI demo (prove the API runs without your own data)

```bash
python scripts/envsci_style.py --demo boxplot --out figures/ --columns double --format svg,png
# --demo {boxplot|heatmap|pca|timeseries|map|stacked}
# generates a self-contained figure from synthetic env data to confirm the install/API works.
```

### 4.6 Backend exclusivity (Gate-F row)

One backend produces all plotting, previews, exports, and QA renders for a given figure. If the chosen
backend (or a needed package like a geo/hydrochem library) is missing, **stop and report the missing
runtime** — do not silently substitute a different tool or fall back to a non-comparable export.

### 4.7 Runtime dependencies

`scripts/envsci_style.py` needs only three packages; everything else is optional and lazily imported:

| Package | Required? | Used for |
|---------|-----------|----------|
| `matplotlib`, `numpy`, `pandas` | **required** | all plotters, styling, export |
| `scipy` | optional | p-value stars in `correlation_heatmap`; gracefully skipped if absent |
| geo backend (`geopandas`/`contextily`) | optional | real tiled basemap behind `spatial_scatter_map` (falls back to a clean CRS-labelled panel) |
| `pykrige`/`scipy` | optional | kriging/IDW interpolation surfaces |

Install the core set with `pip install -r scripts/requirements.txt`. **On Windows, if `python` opens
the Microsoft Store, use the `py` launcher instead** (e.g. `py scripts/envsci_style.py --demo all`).
This is the canonical dependency list Gate-F row 10 ("backend exclusivity → report the missing runtime")
checks against.

---

## 5. Cross-cutting conventions (enforceable on every figure)

### 5.1 Units & basis — non-negotiable
Every quantitative axis carries **units** and, for solids, the **dry-weight vs wet-weight basis**:
- Water: `mg L⁻¹`, `µg L⁻¹`, `ng L⁻¹`.
- Solids (soil/sediment/sludge/biota): `mg kg⁻¹ dw` / `µg g⁻¹ dw` (or `ww` — **state which**).
- Air/aerosol: `µg m⁻³`, `ng m⁻³`.
A solid-matrix axis without `dw`/`ww` **fails Gate F**.

### 5.2 Error bars & n
Define the error representation in the **caption** — SD, SE, or 95% CI — **with the sample size n**.
"Error bars" with no definition fails Gate F. State the center statistic too (mean vs median;
arithmetic vs geometric mean for log-transformed data).

### 5.3 Colorblind safety
- Sequential: `viridis` / `cividis`. Categorical: Okabe–Ito / Tol-bright. Diverging: `RdBu_r` at 0.
- **No rainbow / jet / hsv.** Never encode by red–green alone — add shape/position/label.
- The figure must still read in grayscale (check by desaturating before delivery).

### 5.4 Log axes
Use log10 when data span ≥2 orders of magnitude. **Label the variable, not "log(x)"**, keep real-value
tick labels, and state the base (10) in the caption. Do not log-transform data that crosses zero or
contains true zeros without first explaining the offset.

### 5.5 Maps
Sampling/interpolation maps need a **stated projected CRS**, **scale bar**, **north arrow**, **regional
inset**, and a basemap/data-source note. Lat/lon-only scatter with no furniture fails Gate F.

### 5.6 Bars, significance, layout
- Pollution-index / concentration bars: include **threshold reference lines** with labels; keep edge
  color on bars for separation; hide x-tick labels only if the legend already names the groups.
- Significance: state the **annotation method** (letters from post-hoc, or `*`/`**`/`***` with the
  p-value mapping) and the underlying test + correction in the caption. Never annotate significance the
  stats stage did not compute.
- Spines top/right off, frameless legend, sparse y-ticks, no chartjunk (no 3-D bars, no gradient fills,
  no decorative panel boxes). Tighten y-limits to the data range; do not pad to 0–100 when values sit in
  a narrow band (unless an absolute reference like 100% or a guideline value is the point).
- Multi-panel: each panel a unique question; one shared legend strip beats repeated legends; panel
  letters lowercase bold top-left ~8 pt.

---

## 6. FIGURE-QA CONTRACT (Gate F — pass/fail)

Run this table before delivering any figure, before a revision package, and whenever a figure carries a
statistical, spatial, or risk claim. **Every HARD row must pass.** A failing HARD row blocks Stage 4 and
is reported as a `[FIGURE GAP]`. Soft rows are recommendations; note any you waive and why.

| # | Check | Pass condition | Type |
|---|---|---|---|
| 1 | Core conclusion | A one-sentence claim (with a verb) exists and **every panel maps to it** | HARD |
| 2 | Archetype & hierarchy | Figure has a declared archetype; hero panel ≠ support panels; no redundant panel re-showing another's data | HARD |
| 3 | Axis units + basis | Every quantitative axis has units; **every solid-matrix axis states dw or ww** | HARD |
| 4 | Error bars + n | Error representation (SD/SE/95% CI) **defined in caption with n**; center statistic stated | HARD |
| 5 | Colorblind-safe | No rainbow/jet; **red–green is not the only encoding**; figure interpretable in grayscale | HARD |
| 6 | Significance annotation | Method stated (letters from post-hoc, or `*` mapping) + test + correction in caption; matches stats stage | HARD |
| 7 | Map furniture | Any map has **stated projected CRS + scale bar + north arrow** (inset recommended; basemap sourced) | HARD |
| 8 | Log axes | Log axes label the **variable** (not "log x") with real tick values; base stated in caption | HARD |
| 9 | Source-data trace | Every plotted value traces to a Data-Ledger cell / clean CSV-XLSX / script output | HARD |
| 10 | Backend exclusivity | One backend produced all plotting, previews, exports, and QA renders | HARD |
| 11 | Resolution / vector | ≥300 dpi raster (600 for dense); **SVG primary** with editable text; vector used for line/marker art | HARD |
| 12 | Final size | Single-column ~89 mm or double ~183 mm; height ≤ journal limit; text legible at 5–7 pt | HARD |
| 13 | Threshold lines | Index/risk plots draw + label classification thresholds (Igeo classes, HQ/HI=1, CR 1e-6/1e-4) | SOFT |
| 14 | Interpolation rigor | IDW power / kriging variogram + cross-validation reported; sample points overlaid; no wild extrapolation | SOFT |
| 15 | Ion balance | Hydrochem diagrams use meq L⁻¹ with cation/anion balance checked (±5–10%) | SOFT |
| 16 | Legend economy | Shared/direct labels where possible; no repeated redundant legends; legend quieter than data | SOFT |
| 17 | Panel labels | Lowercase, bold, top-left, ~8 pt at final size | SOFT |

### 6.1 Per-panel statistics legend (capture for every quantitative panel)
```text
n definition (replicate vs site vs sample):
biological/field replicates:
technical/analytical replicates:
center statistic (mean / median / geometric mean):
spread/interval (SD / SE / 95% CI):
test:
multiple-comparison correction:
significance display (letters / p-value mapping):
source-data file:
```

### 6.2 Reviewer-risk prompts (ask before finalizing)
- Is the sample size visible in the legend/caption or source data?
- Are error bars, intervals, and the test defined — and is the test appropriate for skewed/censored env
  data (Spearman not Pearson on raw concentrations; non-parametric where normality fails)?
- Does the design risk **pseudoreplication** (sub-samples treated as independent sites)? Does the figure
  imply more independent replication than exists?
- Are axes comparable across panels that invite comparison? Same site order/colors throughout?
- For maps: representative coverage shown? interpolation honest about where data are sparse?
- Could the same conclusion be made with **fewer panels**?

---

## 7. Handoff

Emit, into the session, for each figure: the **Figure Contract**, the **Gate-F verdict** (pass, or the
list of failing HARD rows as `[FIGURE GAP]`s), the **caption draft** (with units/basis, n, error
definition, test + correction, CRS for maps), and the **source-data trace**. These feed the writing
stage (Results/Discussion reference the panels) and the integrity stage (caption fidelity is checked in
`citations-and-integrity.md` Gate I, phase C). A figure that has not passed Gate F must not be cited as
final evidence downstream.
