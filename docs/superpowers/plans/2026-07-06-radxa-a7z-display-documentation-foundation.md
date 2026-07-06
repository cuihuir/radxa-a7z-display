# radxa-a7z-display Documentation Foundation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Establish the repository documentation foundation, bilingual structure, and local git baseline for long-term A733 HDMI display work.

**Architecture:** The repository is documentation-first. English documents serve as the source of truth, with matching Chinese translations stored beside them. A root README acts as the entry point, while topical documents capture overview, research, architecture, contribution rules, naming, validation, decisions, and sources.

**Tech Stack:** Markdown, local git

---

### Task 1: Create the repository entry points

**Files:**
- Create: `README.md`
- Create: `docs/project-overview.md`
- Create: `docs/project-overview.zh-CN.md`

- [ ] **Step 1: Write the repository summary**

```md
# radxa-a7z-display

Documentation hub for bringing up and maintaining HDMI desktop support on Allwinner A733 boards.
```

- [ ] **Step 2: Add the bilingual project overview**

```md
## Goal

Build and maintain a Debian 12-oriented HDMI desktop bring-up path for A733-based boards.
```

- [ ] **Step 3: Commit the entry points**

```bash
git add README.md docs/project-overview.md docs/project-overview.zh-CN.md
git commit -m "docs: add repository entry points"
```

### Task 2: Add research and architecture references

**Files:**
- Create: `docs/research/a733-display-landscape.md`
- Create: `docs/research/a733-display-landscape.zh-CN.md`
- Create: `docs/architecture/display-stack.md`
- Create: `docs/architecture/display-stack.zh-CN.md`

- [ ] **Step 1: Document the display landscape**

```md
- Radxa A7Z exposes both Micro HDMI and USB-C with DisplayPort Alt Mode support.
- Orange Pi's A733 build tree shows explicit Bookworm support.
```

- [ ] **Step 2: Document the display stack layers**

```md
1. Bootloader and firmware
2. Kernel and DRM/KMS
3. User-space graphics
4. Desktop session
```

- [ ] **Step 3: Commit the research and architecture docs**

```bash
git add docs/research/a733-display-landscape.md docs/research/a733-display-landscape.zh-CN.md docs/architecture/display-stack.md docs/architecture/display-stack.zh-CN.md
git commit -m "docs: add display research and architecture"
```

### Task 3: Add governance and validation docs

**Files:**
- Create: `docs/contributing.md`
- Create: `docs/contributing.zh-CN.md`
- Create: `docs/naming-conventions.md`
- Create: `docs/naming-conventions.zh-CN.md`
- Create: `docs/validation.md`
- Create: `docs/validation.zh-CN.md`
- Create: `docs/decision-log.md`
- Create: `docs/decision-log.zh-CN.md`
- Create: `docs/sources.md`
- Create: `docs/sources.zh-CN.md`

- [ ] **Step 1: Add contribution, naming, and validation rules**

```md
- Update English first, then the matching Chinese translation.
- Use kebab-case names and `.zh-CN.md` translation suffixes.
- Record board, image version, display path, and observed result for validation.
```

- [ ] **Step 2: Add the decision log and sources index**

```md
### 2026-07-06: Repository language policy

- Decision: English is the source of truth and every core document must have a Chinese translation.
```

- [ ] **Step 3: Commit the governance docs**

```bash
git add docs/contributing.md docs/contributing.zh-CN.md docs/naming-conventions.md docs/naming-conventions.zh-CN.md docs/validation.md docs/validation.zh-CN.md docs/decision-log.md docs/decision-log.zh-CN.md docs/sources.md docs/sources.zh-CN.md
git commit -m "docs: add governance and validation guidance"
```

### Task 4: Finalize the local git baseline

**Files:**
- Create: `.gitignore`

- [ ] **Step 1: Add a minimal ignore file**

```gitignore
# Local scratch space
.DS_Store
*.swp
*.tmp
```

- [ ] **Step 2: Check repository status**

```bash
git status --short
```

- [ ] **Step 3: Commit the baseline**

```bash
git add .gitignore docs/superpowers/plans/2026-07-06-radxa-a7z-display-documentation-foundation.md
git commit -m "docs: finalize documentation baseline"
```

