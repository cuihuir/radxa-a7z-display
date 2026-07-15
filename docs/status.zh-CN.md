# 当前状态

> 本文由 `docs/status.json` 生成。请修改 JSON 单一源，然后运行 `python3 tools/render_status.py`。

**2026-07-15**

## 已验证基线

| 项目 | 验证结果 |
| --- | --- |
| 板卡 | Radxa Cubie A7Z / Allwinner A733 |
| 操作系统 | Debian 12 Bookworm · KDE Plasma Wayland |
| 内核 | `5.15.147-21.1-a733` · package `5.15.147-21.1+display2` |
| GPU 包 | `a733-pvr-gpu 24.2.6603887+gpu4` |
| GPU | PowerVR B-Series BXM-4-64 · DDK `24.2@6603887` |
| 图形 API | Vulkan · OpenCL 3.0 · EGL/GBM · OpenGL ES 3.2 |
| 桌面渲染器 | PowerVR 加速的 KWin / Plasma Wayland |
| 显示 | `FLY-HDMI-LCD7` · `1024x600@60Hz` · scale 100% |
| 网络 | AIC8800 Wi-Fi 和 SSH 正常 |
| 显示策略 | 使用 EDID preferred/native 时序，不再强制 Full HD |
| 恢复路径 | 自定义栈使用 `l0` · 原厂内核保留在 `l1` |

## 能力状态

状态：✅ 已解决 · 📘 已文档化 · 🧪 待验证 · 🚧 进行中 · ⬜ 未开始

| 能力 | 当前状态 | 说明 |
| --- | --- | --- |
| Debian 12 Bookworm 启动 | ✅ 已解决 | RSDK 路线镜像可从 SD 卡在 Radxa Cubie A7Z/A733 启动。 |
| HDMI 桌面输出 | ✅ 已解决 | Plasma Wayland 可进入 HDMI-A-1，并使用 EDID preferred/native 时序。 |
| 显示管理器 | ✅ 已解决 | SDDM 可以进入图形登录和桌面。 |
| 默认用户 | ✅ 已解决 | 用户名和密码均为 `radxa`。 |
| Wi-Fi 和 SSH | ✅ 已解决 | 完整显示/GPU 栈下 AIC8800 Wi-Fi 和 SSH 已验证。 |
| 串口 | 📘 已文档化 | 已记录 40-pin 排针 UART0 的启动和恢复诊断方法。 |
| 根文件系统扩容 | ✅ 已解决 | rootfs 可扩展到 SD 卡，并从 `mmcblk0p3` 挂载。 |
| Windows 友好镜像 | ✅ 已解决 | `v0.1.1` 是未修改 GPT 的已验证原始镜像 XZ 压缩版本。 |
| HDMI 小屏原生模式 | ✅ 已解决 | `FLY-HDMI-LCD7` 以原生 `1024x600@60Hz` 工作，无拉伸和裁切。 |
| 完整显示内核包 | ✅ 已解决 | `5.15.147-21.1+display2` 从 `l0` 启动，`l1` 保留恢复路径。 |
| GPU 加速 | ✅ 第一版已解决 | 已验证 `pvrsrvkm`、Vulkan、OpenCL、EGL/GBM 和 PowerVR 加速的 KWin。 |
| DRM render node | ✅ 已解决 | PowerVR 提供 `/dev/dri/card1` 和 `renderD128`，HDMI KMS 继续使用 `card0`。 |
| HDMI 音频 | 🧪 未验证 | 可以看到音频设备，仍需验证播放和 HDMI 音质。 |
| 蓝牙 | 🧪 未验证 | 仍需验证控制器、配对和音频 profile。 |
| NPU | ⬜ 未开始 | A733 NPU 启用和验证尚未开始。 |
| BSP/内核清理 | 🚧 进行中 | 厂商内核日志仍包含 warning 和缺失模块信息。 |
| Debian 13/Trixie | ⬜ 未开始 | Debian 12 仍是当前优先级和已验证桌面目标。 |

## 当前里程碑

- 仓库：已发布到 GitHub 并持续维护。
- 已验证镜像：[`v0.1.1-a733-debian12-kde-raw`](https://github.com/cuihuir/radxa-a7z-display/releases/tag/v0.1.1-a733-debian12-kde-raw)。
- 显示内核：[`v0.2.1-a733-full-kernel-display`](https://github.com/cuihuir/radxa-a7z-display/releases/tag/v0.2.1-a733-full-kernel-display)。
- GPU 里程碑：[`v0.3.0-a733-pvr-gpu`](https://github.com/cuihuir/radxa-a7z-display/blob/main/docs/releases/v0.3.0-a733-pvr-gpu.zh-CN.md)，候选发布已在本地完成验证。

## 下一阶段

- 发布已验证的 `v0.3.0-a733-pvr-gpu` 候选版本。
- 验证 HDMI 音频播放以及蓝牙配对/音频 profile。
- 梳理剩余的厂商 BSP/内核 warning。
- 在普通 1080p 显示器和更多面板上回归验证 EDID 原生模式策略。
- 桌面栈稳定后开始 A733 NPU 启用调研。
