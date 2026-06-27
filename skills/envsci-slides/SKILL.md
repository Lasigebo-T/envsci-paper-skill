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
