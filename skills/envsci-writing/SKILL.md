---
name: envsci-writing
description: >-
  Use when the user wants to DRAFT or POLISH manuscript text for an
  environmental-science field-sampling/monitoring paper — any IMRaD section or
  the language itself. Triggers (English): write the introduction/methods/results/
  discussion/conclusions/abstract/title/highlights/graphical abstract, draft this
  section, polish my English, de-translationese / fix Chinglish, Nature-style
  language edit, tighten/soften this paragraph, reduce overclaiming, structure my
  argument, turn my Chinese notes into English, draft revised manuscript text for
  reviewer comments. Triggers (简体中文): 写引言/前言、写方法、写结果、写讨论、写结论、
  写摘要、起标题、写 highlights/图文摘要、润色、英文打磨、去翻译腔、改 Chinglish、
  降低 overclaim、把中文思路写成英文、按审稿意见改稿正文。Section-aware (Title/Abstract/
  Intro/Study area/Sampling/Methods+QAQC/Results/Discussion/Conclusions),
  enforces the Knowledge-Isolation anti-leakage rule, terminology/units/dw-ww
  consistency, and a Chinese-author dual-output (polished English first, then a
  brief Chinese structural note). Not for citation formatting or the
  anti-fabrication reference check (use envsci-citations); not for peer-review
  simulation or response letters (use envsci-review).
---

# envsci-writing — section-aware drafting, polishing & revision text

## What this is
The writing hand of the envsci-paper family. It drafts and polishes the actual
prose of an environmental-science sampling/monitoring manuscript: every IMRaD
section, the title/abstract/highlights/graphical-abstract apparatus, Nature-style
language polishing, the Chinese-author → English workflow, and the revised
manuscript text when reviewer comments come back. It diagnoses the dominant
failure mode before touching sentences (`section job → paragraph logic →
claim/evidence/boundary → terminology → sentence polish`).

It carries the anti-fabrication ethos into prose: every factual claim must trace
to the Data Ledger, Annotated Bibliography, Study Contract, or a session figure;
missing facts become visible `[MATERIAL GAP]` / `[LLM-SUPPLEMENTED]` tags rather
than improvised numbers, methods steps, standard values, or citations. Units and
dw/ww (or dissolved/total) basis are stated once and held everywhere.

## When to use
- Drafting any section: title, abstract (structured or not), introduction,
  study area, sampling design, methods + QA/QC, results, discussion, conclusions.
- Polishing: de-cluttering, splitting overlong sentences, removing em-dash prose,
  fixing tense by section, softening overclaims, enforcing terminology consistency.
- Chinese authors: turning Chinese research notes into manuscript English
  (translate ideas, not words), then a short Chinese structural note.
- Drafting the *revised manuscript text* for reviewer comments, with a Commitment
  Ledger so nothing promised is silently dropped.

## When NOT to use (hand off to a sibling)
- Formatting references to a journal style, or running the blocking
  anti-fabrication reference/DOI check → **envsci-citations**.
- Simulating peer review or writing the point-by-point response letter →
  **envsci-review** (this skill drafts only the changed manuscript text).
- Computing/justifying indices, non-detect handling, stats, LOD/recovery rules →
  **envsci-data** (writing cites those decisions, it does not derive them).
- Making the actual figures/maps → **envsci-figures**; journal scope/caps →
  **envsci-journals**.

## How to run
1. Read `references/writing.md` **fully** and follow it — the deep how-to lives
   there (per-section movements, mini-templates, the env-sci reviewer-pitfall
   lists, the enforceable §12 language caps, the Chinglish repair table, and the
   §14 Commitment Ledger for revisions). Do not work from this summary alone.
2. Identify the mode — `write <section>`, `polish`, or revision drafting — and the
   dominant failure mode first; never sentence-polish a draft whose section job is
   wrong.
3. Apply the Knowledge-Isolation Directive to every Methods/Results sentence:
   describe only what was documented; tag, do not invent.
4. Emit the drafted/polished text plus any unresolved `[MATERIAL GAP]` /
   `[LLM-SUPPLEMENTED]` tags. Drafted citations and numbers are **not**
   self-verified here — they pass through the integrity gate in envsci-citations.

## Language & integrity stance
Respond in the user's language. The user works in Simplified Chinese: deliver
**polished English first, then a brief Chinese structural note**. Keep technical
terms, analyte/parameter names, units, chemical/CAS names, Latin binomials,
instrument and software names, and DOIs in English throughout. No invented
citations, numbers, DOIs, method steps, or standard values; always carry units and
the declared dw/ww basis; surface non-detect/background assumptions rather than
smoothing them over.
