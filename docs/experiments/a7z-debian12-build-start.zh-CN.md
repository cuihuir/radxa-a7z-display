# A7Z Debian 12 构建与启动记录

## 在哪里构建

镜像应该在主机上构建，不是在 A7Z 板子上构建。

A7Z 只用于刷写和启动验证。RSDK 会在主机侧使用 Debian 仓库、`qemu-user-static`、chroot 和镜像组装工具来生成 rootfs 和磁盘镜像。

## 推荐构建环境

使用以下之一：

- Debian 12 主机或虚拟机。
- Ubuntu 22.04/24.04 主机或虚拟机。
- 本地工作站上的特权 Debian 12 容器或 devcontainer。
- 本地已有的 `debian12` distrobox，可用于元数据检查和 dry run。

当前工作站有 `dnf`、`podman` 和 `distrobox`。RSDK 的 native setup 只处理 Debian/Ubuntu 的 `apt` 环境，所以不要直接在当前宿主系统上构建，除非先进入 Debian/Ubuntu 容器或虚拟机。

## 当前本地源码状态

本地 `sources/rsdk` 已经改成：

- `radxa-a733` 默认 suite 是 `bookworm`。
- `radxa-a733` 仍然默认使用 `kde` 桌面。
- Allwinner 的 `soc_install_recommends` 已加入 `bookworm`。
- RSDK Jsonnet 避开了 Debian 12 `jsonnet 0.18.0` 不支持的新标准库调用。

同样的改动已经保存为：

```bash
patches/rsdk/0001-enable-bookworm-on-radxa-a733.patch
patches/rsdk/0002-jsonnet-0.18-compat.patch
patches/rsdk/0003-a733-bookworm-use-generic-radxa-repo.patch
patches/rsdk/0004-a733-bookworm-skip-radxa-otgutils.patch
patches/rsdk/0005-rsdk-image-tool-dependencies-and-sgdisk-path.patch
```

当前还需要两个 Bookworm 专用修正：

- RSDK 需要跳过不存在的 `https://radxa-repo.github.io/a733-bookworm` 仓库，改用通用 Radxa `bookworm` 仓库。
- A733/Bookworm 需要跳过 `radxa-otgutils`，因为它的 `postinst` 在 mmdebstrap chroot 中执行 `deb-systemd-invoke daemon-reload -q` 会失败。
- RSDK setup / 镜像生成应包含 `libguestfs-tools`、`gdisk`，并在 distrobox 这类环境中稳定找到 `sgdisk`。

## 第一次 dry run

在仓库根目录运行：

```bash
sources/rsdk/src/bin/rsdk build --dry-run radxa-a733
```

预期能看到：

```text
Building radxa-a733 bookworm kde...
```

这说明 A733 的 Debian 12 默认路径已经生效。

## 主机依赖准备

在 Debian/Ubuntu 构建环境里，先初始化子模块：

```bash
cd sources/rsdk
git submodule update --recursive --init
```

然后执行 RSDK setup：

```bash
src/bin/rsdk setup
```

如果手动安装依赖，核心依赖大致是：

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

对于本地已有的 distrobox：

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

已知 distrobox 限制和宿主要求：

- 当前非特权 distrobox 不能写 `/proc/sys/fs/binfmt_misc`，因此无法启用 `qemu-aarch64` binfmt。
- dry run 可以跑通。
- 真实镜像构建需要宿主机提供 `qemu-aarch64` binfmt handler。

宿主注册 binfmt 之前的真实构建失败：

```text
E: arm64 can neither be executed natively nor via qemu user emulation with binfmt_misc
2026-07-07 02:21:08,663 bdebstrap ERROR: mmdebstrap failed with exit code 25. See above for details.
```

当前 Fedora/RPM 宿主可用的包名包括：

```bash
sudo dnf install -y qemu-user-static-aarch64 qemu-user-binfmt
```

安装后验证：

```bash
cat /proc/sys/fs/binfmt_misc/status
ls /proc/sys/fs/binfmt_misc/qemu-aarch64
```

当前宿主状态已验证：

```text
/proc/sys/fs/binfmt_misc/status = enabled
/proc/sys/fs/binfmt_misc/qemu-aarch64 exists
```

然后回到 distrobox 里重试构建。

对本地 distrobox 来说，镜像生成阶段还需要能在普通用户 PATH 中找到 `sgdisk`。`gdisk` 会把它安装到 `/usr/sbin` 和 `/sbin`，但这两个目录不一定在 distrobox 用户 PATH 中。运行镜像生成前使用：

```bash
export PATH=/usr/sbin:/sbin:$PATH
```

## 本地 A733 Bookworm deb 缓存

Radxa 通用 Bookworm 仓库包含一些可用的通用包和元数据，但当前 APT 索引没有发布 A733 kernel 和 U-Boot 二进制包。这些包可以从 Radxa GitHub Releases 下载，所以放到本地 ignored 缓存中：

```bash
tools/download_a733_bookworm_debs.sh
```

默认输出目录：

```text
sources/rsdk/debs/a733-bookworm/
```

## 构建命令

进入 Debian/Ubuntu 构建环境后：

```bash
cd /path/to/buildroot_a733/sources/rsdk
src/bin/rsdk build --debs /path/to/buildroot_a733/sources/rsdk/debs/a733-bookworm radxa-a733
```

因为本地产品元数据已经把 `bookworm` 放在第一位，这条命令会选择：

```bash
radxa-a733 bookworm kde
```

预期输出目录是：

```text
sources/rsdk/out/radxa-a733_bookworm_kde/
```

## 刷写与启动

构建成功后，生成的镜像是：

```bash
sources/rsdk/out/radxa-a733_bookworm_kde/output.img
```

把生成的镜像刷到 microSD 或 eMMC。实际镜像名以 RSDK 输出为准，写盘前必须确认目标磁盘：

```bash
sudo dd if=sources/rsdk/out/radxa-a733_bookworm_kde/output.img of=/dev/<target-disk> bs=4M status=progress conv=fsync
sync
```

上电前：

- 先接 Micro HDMI。
- 接键盘和鼠标。
- 使用稳定的 USB-C 电源。
- 如果有串口，优先接串口。

首次启动检查：

- 是否进入 U-Boot / kernel。
- Micro HDMI 是否有信号。
- Debian 12 是否启动。
- KDE 或显示管理器/桌面会话是否启动。
- 如果桌面失败，优先保存串口日志，必要时从目标 rootfs 里取 `journalctl`。

## 当前已知状态

本地 Debian 12 distrobox 现在可以完成 dry-run 选择：

```bash
distrobox enter debian12 -- bash -lc 'cd /home/tope/project/buildroot_a733/sources/rsdk && src/bin/rsdk build --dry-run radxa-a733'
```

实测结果：

```text
Building radxa-a733 bookworm kde...
Dry run enabled. You can find generated files under '/tmp/rsdk.radxa-a733_bookworm_kde.*'.
```

真实构建命令：

```bash
distrobox enter debian12 -- bash -lc 'cd /home/tope/project/buildroot_a733/sources/rsdk && src/bin/rsdk build --debs /home/tope/project/buildroot_a733/sources/rsdk/debs/a733-bookworm radxa-a733'
```

真实构建已验证进展：

- 不再使用不存在的 `a733-bookworm` 仓库。
- 已使用 Radxa 通用 `bookworm` 仓库。
- `u-boot-radxa-a733`、`linux-headers-radxa-a733`、`linux-image-radxa-a733` 从本地 `.deb` 缓存安装。
- `radxa-overlays-dkms` 能针对 `5.15.147-21-a733` 编译。
- `task-radxa-a733` 从 Radxa 通用 Bookworm 仓库安装。
- `radxa-otgutils` 不再阻塞构建。
- KDE 包安装可以在 qemu-user 下完成。
- RSDK 已生成非空 `rootfs.tar`。

第一次完整构建在 rootfs 完成后失败，原因是缺少 `guestfish`：

```text
/usr/bin/env: 'guestfish': No such file or directory
```

安装 `libguestfs-tools` 后解决了这个依赖。下一次镜像生成进入 shrink 阶段后失败，原因是 PATH 中找不到 `sgdisk`：

```text
sh: 1: sgdisk: not found
```

确认/安装 `gdisk` 后，用 `PATH=/usr/sbin:/sbin:$PATH` 运行，镜像生成成功。

当前生成镜像：

```text
sources/rsdk/out/radxa-a733_bookworm_kde/output.img
大小：6.29 GiB / 6755099648 bytes
分区表：GPT
分区 1：16 MiB Linux filesystem
分区 2：300 MiB EFI System
分区 3：约 6 GiB Linux filesystem
```

下一步要捕获的硬结果是板端启动和 HDMI 桌面行为。
