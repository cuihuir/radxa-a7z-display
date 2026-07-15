# radxa-a7z-display

[English README](README.md)

面向 Radxa A7Z/Z7A 的 Debian 12 KDE Plasma Wayland、HDMI 原生显示，以及可重复部署的 A733 PowerVR GPU 栈。

![Radxa Cubie A7Z 开发板官方图片](https://docs.radxa.com/en/img/cubie/a7z/a7z-top.webp)

产品图片来源：[Radxa Cubie A7Z 文档](https://docs.radxa.com/en/cubie/a7z)。

## 最新验证里程碑

`v0.3.0-a733-pvr-gpu` 已经把 PowerVR BXM GPU 带到验证通过的 Debian 12
桌面栈。候选发布包和校验文件位于
[`artifacts/releases/v0.3.0-a733-pvr-gpu`](artifacts/releases/v0.3.0-a733-pvr-gpu)，
完整技术记录见
[A733 PowerVR GPU 第一版发布说明](docs/releases/v0.3.0-a733-pvr-gpu.zh-CN.md)。

已在 Radxa Cubie A7Z 实机验证：

| 项目 | 验证结果 |
| --- | --- |
| Debian | Debian 12 Bookworm，KDE Plasma Wayland |
| 内核包 | `5.15.147-21.1+display2` |
| GPU 包 | `a733-pvr-gpu 24.2.6603887+gpu4` |
| GPU | PowerVR B-Series BXM-4-64，DDK `24.2@6603887` |
| 图形 API | Vulkan、OpenCL 3.0、EGL/GBM、OpenGL ES 3.2 |
| 桌面渲染器 | PowerVR 加速的 KWin / Plasma Wayland |
| 启动项 | 自定义内核使用 `l0`；原厂恢复内核保留为 `l1` |
| HDMI 小屏 | `FLY-HDMI-LCD7` 原生 `1024x600@60Hz` |
| 网络 | AIC8800 Wi-Fi 和 SSH 正常 |
| 显示策略 | 使用 EDID preferred/native 时序，不再强制 Full HD |

候选发布中包含可安装的 GPU `.deb`、带安全检查的部署脚本、中英文发布说明和 SHA256 校验文件。

## 里程碑：A733 GPU，醒了

![A733 PowerVR GPU 已解锁：Vulkan、OpenCL 和 Plasma Wayland](docs/assets/a733-pvr-gpu-first-activation/a733-pvr-milestone.svg)

**这是 A7Z 从“能启动”跨越到“硬件真正活起来”的时刻。** 最初依靠
`llvmpipe` 绘制的 Debian 12 桌面，现在已经由 PowerVR B-Series BXM-4-64
驱动 KWin。内核模块、匹配固件、厂商用户态、render node、计算 API 和真实
Plasma Wayland 会话，全部在实机上通过验证。

| 第一次点亮桌面 | PowerVR 里程碑 |
| --- | --- |
| 软件渲染器：`llvmpipe` | 硬件渲染器：`PowerVR B-Series BXM-4-64` |
| 只有显示设备 `/dev/dri/card0` | 显示 KMS 与 `card1`、`renderD128` 加速节点分工运行 |
| GPU 存在，但没有真正参与桌面 | `pvrsrvkm` 和 BVNC 匹配固件自动加载 |
| 证明桌面可以输出 | Vulkan、OpenCL 3.0、EGL/GBM、GLES 3.2 和 KWin 全部通过 |

![A733 上正在运行的 PowerVR 加速 Plasma Wayland 会话](docs/assets/a733-pvr-gpu-first-activation/a733-pvr-plasma-wayland.png)

GPU 栈被有意隔离在 `/opt/a733-pvr/24.2.6603887`，不替换 Debian 自带的
Xorg；HDMI 扫描输出继续固定在 `/dev/dri/card0`，原厂内核继续作为 `l1`
恢复路径。这不是一次性的库文件覆盖，而是一条可打包、可部署、可回退，并且有
完整实机验证记录的移植路径。

## 项目背景

我在 2025 年 12 月购买了 Radxa A7Z。全志 A733 在这个级别的开发板中很有吸引力：它拥有 2 个 Cortex-A76 和 6 个 Cortex-A55 核心、Imagination PowerVR GPU，以及 3 TOPS INT8 NPU。刚上市时，入门 A733 板卡仍属于低价爱好者硬件，树莓派外形的 Radxa A7Z 4GB 版本也明显便宜于许多实际性能更弱的开发板。与常见的 RK3566 板卡，例如 Orange Pi 3B 和一些 CM4 类产品相比，A733 的性能价格比非常突出。

硬件很有吸引力，但软件支持并不理想。购买后我发现官方系统更新缓慢，唯一较实用的 GUI 镜像是已经归档的 Debian 11，而更新版本的 Debian 桌面镜像要么缺失，要么无法正常用于 HDMI 桌面。

这个项目的目标是挖掘这块硬件的潜力。第一个目标很明确：让 Radxa A7Z/A733 启动现代 Debian 桌面并正常使用 HDMI。现在 Debian 12 Bookworm KDE 镜像已经可以启动 SDDM、进入 Plasma Wayland，并根据显示器 EDID 选择 preferred 模式。初始 1080p 桌面路径和修复后的 `FLY-HDMI-LCD7` 原生 `1024x600` 路径都已经在实机运行，但最终内核在更多显示器上的回归验证仍待完成。

第一次成功点亮桌面时，我非常兴奋，这也让项目不再只是一组研究笔记。PowerVR 加速则是第二次重大突破：这块板子已经从软件绘制像素，走到了拥有 Vulkan、OpenCL 和硬件加速 Plasma Wayland 的桌面。NPU、音频验证、更多显示器测试和 BSP 清理仍有大量工作，但最关键的桌面路径已经真正跑通。如果你也因为相同原因购买了 A733，或者同样认为这颗 SoC 的潜力没有被官方软件充分发挥，欢迎使用和参与这个项目。

## 能力状态

| 能力 | 当前状态 | 说明 |
| --- | --- | --- |
| Debian 12 Bookworm 启动 | 已解决 | RSDK 路线镜像可从 SD 卡在 Radxa Cubie A7Z/A733 启动。 |
| HDMI 桌面输出 | 已解决 | KDE Plasma Wayland 可进入 HDMI-A-1，并使用显示器 EDID preferred/native 时序。 |
| 显示管理器 | 已解决 | SDDM 可以进入图形登录和桌面。 |
| 默认用户 | 已解决 | 用户名和密码均为 `radxa`。 |
| Wi-Fi 和 SSH | 已解决 | 完整显示内核下 AIC8800 Wi-Fi 正常，SSH 已在 `192.168.123.210` 验证。 |
| 串口 | 已文档化 | UART0 位于 40-pin 排针，可用于启动和恢复诊断。 |
| 根文件系统扩容 | 已解决 | rootfs 可扩展到 SD 卡，并从 `mmcblk0p3` 挂载。 |
| Windows 友好镜像 | 已解决 | `v0.1.1` 是未修改 GPT 的原始镜像 XZ 压缩版本。 |
| HDMI 小屏原生模式 | 已解决 | `FLY-HDMI-LCD7` 已验证为 `1024x600@60Hz`，无拉伸和裁切。 |
| 完整显示内核包 | 已解决 | `5.15.147-21.1+display2` 从 `l0` 启动，SSH、Wi-Fi、KDE 和原生 HDMI 均已验证。 |
| GPU 加速 | 第一版已解决 | A7z 已验证 `pvrsrvkm`、Vulkan、OpenCL、EGL/GBM 和 PowerVR 加速的 KWin/Plasma Wayland。 |
| DRM render node | 已解决 | PowerVR 提供 `/dev/dri/card1` 和 `/dev/dri/renderD128`，HDMI KMS 继续使用 `/dev/dri/card0`。 |
| HDMI 音频 | 未验证 | 可以看到音频设备，但尚未验证播放和 HDMI 音质。 |
| 蓝牙 | 未验证 | 尚未验证控制器、配对和音频 profile。 |
| NPU | 未开始 | A733 具备 NPU 能力，但本项目尚未启用和验证。 |
| BSP/内核清理 | 进行中 | 厂商内核日志仍有 warning 和调试信息。 |
| Debian 13/Trixie | 未开始 | 当前优先级仍是 Debian 12。 |

## 仓库用途

- 固化 A733 显示支持的研究和实机证据。
- 记录 Debian 12 桌面移植中的技术限制。
- 保存实现决策、验证方法和长期维护信息。
- 英文文档作为主文档，并同步维护中文翻译。

## 文档索引

- [项目概览](docs/project-overview.zh-CN.md)
- [当前状态](docs/status.zh-CN.md)
- [A733 显示支持调研](docs/research/a733-display-landscape.zh-CN.md)
- [A733 GPU 加速驱动可行性调研](docs/research/a733-gpu-acceleration-feasibility.zh-CN.md)
- [A733 PowerVR GPU 第一版激活验证](docs/validation-records/2026-07-14-a733-pvr-gpu-first-activation.zh-CN.md)
- [A733 PowerVR GPU 第一版发布说明](docs/releases/v0.3.0-a733-pvr-gpu.zh-CN.md)
- [显示栈架构](docs/architecture/display-stack.zh-CN.md)
- [贡献说明](docs/contributing.zh-CN.md)
- [命名约定](docs/naming-conventions.zh-CN.md)
- [验证方法](docs/validation.zh-CN.md)
- [验证记录模板](docs/validation-template.zh-CN.md)
- [Radxa RSDK 与 Orange Pi A733 对比](docs/comparison/radxa-rsdk-vs-orangepi-a733.zh-CN.md)
- [HDMI 小屏模式选择](docs/experiments/a733-small-hdmi-panel-mode-selection.zh-CN.md)
- [完整显示内核发布说明](docs/releases/v0.2.1-a733-full-kernel-display.zh-CN.md)
- [A7Z 串口和恢复](docs/a7z-serial-console.zh-CN.md)
- [决策记录](docs/decision-log.zh-CN.md)
- [资料索引](docs/sources.zh-CN.md)

## 工具

- `python3 tools/a733_compare.py compare ...`：对比 A733 厂商源码树并生成 Markdown 报告。
- `python3 tools/a733_compare.py check ...`：检查单个源码树是否具备最低分析条件。
- `python3 tools/a7z_debian12_report.py ...`：生成 Radxa/Orange Pi Debian 12 迁移报告。
- `patches/a733-bsp/0001-drm-prefer-edid-native-mode.patch`：移除 A733 强制 FHD 策略，并优先选择 EDID preferred mode。
- `tools/package_a733_kernel_display.sh INPUT.deb OUTPUT.deb`：加入 A7Z initramfs 大小修复并生成 `+display2` 内核包。
- `sudo tools/deploy_a733_display_kernel.sh PACKAGE.deb --activate`：在单实例锁下安装内核，并在切换 `l0` 前验证 DKMS 和 initramfs。
- `tools/download_a733_gpu_vendor.sh DIR`：下载并校验锁定版本的 A733 PowerVR 包。
- `tools/build_a733_gpu_module.sh DKMS.deb KERNEL_TREE OUTPUT.ko`：构建并检查 `pvrsrvkm`。
- `tools/package_a733_gpu.sh MODULE.ko USERSPACE.deb OUTPUT.deb`：生成不覆盖 Xorg 的 GPU 包。
- `sudo tools/deploy_a733_gpu.sh PACKAGE.deb --activate`：安装 GPU 包并保留 `l1` 恢复项。

## 维护规则

- 英文文档是主文档。
- 核心英文文档必须有对应的 `.zh-CN.md` 中文翻译。
- 决策统一记录在 decision log，不散落在临时笔记中。
- 硬件、BSP 和发布结论必须有来源或实机证据。
- 文档保持实用和轻量；这是个人项目，也欢迎其他贡献者参与。

## 下载镜像

已验证的 Debian 12 KDE 镜像发布于
[`v0.1.1-a733-debian12-kde-raw`](https://github.com/cuihuir/radxa-a7z-display/releases/tag/v0.1.1-a733-debian12-kde-raw)：

- 镜像：`radxa-a733-debian12-kde-20260713.img.xz`
- 校验文件：`SHA256SUMS`
- XZ 解压后与实机启动成功的 RSDK `output.img` 完全一致，GPT 布局和分区属性未被修改。

`v0.1.0-a733-debian12-kde` 已撤回。该版本经过 PiShrink 处理，无法在 A7Z 启动，请勿使用。

Linux 下解压和烧录：

```bash
xz -d radxa-a733-debian12-kde-20260713.img.xz
sudo dd if=radxa-a733-debian12-kde-20260713.img \
  of=/dev/<目标磁盘> bs=4M status=progress conv=fsync
sync
```

Windows 下可以先尝试使用 Rufus 或 balenaEtcher 直接写入 `.img.xz`。如果工具不支持 XZ，请先解压为 `.img` 再烧录。

## 安装完整显示内核

先启动 Debian 12 镜像，然后从
[`v0.2.1-a733-full-kernel-display`](https://github.com/cuihuir/radxa-a7z-display/releases/tag/v0.2.1-a733-full-kernel-display)
下载：

- `linux-image-5.15.147-21.1-a733_5.15.147-21.1+display2_arm64.deb`
- `deploy_a733_display_kernel.sh`
- `SHA256SUMS`

在 A7Z 上校验并安装：

```bash
sha256sum -c SHA256SUMS
chmod +x deploy_a733_display_kernel.sh
sudo ./deploy_a733_display_kernel.sh \
  linux-image-5.15.147-21.1-a733_5.15.147-21.1+display2_arm64.deb \
  --activate
sudo reboot
```

部署脚本使用单实例锁，并等待唯一的前台 `dpkg`/DKMS 流程完成。即使终端暂时没有输出，也不要再启动第二个包管理或 DKMS 命令。

重启后验证：

```bash
uname -r
dpkg -s linux-image-5.15.147-21.1-a733 | grep -E '^(Status|Version):'
ip -brief address show wlan0
sudo journalctl -b -k --no-pager \
  | grep -E 'Configuration mode|drm hdmi mode set'
```

测试小屏的预期输出：

```text
5.15.147-21.1-a733
Version: 5.15.147-21.1+display2
HDMI-A-1: Configuration mode 1024x600@60Hz
drm hdmi mode set: 1024*600
```

## 恢复方法

原厂内核保留为 `l1`。如果自定义内核无法启动，将 SD 卡挂载到另一台 Linux 机器并修改默认启动项：

```bash
sudo mount /dev/<根分区> /mnt/a7z-root
sudo sed -i 's/^default l0$/default l1/' \
  /mnt/a7z-root/boot/extlinux/extlinux.conf
sync
sudo umount /mnt/a7z-root
```

initramfs 大小问题、DKMS 并发事故和完整排查过程记录在
[A733 HDMI 小屏模式选择](docs/experiments/a733-small-hdmi-panel-mode-selection.zh-CN.md)。

## 第一次成功启动 Debian 12 KDE

日期：2026-07-07

我们从 Radxa RSDK 路线构建 Debian 12 Bookworm KDE 镜像，写入 SD 卡后在 Radxa Cubie A7Z/A733 上启动，并成功进入 HDMI Plasma 桌面。

首次验证信息：

- 主机名：`radxa-cubie-a7z`
- 用户名/密码：`radxa` / `radxa`
- 系统：Debian GNU/Linux 12 Bookworm
- 内核：`5.15.147-21-a733`
- 桌面：KDE Plasma 5.27.5，Wayland
- 显示：HDMI-A-1，1920x1080 60Hz
- 显示管理器：SDDM
- 网络：Wi-Fi 正常，SSH 地址为 `192.168.123.210`
- 存储：根文件系统扩展到 SD 卡，挂载于 `mmcblk0p3`

实机截图：

![A733 Debian 12 KDE 桌面](docs/assets/a733-debian12-first-boot/debian12-kde-hdmi-01.png)

![A733 系统信息](docs/assets/a733-debian12-first-boot/debian12-kde-system-info.png)

![A733 显示设置](docs/assets/a733-debian12-first-boot/debian12-kde-display-settings.png)

![A733 KDE 终端验证](docs/assets/a733-debian12-first-boot/debian12-kde-terminal-validation.png)

首次启动时记录的问题（GPU 项已于 2026-07-14 解决）：

- 当时图形渲染仍是 `llvmpipe`；这一结果已经被上方 PowerVR 里程碑取代。
- 当时只有 `/dev/dri/card0`；PowerVR 栈现在会创建 `card1` 和 `renderD128`。
- HDMI 音频可见但尚未验证播放质量。
- 厂商内核日志仍包含 GPU、电源域、音频和调试相关 warning。

详细记录：[2026-07-07 A733 Debian 12 KDE 首次启动验证](docs/validation-records/2026-07-07-a733-debian12-kde-first-boot.zh-CN.md)。
