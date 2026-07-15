# A7Z Debian 12 试验检查清单

> 历史试验检查清单。本文记录 Debian 12 首次启动路径；当前能力状态以
> [`docs/status.json`](../status.json) 为单一源，并生成到
> [`docs/status.zh-CN.md`](../status.zh-CN.md)。

除仍有历史构建参考价值的项目外，这份检查清单已经关闭。

## 当前假设

- Radxa `rsdk` 可以为 `radxa-a733` 暴露 `bookworm`，不需要重写整套 A733 栈。
- 桌面路径大概率会先靠现有的板级启动/显示部分，再靠 Debian 12 的用户态和桌面打包去跑通。
- 第一条要验证的显示路径是 Micro HDMI。

## 当前本地改动

- [x] 确认 Radxa A733 真正的构建源码是 `rsdk`。
- [x] 确认 `radxa-cubie-a7z` 只是 workflow / release 外壳。
- [x] 确认 Radxa RSDK 里 A733 桌面的限制点。
- [x] 确认 Orange Pi A733 的 Bookworm 桌面打包方式可作为参考。
- [x] 在 `radxa-a733` 的支持 suite 中启用 `bookworm`。
- [x] 在 Allwinner 的 `soc_install_recommends` 里加入 `bookworm`。
- [x] 把这次 Radxa 试验改动整理成可复用的 patch 产物。
- [x] 确认 `radxa-a733` 现在本地默认指向 `bookworm`。
- [x] 第一次 dry run 失败后，已初始化 RSDK 子模块。
- [x] 确认当前宿主需要 Debian/Ubuntu 构建环境。
- [x] 使用本地已有的 Debian 12 distrobox 安装依赖并验证 dry run。
- [x] 增加 Debian 12 适用的 Jsonnet 0.18 兼容补丁。
- [x] 确认 Debian 12 distrobox 可以完成 `radxa-a733 bookworm kde` dry run。
- [x] 确认宿主机已经注册 `qemu-aarch64` binfmt。
- [x] 确认 Radxa 的 `a733-bookworm` 仓库不存在。
- [x] 确认 Radxa 通用 `bookworm` 仓库存在且可用。
- [x] 增加 A733 Bookworm kernel/U-Boot 本地 `.deb` 缓存下载脚本。
- [x] 在 RSDK 中跳过不存在的 A733 Bookworm SoC 仓库。
- [x] 在 A733/Bookworm 中跳过会在 chroot 失败的 `radxa-otgutils`。
- [x] 确认 A733 kernel、headers、U-Boot 可以从本地缓存安装。
- [x] 确认 `task-radxa-a733` 可以从 Radxa 通用 Bookworm 仓库安装。
- [x] 确认完整 rootfs 可以在 qemu-user 下构建完成。
- [x] 确认镜像生成需要 `libguestfs-tools`。
- [x] 确认镜像 shrink 阶段需要从 PATH 找到 `gdisk` 提供的 `sgdisk`。
- [x] 确认 RSDK 可以生成 `output.img`。
- [x] 将镜像工具依赖/PATH 修正固化为 `patches/rsdk/0005-rsdk-image-tool-dependencies-and-sgdisk-path.patch`。

## 接下来要盯的点

- [x] `rsdk build radxa-a733` 现在是否默认变成 `bookworm`？
- [ ] A733 上的 KDE 在 `bookworm` 下是否仍然避开 GDM？
- [ ] 生成出来的镜像是否还能保持 Micro HDMI 作为首个可用路径？
- [ ] 有没有任何包钩子默认还在假设 `trixie` 专用行为？
- [ ] 更新后的 A7Z 报告是否还指向真正的下一处阻塞点？
- [x] 在 Debian/Ubuntu 构建环境里 dry run 能否跑完？
- [x] 确认当前 distrobox 真实镜像构建会失败，原因是宿主缺少 `qemu-aarch64` binfmt。
- [x] 宿主机是否已经通过 `binfmt_misc` 注册 `qemu-aarch64`？
- [x] KDE 包集合是否能在 qemu-user 下完成安装？
- [x] RSDK 是否生成非空 `rootfs.tar`？
- [x] RSDK 是否在 rootfs 完成后生成可刷写镜像？
- [x] 生成镜像是否能在 A7Z/Z7A 上启动？
- [x] A7Z/Z7A 上 HDMI 是否能显示可用桌面？
- [x] Debian 12 是否能在 HDMI 上进入 SDDM/KDE？
- [x] 保存第一次成功板端截图。
- [x] 记录第一次成功板端验证。
- [x] 桌面是否能暴露 PowerVR 硬件 GPU 加速，而不是 `llvmpipe`？
- [ ] HDMI 音频播放是否工作？
- [ ] 蓝牙配对是否工作？

## 已知发现

- `rsdk` 已经有 A733 专属的 KDE 逻辑，包含 GLES 和有限 framebuffer 的处理。
- `rsdk` 已经有 `bookworm` 的桌面包逻辑。
- 公共侧的主要阻塞点就是产品元数据只公开了 `trixie`。
- 本地元数据修改后，剩下的阻塞点应该转向真实的构建/启动验证。
- 第一次 dry run 已经选中 `radxa-a733 bookworm kde`，随后因缺少 `jsonnet` 停止。
- RSDK native setup 只支持 Debian/Ubuntu；当前宿主使用 `dnf`。
- Debian 12 自带 `jsonnet 0.18.0`，缺少当前 RSDK 使用的较新 `std.contains` 和 `std.all`。
- 将这些调用替换为 `std.member` 和 `std.filter`/长度比较后，Debian 12 distrobox 可以完成 dry run。
- 在当前非特权 distrobox 内安装 `qemu-user-static` 时，会提示不能写 `/proc/sys/fs/binfmt_misc`。
- 真实构建会立即失败，因为 arm64 既不能原生运行，也不能通过 binfmt 运行。
- Fedora/RPM 宿主已有可用的 `qemu-user-static-aarch64` 和 `qemu-user-binfmt` 包，但当前会话里 `sudo` 需要密码。
- 宿主机现在已启用 binfmt，且 `/proc/sys/fs/binfmt_misc/qemu-aarch64` 存在。
- `https://radxa-repo.github.io/a733-bookworm/pkgs.json` 返回 404，所以 A733/Bookworm 不能添加这个仓库。
- `https://radxa-repo.github.io/bookworm/pkgs.json` 存在并包含 A733 相关源码元数据，但 APT 索引没有发布 A733 kernel/U-Boot 二进制包名。
- A733 kernel/U-Boot 包可以通过 `--debs sources/rsdk/debs/a733-bookworm` 提供。
- `radxa-otgutils` 版本 `0.3.3` 的 postinst 不适合 chroot；跳过它可以避开之前的 mmdebstrap 失败。
- 完整 KDE 安装在 qemu-user 下很慢，除非进程状态停止变化，否则应视为长耗时验证阶段，不应直接判定为卡死。
- 完整 rootfs 已经生成，产物是 `sources/rsdk/out/radxa-a733_bookworm_kde/rootfs.tar`。
- RSDK 镜像生成需要 `guestfish`；Debian 构建环境需要安装 `libguestfs-tools`。
- RSDK 镜像 shrink 阶段会调用 `sgdisk`；需要安装 `gdisk`，并确保 `/usr/sbin` 或 `/sbin` 在 PATH 中。
- Patch `0005` 会让 RSDK setup 安装 `libguestfs-tools`/`gdisk`，并让生成的镜像脚本用显式 sbin PATH 调用 `sgdisk`。
- `sources/rsdk/out/radxa-a733_bookworm_kde/output.img` 已经生成成功，分区表为 GPT。
- 生成镜像已经可以从 SD 卡启动，并通过 HDMI 进入 KDE Plasma Wayland。
- 本镜像观察到的默认登录是 `radxa` / `radxa`。
- HDMI 连接为 `card0-HDMI-A-1`，GUI 工作在 1920x1080。
- 首次启动时 `glxinfo` 显示 `llvmpipe`。2026-07-14 完成的 PowerVR
  移植随后启用了 BXM-4-64、Vulkan、OpenCL 和 KWin 硬件加速。
- 第一次 SSH 检查没有发现 failed systemd system units。

## 当时的下一步

- 当时的首要任务是 GPU 加速，目前已经完成。HDMI 音频和蓝牙验证继续由
  自动生成的当前状态跟踪。

## 备注

- 这份清单保持短。
- 只记录会影响下一步判断的内容。
