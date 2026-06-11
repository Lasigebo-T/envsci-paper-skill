#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""envsci_style.py — publication-grade matplotlib style + environmental-science plotters.

This module is the figure engine for the ``enviro-paper`` skill (Stage 4 / ``figures``
mode). It enforces the journal-figure conventions used across env-sci venues (STOTEN,
Water Research, ES&T, Environmental Pollution, JHM, ESPR, ...) and ships a small catalogue
of ready-made plotters that map 1:1 to the recipes in ``references/figures.md``.

Design rules (enforced here, audited by the Figure-QA contract / Gate F):
  * Colorblind-safe by default. Categorical = Okabe-Ito / Tol-bright; sequential = viridis/
    cividis. Rainbow / jet are never used.
  * Editable SVG text: ``svg.fonttype='none'`` and ``pdf.fonttype=42`` so labels stay as
    real <text> nodes for Illustrator / Inkscape.
  * SVG is the primary export, PNG (>=300 dpi) the secondary. ``save_figure`` writes both.
  * Every plotter RETURNS ``(fig, ax)``; none calls ``plt.show()``; saving is always explicit.
  * Axis labels carry a units placeholder so the user is reminded to state units + the
    dry-weight / wet-weight basis (a Gate-F requirement). Error bars are defined with ``n``.

Dependencies: matplotlib + numpy + pandas only. ``scipy`` / ``sklearn`` are imported LAZILY
inside the functions that can benefit from them (and every such function has a pure-numpy
fallback), so the module imports cleanly with only the three core packages installed.

Typical use
-----------
    from envsci_style import set_envsci_style, fig_size, save_figure, boxplot_by_group
    set_envsci_style()
    fig, ax = boxplot_by_group(df, value="Pb_mg_kg", group="site", log_y=True,
                               sig_letters={"S1": "a", "S2": "b", "S3": "ab"})
    ax.set_ylabel(r"Pb (mg kg$^{-1}$ dw)")          # ALWAYS state units + dw/ww basis
    save_figure(fig, "fig2_pb_by_site", formats=("svg", "png"), dpi=300)

CLI smoke test (generates one demo figure per plotter into ``_demo_figs/``)::

    python envsci_style.py                         # all demos, single-column
    python envsci_style.py --demo boxplot --out figs --columns double --format svg,png

Python 3.9+. Headless-safe (forces the ``Agg`` backend when imported without a display).
"""

from __future__ import annotations

import argparse
import os
import sys
from typing import Optional, Sequence, Tuple

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Headless safety: pick a non-interactive backend BEFORE importing pyplot when
# no display is available (CI, batch figure generation, the skill's runtime).
# ---------------------------------------------------------------------------
import matplotlib

if os.environ.get("MPLBACKEND") is None and not os.environ.get("DISPLAY") and sys.platform not in ("darwin", "win32"):
    matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402


def _get_cmap(name):
    """matplotlib-version-agnostic colormap lookup (avoids the deprecated cm.get_cmap)."""
    try:
        return matplotlib.colormaps[name]            # matplotlib >= 3.5
    except Exception:                                # pragma: no cover - very old mpl
        return plt.get_cmap(name)


# ===========================================================================
# 1. Colorblind-safe palettes  (Okabe-Ito + Paul Tol "bright")
# ===========================================================================
# Okabe & Ito (2008), "Color Universal Design" — 8 hues distinguishable under the
# common forms of color-vision deficiency and legible in grayscale.
OKABE_ITO = [
    "#0072B2",  # blue
    "#E69F00",  # orange
    "#009E73",  # bluish green
    "#D55E00",  # vermillion
    "#CC79A7",  # reddish purple
    "#56B4E9",  # sky blue
    "#F0E442",  # yellow
    "#000000",  # black
]

# Paul Tol "bright" — an alternative categorical set, also CVD-safe.
TOL_BRIGHT = [
    "#4477AA",  # blue
    "#EE6677",  # red
    "#228833",  # green
    "#CCBB44",  # yellow
    "#66CCEE",  # cyan
    "#AA3377",  # purple
    "#BBBBBB",  # grey
]

# Sequential / diverging colormaps that are perceptually uniform AND CVD-safe.
SEQUENTIAL_SAFE = ("viridis", "cividis", "mako", "magma", "plasma")
DIVERGING_SAFE = ("RdBu_r", "BrBG", "PuOr", "coolwarm")

# Colormaps we explicitly refuse to emit (perceptually misleading / not CVD-safe).
_BANNED_CMAPS = {"jet", "rainbow", "gist_rainbow", "hsv", "nipy_spectral", "gist_ncar"}

_PALETTES = {"okabe_ito": OKABE_ITO, "tol_bright": TOL_BRIGHT}

# Module-level active palette; reset by ``set_envsci_style``.
_ACTIVE_PALETTE = list(OKABE_ITO)


def get_palette(name: str = "okabe_ito") -> list:
    """Return a copy of a named colorblind-safe categorical palette.

    Parameters
    ----------
    name : {"okabe_ito", "tol_bright"}
    """
    key = name.lower()
    if key not in _PALETTES:
        raise ValueError(f"Unknown palette {name!r}; choose from {sorted(_PALETTES)}.")
    return list(_PALETTES[key])


def get_colors(n: int, palette: str = "okabe_ito") -> list:
    """Return ``n`` colorblind-safe categorical colors.

    For ``n`` up to the palette length, returns distinct hues. For larger ``n`` it
    cycles the palette (a warning that you probably have too many categories for a
    single legible figure — consider faceting).
    """
    base = get_palette(palette)
    if n <= len(base):
        return base[:n]
    reps = (n + len(base) - 1) // len(base)
    return (base * reps)[:n]


def _safe_cmap(cmap: str, *, kind: str = "sequential") -> str:
    """Reject rainbow/jet; fall back to a safe default of the requested kind."""
    if cmap is None:
        return "viridis" if kind == "sequential" else "RdBu_r"
    if cmap.replace("_r", "") in _BANNED_CMAPS or cmap in _BANNED_CMAPS:
        fallback = "viridis" if kind == "sequential" else "RdBu_r"
        import warnings

        warnings.warn(
            f"Colormap {cmap!r} is not colorblind-safe (banned). Using {fallback!r} instead.",
            stacklevel=2,
        )
        return fallback
    return cmap


# ===========================================================================
# 2. Publication style  (rcParams)
# ===========================================================================
def set_envsci_style(
    base_font_pt: float = 7.0,
    palette: str = "okabe_ito",
    sequential: str = "viridis",
) -> None:
    """Apply env-sci publication rcParams. Call ONCE before creating any figure.

    Concrete settings (journal-figure standard, adapted from the nature-figure study):
      * sans-serif Arial -> Helvetica -> DejaVu Sans fallback chain
      * ``svg.fonttype='none'`` (editable SVG text) and ``pdf.fonttype=42`` (TrueType)
      * base font ``base_font_pt`` (7 pt is the journal small-multiple default; bump to
        8 for single large panels)
      * top/right spines off, thin axes (0.8 pt), small ticks, legend frame off
      * ``savefig.dpi=300``, white figure/axes facecolor, tight bbox on save
      * registers the colorblind-safe categorical palette as the default color cycle
        and sets a CVD-safe sequential colormap; rainbow/jet are never the default.

    Parameters
    ----------
    base_font_pt : float
        Base font size in points. Tick labels scale to ~0.85x, titles to ~1.1x.
    palette : {"okabe_ito", "tol_bright"}
        Default categorical color cycle.
    sequential : str
        Default sequential colormap (must be CVD-safe; rainbow/jet are rejected).
    """
    global _ACTIVE_PALETTE
    _ACTIVE_PALETTE = get_palette(palette)
    seq = _safe_cmap(sequential, kind="sequential")

    small = round(base_font_pt * 0.85, 1)

    rc = {
        # --- fonts (MANDATORY editable-text trio first) ---
        "font.family": "sans-serif",
        "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans", "Liberation Sans"],
        "svg.fonttype": "none",
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        # --- font sizes ---
        "font.size": base_font_pt,
        "axes.titlesize": round(base_font_pt * 1.1, 1),
        "axes.labelsize": base_font_pt,
        "xtick.labelsize": small,
        "ytick.labelsize": small,
        "legend.fontsize": small,
        "figure.titlesize": round(base_font_pt * 1.2, 1),
        # --- spines / axes ---
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.linewidth": 0.8,
        "axes.edgecolor": "#333333",
        "axes.labelcolor": "#000000",
        "axes.titlelocation": "left",
        "axes.titleweight": "bold",
        "axes.grid": False,
        # --- ticks (small, outward) ---
        "xtick.direction": "out",
        "ytick.direction": "out",
        "xtick.major.size": 2.5,
        "ytick.major.size": 2.5,
        "xtick.major.width": 0.8,
        "ytick.major.width": 0.8,
        "xtick.minor.size": 1.5,
        "ytick.minor.size": 1.5,
        "xtick.color": "#333333",
        "ytick.color": "#333333",
        # --- lines / markers ---
        "lines.linewidth": 1.2,
        "lines.markersize": 4.0,
        "lines.markeredgewidth": 0.6,
        # --- legend ---
        "legend.frameon": False,
        "legend.handlelength": 1.4,
        "legend.handletextpad": 0.5,
        "legend.columnspacing": 1.0,
        "legend.borderaxespad": 0.3,
        # --- figure / save ---
        "figure.facecolor": "white",
        "figure.dpi": 150,
        "savefig.dpi": 300,
        "savefig.facecolor": "white",
        "savefig.bbox": "tight",
        "savefig.pad_inches": 0.02,
        "axes.facecolor": "white",
        # --- image defaults (CVD-safe sequential) ---
        "image.cmap": seq,
        # --- math text uses the regular font (no italic serif by default) ---
        "mathtext.default": "regular",
    }
    plt.rcParams.update(rc)
    # Default categorical color cycle.
    plt.rcParams["axes.prop_cycle"] = plt.cycler(color=_ACTIVE_PALETTE)


# ===========================================================================
# 3. Sizing + saving
# ===========================================================================
# Journal column widths.  Single column ~= 89 mm, double column ~= 183 mm.
_MM_PER_IN = 25.4
_WIDTH_MM = {"single": 89.0, "double": 183.0, 1: 89.0, 2: 183.0}


def fig_size(columns="single", ratio: float = 0.75, height_mm: Optional[float] = None) -> Tuple[float, float]:
    """Return ``(width_in, height_in)`` for a single- or double-column figure.

    Parameters
    ----------
    columns : {"single", "double", 1, 2}
        ``single`` -> 89 mm wide, ``double`` -> 183 mm wide.
    ratio : float
        Height-to-width ratio when ``height_mm`` is not given (default 0.75).
    height_mm : float, optional
        Explicit height in millimetres; overrides ``ratio``.
    """
    if columns not in _WIDTH_MM:
        raise ValueError("columns must be one of 'single', 'double', 1, 2.")
    w_mm = _WIDTH_MM[columns]
    h_mm = float(height_mm) if height_mm is not None else w_mm * ratio
    return (w_mm / _MM_PER_IN, h_mm / _MM_PER_IN)


def save_figure(
    fig,
    name: str,
    formats: Sequence[str] = ("svg", "png"),
    dpi: int = 300,
    outdir: Optional[str] = None,
    tight: bool = True,
) -> list:
    """Save ``fig`` to one or more formats. SVG is written first (editable text).

    The figure is closed after saving (free memory; never leak open figures in a
    batch run). ``name`` may be a bare stem ("fig2_pb") or include a directory.

    Parameters
    ----------
    fig : matplotlib Figure
    name : str
        Path stem WITHOUT extension (e.g. ``"figs/fig2_pb_by_site"``). If ``outdir``
        is given, it is prepended.
    formats : sequence of str
        Any of svg, png, pdf, tiff/tif, eps, jpg. SVG is always emitted first if present.
    dpi : int
        Raster dpi (300 standard; pass 600 for dense maps/heatmaps).
    outdir : str, optional
        Directory to write into (created if missing).
    tight : bool
        Apply ``fig.tight_layout()`` before saving.

    Returns
    -------
    list[str] : the written file paths.
    """
    stem = name
    if outdir:
        os.makedirs(outdir, exist_ok=True)
        stem = os.path.join(outdir, os.path.basename(name))
    else:
        parent = os.path.dirname(stem)
        if parent:
            os.makedirs(parent, exist_ok=True)

    # Strip any extension the caller accidentally included.
    root, ext = os.path.splitext(stem)
    if ext.lstrip(".").lower() in {"svg", "png", "pdf", "tiff", "tif", "eps", "jpg", "jpeg"}:
        stem = root

    if tight:
        try:
            fig.tight_layout()
        except Exception:
            pass  # tight_layout can fail on exotic layouts; saving still proceeds.

    # SVG first, then everything else.
    ordered = sorted(formats, key=lambda f: 0 if f.lower() == "svg" else 1)
    written = []
    for fmt in ordered:
        fmt = fmt.lower()
        path = f"{stem}.{fmt}"
        save_kw = {"dpi": dpi}
        if fmt in ("tiff", "tif"):
            save_kw["pil_kwargs"] = {"compression": "tiff_lzw"}
        fig.savefig(path, **save_kw)
        written.append(path)

    plt.close(fig)
    return written


# ===========================================================================
# 4. Small internal helpers
# ===========================================================================
def _new_ax(ax, columns="single", ratio: float = 0.75):
    """Return ``(fig, ax)``; create a correctly-sized figure if ``ax`` is None."""
    if ax is None:
        fig, ax = plt.subplots(figsize=fig_size(columns, ratio))
    else:
        fig = ax.figure
    return fig, ax


def _clean_numeric(s: pd.Series) -> pd.Series:
    """Coerce to numeric and drop NaN/inf."""
    s = pd.to_numeric(s, errors="coerce")
    return s[np.isfinite(s)]


def _contrast_text_color(rgb) -> str:
    """Black or white text for legibility on a colored cell (luminance rule)."""
    r, g, b = rgb[:3]
    lum = 0.299 * r + 0.587 * g + 0.114 * b
    return "white" if lum < 0.5 else "black"


# ===========================================================================
# 5. Plotters  (each returns (fig, ax); each enforces a Gate-F convention)
# ===========================================================================
def boxplot_by_group(
    df: pd.DataFrame,
    value: str,
    group: str,
    *,
    hue: Optional[str] = None,
    log_y: bool = False,
    sig_letters: Optional[dict] = None,
    order: Optional[Sequence] = None,
    palette: str = "okabe_ito",
    show_points: bool = True,
    ax=None,
):
    """Boxplot of ``value`` grouped by ``group`` (e.g. site or season).

    Concentration data are usually right-skewed and span orders of magnitude — pass
    ``log_y=True`` for a base-10 log axis (the label is annotated, not relabelled to
    "log x"). Post-hoc significance letters (a, b, ab, ...) from a Tukey/Dunn test can
    be supplied via ``sig_letters`` and are drawn above each box. Raw points are
    overlaid (jittered) when groups are small so the reader sees the real ``n``.

    Parameters
    ----------
    df : DataFrame
    value, group : str
        Column names. ``value`` is numeric; ``group`` is categorical.
    hue : str, optional
        Optional second grouping (e.g. season within site) -> side-by-side boxes.
    log_y : bool
        Use a base-10 log y-axis (only valid for strictly positive data).
    sig_letters : dict, optional
        ``{group_level: "a"}`` compact-letter-display annotations.
    order : sequence, optional
        Explicit ordering of group levels.
    palette : str
        Colorblind-safe palette name.
    show_points : bool
        Overlay jittered raw observations.

    Returns
    -------
    (fig, ax)

    Notes
    -----
    Set ``ax.set_ylabel`` to include UNITS and the dw/ww basis (Gate F). The caption
    must state the box elements (median, IQR, whiskers = 1.5*IQR) and ``n`` per group.
    """
    if value not in df or group not in df:
        raise KeyError(f"Columns {value!r} and {group!r} must exist in the DataFrame.")

    work = df[[group, value] + ([hue] if hue else [])].copy()
    work[value] = pd.to_numeric(work[value], errors="coerce")
    work = work[np.isfinite(work[value])]

    levels = list(order) if order is not None else list(pd.unique(work[group]))
    fig, ax = _new_ax(ax)

    if hue:
        hue_levels = list(pd.unique(work[hue]))
        colors = get_colors(len(hue_levels), palette)
        n_h = len(hue_levels)
        width = 0.8 / max(n_h, 1)
        for hi, hlev in enumerate(hue_levels):
            positions, data = [], []
            for gi, glev in enumerate(levels):
                vals = _clean_numeric(work.loc[(work[group] == glev) & (work[hue] == hlev), value])
                if len(vals) == 0:
                    continue
                positions.append(gi + (hi - (n_h - 1) / 2) * width)
                data.append(vals.values)
            if data:
                bp = ax.boxplot(
                    data, positions=positions, widths=width * 0.9,
                    patch_artist=True, showfliers=False, manage_ticks=False,
                )
                _style_box(bp, colors[hi % len(colors)])
                bp["boxes"][0].set_label(str(hlev))
        ax.legend(title=str(hue))
    else:
        colors = get_colors(len(levels), palette)
        data, positions, ns = [], [], []
        for gi, glev in enumerate(levels):
            vals = _clean_numeric(work.loc[work[group] == glev, value])
            data.append(vals.values)
            positions.append(gi)
            ns.append(len(vals))
        bp = ax.boxplot(
            data, positions=positions, widths=0.6,
            patch_artist=True, showfliers=False, manage_ticks=False,
        )
        for i, box in enumerate(bp["boxes"]):
            _style_box_single(bp, i, colors[i % len(colors)])
        if show_points:
            rng = np.random.default_rng(0)
            for gi, vals in enumerate(data):
                if len(vals) and len(vals) <= 40:
                    jit = rng.uniform(-0.12, 0.12, size=len(vals))
                    ax.scatter(np.full(len(vals), gi) + jit, vals, s=8,
                               color="#333333", alpha=0.55, zorder=3, linewidths=0)
        # annotate n under each group
        for gi, n in enumerate(ns):
            ax.annotate(f"n={n}", (gi, 0), xytext=(0, -14),
                        textcoords="offset points", ha="center", va="top",
                        fontsize=plt.rcParams["xtick.labelsize"] * 0.8, color="#666666")

    if log_y:
        ax.set_yscale("log")

    ax.set_xticks(range(len(levels)))
    ax.set_xticklabels([str(x) for x in levels])
    ax.set_xlabel(str(group))
    ax.set_ylabel(f"{value}  [units, state dw/ww]")

    # Significance letters above each box.
    if sig_letters:
        ymax = ax.get_ylim()[1]
        for gi, glev in enumerate(levels):
            letter = sig_letters.get(glev)
            if letter is None:
                continue
            vals = _clean_numeric(work.loc[work[group] == glev, value])
            top = vals.max() if len(vals) else (ymax if not log_y else ymax)
            ax.annotate(str(letter), (gi, top), xytext=(0, 4),
                        textcoords="offset points", ha="center", va="bottom",
                        fontweight="bold", fontsize=plt.rcParams["font.size"])

    return fig, ax


def _style_box(bp, color):
    """Color every box in a boxplot dict (used for the hued path)."""
    for box in bp["boxes"]:
        box.set(facecolor=color, edgecolor="#222222", linewidth=0.8, alpha=0.85)
    for med in bp["medians"]:
        med.set(color="#111111", linewidth=1.1)
    for w in bp["whiskers"] + bp["caps"]:
        w.set(color="#444444", linewidth=0.8)


def _style_box_single(bp, i, color):
    """Color the i-th box (used for the single-grouping path)."""
    bp["boxes"][i].set(facecolor=color, edgecolor="#222222", linewidth=0.8, alpha=0.85)
    bp["medians"][i].set(color="#111111", linewidth=1.1)
    for j in (2 * i, 2 * i + 1):
        if j < len(bp["whiskers"]):
            bp["whiskers"][j].set(color="#444444", linewidth=0.8)
        if j < len(bp["caps"]):
            bp["caps"][j].set(color="#444444", linewidth=0.8)


def correlation_heatmap(
    df: pd.DataFrame,
    *,
    columns: Optional[Sequence[str]] = None,
    method: str = "spearman",
    annot_significant: bool = True,
    cmap: str = "RdBu_r",
    vmin: float = -1.0,
    vmax: float = 1.0,
    mask_upper: bool = False,
    ax=None,
):
    """Correlation matrix heatmap with a diverging colormap centered at 0.

    Default coefficient is Spearman (rank) because raw environmental concentrations are
    rarely bivariate-normal; pass ``method="pearson"`` for normal/transformed data. When
    SciPy is available, cells whose p-value < 0.05 are starred (the caption must record
    the multiple-testing correction applied, e.g. Benjamini-Hochberg).

    Parameters
    ----------
    df : DataFrame
    columns : sequence of str, optional
        Subset of numeric columns to correlate (default: all numeric columns).
    method : {"spearman", "pearson", "kendall"}
    annot_significant : bool
        Star cells with p < 0.05 (requires SciPy; silently skipped if absent).
    cmap : str
        Diverging colormap (rainbow/jet rejected).
    mask_upper : bool
        Blank the upper triangle (show each pair once).

    Returns
    -------
    (fig, ax)
    """
    num = df[list(columns)] if columns is not None else df.select_dtypes(include=[np.number])
    num = num.apply(pd.to_numeric, errors="coerce")
    if num.shape[1] < 2:
        raise ValueError("Need at least two numeric columns to build a correlation matrix.")

    corr = num.corr(method=method)
    labels = list(corr.columns)
    M = corr.values.copy()

    # p-values (optional, SciPy).
    pvals = None
    if annot_significant:
        try:
            from scipy import stats  # lazy

            k = len(labels)
            pvals = np.ones((k, k))
            for i in range(k):
                for j in range(i + 1, k):
                    a = num.iloc[:, i]
                    b = num.iloc[:, j]
                    ok = np.isfinite(a) & np.isfinite(b)
                    if ok.sum() < 3:
                        continue
                    if method == "pearson":
                        _, p = stats.pearsonr(a[ok], b[ok])
                    elif method == "kendall":
                        _, p = stats.kendalltau(a[ok], b[ok])
                    else:
                        _, p = stats.spearmanr(a[ok], b[ok])
                    pvals[i, j] = pvals[j, i] = p
        except Exception:
            pvals = None

    cmap = _safe_cmap(cmap, kind="diverging")
    Mplot = M.copy()
    if mask_upper:
        iu = np.triu_indices_from(Mplot, k=1)
        Mplot[iu] = np.nan

    fig, ax = _new_ax(ax, ratio=0.9)
    im = ax.imshow(Mplot, cmap=cmap, vmin=vmin, vmax=vmax, aspect="equal")

    ax.set_xticks(range(len(labels)))
    ax.set_yticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=45, ha="right")
    ax.set_yticklabels(labels)
    ax.tick_params(length=0)
    for spine in ax.spines.values():
        spine.set_visible(False)

    cmap_obj = _get_cmap(cmap)
    rng = vmax - vmin if vmax != vmin else 1.0
    for i in range(len(labels)):
        for j in range(len(labels)):
            if mask_upper and j > i:
                continue
            val = M[i, j]
            norm_val = (val - vmin) / rng
            txt_color = _contrast_text_color(cmap_obj(np.clip(norm_val, 0, 1)))
            star = ""
            if pvals is not None and i != j and pvals[i, j] < 0.05:
                star = "*"
            ax.text(j, i, f"{val:.2f}{star}", ha="center", va="center",
                    fontsize=plt.rcParams["xtick.labelsize"] * 0.85, color=txt_color)

    cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label(f"{method.capitalize()} correlation")
    cbar.outline.set_linewidth(0.6)
    return fig, ax


def pca_biplot(
    df: pd.DataFrame,
    features: Sequence[str],
    *,
    color_by: Optional[str] = None,
    standardize: bool = True,
    n_components: int = 2,
    arrow_scale: float = 1.0,
    palette: str = "okabe_ito",
    label_loadings: bool = True,
    ax=None,
):
    """PCA score plot with loading arrows (biplot), computed via numpy SVD.

    Uses a pure-numpy SVD so no scikit-learn is required. Variables are auto-scaled
    (z-scored) by default — mandatory when analytes differ in magnitude/units — and axis
    labels carry the explained-variance percentage ("PC1 (xx.x%)"). Samples can be
    colored by a categorical column via ``color_by`` with a CVD-safe palette.

    Parameters
    ----------
    df : DataFrame
    features : sequence of str
        Numeric columns entering the PCA.
    color_by : str, optional
        Categorical column used to color the score points.
    standardize : bool
        Z-score each feature before SVD (correlation-PCA). Recommended.
    n_components : int
        Number kept (>=2 used for the 2-D plot).
    arrow_scale : float
        Multiplier on loading-arrow length for legibility.

    Returns
    -------
    (fig, ax)
    """
    feats = list(features)
    X = df[feats].apply(pd.to_numeric, errors="coerce")
    keep = np.isfinite(X.values).all(axis=1)
    X = X.loc[keep]
    if X.shape[0] < 3:
        raise ValueError("PCA needs at least 3 complete observations.")
    groups = df.loc[keep, color_by] if color_by and color_by in df else None

    M = X.values.astype(float)
    mean = M.mean(axis=0)
    Mc = M - mean
    if standardize:
        std = Mc.std(axis=0, ddof=1)
        std[std == 0] = 1.0
        Mc = Mc / std

    # Economy SVD: Mc = U S Vt.  Scores = U*S ; loadings = Vt rows (eigenvectors).
    U, S, Vt = np.linalg.svd(Mc, full_matrices=False)
    n = Mc.shape[0]
    explained = (S ** 2) / (S ** 2).sum() * 100.0
    n_components = max(2, min(n_components, len(S)))
    scores = U[:, :n_components] * S[:n_components]
    loadings = Vt[:n_components, :].T  # (n_features, n_components)

    fig, ax = _new_ax(ax)

    # Score points.
    if groups is not None:
        levels = list(pd.unique(groups))
        colors = get_colors(len(levels), palette)
        for gi, lev in enumerate(levels):
            sel = (groups.values == lev)
            ax.scatter(scores[sel, 0], scores[sel, 1], s=22, color=colors[gi % len(colors)],
                       edgecolors="white", linewidths=0.4, label=str(lev), zorder=3)
        ax.legend(title=str(color_by), loc="best")
    else:
        ax.scatter(scores[:, 0], scores[:, 1], s=22, color=_ACTIVE_PALETTE[0],
                   edgecolors="white", linewidths=0.4, zorder=3)

    # Loading arrows, scaled to the score cloud.
    score_span = np.abs(scores[:, :2]).max() or 1.0
    load_span = np.abs(loadings[:, :2]).max() or 1.0
    k = (score_span / load_span) * 0.7 * arrow_scale
    for i, feat in enumerate(feats):
        dx, dy = loadings[i, 0] * k, loadings[i, 1] * k
        ax.annotate("", xy=(dx, dy), xytext=(0, 0),
                    arrowprops=dict(arrowstyle="->", color="#B22222", lw=1.0))
        if label_loadings:
            ax.text(dx * 1.08, dy * 1.08, str(feat), color="#B22222",
                    fontsize=plt.rcParams["xtick.labelsize"] * 0.9,
                    ha="center", va="center")

    ax.axhline(0, color="#cccccc", lw=0.6, zorder=0)
    ax.axvline(0, color="#cccccc", lw=0.6, zorder=0)
    ax.set_xlabel(f"PC1 ({explained[0]:.1f}%)")
    ax.set_ylabel(f"PC2 ({explained[1]:.1f}%)")
    return fig, ax


def time_series(
    df: pd.DataFrame,
    time: str,
    value: str,
    *,
    group: Optional[str] = None,
    error: Optional[str] = "sd",
    n: Optional[int] = None,
    detection_limit: Optional[float] = None,
    palette: str = "okabe_ito",
    marker: str = "o",
    ax=None,
):
    """Temporal trend of ``value`` against ``time``, optionally by ``group``.

    When several replicates share a time point the mean is plotted with an error band;
    ``error`` selects ``sd`` (standard deviation), ``se`` (standard error), or ``ci``
    (95% normal CI). The chosen dispersion and ``n`` MUST be restated in the caption
    (Gate F). A detection-limit reference line can be drawn so below-LOD context is clear.

    Parameters
    ----------
    df : DataFrame
    time, value : str
    group : str, optional
        Plot one line per group level.
    error : {"sd", "se", "ci", None}
        Band type when multiple observations per time point exist.
    n : int, optional
        Replicate count to annotate (informational only).
    detection_limit : float, optional
        Horizontal reference line for the analytical LOD/LOQ.

    Returns
    -------
    (fig, ax)
    """
    work = df.copy()
    work[value] = pd.to_numeric(work[value], errors="coerce")
    work = work[np.isfinite(work[value])]

    fig, ax = _new_ax(ax)
    levels = list(pd.unique(work[group])) if group else [None]
    colors = get_colors(len(levels), palette)

    for gi, lev in enumerate(levels):
        sub = work if lev is None else work[work[group] == lev]
        agg = sub.groupby(time)[value].agg(["mean", "std", "count"]).sort_index()
        x = agg.index.values
        y = agg["mean"].values
        sd = agg["std"].fillna(0).values
        cnt = agg["count"].values.astype(float)
        cnt[cnt == 0] = 1

        if error == "se":
            err = sd / np.sqrt(cnt)
        elif error == "ci":
            err = 1.96 * sd / np.sqrt(cnt)
        elif error == "sd":
            err = sd
        else:
            err = None

        color = colors[gi % len(colors)]
        ax.plot(x, y, marker=marker, color=color, lw=1.4, ms=4,
                label=(str(lev) if lev is not None else None), zorder=3)
        if err is not None and np.any(err > 0):
            ax.fill_between(x, y - err, y + err, color=color, alpha=0.18, linewidth=0, zorder=1)

    if detection_limit is not None:
        ax.axhline(detection_limit, color="#888888", ls="--", lw=0.9, zorder=0)
        ax.annotate("LOD/LOQ", (ax.get_xlim()[0], detection_limit),
                    xytext=(2, 2), textcoords="offset points",
                    fontsize=plt.rcParams["xtick.labelsize"] * 0.85, color="#888888",
                    va="bottom", ha="left")

    ax.set_xlabel(str(time))
    err_note = {"sd": "mean +/- SD", "se": "mean +/- SE", "ci": "mean (95% CI)"}.get(error or "", "mean")
    n_note = f", n={n}" if n is not None else ""
    ax.set_ylabel(f"{value}  [units, state dw/ww]")
    if group:
        ax.legend(title=str(group))
    ax.set_title(f"{err_note}{n_note}", loc="right",
                 fontsize=plt.rcParams["xtick.labelsize"] * 0.85,
                 fontweight="normal", color="#666666")
    return fig, ax


def spatial_scatter_map(
    df: pd.DataFrame,
    lon: str,
    lat: str,
    value: Optional[str] = None,
    *,
    basemap: bool = False,
    crs: str = "EPSG:4326",
    label: Optional[str] = None,
    sequential: str = "viridis",
    scalebar: bool = True,
    north_arrow: bool = True,
    ax=None,
):
    """Sampling-site map (pure-matplotlib fallback; no geo backend required).

    Plots sites at ``(lon, lat)``, optionally colored by ``value`` with a CVD-safe
    sequential colormap and a colorbar. A Gate-F-compliant map states its CRS, carries a
    north arrow and a scale bar, so those annotations are added by default. ``basemap`` is
    accepted for API symmetry but a tiled basemap needs an optional geo backend; here we
    draw a clean white panel and label the CRS explicitly.

    Parameters
    ----------
    df : DataFrame
    lon, lat : str
        Longitude / latitude (or projected X/Y) column names.
    value : str, optional
        Column used to color markers (adds a colorbar).
    crs : str
        Coordinate reference system label shown on the panel (e.g. "EPSG:4326").
    scalebar, north_arrow : bool
        Draw the cartographic annotations (required by Gate F).

    Returns
    -------
    (fig, ax)

    Notes
    -----
    A true projected basemap belongs in a GIS step; this fallback guarantees the figure
    renders anywhere. The caption must give the projection used for any distance reading.
    """
    work = df.copy()
    work[lon] = pd.to_numeric(work[lon], errors="coerce")
    work[lat] = pd.to_numeric(work[lat], errors="coerce")
    work = work[np.isfinite(work[lon]) & np.isfinite(work[lat])]

    fig, ax = _new_ax(ax, ratio=0.85)

    if value and value in work:
        vals = pd.to_numeric(work[value], errors="coerce")
        cmap = _safe_cmap(sequential, kind="sequential")
        sc = ax.scatter(work[lon], work[lat], c=vals, cmap=cmap, s=40,
                        edgecolors="#222222", linewidths=0.5, zorder=3)
        cbar = fig.colorbar(sc, ax=ax, fraction=0.046, pad=0.04)
        cbar.set_label(label or f"{value}  [units]")
        cbar.outline.set_linewidth(0.6)
    else:
        ax.scatter(work[lon], work[lat], s=40, color=_ACTIVE_PALETTE[0],
                   edgecolors="#222222", linewidths=0.5, zorder=3)

    ax.set_xlabel(f"Longitude / X ({crs})")
    ax.set_ylabel(f"Latitude / Y ({crs})")
    ax.set_aspect("equal", adjustable="datalim")
    ax.grid(True, color="#eeeeee", lw=0.5, zorder=0)

    # North arrow (top-right, axes fraction).
    if north_arrow:
        ax.annotate("N", xy=(0.94, 0.95), xytext=(0.94, 0.83),
                    xycoords="axes fraction", textcoords="axes fraction",
                    ha="center", va="center", fontweight="bold",
                    fontsize=plt.rcParams["font.size"],
                    arrowprops=dict(arrowstyle="-|>", color="#222222", lw=1.2))

    # Scale bar (lower-left): a round fraction of the x-extent, labelled in CRS units.
    if scalebar and len(work) > 1:
        xmin, xmax = work[lon].min(), work[lon].max()
        span = xmax - xmin
        if span > 0:
            raw = span * 0.25
            mag = 10 ** np.floor(np.log10(raw))
            bar = round(raw / mag) * mag
            unit = "deg" if crs.upper().endswith("4326") else "units"
            x0 = xmin + span * 0.05
            ymin = work[lat].min()
            yspan = (work[lat].max() - ymin) or 1.0
            y0 = ymin - yspan * 0.02
            ax.plot([x0, x0 + bar], [y0, y0], color="#222222", lw=2.5,
                    solid_capstyle="butt", clip_on=False, zorder=4)
            ax.annotate(f"{bar:g} {unit}", ((x0 + x0 + bar) / 2, y0),
                        xytext=(0, 3), textcoords="offset points",
                        ha="center", va="bottom",
                        fontsize=plt.rcParams["xtick.labelsize"] * 0.85, color="#222222")

    if basemap:
        ax.set_title("basemap requested (add a GIS backend for tiles)", loc="right",
                     fontsize=plt.rcParams["xtick.labelsize"] * 0.8, color="#999999",
                     fontweight="normal")
    return fig, ax


def stacked_composition(
    df: pd.DataFrame,
    sample_col: str,
    fraction_cols: Sequence[str],
    *,
    normalize: bool = True,
    order: Optional[Sequence] = None,
    palette: str = "tol_bright",
    horizontal: bool = False,
    ax=None,
):
    """Stacked composition bars (congener / fraction / ionic profiles per sample).

    With ``normalize=True`` each bar sums to 100% (relative composition); set it False to
    show absolute concentrations. Components keep a consistent stacking order and CVD-safe
    colors across all bars so profiles are comparable.

    Parameters
    ----------
    df : DataFrame
    sample_col : str
        Column identifying each sample/site (the bar groups).
    fraction_cols : sequence of str
        Component columns to stack (e.g. PAH rings, PCB homologues, major ions).
    normalize : bool
        Convert each bar to percentage composition.
    order : sequence, optional
        Explicit sample ordering.
    horizontal : bool
        Horizontal stacked bars (useful for many/long sample labels).

    Returns
    -------
    (fig, ax)
    """
    comps = list(fraction_cols)
    work = df[[sample_col] + comps].copy()
    for c in comps:
        work[c] = pd.to_numeric(work[c], errors="coerce").fillna(0.0)

    if order is not None:
        work[sample_col] = pd.Categorical(work[sample_col], categories=list(order), ordered=True)
        work = work.sort_values(sample_col)

    samples = work[sample_col].astype(str).values
    mat = work[comps].values.astype(float)

    if normalize:
        totals = mat.sum(axis=1, keepdims=True)
        totals[totals == 0] = 1.0
        mat = mat / totals * 100.0
        axis_label = "Composition (%)"
    else:
        axis_label = "Concentration  [units, state dw/ww]"

    colors = get_colors(len(comps), palette)
    fig, ax = _new_ax(ax)
    idx = np.arange(len(samples))
    cum = np.zeros(len(samples))

    for ci, comp in enumerate(comps):
        seg = mat[:, ci]
        if horizontal:
            ax.barh(idx, seg, left=cum, color=colors[ci % len(colors)],
                    edgecolor="white", linewidth=0.4, label=str(comp))
        else:
            ax.bar(idx, seg, bottom=cum, color=colors[ci % len(colors)],
                   edgecolor="white", linewidth=0.4, label=str(comp))
        cum += seg

    if horizontal:
        ax.set_yticks(idx)
        ax.set_yticklabels(samples)
        ax.set_xlabel(axis_label)
        ax.set_ylabel(str(sample_col))
    else:
        ax.set_xticks(idx)
        ax.set_xticklabels(samples, rotation=45, ha="right")
        ax.set_ylabel(axis_label)
        ax.set_xlabel(str(sample_col))

    ax.legend(title="Component", bbox_to_anchor=(1.02, 1.0), loc="upper left",
              frameon=False, fontsize=plt.rcParams["legend.fontsize"])
    return fig, ax


# ===========================================================================
# 6. Demo data + CLI smoke test
# ===========================================================================
def _demo_dataframe(seed: int = 7) -> pd.DataFrame:
    """A small synthetic field-sampling dataframe used by the CLI demos."""
    rng = np.random.default_rng(seed)
    sites = ["S1", "S2", "S3", "S4"]
    seasons = ["autumn", "spring"]
    rows = []
    base_pb = {"S1": 18, "S2": 42, "S3": 75, "S4": 30}
    base_cd = {"S1": 0.4, "S2": 1.1, "S3": 2.3, "S4": 0.7}
    for s in sites:
        for season in seasons:
            for rep in range(5):
                pb = max(0.1, rng.lognormal(np.log(base_pb[s]), 0.25))
                cd = max(0.01, rng.lognormal(np.log(base_cd[s]), 0.3))
                zn = max(1.0, rng.lognormal(np.log(base_pb[s] * 2.0), 0.2))
                cu = max(0.5, rng.lognormal(np.log(base_pb[s] * 0.6), 0.25))
                rows.append({
                    "site": s,
                    "season": season,
                    "rep": rep,
                    "month": rng.integers(1, 13),
                    "lon": 120.0 + sites.index(s) * 0.05 + rng.normal(0, 0.005),
                    "lat": 30.0 + sites.index(s) * 0.04 + rng.normal(0, 0.005),
                    "Pb": pb, "Cd": cd, "Zn": zn, "Cu": cu,
                    # composition fractions (PAH ring classes, arbitrary units)
                    "ring2": rng.uniform(5, 20),
                    "ring3": rng.uniform(20, 45),
                    "ring4": rng.uniform(15, 40),
                    "ring5_6": rng.uniform(5, 25),
                })
    df = pd.DataFrame(rows)
    # inject a few missing values to prove robustness
    df.loc[df.sample(3, random_state=seed).index, "Cd"] = np.nan
    return df


def _run_demo(which: str, outdir: str, columns: str, formats: Sequence[str]) -> list:
    """Build one demo figure and save it; returns written paths."""
    df = _demo_dataframe()
    written = []

    if which in ("boxplot", "all"):
        fig, ax = boxplot_by_group(
            df, value="Pb", group="site", log_y=True,
            sig_letters={"S1": "a", "S2": "b", "S3": "c", "S4": "ab"})
        ax.set_ylabel(r"Pb (mg kg$^{-1}$ dw)")
        written += save_figure(fig, "demo_boxplot", formats=formats, outdir=outdir)

    if which in ("heatmap", "all"):
        fig, ax = correlation_heatmap(df[["Pb", "Cd", "Zn", "Cu"]], method="spearman")
        written += save_figure(fig, "demo_heatmap", formats=formats, outdir=outdir)

    if which in ("pca", "all"):
        fig, ax = pca_biplot(df, features=["Pb", "Cd", "Zn", "Cu"], color_by="site")
        written += save_figure(fig, "demo_pca", formats=formats, outdir=outdir)

    if which in ("timeseries", "all"):
        fig, ax = time_series(df, time="month", value="Zn", group="site",
                              error="se", n=5, detection_limit=2.0)
        ax.set_ylabel(r"Zn (mg kg$^{-1}$ dw)")
        written += save_figure(fig, "demo_timeseries", formats=formats, outdir=outdir)

    if which in ("map", "all"):
        sites = df.groupby("site").agg(lon=("lon", "mean"), lat=("lat", "mean"),
                                       Pb=("Pb", "mean")).reset_index()
        fig, ax = spatial_scatter_map(sites, lon="lon", lat="lat", value="Pb",
                                      label=r"mean Pb (mg kg$^{-1}$ dw)")
        written += save_figure(fig, "demo_map", formats=formats, outdir=outdir)

    if which in ("stacked", "all"):
        prof = df.groupby("site")[["ring2", "ring3", "ring4", "ring5_6"]].mean().reset_index()
        fig, ax = stacked_composition(prof, sample_col="site",
                                      fraction_cols=["ring2", "ring3", "ring4", "ring5_6"],
                                      normalize=True)
        written += save_figure(fig, "demo_stacked", formats=formats, outdir=outdir)

    return written


def _build_cli() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="envsci_style — publication style + env-sci plotters. "
                    "Run without args to generate one demo per plotter.")
    p.add_argument("--demo", default="all",
                   choices=["all", "boxplot", "heatmap", "pca", "timeseries", "map", "stacked"],
                   help="Which demo figure(s) to generate (default: all).")
    p.add_argument("--out", default="_demo_figs", help="Output directory (default: _demo_figs).")
    p.add_argument("--columns", default="single", choices=["single", "double"],
                   help="Column width preset for the active style.")
    p.add_argument("--format", default="svg,png",
                   help="Comma-separated export formats (default: svg,png).")
    return p


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = _build_cli().parse_args(argv)
    formats = tuple(f.strip() for f in args.format.split(",") if f.strip())
    # single->8pt base reads better; double-column dense panels stay at 7pt.
    set_envsci_style(base_font_pt=8.0 if args.columns == "single" else 7.0)
    written = _run_demo(args.demo, args.out, args.columns, formats)
    print(f"Wrote {len(written)} file(s) to {os.path.abspath(args.out)}:")
    for w in written:
        print("  -", w)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
