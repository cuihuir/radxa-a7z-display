# radxa-a7z-display

Documentation hub for bringing up and maintaining HDMI desktop support on Allwinner A733 boards, with a focus on Radxa A7Z/Z7A and related Orange Pi references.

## What this repository is for

- Collect and preserve research notes about A733 display support.
- Record the technical constraints around Debian 12 desktop bring-up.
- Track implementation decisions, validation steps, and long-term maintenance rules.
- Keep English source documents and Chinese translations side by side.

## Document map

- [Project Overview](docs/project-overview.md)
- [Current Status](docs/status.md)
- [Display Landscape Research](docs/research/a733-display-landscape.md)
- [Display Stack Architecture](docs/architecture/display-stack.md)
- [Contributing Guide](docs/contributing.md)
- [Naming Conventions](docs/naming-conventions.md)
- [Validation Guide](docs/validation.md)
- [Decision Log](docs/decision-log.md)
- [Sources Index](docs/sources.md)

## Maintenance rules

- English documents are the source of truth.
- Every core document must have a matching `.zh-CN.md` translation.
- Keep decisions in the decision log, not scattered across notes.
- Add sources for any hardware, BSP, or release claim before treating it as a project fact.

## Current status

- Project name: `radxa-a7z-display`
- Scope: Debian 12 HDMI desktop bring-up and long-term maintenance on A733 boards
- Repository state: local git initialized
