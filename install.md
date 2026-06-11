# Installing `enviro-paper`

`enviro-paper` is **not** a Python or npm package. It is one reusable Agent Skill folder
centred on `SKILL.md`. The important rule:

- copy the **entire** `skills/enviro-paper/` folder, not only `SKILL.md`
- the workflow depends on `references/` (deep how-to) and `scripts/` (runnable tools)
- copying only `SKILL.md` will silently break figure generation and the integrity gate

It works in any agent that supports the open [Agent Skills](https://agentskills.io/) standard.
Below are the two most common hosts.

---

## 1. What gets installed

```text
skills/
└── enviro-paper/
    ├── SKILL.md            # the router (always read first)
    ├── references/         # 7 on-demand deep references
    └── scripts/            # envsci_style.py, check_references.py, requirements.txt
```

---

## 2. Codex

### Option A — plugin marketplace (whole bundle)

```bash
codex plugin marketplace add https://github.com/Lasigebo-T/envsci-paper-skill --ref main
codex plugin add enviro-paper@envsci-paper-skill
```

If the skill does not appear, refresh the plugin page or start a new Codex session. (Exact
marketplace syntax can vary by Codex version; if in doubt use Option B, which always works.)

### Option B — manual local skill

```bash
git clone https://github.com/Lasigebo-T/envsci-paper-skill.git
cd envsci-paper-skill
mkdir -p ~/.codex/skills
cp -R skills/enviro-paper ~/.codex/skills/
```

Restart Codex. Then ask naturally, e.g. `Compute Igeo and the Hakanson risk index for these sediments.`

---

## 3. Claude Code

### Option A — plugin marketplace (whole bundle)

```bash
claude plugin marketplace add Lasigebo-T/envsci-paper-skill
claude plugin install enviro-paper@envsci-paper-skill
```

### Option B — manual user skill

```bash
git clone https://github.com/Lasigebo-T/envsci-paper-skill.git
mkdir -p ~/.claude/skills
cp -R envsci-paper-skill/skills/enviro-paper ~/.claude/skills/
```

Start a new Claude Code session. The skill auto-triggers on environmental-science requests, or
call it explicitly with `/enviro-paper`.

### Windows (PowerShell)

```powershell
git clone https://github.com/Lasigebo-T/envsci-paper-skill.git
New-Item -ItemType Directory -Force "$HOME\.claude\skills" | Out-Null
Copy-Item -Recurse -Force ".\envsci-paper-skill\skills\enviro-paper" "$HOME\.claude\skills\"
```

> **Python on Windows:** if `python` opens the Microsoft Store and does nothing, use the `py`
> launcher instead — e.g. `py "$HOME\.claude\skills\enviro-paper\scripts\envsci_style.py" --demo all`.

---

## 4. Install from a local download (no GitHub needed)

If someone gave you a `envsci-paper-skill-v1.0.0.zip`:

1. Unzip it anywhere.
2. Copy the inner `skills/enviro-paper/` folder into `~/.claude/skills/` (Claude Code) or
   `~/.codex/skills/` (Codex).
3. Restart the agent.

That's the whole install — the skill is plain text + two Python scripts.

---

## 5. Verify the install

```bash
# from inside the skill folder
python scripts/check_references.py --selftest      # prints: selftest: OK
python scripts/envsci_style.py --demo all          # writes 12 demo figures to _demo_figs/
```

(Use `py` instead of `python` on Windows if needed.) Requires `matplotlib numpy pandas`
for the figure script: `pip install -r scripts/requirements.txt`.

---

## 6. Update

```bash
cd envsci-paper-skill
git pull
cp -R skills/enviro-paper ~/.claude/skills/      # or ~/.codex/skills/
```
