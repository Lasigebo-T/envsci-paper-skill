# envsci-slides — deep reference

> **Loaded by:** `envsci-slides` skill (SKILL.md). Read this file fully before building any
> graphical abstract (GA), TOC graphic, or slide deck. Do not preload.
>
> **Integrity rule (inherited from the umbrella):** every number, claim, and visual element on a
> slide or GA MUST already exist in the I-gate-verified manuscript. This skill NEVER introduces
> new numbers or claims — it only re-presents verified content.
>
> **Sibling boundaries:** GA / highlights TEXT → envsci-writing; per-journal GA / TOC size
> specs → envsci-journals (consumed here, do not duplicate); publication figures and any new
> data plot → envsci-figures; general chart-choice / visual-QA / Chinese-font fixes →
> scipilot-figure-skill.

---

## §1 Mental model (contract first)

Before opening any script or canvas, write a short **visual contract** in your working notes.
This is the single design decision that all later choices serve; change it here and propagate,
never patch around it downstream.

**Required contract fields (GA or deck — fill before anything else):**

```text
Artifact type  : GA | TOC graphic | conference deck | group deck | defense deck
One core message: one sentence with a verb
                  e.g. "Pore-water SRP flux across the SWI is net-positive at all sites
                  and explains [X]% of the overlying water column loading."
                  NOT "SWI nutrient flux results."
Archetype      : (pick from §3 for GA/TOC; from §4 for deck)
Verified source: manuscript section, figure ID, or Data-Ledger cell that authorizes each claim
Target journal : (for GA/TOC — drives size via envsci-journals)
Canvas preset  : elsevier-ga | est-toc
```

**Hard rules:**

- Define the ONE core message before drawing anything. Every visual element must serve it; elements that do not are cut.
- Pick an archetype from §3 (GA/TOC) or §4 (deck) before choosing a layout. Template-first design produces cluttered, unfocused GAs.
- Pull only VERIFIED assets: figures from envsci-figures (already Gate-F cleared), numbers from the Data Ledger / I-gate-verified manuscript, text fragments from envsci-writing, size specs from envsci-journals. Never invent, recompute, or extrapolate.
- If you do not have a cleared figure for a visual element, report a `[SLIDES GAP]` — do not sketch a placeholder with made-up data.

---

## §2 Hard specs

### §2.1 Elsevier graphical abstract (preset: `elsevier-ga`)

- Canvas: minimum **531 × 1328 px (height × width) — i.e. 1328 px wide × 531 px tall (landscape)** at ≥ 150 dpi for raster; vector (SVG/EPS/PDF) also accepted and preferred for scalability.
- Print-legibility target: must read clearly when printed at **~13 cm wide × 5 cm tall** (landscape).
- Use `ga_canvas.py --preset elsevier-ga` — this delivers the correct px/dpi canvas so you never have to re-derive from the Guide for Authors.
- Title text, highlights text, and abstract wording are NOT produced here — delegate to envsci-writing; pull the approved text back into the canvas.

### §2.2 ACS ES&T TOC graphic (preset: `est-toc`)

- Canvas: **3.25 × 1.75 in, ≥ 300 dpi** raster; SVG-first workflow recommended.
- The TOC graphic must be accompanied by a **50–60-word synopsis** (plain-language, supplied by envsci-writing, approved before submission). The synopsis is NOT the abstract; it is a short standalone description of the TOC image.
- Use `ga_canvas.py --preset est-toc` — this sets the exact dimensions and DPI.
- Synopsis word count: count with a word counter before submission; both under-50 and over-60 are noncompliant.

### §2.3 Cross-journal typography and color rules (GA and TOC)

- **Colorblind-safe palette required** — use Okabe–Ito or Tol-bright for categorical elements; `viridis`/`cividis` for sequential gradients. No red–green-only encoding.
- **Embed fonts** (SVG: `svg.fonttype='none'` keeps text as editable `<text>` nodes; if exporting PNG, verify text is rendered, not missing).
- **Minimum legible font size at final printed dimensions:** text in the GA must be readable at the 5 × 13 cm print size; labels smaller than ~6–7 pt at that size fail the thumbnail check (§6).
- **SVG-first → PNG:** export SVG for editorial/revision; export PNG (≥ 300 dpi, or 600 dpi if dense) for submission portals. Never deliver only a rasterized PNG with embedded text that cannot be re-edited.
- Per-journal size details beyond the two presets above: defer entirely to **envsci-journals** — do not duplicate or guess from memory.

---

## §3 GA archetype catalogue (env-sci field-sampling oriented)

Each archetype has a `do / don't` pair and an **information-density ceiling** — a GA is not a Results figure; it should convey one message to a reader who has spent three seconds on it.

### §3.1 Mechanism / process schematic

**Shows:** the key biogeochemical or physical process driving your main finding (e.g. internal P loading via Fe-P redox release at the SWI). Arrows represent fluxes or transformations; boxes are compartments.

**Do:** label every compartment and arrow with a quantity unit or direction; keep the process loop tight (three to five steps maximum). **Don't:** include all the processes you studied — just the one the paper argues is dominant.

**Information-density ceiling:** ≤ 5 labeled compartments; ≤ 3 distinct flux arrows; no embedded data tables.

**Fits:** mechanistic water/sediment/soil studies where the process is the novelty, not just the occurrence.

### §3.2 Before → after

**Shows:** a clear state-change contrast — pre/post remediation, dry/wet season, upstream/downstream — with one key metric annotated on each panel.

**Do:** use a consistent color vocabulary between the two panels; annotate the key value (direction, magnitude) explicitly. **Don't:** show multiple metrics per panel — pick the one metric that clinches the story.

**Information-density ceiling:** 2 panels; 1–2 annotated values per panel; no axis grids.

**Fits:** remediation studies, seasonal contrast papers, before/after event (e.g. algal bloom onset).

### §3.3 Spatial-gradient mini-map

**Shows:** the spatial pattern of a key analyte across sampling sites on a schematic or simplified basemap. Marker size or color encodes the magnitude.

**Do:** include a simplified geographic outline (lake, river, estuary) as spatial context; label site IDs or gradient direction (upstream → downstream). **Don't:** use a full cartographic basemap at GA resolution — it becomes unreadable at thumbnail scale; simplify.

**Information-density ceiling:** ≤ 8 sites; one encoded variable (marker color or size, not both independently); no legend table, use a single gradient bar.

**Fits:** spatial-gradient / pollution-hotspot studies with a clear geographic narrative.

### §3.4 input → system → output FLUX diagram (SWI pore-water / peeper nutrient flux)

This is the recommended archetype for peeper-based SWI nutrient flux studies. The `input→system→output` structure maps naturally: external/atmospheric/watershed **inputs** → **system** (hyporheic / sediment pore-water compartment, sampled by peeper) → overlying-water-column **output** (flux direction and magnitude). Use it when your main claim is about the direction and magnitude of the net flux.

**Do:** label each arrow with flux direction (↑ or ↓) and a representative range or the dominant analyte (e.g. SRP, NH₄⁺, SiO₂); mark the SWI interface visibly; color-code the system compartment to the peeper's sampling depth profile. **Don't:** include all analytes measured — show the one analyte that is the paper's main argument; secondary analytes go in the body.

**Information-density ceiling:** 3 boxes (input / system / output); ≤ 4 flux arrows; one numeric annotation (the sign and order-of-magnitude of net flux); no embedded graphs.

**Fits:** pore-water flux studies (peeper, equilibrium dialysis), hyporheic exchange, sediment nutrient release, internal loading papers.

### §3.5 Conceptual cross-section

**Shows:** a schematic depth-transect or stratigraphic section with annotated zones (e.g. oxic/anoxic; photic/aphotic; vadose/saturated zone).

**Do:** exaggerate vertical scale deliberately (and label it schematic); annotate which zone drives the main finding; use a simple two-color background (water vs sediment, or vadose vs saturated). **Don't:** try to match real depth data — this is conceptual, not a profile plot.

**Information-density ceiling:** ≤ 3 labeled depth zones; ≤ 3 annotated process labels; no numeric axes.

**Fits:** sediment-coring / pore-water / groundwater studies where depth zonation is the explanatory variable.

---

## §4 Deck archetypes + rhythm templates

The deck is a RE-COMPOSITION of verified content — every slide's claim must already exist in the I-gate-cleared manuscript. The rhythm template is a pacing guide, not a rigid order; adapt to the talk length and audience. The durations and slide counts below are **advisory, not enforced by deck_build.py** — the script renders whatever slides the outline JSON contains.

### §4.1 Conference (~10–12 min; ~12–15 slides)

**Rhythm:** hook (problem relevance, 1 slide) → gap (what we don't know, 1 slide) → light methods (sampling design + key analytical approach, 1–2 slides) → key results (3–4 slides: your best figures) → take-home (1 slide: one sentence + implication).

**Principles:** one message per slide; lead with the result (headline first, evidence below); methods slides should answer "enough to trust the result", not replicate the Methods section. Speaker notes carry the nuance; the slide carries only the headline and one figure or table.

### §4.2 Group meeting (deeper; ~20–30 slides)

**Rhythm:** context + rationale → full sampling design + QC → methods (including troubleshooting: what went wrong and how it was handled) → results-by-question (one question per slide cluster) → interpretation + open questions → next steps.

**Principles:** this audience can handle methodological depth; include QA/QC checks (e.g. peeper equilibration time, blank corrections, detection limits) explicitly. Raise unresolved questions openly — the purpose is feedback, not a polished story.

### §4.3 Defense (full; ~30–40 slides for a 45–60 min defense)

**Rhythm:** introduction + significance → full literature gap → objectives (numbered, traceable to results) → full methods + QA/QC (one slide per major method, one for QC outcomes) → results (one slide per objective) → discussion (mechanism, comparison with literature) → conclusions (numbered, mirror objectives) → limitations + future work + significance.

**Principles:** every method decision defensible from first principles; anticipate Q&A (add backup slides for: detection limits, statistical assumptions, alternative interpretations, field QC); include raw data or uncertainty ranges where examiners may probe; never exceed 1 claim per slide.

### §4.4 Slide-type catalogue

| Slide type | When to use | Max density rule |
|---|---|---|
| Title / hook | Opening and each major section break | 1 sentence + 1 visual |
| Single-figure result | Each key finding | 1 figure + 1-sentence headline |
| Methods schematic | Explain sampling / analytical workflow | 1 diagram; ≤ 5 labeled steps |
| Comparison table | Cross-site or cross-paper result summary | ≤ 6 rows × 4 columns |
| Take-home / conclusions | Final slide (and defense conclusions) | ≤ 5 bullet points; each ≤ 12 words |
| Backup / appendix | Anticipated Q&A detail | Any depth; clearly labeled "backup" |

### §4.5 How to write speaker notes

Speaker notes are the full sentence that you would say aloud for each bullet. They carry: the quantitative nuance omitted from the slide (ranges, n, uncertainty), the interpretation connector ("this implies…"), the transition to the next slide, and any known reviewer / committee questions. A slide with no speaker notes is incomplete for defense or conference delivery.

---

## §5 Tooling & outline schema

### §5.1 `ga_canvas.py` — GA and TOC canvas builder

```bash
# Elsevier GA canvas (1328 × 531 px at 300 dpi, or vector)
py scripts/ga_canvas.py --preset elsevier-ga --title "Your paper title" --out ga

# ACS ES&T TOC graphic (3.25 × 1.75 in, 300 dpi)
py scripts/ga_canvas.py --preset est-toc --title "Your paper title" --out toc

# List available presets
py scripts/ga_canvas.py --list-presets
```

**Presets:**
- `elsevier-ga` — 1328 × 531 px (width × height) at 300 dpi; outputs `<out>.svg` + `<out>.png`. Width is the long axis (landscape); the minimum short axis is 531 px.
- `est-toc` — 3.25 × 1.75 in at 300 dpi (975 × 525 px at 300 dpi); outputs `<out>.svg` + `<out>.png`.

**Workflow:** the script creates the canvas with the correct dimensions — you then populate it by placing your Gate-F-cleared figures and text (from envsci-writing) within the canvas boundary. The script does not generate content; it enforces size compliance.

**Export and naming convention:** `<paper-id>_ga_elsevier.<ext>` for Elsevier GA; `<paper-id>_toc_est.<ext>` for ES&T TOC. Keep SVG and PNG side-by-side in `figures/ga/`.

### §5.2 `deck_build.py` — PPTX deck builder

```bash
py scripts/deck_build.py outline.json --out talk.pptx
py scripts/deck_build.py outline.json --out group_meeting.pptx
py scripts/deck_build.py outline.json --out defense.pptx
```

The template is selected by the `template` field inside the outline JSON (conference / group / defense), not by a CLI flag; `--out` only sets the output filename.

**Outline JSON schema — all fields:**

```json
{
  "title": "Paper or talk title (string)",
  "subtitle": "Venue, date, or author line (string)",
  "template": "conference | group | defense",
  "slides": [
    {
      "heading": "Slide headline — one sentence, the take-home claim (string)",
      "bullets": ["Bullet point 1 text", "Bullet point 2 text"],
      "notes": "Full speaker notes: what you say aloud, nuance, transitions (string)",
      "image": "path/to/figure.svg or .png — relative to outline.json (string or null)"
    }
  ]
}
```

**Field notes:**
- `title` — deck-level title; appears on the title slide.
- `subtitle` — deck-level subtitle (conference name + date, or "Group meeting YYYY-MM-DD").
- `template` — controls slide master, font sizes, and layout defaults; one of `conference`, `group`, `defense`.
- `slides[].heading` — the slide headline; shown large at the top of the slide. Write it as a conclusion, not a topic label (e.g. "SRP flux is net-positive at all sites" not "SRP flux results").
- `slides[].bullets` — body text items. Keep each bullet ≤ 12 words for conference; ≤ 20 words for defense. Omit if the slide is a full-bleed figure slide (use `image` only).
- `slides[].notes` — speaker notes full text. This is what you say; write complete sentences.
- `slides[].image` — path to a single figure (SVG preferred; PNG fallback). Must be a Gate-F-cleared figure from envsci-figures or the ga/toc canvas. Use `null` if the slide has no figure.

**Worked example (one slide for an SWI flux conference talk):**

```json
{
  "heading": "Pore-water SRP flux is net-positive at all five sites",
  "bullets": [
    "Flux direction: sediment → overlying water at every site",
    "Highest release at Site [site-ID] (near macrophyte bed)"
  ],
  "notes": "Explain the peeper method briefly: dialysis cells equilibrated for [N] days, SRP analysed by [method]. Point to Site [site-ID] on the figure — note the connection to anoxic Fe-P cycling described in the next slide. Anticipated question: detection limits for pore-water SRP — answer is on backup slide B2.",
  "image": "figures/fig3_srp_flux_profile.svg"
}
```

Note: numeric values and site identifiers in speaker notes must be drawn from the Data Ledger / verified manuscript — the placeholders `[N]`, `[method]`, and `[site-ID]` above are intentional; fill them from your verified source before use.

### §5.3 Templates

- `conference` — clean two-column master; large heading; one figure zone; minimal bullets. Optimized for 16:9 widescreen projection.
- `group` — two-column with a wider text zone; supports more bullets and a figure; 16:9 or 4:3.
- `defense` — full-structure master with section headers, slide number, and a wide notes-visible layout for rehearsal. 16:9.

### §5.4 Dependencies

```bash
pip install -r scripts/requirements.txt
# Core: matplotlib (ga_canvas.py renders BOTH the SVG and the PNG via its Agg backend savefig)
#       python-pptx (deck_build.py builds the .pptx)
# Use `py` launcher on Windows if `python` opens the Microsoft Store
```

---

## §6 Gate-S (slides-QA contract)

**Gate-S** is the slides-specific QA gate, mirroring Gate-F (figures) and Gate-I (integrity). No GA, TOC graphic, or deck is complete until all HARD rows below pass. A failing HARD row is reported as a `[SLIDES GAP]`, not patched silently.

### §6.1 GA / TOC graphic checks

| # | Check | Pass condition | Type |
|---|---|---|---|
| S1 | Thumbnail legibility | Core message readable at ~13 cm wide × 5 cm tall (Elsevier) or 3.25 × 1.75 in (ES&T) without magnification; no text overlap | HARD |
| S2 | Word/information density | ≤ 5 labeled compartments or ≤ 8 site markers or ≤ 3 flux arrows (per archetype ceiling in §3) | HARD |
| S3 | Colorblind-safe palette | Okabe–Ito / Tol-bright / viridis; no red–green-only encoding | HARD |
| S4 | Units present | Every quantity shown carries its unit (flux: mmol m⁻² d⁻¹; concentration: µg L⁻¹; etc.) | HARD |
| S5 | Size / DPI compliant | Matches the active preset (`elsevier-ga` or `est-toc`) or verified journal spec from envsci-journals | HARD |
| S6 | Synopsis word count | ES&T TOC only: synopsis is exactly **50–60 words** (count before submission) | HARD |
| S7 | No new / unverified numbers | Every numeric annotation traces to a Data-Ledger cell or I-gate-verified manuscript text | HARD |
| S8 | Fonts embedded | SVG has `svg.fonttype='none'` (editable text); PNG renders all text at correct size | HARD |

### §6.2 Deck checks

| # | Check | Pass condition | Type |
|---|---|---|---|
| S9 | One message per slide | Each slide has exactly one headline claim; bullets support it, not replace it | HARD |
| S10 | Font-size threshold | Body text ≥ 18 pt; headlines ≥ 24 pt at 16:9 projection; no smaller text except figure axis labels inside images | HARD |
| S11 | Figure traceability | Every figure on a slide is the exact file output by envsci-figures (Gate-F cleared); file path recorded in outline JSON `image` field | HARD |
| S12 | No fabricated content | No number, claim, or visual element absent from the I-gate-verified manuscript | HARD |
| S13 | Speaker notes complete | Every slide with a spoken transition has non-empty `notes` in the outline JSON | SOFT |
| S14 | Backup slides labeled | Any slide beyond the main deck is in an "Appendix / Backup" section with a clear label | SOFT |

### §6.3 Gate-S verdict format

Report the verdict as: `Gate-S: PASS` or `Gate-S: FAIL — [SLIDES GAP] rows S<n>, S<n>` with a one-line description of each failure and the action needed to clear it.

---

## §7 Handoff

### §7.1 GA / TOC → journal submission package

Deliver:
- `<paper-id>_ga_elsevier.svg` + `<paper-id>_ga_elsevier.png` (for Elsevier targets), or `<paper-id>_toc_est.svg` + `<paper-id>_toc_est.png` (for ES&T).
- The approved synopsis text (50–60 words; ES&T only) as a plain `.txt` file alongside the TOC image.
- Gate-S verdict confirming rows S1–S8 all pass.
- These outputs are components of the submission package assembled by **envsci-journals** at Stage 10 — hand off the files and verdict there.

### §7.2 Deck → standalone dissemination

The deck must stand alone without the manuscript: every slide's claim is self-evident from the slide + speaker notes + figure. Deliver:
- `talk.pptx` (or `group_meeting.pptx` / `defense.pptx`).
- The `outline.json` source file (for future edits without reverse-engineering the PPTX).
- Gate-S verdict confirming rows S9–S12 all pass (S13–S14 are SOFT: flag if absent but do not block delivery).

### §7.3 Integrity pointer → envsci-citations

Every number that appears on a slide or GA must already be verified in the manuscript's integrity pass (Gate-I in **envsci-citations**). If you encounter a candidate number in the manuscript that has NOT passed Gate-I, stop, flag it as a `[SLIDES GAP]` (pending integrity clearance), and request the envsci-citations gate before including it. Do not include provisional numbers on the assumption they will be verified later.

### §7.4 Sibling boundary summary

| Need | Correct skill |
|---|---|
| GA / highlights text, synopsis wording | **envsci-writing** |
| Per-journal GA / TOC size specs beyond the two presets | **envsci-journals** |
| Underlying publication figures, any new data plot | **envsci-figures** |
| General chart-choice, visual-QA, Chinese-font fixes | **scipilot-figure-skill** |
| Number/citation integrity verification | **envsci-citations** |
