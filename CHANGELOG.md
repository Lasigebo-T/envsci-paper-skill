# Changelog

All notable changes to `enviro-paper` are documented here.
This project adheres to [Semantic Versioning](https://semver.org/).

## [1.0.0] — 2026-06-12

Initial public release.

### Added
- **`enviro-paper` skill** — a single router-style Agent Skill for environmental-science
  field-sampling and monitoring papers, working with both **Claude Code** and **Codex**.
- **10-stage pipeline** with two blocking anti-fabrication integrity gates (I-1 before review,
  I-2 fresh after revision) and quality gates D / S / F.
- **7 reference modules**: research-and-literature, data-analysis, figures, writing,
  citations-and-integrity, review-and-response, journals.
- **`scripts/envsci_style.py`** — matplotlib publication-style module + env-sci plotters
  (site map, boxplot by site/season, correlation heatmap, PCA biplot, spatial scatter,
  stacked composition), exporting SVG + 300 dpi PNG with a colorblind-safe palette.
- **`scripts/check_references.py`** — offline, stdlib-only reference-integrity linter
  (malformed/duplicate DOIs, missing fields, implausible years; exit 1 on any HIGH issue).
- **Pollution & risk index library** with formulas, canonical references, threshold tables,
  and worked examples: Igeo, EF, CF/PLI, Hakanson Er/RI, Nemerow, WQI, and US-EPA HQ/HI/CR.
- **Bilingual** triggering and output (English / Simplified Chinese).
- Plugin packaging for both ecosystems: `.claude-plugin/` (Claude Code) and
  `plugins/enviro-paper/.codex-plugin/` (Codex).

### Notes
- Both scripts were executed during build (Python 3.14 / matplotlib 3.10 / numpy 2.3 / pandas 2.3):
  `check_references.py --selftest` passes; `envsci_style.py --demo all` generates all 12 figures.
- Index formulas and thresholds were cross-checked against their canonical sources.
- Design fuses [academic-research-skills](https://github.com/imbad0202/academic-research-skills)
  (rigor) and [nature-skills](https://github.com/Yuan1z0825/nature-skills) (concrete outputs),
  both MIT-licensed, with a new environmental-science analytical layer.
