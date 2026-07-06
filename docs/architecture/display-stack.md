# Display Stack Architecture

## Goal

Define the minimum display stack required to bring up and keep an HDMI desktop working on A733 boards.

## Layers

1. Bootloader and firmware
   - Select the correct board configuration.
   - Load the correct device tree and kernel arguments.

2. Kernel and DRM/KMS
   - Provide panel, HDMI, and connector detection.
   - Handle framebuffer handoff and modesetting.

3. User-space graphics
   - Start a display manager or compositor.
   - Load any required GPU user-space components.

4. Desktop session
   - Launch a minimal desktop environment that can be used to validate display, input, and basic rendering.

## Design principles

- Prefer the simplest hardware path that works reliably.
- Treat Micro HDMI as the primary bring-up path unless evidence shows another path is equally stable.
- Keep vendor-specific parts isolated so they can be swapped or updated without rewriting the whole stack.
- Document every hardware-specific assumption explicitly.

## Risks

- GPU user-space compatibility may lag behind kernel support.
- USB-C display paths may depend on a different and less stable subsystem than Micro HDMI.
- Debian release upgrades can break one layer even when another layer still boots.

