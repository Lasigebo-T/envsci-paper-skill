#!/usr/bin/env python3
"""check_references.py — stdlib-only reference-integrity checker for env-sci papers.

The executable arm of the enviro-paper skill's integrity gates (Gate I-1 / I-2).
It performs STRUCTURAL, OFFLINE checks on a paper's reference list — the half of
citation verification that needs no network. It detects the cheap, high-signal
fabrication tells (malformed/missing DOIs, duplicate DOIs, duplicate titles,
implausible years, missing required fields) so that a human reviewer or the
online triangulation step never wastes effort on an obviously broken list.

WHAT THIS DOES NOT DO (by design):
    It does NOT resolve DOIs over the network, query Crossref/OpenAlex/Semantic
    Scholar, or confirm that a reference actually EXISTS. A clean report here
    means the list is *structurally* plausible, NOT that every entry is real.
    Online DOI resolution + title cross-check (the "DOI Misdirection" /
    triangulation step) is a SEPARATE, manual/online step performed by the
    integrity mode — this tool is intentionally pure-stdlib so it runs anywhere
    with zero install. Treat a PASS here as "necessary, not sufficient."

INPUT FORMATS (auto-detected by extension/content, or forced via --format):
    bibtex : a .bib file. Basic parser — pulls entry type, cite-key, and the
             fields author / title / year / journal / doi (booktitle and
             url->doi are also harvested as fallbacks).
    json   : a JSON list of objects {author, title, year, journal, doi}.
             (A dict with a top-level "references"/"items" list also works.)
    md     : a markdown / numbered / plain-text reference list. Best-effort:
             each non-empty line (or numbered item) becomes one entry; DOIs
             and 4-digit years are extracted by regex. Field-completeness
             checks are relaxed for this format (free text has no labeled
             fields), but DOI / year / duplicate checks still apply.

CHECKS (grouped by severity in the report):
    HIGH   : invalid / malformed DOI, duplicate DOI, duplicate (normalized)
             title, implausible year (outside [--min-year, --max-year]).
    MEDIUM : entry missing a required field (author/title/year/journal) — only
             enforced for structured formats (bibtex/json).
    LOW    : entry has no DOI at all (common & legitimate for older refs;
             reported for awareness, never fails the run).

EXIT CODE:
    0  no HIGH-severity issues (LOW/MEDIUM may still be present).
    1  one or more HIGH-severity issues (wire `check_references.py ... ; $LASTEXITCODE`
       or `|| exit 1` into Gate I to hard-block a fabricated/broken list).

USAGE:
    python check_references.py refs.bib
    python check_references.py refs.json --format json
    python check_references.py manuscript.md --format md --json
    python check_references.py refs.bib --max-year 2026 --json --out report.json

SELF-TEST (inline, no network, no external fixtures):
    python check_references.py --selftest
    Builds a tiny in-memory reference set with one of every defect, runs the
    full check suite, and asserts the issue counts. Prints "selftest: OK" and
    exits 0 on success; raises AssertionError (exit 1) on regression.

Pure stdlib: re, sys, json, argparse, collections, pathlib, typing. Python 3.9+.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Per the Crossref DOI syntax (and the registration-agency pattern used by the
# enviro-paper integrity reference): a DOI is "10." + a 4-9 digit registrant
# code + "/" + an opaque suffix of at least one non-space character.
DOI_REGEX = re.compile(r"^10\.\d{4,9}/\S+$")

# Looser pattern used to *extract* a DOI embedded in free text / a URL.
DOI_IN_TEXT_REGEX = re.compile(r"10\.\d{4,9}/[^\s\"'<>,;)]+", re.IGNORECASE)

# A standalone plausible publication year (4 digits, 19xx/20xx).
YEAR_IN_TEXT_REGEX = re.compile(r"\b((?:19|20)\d{2})\b")

REQUIRED_FIELDS = ("author", "title", "year", "journal")

DEFAULT_MIN_YEAR = 1900
DEFAULT_MAX_YEAR = 2026

# Severity ordering for stable, grouped reporting.
SEVERITY_ORDER = ("HIGH", "MEDIUM", "LOW")


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------


class Reference:
    """One parsed reference. `key` is a human-facing label (cite-key, index, or
    'item N'); `raw` keeps the original text for md-format diagnostics."""

    __slots__ = ("key", "author", "title", "year", "journal", "doi", "raw")

    def __init__(
        self,
        key: str,
        author: Optional[str] = None,
        title: Optional[str] = None,
        year: Optional[str] = None,
        journal: Optional[str] = None,
        doi: Optional[str] = None,
        raw: str = "",
    ) -> None:
        self.key = key
        self.author = _clean(author)
        self.title = _clean(title)
        self.year = _clean(year)
        self.journal = _clean(journal)
        self.doi = _clean(doi)
        self.raw = raw

    def as_dict(self) -> Dict[str, Optional[str]]:
        return {
            "key": self.key,
            "author": self.author,
            "title": self.title,
            "year": self.year,
            "journal": self.journal,
            "doi": self.doi,
        }


class Issue:
    """A single detected problem against a reference (or the whole list)."""

    __slots__ = ("severity", "code", "key", "message")

    def __init__(self, severity: str, code: str, key: str, message: str) -> None:
        self.severity = severity
        self.code = code
        self.key = key
        self.message = message

    def as_dict(self) -> Dict[str, str]:
        return {
            "severity": self.severity,
            "code": self.code,
            "key": self.key,
            "message": self.message,
        }


# ---------------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------------


def _clean(s: Optional[str]) -> Optional[str]:
    """Trim whitespace and surrounding braces/quotes; return None if empty."""
    if s is None:
        return None
    s = str(s).strip()
    # Strip one layer of bibtex braces / wrapping quotes.
    while len(s) >= 2 and ((s[0] == "{" and s[-1] == "}") or (s[0] == '"' and s[-1] == '"')):
        s = s[1:-1].strip()
    s = " ".join(s.split())
    return s or None


def _normalize_title(s: str) -> str:
    """Case-insensitive, punctuation-stripped, whitespace-collapsed.

    Matches the normalization used by the online triangulation clients so that
    a duplicate flagged here is the same notion of 'same title' used downstream.
    """
    out = []
    for ch in s.lower():
        out.append(ch if ch.isalnum() else " ")
    return " ".join("".join(out).split())


def _normalize_doi(s: str) -> str:
    """Canonicalize a DOI for duplicate detection: strip resolver prefixes and
    lowercase (DOIs are case-insensitive per the DOI handbook)."""
    s = s.strip()
    for prefix in (
        "https://doi.org/",
        "http://doi.org/",
        "https://dx.doi.org/",
        "http://dx.doi.org/",
        "doi:",
        "DOI:",
    ):
        if s.lower().startswith(prefix.lower()):
            s = s[len(prefix):]
            break
    return s.strip().lower()


# ---------------------------------------------------------------------------
# Format detection
# ---------------------------------------------------------------------------


def detect_format(path: Optional[Path], text: str) -> str:
    """Return 'bibtex' | 'json' | 'md', auto-detected from extension then content."""
    if path is not None:
        ext = path.suffix.lower()
        if ext == ".bib":
            return "bibtex"
        if ext == ".json":
            return "json"
        if ext in (".md", ".markdown", ".txt"):
            # .txt could still be a bib/json; fall through to content sniff but
            # default to md for these extensions.
            sniffed = _sniff_content(text)
            return sniffed or "md"
    sniffed = _sniff_content(text)
    return sniffed or "md"


def _sniff_content(text: str) -> Optional[str]:
    stripped = text.lstrip()
    if not stripped:
        return None
    if stripped[0] in "[{":
        # Could be JSON; confirm it parses, else treat as text later.
        try:
            json.loads(text)
            return "json"
        except (ValueError, TypeError):
            pass
    if "@" in text and re.search(r"@\s*\w+\s*\{", text):
        return "bibtex"
    return None


# ---------------------------------------------------------------------------
# Parsers
# ---------------------------------------------------------------------------


def parse_bibtex(text: str) -> List[Reference]:
    """Basic BibTeX parser: split on @entries, brace-balance each body, then
    pull key=value fields. Not a full parser — no @string/@preamble expansion,
    no crossref inheritance — but robust to the common cases the integrity gate
    sees (Elsevier/ACS/Springer exports)."""
    refs: List[Reference] = []
    i = 0
    n = len(text)
    while i < n:
        at = text.find("@", i)
        if at == -1:
            break
        # Read entry type up to the opening brace.
        brace = text.find("{", at)
        if brace == -1:
            break
        entry_type = text[at + 1:brace].strip().lower()
        if entry_type in ("string", "preamble", "comment"):
            # Skip these — advance past their balanced body.
            i = _skip_balanced(text, brace)
            continue
        body_end = _find_matching_brace(text, brace)
        if body_end == -1:
            break
        body = text[brace + 1:body_end]
        i = body_end + 1

        # First comma separates cite-key from fields.
        comma = body.find(",")
        if comma == -1:
            cite_key = body.strip() or f"entry{len(refs) + 1}"
            fields_blob = ""
        else:
            cite_key = body[:comma].strip() or f"entry{len(refs) + 1}"
            fields_blob = body[comma + 1:]

        fields = _parse_bibtex_fields(fields_blob)
        doi = fields.get("doi") or _doi_from_url(fields.get("url", ""))
        journal = fields.get("journal") or fields.get("booktitle") or fields.get("journaltitle")
        refs.append(
            Reference(
                key=cite_key,
                author=fields.get("author"),
                title=fields.get("title"),
                year=fields.get("year"),
                journal=journal,
                doi=doi,
                raw="",
            )
        )
    return refs


def _parse_bibtex_fields(blob: str) -> Dict[str, str]:
    """Parse 'name = {value}' / 'name = "value"' / 'name = value,' pairs from a
    bibtex entry body. Handles brace-nested values and quoted values."""
    fields: Dict[str, str] = {}
    i = 0
    n = len(blob)
    while i < n:
        # Find next 'name ='.
        m = re.compile(r"([A-Za-z][A-Za-z0-9_\-]*)\s*=\s*").search(blob, i)
        if not m:
            break
        name = m.group(1).lower()
        j = m.end()
        if j >= n:
            break
        if blob[j] == "{":
            end = _find_matching_brace(blob, j)
            if end == -1:
                break
            value = blob[j + 1:end]
            i = end + 1
        elif blob[j] == '"':
            # Read until the next unescaped double quote.
            end = blob.find('"', j + 1)
            while end != -1 and blob[end - 1] == "\\":
                end = blob.find('"', end + 1)
            if end == -1:
                break
            value = blob[j + 1:end]
            i = end + 1
        else:
            # Bare value (number or @string ref) up to comma/newline.
            end = j
            while end < n and blob[end] not in ",\n":
                end += 1
            value = blob[j:end]
            i = end
        # Skip a trailing comma.
        while i < n and blob[i] in ", \n\r\t":
            i += 1
        fields[name] = " ".join(value.split())
    return fields


def _find_matching_brace(text: str, open_idx: int) -> int:
    """Index of the brace matching text[open_idx]=='{', or -1 if unbalanced."""
    depth = 0
    for k in range(open_idx, len(text)):
        c = text[k]
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return k
    return -1


def _skip_balanced(text: str, open_idx: int) -> int:
    end = _find_matching_brace(text, open_idx)
    return (end + 1) if end != -1 else len(text)


def _doi_from_url(url: str) -> Optional[str]:
    if not url:
        return None
    m = DOI_IN_TEXT_REGEX.search(url)
    return m.group(0) if m else None


def parse_json(text: str) -> List[Reference]:
    """Parse a JSON list of {author,title,year,journal,doi} (or a dict wrapping
    such a list under 'references'/'items'/'entries')."""
    data = json.loads(text)
    if isinstance(data, dict):
        for k in ("references", "items", "entries", "bibliography"):
            if isinstance(data.get(k), list):
                data = data[k]
                break
        else:
            # A single reference object.
            data = [data]
    if not isinstance(data, list):
        raise ValueError("JSON references must be a list (or a dict wrapping one).")

    refs: List[Reference] = []
    for idx, item in enumerate(data, start=1):
        if not isinstance(item, dict):
            refs.append(Reference(key=f"item {idx}", raw=str(item)))
            continue
        key = str(item.get("id") or item.get("key") or item.get("citation_key") or f"item {idx}")
        year = item.get("year")
        if isinstance(year, (int, float)):
            year = str(int(year))
        # CSL-JSON authors may be a list of {family,given}.
        author = item.get("author")
        if isinstance(author, list):
            author = _format_csl_authors(author)
        journal = (
            item.get("journal")
            or item.get("container-title")
            or item.get("venue")
            or item.get("booktitle")
        )
        doi = item.get("doi") or item.get("DOI")
        refs.append(
            Reference(
                key=key,
                author=author if isinstance(author, str) else None,
                title=item.get("title"),
                year=year if isinstance(year, str) else None,
                journal=journal if isinstance(journal, str) else None,
                doi=doi if isinstance(doi, str) else None,
                raw="",
            )
        )
    return refs


def _format_csl_authors(authors: List[Any]) -> Optional[str]:
    names = []
    for a in authors:
        if isinstance(a, dict):
            fam = a.get("family") or a.get("last") or ""
            giv = a.get("given") or a.get("first") or ""
            literal = a.get("literal")
            if literal:
                names.append(str(literal))
            elif fam or giv:
                names.append(f"{fam}, {giv}".strip(", "))
        elif isinstance(a, str):
            names.append(a)
    return "; ".join(n for n in names if n) or None


def parse_markdown(text: str) -> List[Reference]:
    """Best-effort parser for a markdown / numbered / plain-text reference list.

    Each reference is assumed to occupy one line (the common case for a pasted
    bibliography). Leading list markers ('1.', '[1]', '-', '*') are stripped.
    DOI and a plausible year are regex-extracted; the remaining text is kept as
    `raw` so missing-field checks can be relaxed (free text is not labeled)."""
    refs: List[Reference] = []
    for line in text.splitlines():
        s = line.strip()
        if not s:
            continue
        # Skip obvious heading / fence lines.
        if s.startswith("#") or s.startswith("```"):
            continue
        # Strip a leading enumerator: "1.", "12)", "[3]", "-", "*", "•".
        s_stripped = re.sub(r"^\s*(\[\d+\]|\(\d+\)|\d+[.)]|[-*•])\s+", "", s)
        if not s_stripped:
            continue
        doi_m = DOI_IN_TEXT_REGEX.search(s_stripped)
        doi = doi_m.group(0).rstrip(".") if doi_m else None
        year_m = YEAR_IN_TEXT_REGEX.search(s_stripped)
        year = year_m.group(1) if year_m else None
        refs.append(
            Reference(
                key=f"ref {len(refs) + 1}",
                title=None,
                year=year,
                doi=doi,
                raw=s_stripped,
            )
        )
    return refs


def parse_references(text: str, fmt: str) -> List[Reference]:
    if fmt == "bibtex":
        return parse_bibtex(text)
    if fmt == "json":
        return parse_json(text)
    if fmt == "md":
        return parse_markdown(text)
    raise ValueError(f"Unknown format: {fmt!r}")


# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------


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


def _check_doi(ref: Reference) -> List[Issue]:
    if not ref.doi:
        # No DOI is LOW (legitimate for older / grey-lit references).
        return [Issue("LOW", "DOI_MISSING", ref.key, "no DOI present")]
    canon = _normalize_doi(ref.doi)
    if not DOI_REGEX.match(canon):
        return [
            Issue(
                "HIGH",
                "DOI_INVALID",
                ref.key,
                f"malformed DOI {ref.doi!r} (expected 10.NNNN/suffix)",
            )
        ]
    return []


def _check_year(ref: Reference, min_year: int, max_year: int) -> List[Issue]:
    if not ref.year:
        return []  # missing-year handled by required-field check (structured fmts)
    m = re.search(r"(\d{4})", ref.year)
    if not m:
        return [Issue("HIGH", "YEAR_INVALID", ref.key, f"unparseable year {ref.year!r}")]
    y = int(m.group(1))
    if y < min_year or y > max_year:
        return [
            Issue(
                "HIGH",
                "YEAR_IMPLAUSIBLE",
                ref.key,
                f"year {y} outside plausible range [{min_year}, {max_year}]",
            )
        ]
    return []


def _check_forward_reference(ref: Reference, manuscript_year: int) -> List[Issue]:
    """Cited source dated after the manuscript's writing year = impossible basis.

    May co-fire with YEAR_IMPLAUSIBLE if the cited year also exceeds max_year;
    that is intentional — the two checks are orthogonal.
    """
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


def _check_required_fields(ref: Reference) -> List[Issue]:
    out: List[Issue] = []
    values = {
        "author": ref.author,
        "title": ref.title,
        "year": ref.year,
        "journal": ref.journal,
    }
    missing = [f for f in REQUIRED_FIELDS if not values[f]]
    if missing:
        out.append(
            Issue(
                "MEDIUM",
                "FIELD_MISSING",
                ref.key,
                f"missing required field(s): {', '.join(missing)}",
            )
        )
    return out


def _check_duplicate_dois(refs: List[Reference]) -> List[Issue]:
    by_doi: Dict[str, List[str]] = defaultdict(list)
    for ref in refs:
        if ref.doi:
            canon = _normalize_doi(ref.doi)
            if DOI_REGEX.match(canon):  # only dedupe well-formed DOIs
                by_doi[canon].append(ref.key)
    out: List[Issue] = []
    for doi, keys in by_doi.items():
        if len(keys) > 1:
            out.append(
                Issue(
                    "HIGH",
                    "DOI_DUPLICATE",
                    ", ".join(keys),
                    f"DOI {doi} appears in {len(keys)} entries: {', '.join(keys)}",
                )
            )
    return out


def _check_duplicate_titles(refs: List[Reference]) -> List[Issue]:
    by_title: Dict[str, List[str]] = defaultdict(list)
    for ref in refs:
        if ref.title:
            norm = _normalize_title(ref.title)
            if norm:
                by_title[norm].append(ref.key)
    out: List[Issue] = []
    for _norm, keys in by_title.items():
        if len(keys) > 1:
            out.append(
                Issue(
                    "HIGH",
                    "TITLE_DUPLICATE",
                    ", ".join(keys),
                    f"identical normalized title in {len(keys)} entries: {', '.join(keys)}",
                )
            )
    return out


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------


def summarize(issues: List[Issue]) -> Dict[str, int]:
    counts = Counter(i.severity for i in issues)
    return {sev: counts.get(sev, 0) for sev in SEVERITY_ORDER}


def build_report(
    refs: List[Reference],
    issues: List[Issue],
    fmt: str,
    min_year: int,
    max_year: int,
) -> Dict[str, Any]:
    counts = summarize(issues)
    return {
        "format": fmt,
        "reference_count": len(refs),
        "year_window": [min_year, max_year],
        "summary": counts,
        "passed": counts["HIGH"] == 0,
        "issues": [i.as_dict() for i in issues],
    }


def render_text(report: Dict[str, Any]) -> str:
    lines: List[str] = []
    lines.append("=" * 68)
    lines.append("  enviro-paper reference-integrity check (structural / offline)")
    lines.append("=" * 68)
    lines.append(f"  format            : {report['format']}")
    lines.append(f"  references parsed : {report['reference_count']}")
    yw = report["year_window"]
    lines.append(f"  plausible years   : {yw[0]}-{yw[1]}")
    lines.append("")

    issues = report["issues"]
    if not issues:
        lines.append("  No issues found. (Structural checks only — online DOI")
        lines.append("  resolution / existence verification is a separate step.)")
        lines.append("")
    else:
        by_sev: Dict[str, List[Dict[str, str]]] = defaultdict(list)
        for it in issues:
            by_sev[it["severity"]].append(it)
        for sev in SEVERITY_ORDER:
            group = by_sev.get(sev, [])
            if not group:
                continue
            lines.append(f"  [{sev}] {len(group)} issue(s)")
            lines.append("  " + "-" * 64)
            for it in group:
                lines.append(f"    - ({it['code']}) {it['key']}: {it['message']}")
            lines.append("")

    s = report["summary"]
    lines.append("  SUMMARY")
    lines.append("  " + "-" * 64)
    lines.append(f"    HIGH   : {s['HIGH']}")
    lines.append(f"    MEDIUM : {s['MEDIUM']}")
    lines.append(f"    LOW    : {s['LOW']}")
    verdict = "PASS (no high-severity issues)" if report["passed"] else "FAIL (high-severity issues present)"
    lines.append("")
    lines.append(f"  VERDICT: {verdict}")
    lines.append("=" * 68)
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------


def run_selftest() -> int:
    """Build an in-memory reference set with one of every defect and assert the
    check suite catches exactly them. No network, no files."""
    refs = [
        # Clean entry — should raise nothing.
        Reference("ok2020", "Smith, J.", "A clean study", "2020", "Water Res.", "10.1016/j.watres.2020.116001"),
        # Malformed DOI -> HIGH DOI_INVALID.
        Reference("baddoi", "Lee, K.", "Bad doi paper", "2021", "STOTEN", "not-a-doi"),
        # Implausible year -> HIGH YEAR_IMPLAUSIBLE.
        Reference("badyear", "Wang, L.", "Future paper", "2099", "ESPR", "10.1007/s11356-099-12345-6"),
        # Duplicate DOI of ok2020 -> HIGH DOI_DUPLICATE.
        Reference("dupdoi", "Chen, M.", "Different title here", "2020", "EP", "10.1016/j.watres.2020.116001"),
        # Duplicate title of ok2020 (different DOI) -> HIGH TITLE_DUPLICATE.
        Reference("duptitle", "Other, A.", "a clean STUDY", "2019", "JHM", "10.1016/j.jhazmat.2019.99999"),
        # Missing required fields (no journal) -> MEDIUM FIELD_MISSING.
        Reference("missing", "Author, B.", "Some title", "2018", None, "10.1021/es.2018.00001"),
        # No DOI -> LOW DOI_MISSING.
        Reference("nodoi", "Nobody, C.", "Old reference", "1995", "Mar. Pollut. Bull.", None),
    ]
    issues = check_references(refs, fmt="bibtex", min_year=1900, max_year=2026)
    codes = Counter(i.code for i in issues)

    assert codes["DOI_INVALID"] == 1, codes
    assert codes["YEAR_IMPLAUSIBLE"] == 1, codes
    assert codes["DOI_DUPLICATE"] == 1, codes
    assert codes["TITLE_DUPLICATE"] == 1, codes
    assert codes["FIELD_MISSING"] == 1, codes
    assert codes["DOI_MISSING"] == 1, codes  # only 'nodoi' lacks a DOI

    counts = summarize(issues)
    # HIGH = invalid + implausible + dup doi + dup title = 4.
    assert counts["HIGH"] == 4, counts
    assert counts["MEDIUM"] == 1, counts
    assert counts["LOW"] == 1, counts

    # Forward reference (cited year > manuscript year) -> HIGH TEMPORAL_FORWARD_REF.
    fwd_refs = [
        Reference("future", "Ahead, Z.", "Cited from the future", "2027", "STOTEN", "10.1016/j.stoten.2027.1"),
        Reference("okpast", "Past, Y.", "A normal prior", "2019", "Water Res.", "10.1016/j.watres.2019.2"),
        Reference("sameyr", "Now, N.", "Same year as manuscript", "2025", "EP", "10.1016/j.envpol.2025.3"),
    ]
    fwd_issues = check_references(fwd_refs, fmt="bibtex", manuscript_year=2025)
    fwd_codes = Counter(i.code for i in fwd_issues)
    assert fwd_codes["TEMPORAL_FORWARD_REF"] == 1, fwd_codes
    # Without manuscript_year, no temporal check fires.
    none_issues = check_references(fwd_refs, fmt="bibtex")
    assert Counter(i.code for i in none_issues)["TEMPORAL_FORWARD_REF"] == 0, none_issues

    # Format-detection sanity.
    assert detect_format(Path("x.bib"), "@article{a, doi={10.1/x}}") == "bibtex"
    assert detect_format(Path("x.json"), "[]") == "json"
    assert detect_format(None, '[{"title": "t"}]') == "json"
    assert detect_format(None, "@article{k, title={T}}") == "bibtex"
    assert detect_format(Path("x.md"), "1. Some ref 2020.") == "md"

    # Parser round-trips.
    bib = "@article{k1,\n author = {Smith, J.},\n title = {{A Title}},\n year = {2020},\n journal = {Water Research},\n doi = {10.1016/j.watres.2020.1}\n}"
    parsed = parse_bibtex(bib)
    assert len(parsed) == 1 and parsed[0].key == "k1", parsed
    assert parsed[0].doi == "10.1016/j.watres.2020.1", parsed[0].doi
    assert parsed[0].title == "A Title", parsed[0].title

    md = "1. Smith J. (2020). A study. https://doi.org/10.1016/j.watres.2020.5\n[2] No doi here, 2015."
    pmd = parse_markdown(md)
    assert len(pmd) == 2, pmd
    assert pmd[0].year == "2020" and pmd[0].doi == "10.1016/j.watres.2020.5", pmd[0].as_dict()
    assert pmd[1].year == "2015" and pmd[1].doi is None, pmd[1].as_dict()

    print("selftest: OK")
    return 0


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        prog="check_references.py",
        description="Structural, offline reference-integrity checker for env-sci papers.",
        epilog="Online DOI resolution / existence verification is a SEPARATE step; "
        "a clean report here means structurally plausible, not real.",
    )
    parser.add_argument(
        "path",
        nargs="?",
        help="Path to a .bib / .json / .md(.txt) reference file.",
    )
    parser.add_argument(
        "--format",
        choices=("auto", "bibtex", "json", "md"),
        default="auto",
        help="Input format (default: auto-detect by extension/content).",
    )
    parser.add_argument(
        "--min-year",
        type=int,
        default=DEFAULT_MIN_YEAR,
        help=f"Lowest plausible publication year (default {DEFAULT_MIN_YEAR}).",
    )
    parser.add_argument(
        "--max-year",
        type=int,
        default=DEFAULT_MAX_YEAR,
        help=f"Highest plausible publication year (default {DEFAULT_MAX_YEAR}).",
    )
    parser.add_argument(
        "--manuscript-year",
        type=int,
        default=None,
        help="Manuscript writing year; enables forward-reference check "
        "(any cited year > this is flagged TEMPORAL_FORWARD_REF).",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit a machine-readable JSON report instead of human-readable text.",
    )
    parser.add_argument(
        "--out",
        help="Write the report to this file instead of stdout.",
    )
    parser.add_argument(
        "--selftest",
        action="store_true",
        help="Run the inline self-test (no file/network needed) and exit.",
    )
    args = parser.parse_args(argv)

    if args.selftest:
        return run_selftest()

    if not args.path:
        parser.error("a reference file path is required (or use --selftest)")

    path = Path(args.path)
    if not path.is_file():
        print(f"error: file not found: {path}", file=sys.stderr)
        return 1

    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as e:
        # Retry latin-1 for stubborn legacy exports.
        try:
            text = path.read_text(encoding="latin-1")
        except OSError:
            print(f"error: could not read {path}: {e}", file=sys.stderr)
            return 1

    fmt = args.format if args.format != "auto" else detect_format(path, text)

    try:
        refs = parse_references(text, fmt)
    except (ValueError, json.JSONDecodeError) as e:
        print(f"error: could not parse {path} as {fmt}: {e}", file=sys.stderr)
        return 1

    if not refs:
        print(
            f"warning: no references parsed from {path} (format={fmt}). "
            "Check --format or the file content.",
            file=sys.stderr,
        )

    issues = check_references(
        refs, fmt, min_year=args.min_year, max_year=args.max_year,
        manuscript_year=args.manuscript_year,
    )
    report = build_report(refs, issues, fmt, args.min_year, args.max_year)

    output = json.dumps(report, indent=2, ensure_ascii=False) if args.json else render_text(report)

    if args.out:
        try:
            Path(args.out).write_text(output + "\n", encoding="utf-8")
        except OSError as e:
            print(f"error: could not write {args.out}: {e}", file=sys.stderr)
            return 1
    else:
        print(output)

    return 0 if report["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
