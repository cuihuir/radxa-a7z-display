# Radxa Cubie A7Z Debian 12 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a small, practical toolchain that helps port `radxa-cubie-a7z` toward a Debian 12 desktop by extracting the relevant Radxa and Orange Pi source-tree signals, then turning them into an A7Z-specific migration report.

**Architecture:** Keep the code focused on one job: inspect the local Radxa RSDK tree and the local Orange Pi build tree, extract A7Z-related product, package, and board metadata, and render a concise Markdown report with explicit gaps. The tool should not download images, build kernels, or flash boards. It should make the next human decision easier.

**Tech Stack:** Python 3.14, standard library only, unittest, Markdown

---

### Task 1: Define the A7Z Debian 12 report shape

**Files:**
- Create: `docs/a7z-debian12-report-format.md`
- Create: `docs/a7z-debian12-report-format.zh-CN.md`

- [ ] **Step 1: Write the report sections**

```md
## Inputs
## Radxa signals
## Orange Pi signals
## Debian 12 desktop implications
## Missing pieces
## Recommended next action
```

- [ ] **Step 2: Commit the format document**

```bash
git add docs/a7z-debian12-report-format.md docs/a7z-debian12-report-format.zh-CN.md
git commit -m "docs: define A7Z Debian 12 report format"
```

### Task 2: Add the A7Z Debian 12 report generator

**Files:**
- Create: `tools/a7z_debian12_report.py`
- Create: `tests/test_a7z_debian12_report.py`
- Modify: `README.md`

- [ ] **Step 1: Write the failing tests**

```python
def test_report_includes_radxa_a733_trixie_and_kmscon():
    ...

def test_report_includes_orangepi_a733_bookworm_and_pvrsrvkm():
    ...

def test_report_flags_missing_builder_tree_as_gap():
    ...
```

- [ ] **Step 2: Run the tests and confirm they fail**

Run: `python3 -m unittest discover -s tests -v`
Expected: fail because `tools.a7z_debian12_report` does not exist yet.

- [ ] **Step 3: Implement the minimal generator**

```python
def build_report(radxa_root: Path, orangepi_root: Path) -> str:
    ...
```

- [ ] **Step 4: Run the tests again**

Run: `python3 -m unittest discover -s tests -v`
Expected: pass.

- [ ] **Step 5: Add a README entry**

```md
- `python3 tools/a7z_debian12_report.py <radxa-rsdk> <orangepi-build> --output report.md`
```

### Task 3: Make the report actionable

**Files:**
- Modify: `docs/decision-log.md`
- Modify: `docs/decision-log.zh-CN.md`
- Modify: `docs/status.md`
- Modify: `docs/status.zh-CN.md`

- [ ] **Step 1: Record the decision to focus on Debian 12 first**

```md
- Decision: Debian 12 is the primary A7Z desktop target.
```

- [ ] **Step 2: Record the current implementation status**

```md
- A7Z Debian 12 report generator exists.
```

- [ ] **Step 3: Commit the implementation milestone**

```bash
git add README.md tools/a7z_debian12_report.py tests/test_a7z_debian12_report.py docs/decision-log.md docs/decision-log.zh-CN.md docs/status.md docs/status.zh-CN.md
git commit -m "feat: add A7Z Debian 12 report generator"
```

