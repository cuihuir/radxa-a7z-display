# A733 Display Landscape Research

## Purpose

Capture what is known about HDMI display support on A733 boards, especially the difference between vendor BSP support and what can reasonably be expected from Debian 12.

## Observations

- Radxa A7Z exposes both Micro HDMI and USB-C with DisplayPort Alt Mode support, so the hardware path exists.
- Radxa's public release line shows Debian desktop images, but the stable public evidence does not point to a fully polished Debian 12 desktop path for A733.
- Community discussion indicates Micro HDMI is the more reliable display path than USB-C to HDMI adapters.
- Orange Pi's A733 boards and build tree show explicit Bookworm support and a more active effort around the desktop image path.
- Mesa's PowerVR support for BXM-4-64 exists, but it is still an active-development path rather than a finished "everything just works" desktop stack.

## Working conclusion

Debian 12 HDMI desktop on A733 is plausible, but it is not a "stock Debian only" problem. It depends on board support package quality, kernel display plumbing, firmware or user-space GPU components, and validation discipline.

## Evidence handling rule

Any claim in this file should be backed by one of:

- An official board page.
- A vendor release page.
- A source repository or board configuration file.
- A reproducible validation result recorded in this repository.

