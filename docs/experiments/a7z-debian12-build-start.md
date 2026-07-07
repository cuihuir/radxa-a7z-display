# A7Z Debian 12 Build And Startup Notes

## Build location

Build the image on a host machine, not on the A7Z board.

The A7Z should be used for flashing and boot validation only. RSDK builds a root filesystem and disk image using host-side tools, Debian package repositories, `qemu-user-static`, and chroot/image assembly helpers.

## Recommended build environment

Use one of these:

- Debian 12 host or VM.
- Ubuntu 22.04/24.04 host or VM.
- A privileged Debian 12 container/devcontainer on the local workstation.
- The existing local `debian12` distrobox for metadata checks and dry runs.

The current workstation has `dnf`, `podman`, and `distrobox`. RSDK native setup only handles Debian/Ubuntu via `apt`, so do not try to build directly on this host without a Debian/Ubuntu container or VM.

## Local source state

The local `sources/rsdk` tree has already been modified so that:

- `radxa-a733` defaults to `bookworm`.
- `radxa-a733` keeps `kde` as the default desktop edition.
- Allwinner `soc_install_recommends` includes `bookworm`.
- RSDK Jsonnet avoids newer standard-library calls unsupported by Debian 12 `jsonnet 0.18.0`.

The same change is preserved as:

```bash
patches/rsdk/0001-enable-bookworm-on-radxa-a733.patch
patches/rsdk/0002-jsonnet-0.18-compat.patch
patches/rsdk/0003-a733-bookworm-use-generic-radxa-repo.patch
patches/rsdk/0004-a733-bookworm-skip-radxa-otgutils.patch
patches/rsdk/0005-rsdk-image-tool-dependencies-and-sgdisk-path.patch
```

Two extra Bookworm-specific fixes are currently needed:

- RSDK must skip the nonexistent `https://radxa-repo.github.io/a733-bookworm` repository and use the generic Radxa `bookworm` repository instead.
- RSDK must skip `radxa-otgutils` for A733/Bookworm because its `postinst` calls `deb-systemd-invoke daemon-reload -q` in a way that fails inside the mmdebstrap chroot.
- RSDK setup/image generation should include `libguestfs-tools`, `gdisk`, and a stable `sgdisk` PATH for distrobox-style environments.

## First dry run

From the repository root:

```bash
sources/rsdk/src/bin/rsdk build --dry-run radxa-a733
```

Expected early line:

```text
Building radxa-a733 bookworm kde...
```

This confirms that the A733 Debian 12 default selection is active.

## Host dependency setup

For a Debian/Ubuntu build environment, initialize submodules first:

```bash
cd sources/rsdk
git submodule update --recursive --init
```

Then run RSDK setup:

```bash
src/bin/rsdk setup
```

If running setup manually, the important host-side packages include:

```bash
sudo apt-get update
sudo dpkg --add-architecture arm64
sudo apt-get install -y \
  bash-completion \
  bdebstrap \
  binfmt-support \
  qemu-user-static \
  libguestfs-tools \
  gdisk \
  debian-archive-keyring \
  debian-ports-archive-keyring \
  jsonnet \
  jq \
  gpg \
  libfakechroot:arm64 \
  libfakeroot:arm64
```

For the existing local distrobox:

```bash
distrobox enter debian12 -- bash -lc '
  cd /home/tope/project/buildroot_a733/sources/rsdk
  sudo apt-get update
  sudo dpkg --add-architecture arm64
  sudo apt-get update
  sudo apt-get install -y \
    bash-completion \
    bdebstrap \
    binfmt-support \
    qemu-user-static \
    libguestfs-tools \
    gdisk \
    debian-archive-keyring \
    debian-ports-archive-keyring \
    jsonnet \
    jq \
    gpg \
    libfakechroot:arm64 \
    libfakeroot:arm64
'
```

Known distrobox limitation and host requirement:

- The current unprivileged distrobox cannot enable `qemu-aarch64` through `/proc/sys/fs/binfmt_misc`.
- Dry run works in this environment.
- A real image build needs the host to provide a `qemu-aarch64` binfmt handler.

Observed real-build failure before host binfmt registration:

```text
E: arm64 can neither be executed natively nor via qemu user emulation with binfmt_misc
2026-07-07 02:21:08,663 bdebstrap ERROR: mmdebstrap failed with exit code 25. See above for details.
```

On the current Fedora/RPM host, available package names include:

```bash
sudo dnf install -y qemu-user-static-aarch64 qemu-user-binfmt
```

After installing those packages, verify:

```bash
cat /proc/sys/fs/binfmt_misc/status
ls /proc/sys/fs/binfmt_misc/qemu-aarch64
```

Current host status is now verified:

```text
/proc/sys/fs/binfmt_misc/status = enabled
/proc/sys/fs/binfmt_misc/qemu-aarch64 exists
```

Then retry the build inside distrobox.

For the local distrobox, image generation also needs `sgdisk` to be visible in the user PATH. `gdisk` installs it under `/usr/sbin` and `/sbin`, which are not always present for the distrobox user. Use:

```bash
export PATH=/usr/sbin:/sbin:$PATH
```

## Local A733 Bookworm deb cache

Radxa's generic Bookworm repository contains useful common packages and metadata, but it does not currently publish the A733 kernel and U-Boot binary packages through the APT index. Those packages are available from Radxa GitHub Releases, so keep them in a local ignored cache:

```bash
tools/download_a733_bookworm_debs.sh
```

Default output:

```text
sources/rsdk/debs/a733-bookworm/
```

## Build command

Inside the Debian/Ubuntu build environment:

```bash
cd /path/to/buildroot_a733/sources/rsdk
src/bin/rsdk build --debs /path/to/buildroot_a733/sources/rsdk/debs/a733-bookworm radxa-a733
```

Because the local product metadata now puts `bookworm` first, this selects:

```bash
radxa-a733 bookworm kde
```

The expected output directory is:

```text
sources/rsdk/out/radxa-a733_bookworm_kde/
```

## Flash and startup

After a successful build, locate the generated image:

```bash
sources/rsdk/out/radxa-a733_bookworm_kde/output.img
```

Flash the generated image to microSD or eMMC. The exact image name depends on RSDK output naming, so verify the filename before writing:

```bash
sudo dd if=sources/rsdk/out/radxa-a733_bookworm_kde/output.img of=/dev/<target-disk> bs=4M status=progress conv=fsync
sync
```

Before powering the board:

- Connect Micro HDMI first.
- Connect keyboard and mouse.
- Use a stable USB-C power supply.
- Prefer serial console if available.

First boot checks:

- Board reaches U-Boot/kernel.
- Micro HDMI shows a signal.
- Debian 12 boots.
- KDE or a display manager/session starts.
- If desktop fails, collect serial logs and `journalctl` from the target rootfs if possible.

## Current known status

The local Debian 12 distrobox now completes dry-run selection:

```bash
distrobox enter debian12 -- bash -lc 'cd /home/tope/project/buildroot_a733/sources/rsdk && src/bin/rsdk build --dry-run radxa-a733'
```

Observed result:

```text
Building radxa-a733 bookworm kde...
Dry run enabled. You can find generated files under '/tmp/rsdk.radxa-a733_bookworm_kde.*'.
```

The real build now runs with:

```bash
distrobox enter debian12 -- bash -lc 'cd /home/tope/project/buildroot_a733/sources/rsdk && src/bin/rsdk build --debs /home/tope/project/buildroot_a733/sources/rsdk/debs/a733-bookworm radxa-a733'
```

Verified progress in the real build:

- The nonexistent `a733-bookworm` repository is no longer used.
- The generic Radxa `bookworm` repository is used.
- `u-boot-radxa-a733`, `linux-headers-radxa-a733`, and `linux-image-radxa-a733` install from the local `.deb` cache.
- `radxa-overlays-dkms` builds against `5.15.147-21-a733`.
- `task-radxa-a733` installs from generic Radxa Bookworm.
- `radxa-otgutils` no longer blocks the build.
- KDE package installation completes under qemu-user.
- RSDK emits a non-empty `rootfs.tar`.

The first full run then failed after rootfs completion because `guestfish` was missing:

```text
/usr/bin/env: 'guestfish': No such file or directory
```

Installing `libguestfs-tools` fixed that dependency. The next image-generation run reached the shrink stage and failed because `sgdisk` was not visible in PATH:

```text
sh: 1: sgdisk: not found
```

Installing/confirming `gdisk` and running with `PATH=/usr/sbin:/sbin:$PATH` fixed the image-generation step.

Current generated image:

```text
sources/rsdk/out/radxa-a733_bookworm_kde/output.img
size: 6.29 GiB / 6755099648 bytes
partition table: GPT
partition 1: 16 MiB Linux filesystem
partition 2: 300 MiB EFI System
partition 3: ~6 GiB Linux filesystem
```

The next hard result to capture is board-side boot and HDMI desktop behavior.
