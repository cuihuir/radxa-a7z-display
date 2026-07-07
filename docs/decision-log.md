# Decision Log

## How to use this file

Record durable project decisions here. Keep notes short and explicit.

## Entry format

- Date
- Decision
- Reason
- Impact

## Current decisions

### 2026-07-06: Repository language policy

- Decision: English is the source of truth and every core document must have a Chinese translation.
- Reason: The project will be maintained over time and needs a stable bilingual record.
- Impact: Every major doc change must update both language versions.

### 2026-07-06: Repository identity

- Decision: Use `radxa-a7z-display` as the project name.
- Reason: The name is specific, searchable, and matches the project scope.
- Impact: The repository, documentation, and future GitHub remote should use this identity.

### 2026-07-06: Source comparison tool scope

- Decision: Start with a small comparison tool that inspects vendor source trees and renders a Markdown diff report.
- Reason: The most useful first code step is a tool that helps compare board configs, family configs, and DTS files without pulling in download or build automation.
- Impact: The initial implementation stays small, testable, and directly useful for A733 port analysis.

### 2026-07-06: Tree check subcommand

- Decision: Add a single-tree validation mode to the comparison tool for minimum A733 source-tree checks.
- Reason: A lightweight source-tree checker is a more useful next step than a download or build pipeline.
- Impact: The tool can now answer both "what differs" and "is this tree minimally ready to inspect?".

### 2026-07-06: Radxa source tree target

- Decision: Treat `rsdk` as the real Radxa A733 build source and keep `radxa-cubie-a7z` as a release/workflow shell.
- Reason: The public Radxa product repo only points to the builder; the actual A733 policy and package wiring live in `rsdk`.
- Impact: Source comparison and port analysis should use `rsdk` against Orange Pi's build tree.

### 2026-07-06: A7Z Debian 12 report generator

- Decision: Add a dedicated A7Z Debian 12 migration report generator that reads the local Radxa and Orange Pi source trees.
- Reason: The main goal is to get `radxa-cubie-a7z` onto Debian 12 desktop, so the tool should turn source signals into a practical migration brief.
- Impact: The repository now has a code path that supports the actual porting decision instead of only comparing trees.
