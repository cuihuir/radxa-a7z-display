# Validation Guide

## Purpose

Define how we prove a claim, a build, or a bring-up step is real.

## Validation levels

1. Documentation validation
   - Check that links resolve.
   - Check that English and Chinese versions match in scope.
   - Check that claims are sourced.

2. Build validation
   - Record the exact build command.
   - Record the board, image type, and release version.
   - Record success or failure with the relevant log snippet.

3. Bring-up validation
   - Record the display path used, such as Micro HDMI or USB-C DP Alt Mode.
   - Record whether a desktop session starts.
   - Record whether graphics acceleration is available or only software rendering is used.

## Minimum evidence for a hardware claim

- Board name and revision.
- Kernel or image version.
- Display path used.
- Result observed.
- Source of the result, such as a log, screenshot, or reproducible command output.

