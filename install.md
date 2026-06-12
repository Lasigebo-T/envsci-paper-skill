# Installing the envsci-paper skill collection

This repo is a **collection of 9 Agent Skills** (1 umbrella `enviro-paper` + 8 `envsci-*` function
skills). Each is one folder under `skills/`, centred on `SKILL.md` (+ `references/` and, where
relevant, `scripts/`). Copy whole folders, not just `SKILL.md`.

You can install **all 9** (recommended) or **just the one(s) you need** — each skill is standalone
and independently selectable.

```text
skills/
├── enviro-paper/        # umbrella orchestrator (full pipeline) — SKILL.md only
├── envsci-ideate/       # ideation / novelty
├── envsci-litsearch/    # literature discovery + sourcing
├── envsci-data/         # QA/QC, stats, pollution & risk indices
├── envsci-figures/      # env-sci publication figures (+ scripts/envsci_style.py)
├── envsci-writing/      # IMRaD drafting + polishing
├── envsci-citations/    # citation formatting + integrity gate (+ scripts/check_references.py)
├── envsci-review/       # peer-review simulation + response letters
└── envsci-journals/     # target-journal scope/format + fit
```

## 1. Claude Code

**Plugin marketplace (whole collection):**
```bash
claude plugin marketplace add Lasigebo-T/envsci-paper-skill
claude plugin install enviro-paper@envsci-paper-skill
```

**Manual — all 9:**
```bash
git clone https://github.com/Lasigebo-T/envsci-paper-skill.git
mkdir -p ~/.claude/skills
cp -R envsci-paper-skill/skills/* ~/.claude/skills/
```

**Manual — only one skill (e.g. figures):**
```bash
cp -R envsci-paper-skill/skills/envsci-figures ~/.claude/skills/
```

**Windows (PowerShell):**
```powershell
git clone https://github.com/Lasigebo-T/envsci-paper-skill.git
New-Item -ItemType Directory -Force "$HOME\.claude\skills" | Out-Null
Copy-Item -Recurse -Force ".\envsci-paper-skill\skills\*" "$HOME\.claude\skills\"
```

## 2. Codex

```bash
codex plugin marketplace add https://github.com/Lasigebo-T/envsci-paper-skill --ref main
codex plugin add enviro-paper@envsci-paper-skill
# or manual:
git clone https://github.com/Lasigebo-T/envsci-paper-skill.git
mkdir -p ~/.codex/skills && cp -R envsci-paper-skill/skills/* ~/.codex/skills/
```

## 3. Figure companion (recommended)

`envsci-figures` composes with the separate **scipilot-figure-skill** (general chart selection,
visual-QA loop, journal specs, Chinese fonts). Install it on its own:
```bash
git clone https://github.com/Haojae/scipilot-figure-skill.git
cp -R scipilot-figure-skill ~/.claude/skills/      # or ~/.codex/skills/
```

## 4. Verify

```bash
# from inside the repo
python skills/envsci-citations/scripts/check_references.py --selftest    # selftest: OK
python skills/envsci-figures/scripts/envsci_style.py --demo all          # 12 demo figures
```
Use `py` instead of `python` on Windows if `python` opens the Microsoft Store. The figure script
needs `matplotlib numpy pandas` (`pip install -r skills/envsci-figures/scripts/requirements.txt`).

## 5. Install from a local zip (no GitHub)

Unzip, then copy the inner `skills/<name>/` folder(s) into `~/.claude/skills/` (Claude Code) or
`~/.codex/skills/` (Codex), and restart the agent.
