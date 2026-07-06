# Project Overview

## Goal

Build and maintain a Debian 12-oriented HDMI desktop bring-up path for A733-based boards, starting from Radxa A7Z/Z7A and using Orange Pi A733 boards as reference material where useful.

## Scope

This project covers:

- Board-level display bring-up on A733 hardware.
- HDMI-connected GUI desktop on Debian 12 or later.
- Documentation of BSP dependencies, kernel/display stack constraints, and practical validation steps.
- Cross-vendor comparison between Radxa and Orange Pi A733 implementations.
- Long-term maintenance rules for assets, notes, and decisions.

This project does not cover:

- General-purpose Linux support for unrelated boards.
- Application-layer desktop customization beyond what is needed to validate the display stack.
- Upstream kernel or Mesa development unrelated to A733 display bring-up unless it directly affects the board support path.

## Working model

The repository is documentation-first. Source material, test results, and conclusions should be captured as files, not as transient chat history.

## Success criteria

- A maintainer can understand the current state of A733 HDMI desktop support without reading chat history.
- The repository contains a clear record of constraints, known-good validation steps, and open risks.
- The document set stays bilingual and internally consistent over time.

## Key references

- Radxa A7Z documentation: https://docs.radxa.com/en/cubie/a7z
- Radxa build repository: https://github.com/radxa-build/radxa-cubie-a7z
- Radxa A733 build repository: https://github.com/radxa-build/radxa-a733
- Armbian forum discussion: https://forum.armbian.com/topic/56130-radxa-cubie-a7aa7z-allwinner-a733/

