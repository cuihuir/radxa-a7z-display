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

### 2026-07-06: Radxa A733 Bookworm trial branch

- Decision: Expose `bookworm` in the local Radxa `rsdk` trial branch for `radxa-a733` and keep the existing `kde` default.
- Reason: The actual build path needs a Debian 12 entry point before runtime validation can begin.
- Impact: `radxa-a733` now defaults to `bookworm` locally, and the next step is a real build/boot test on A7Z.

### 2026-07-13: Do not PiShrink A733 release images

- Decision: Release the verified raw image compressed with XZ or Zstandard; do not run PiShrink or another tool that rewrites the GPT.
- Reason: The raw RSDK `output.img` boots on A7Z, while the PiShrink output does not. PiShrink changed the root partition UUID and removed its `LegacyBIOSBootable` GPT attribute.
- Impact: `v0.1.0-a733-debian12-kde` is withdrawn as an install image. A replacement must preserve the original partition table byte-for-byte and be flashed and boot-tested before release.

### 2026-07-14: Restore EDID-native HDMI selection

- Decision: Remove A733's forced-FHD/largest-60Hz DRM policy and select DRM preferred modes before a first-mode fallback.
- Reason: The policy forced the `FLY-HDMI-LCD7` native `1024x600` panel to use `1920x1080`, causing stretching and cropping.
- Impact: The verified stable deployment is the vendor `5.15.147-21-a733` kernel with the patched A7Z DTB; future full-kernel packages must avoid concurrent DKMS rebuilds.

### 2026-07-14: Keep the A7Z initramfs near the vendor size

- Decision: Package an initramfs hook that removes early fsck binaries and their ext2fs-only libraries from the A7Z display kernel initramfs.
- Reason: Valid 42.67 MB initramfs images failed before persistent kernel logging, while 42.25 MB images booted with the same kernel, DTB, modules, and command line.
- Impact: The `+display2` package generates a 42,251,173-byte initramfs and boots successfully. System and offline filesystem repair tools remain installed on the root filesystem.
