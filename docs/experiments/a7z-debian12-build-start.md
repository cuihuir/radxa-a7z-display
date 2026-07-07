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
```

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
    debian-archive-keyring \
    debian-ports-archive-keyring \
    jsonnet \
    jq \
    gpg \
    libfakechroot:arm64 \
    libfakeroot:arm64
'
```

Known distrobox limitation:

- The current unprivileged distrobox cannot enable `qemu-aarch64` through `/proc/sys/fs/binfmt_misc`.
- Dry run works in this environment.
- A real image build currently fails until the host provides a `qemu-aarch64` binfmt handler.

Observed real-build failure in the current distrobox:

```text
E: arm64 can neither be executed natively nor via qemu user emulation with binfmt_misc
2026-07-07 02:21:08,663 bdebstrap ERROR: mmdebstrap failed with exit code 25. See above for details.
```

The host has `binfmt_misc` enabled, but no `qemu-aarch64` handler. On the current Fedora/RPM host, available package names include:

```bash
sudo dnf install -y qemu-user-static-aarch64 qemu-user-binfmt
```

After installing those packages, verify:

```bash
cat /proc/sys/fs/binfmt_misc/status
ls /proc/sys/fs/binfmt_misc/qemu-aarch64
```

Then retry the build inside distrobox.

## Build command

Inside the Debian/Ubuntu build environment:

```bash
cd /path/to/buildroot_a733/sources/rsdk
src/bin/rsdk build radxa-a733
```

Because the local product metadata now puts `bookworm` first, this is equivalent to:

```bash
src/bin/rsdk build radxa-a733 bookworm kde
```

The expected output directory is:

```text
sources/rsdk/out/radxa-a733_bookworm_kde/
```

## Flash and startup

After a successful build, locate the generated image under:

```bash
ls sources/rsdk/out/radxa-a733_bookworm_kde/
```

Flash the generated image to microSD or eMMC. The exact image name depends on RSDK output naming, so verify the filename before writing:

```bash
sudo dd if=<generated-image>.img of=/dev/<target-disk> bs=4M status=progress conv=fsync
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

## Current known blocker

The RPM host dry run reached:

```text
Building radxa-a733 bookworm kde...
```

Then stopped because `jsonnet` was not available on the host. This is expected on the current `dnf` host and should be solved by using a Debian/Ubuntu build environment.

The local Debian 12 distrobox now completes:

```bash
distrobox enter debian12 -- bash -lc 'cd /home/tope/project/buildroot_a733/sources/rsdk && src/bin/rsdk build --dry-run radxa-a733'
```

Observed result:

```text
Building radxa-a733 bookworm kde...
Dry run enabled. You can find generated files under '/tmp/rsdk.radxa-a733_bookworm_kde.Fwajs51g'.
```

The next blocker is host-level `qemu-aarch64` binfmt registration. The current user session cannot install it automatically because `sudo` requires a password.
