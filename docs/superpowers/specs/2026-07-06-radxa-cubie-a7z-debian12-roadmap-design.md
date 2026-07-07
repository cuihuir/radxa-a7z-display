# Radxa Cubie A7Z Debian 12 Desktop Roadmap Design

## Goal

Bring up a working HDMI desktop on the Radxa Cubie A7Z using Debian 12 as the primary target. Debian 13 remains a secondary follow-up target, and Armbian stays available as a fallback path if it is materially easier to maintain.

## What success looks like

- The board boots reliably.
- Micro HDMI produces a stable display output.
- A desktop login/session appears on Debian 12.
- The system remains usable without needing a perfect graphics stack on day one.
- The work is documented well enough that the next step can be repeated or adjusted without starting over.

## Constraints

- The official Radxa A7Z public Debian 11 image is the current baseline, but it is not the final target.
- Radxa's public A733/RSDK materials indicate that A733 graphics support is limited and that some desktop components need special handling.
- Debian 12 is the main target, so choices should favor compatibility and stability over novelty.
- The first bring-up path should use the simplest display route: Micro HDMI.

## Recommended approach

Use the existing Radxa Debian 11 image and Radxa A733 build metadata as the reference baseline, then move toward Debian 12 in small steps:

1. Confirm the board boots on the existing known-good path.
2. Rebuild or adapt the image layer for Debian 12 while keeping the board-specific boot and display pieces intact.
3. Keep Micro HDMI as the first validation path.
4. Accept software rendering or incomplete acceleration early if needed, as long as the desktop is usable.
5. Record every step with an explicit pass/fail check.

This is the least risky route because it preserves the known board-specific pieces while changing only the distro layer and the desktop packaging as needed.

## Alternative paths considered

### Option A: Debian 12 first, minimal desktop

Target a minimal desktop bring-up as soon as possible, even if GPU acceleration is incomplete.

Pros:
- Fastest route to visible progress.
- Best fit for a personal project.
- Lowest risk of getting stuck on graphics polish.

Cons:
- The desktop may begin as software-rendered or partially accelerated.

### Option B: Debian 11 baseline migration

Start from the official Radxa Debian 11 image and move package-by-package toward Debian 12.

Pros:
- Closest to the current vendor baseline.
- Easier to identify what breaks during the upgrade.

Cons:
- Can trap the work in old packaging assumptions.
- May slow down the actual Debian 12 desktop goal.

### Option C: Armbian fallback

Use Armbian if it provides a quicker desktop path on the same board.

Pros:
- Could save time if Radxa packaging is too brittle.

Cons:
- Splits attention away from the primary Debian 12 goal.
- Adds another distribution-specific maintenance track.

Recommendation: Option A with the official Debian 11 image kept as a reference, not as the main destination.

## Roadmap

### Phase 1: Boot and display

Goal:
- Prove the board still boots and can drive Micro HDMI on the chosen image path.

Checks:
- Board powers on cleanly.
- HDMI signal appears.
- Kernel logs show the expected display path.

### Phase 2: Desktop entry

Goal:
- Reach a desktop login or session on Debian 12.

Checks:
- Display manager or session starts.
- Keyboard and mouse input work.
- Desktop is usable even if acceleration is limited.

### Phase 3: Graphics hardening

Goal:
- Improve GPU usage and reduce obvious rendering issues.

Checks:
- Confirm whether the session is software-rendered or accelerated.
- Confirm whether the chosen desktop stack is stable across reboots.

### Phase 4: Maintenance path

Goal:
- Keep the result reproducible.

Checks:
- Build steps are documented.
- Validation records exist for each major test.
- A second run can reproduce the same outcome.

## Validation standard

Each milestone should record:

- Board and revision.
- Image or build source.
- Kernel version.
- Display path.
- Desktop environment or session manager.
- Result observed.
- Evidence captured, such as log snippets or screenshots.

Minimum pass criteria for Phase 2:

- The board boots.
- Micro HDMI works.
- A usable desktop session appears.

Minimum pass criteria for the overall goal:

- Debian 12 desktop works on the A7Z with a documented path that can be repeated.

## Source anchors

- Radxa A7Z public product page and downloads.
- Radxa RSDK A733 metadata and package logic.
- Orange Pi A733 build tree as a reference for Debian 12 desktop packaging.
- The local source comparison tool output in this repository.

