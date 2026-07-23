# 当前状态

> 本文由 `docs/status.json` 生成。请修改 JSON 单一源，然后运行 `python3 tools/render_status.py`。

**2026-07-22**

## 已验证基线

| 项目 | 验证结果 |
| --- | --- |
| 板卡 | Radxa Cubie A7Z / Allwinner A733 |
| 操作系统 | Debian 12 Bookworm · KDE Plasma Wayland |
| 内核 | `5.15.147-21.1-a733` · package `5.15.147-21.1+display4` |
| GPU 包 | `a733-pvr-gpu 24.2.6603887+gpu8` |
| GPU | PowerVR B-Series BXM-4-64 · DDK `24.2@6603887` |
| 图形 API | Vulkan · OpenCL 3.0 · EGL/GBM · OpenGL ES 3.2 |
| 桌面渲染器 | PowerVR 加速的 KWin / Plasma Wayland |
| 显示 | `FLY-HDMI-LCD7` · `1024x600@60Hz` · scale 100% |
| 网络 | AIC8800 Wi-Fi 和 SSH 正常 |
| 显示策略 | 使用 EDID preferred/native 时序，不再强制 Full HD |
| 恢复路径 | 正常桌面使用 `l0` · 原厂回退使用 `l1` · 早期 fsck 恢复使用 `a7z-recovery` |

## 能力状态

状态：✅ 已解决 · 📘 已文档化 · 🧪 待验证 · 🚧 进行中 · ⬜ 未开始

| 能力 | 当前状态 | 说明 |
| --- | --- | --- |
| Debian 12 Bookworm 启动 | ✅ 已解决 | RSDK 路线镜像可从 SD 卡在 Radxa Cubie A7Z/A733 启动。 |
| HDMI 桌面输出 | ✅ 已解决 | Plasma Wayland 可进入 HDMI-A-1，并使用 EDID preferred/native 时序。 |
| 显示管理器 | ✅ 已解决 | SDDM 可以进入图形登录和桌面。 |
| 默认用户 | ✅ 已解决 | 用户名和密码均为 `radxa`。 |
| 异常断电文件系统恢复 | ✅ 已解决 | 独立的 14.7 MB recovery initramfs 已在挂载根分区前修复注入的 ext4 块组描述符故障并继续完整启动；无法自动修复的错误仍需离线 fsck。 |
| Wi-Fi 和 SSH | ✅ 已解决 | 完整显示/GPU 栈下 AIC8800 Wi-Fi 和 SSH 已验证。 |
| 串口 | 📘 已文档化 | 已记录 40-pin 排针 UART0 的启动和恢复诊断方法。 |
| 根文件系统扩容 | ✅ 已解决 | rootfs 可扩展到 SD 卡，并从 `mmcblk0p3` 挂载。 |
| Windows 友好镜像 | ✅ 已解决 | `v0.3.3` 的 XZ 镜像整合 Debian 12 KDE、`display4`、`gpu8`、打包版 XWayland/KWin 加速、原厂 `l1` 和已验证的 `a7z-recovery` early-fsck 启动项。 |
| HDMI 小屏原生模式 | ✅ 已解决 | `FLY-HDMI-LCD7` 以原生 `1024x600@60Hz` 工作，无拉伸和裁切。 |
| HDMI 热插拔恢复 | ✅ 已解决 | `display4` 让 HDMI 硬件变化与 DRM atomic 状态保持同步；在 SDDM 下拔插可自动恢复，无需 xrandr 或 udev workaround。 |
| 完整显示内核包 | ✅ 已解决 | `5.15.147-21.1+display4` 从 `l0` 启动，包内包含 A7Z DTB，并在恢复项 `l1` 保留显式 vendor DTB 和 GPU 黑名单。 |
| GPU 加速 | ✅ 第一版已解决 | `gpu8` 已集成通过验证的 `pvrsrvkm`、Vulkan、OpenCL、EGL/GBM、PowerVR 加速的 KWin 和打包版 XWayland GLES glamor 路径，并使用兼容的显示内核依赖范围。 |
| GPU 桌面环境隔离 | ✅ 已解决 | 普通 Plasma 客户端、Discover 和 KScreenLocker 保持清洁环境；只有 KWin 和兼容的打包版 XWayland 获得限定范围的 PowerVR 库。 |
| XWayland 加速 | ✅ 已解决 | 打包版 XWayland 24.1.6 GLES glamor 的 GPU 利用率可达 100%，使用原生 visual 的 X11 EGL/GLES 可由 PowerVR 渲染；桌面 GLX 仍为 llvmpipe。 |
| DRM render node | ✅ 已解决 | PowerVR 提供 `/dev/dri/card1` 和 `renderD128`，HDMI KMS 继续使用 `card0`。 |
| HDMI 音频 | 🧪 未验证 | 可以看到音频设备，仍需验证播放和 HDMI 音质。 |
| 蓝牙 | 🧪 未验证 | 仍需验证控制器、配对和音频 profile。 |
| NPU | ⬜ 未开始 | A733 NPU 启用和验证尚未开始。 |
| BSP/内核清理 | 🚧 进行中 | 厂商内核日志仍包含 warning 和缺失模块信息。 |
| Debian 13/Trixie | ⬜ 未开始 | Debian 12 仍是当前优先级和已验证桌面目标。 |

## 当前里程碑

- 仓库：已发布到 GitHub 并持续维护。
- 已验证镜像：[`v0.1.1-a733-debian12-kde-raw`](https://github.com/cuihuir/radxa-a7z-debian12/releases/tag/v0.1.1-a733-debian12-kde-raw)。
- 显示内核：[`v0.2.1-a733-full-kernel-display`](https://github.com/cuihuir/radxa-a7z-debian12/releases/tag/v0.2.1-a733-full-kernel-display)。
- GPU 镜像：[`v0.3.0-a733-pvr-gpu`](https://github.com/cuihuir/radxa-a7z-debian12/releases/tag/v0.3.0-a733-pvr-gpu)，整合已验证的显示内核和 PowerVR 第一版移植。
- 热插拔更新：[`v0.3.1-a733-hdmi-hotplug`](https://github.com/cuihuir/radxa-a7z-debian12/releases/tag/v0.3.1-a733-hdmi-hotplug)，修复 HDMI 重连并强化 `l0`/`l1` 启动项。
- 断电恢复镜像：[`v0.3.3-a733-touchscreen-recovery`](https://github.com/cuihuir/radxa-a7z-debian12/releases/tag/v0.3.3-a733-touchscreen-recovery)，加入实机验证的 early-fsck 路径和可直接烧录的整合镜像。

## 下一阶段

- 使用发布优化重新构建已验证的 KWin 集成，扩展稳定性覆盖，并确认仅提供 GLES 的厂商栈在桌面 GLX 上的实际边界。
- 验证 HDMI 音频播放以及蓝牙配对/音频 profile。
- 梳理剩余的厂商 BSP/内核 warning。
- 在普通 1080p 显示器和更多面板上回归验证 EDID 原生模式策略。
- 桌面栈稳定后开始 A733 NPU 启用调研。
