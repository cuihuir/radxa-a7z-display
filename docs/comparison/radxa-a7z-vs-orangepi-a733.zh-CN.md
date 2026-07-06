# Radxa A7Z/Z7A 与 Orange Pi 4 Pro / Zero 3W 对照

## 目的

对比当前最值得关注的 A733 板卡路线，重点看 HDMI 显示、桌面可用性，以及厂商今天到底把 Debian 桌面支持做到什么程度。

## 先说结论

- 如果问题是“哪家现在更明显地把 A733 的 Debian 12 桌面路径摆出来”，Orange Pi 更靠前。
- 如果问题是“哪块板更适合拿来做 A733 的 HDMI 启动参考”，两者都能用，但 Radxa A7Z 的 Micro HDMI 路径更干净，Orange Pi 4 Pro 的 Bookworm 构建树更直接。
- 如果问题是“能不能拿来做我们自己的 A733 基线”，可以。真正有价值的是同一颗 SoC 和不同 BSP 打包方式，不是板子上的品牌名。

## 板卡概览

| 板卡 | 显示输出 | 官方桌面镜像信号 | BSP 信号 | 实际意义 |
| --- | --- | --- | --- | --- |
| Radxa Cubie A7Z | Micro HDMI、USB-C DP Alt Mode | Radxa 的 A733 下载页当前公开的是 Debian 11 桌面镜像，仓库也说明公开支持重点是 Debian Desktop | 有厂商 BSP，但公开信息对“支持哪些桌面组合”更保守 | 适合作为 HDMI 启动的基础参考；Bookworm 桌面路径公开证据较少 |
| Radxa Cubie A7Z / A7A 镜像家族 | A733 统一镜像家族 | Radxa 文档明确这是 A733 通用镜像页，适用于 A7Z、A7A 等 | R6 是稳定线，t 系列是测试线 | 适合参考 Radxa 是怎么组织 A733 通用支持的 |
| Orange Pi 4 Pro | HDMI 2.0 | 板级配置里明确列出 `bookworm jammy bullseye` | `BOARDFAMILY="sun60iw2"`，并且模块里直接带 `pvrsrvkm` | 这是 A733 上 Bookworm 桌面支持最直接的官方线索 |
| Orange Pi Zero 3W | Mini HDMI 2.0 | 同样属于 A733 家族并走 `sun60iw2` 支持路径 | 有板级配置，但桌面参考价值不如 4 Pro 直接 | 适合作为小板/紧凑板的补充参考 |

## Radxa 的情况

Radxa A7Z 在显示相关硬件上有两个关键点：

- 一个独立的 Micro HDMI 接口。
- 一个支持 DisplayPort Alt Mode 的 USB-C 接口。

做板级启动时，这意味着有两条路径。实际优先级上，Micro HDMI 更适合作为第一目标，因为它最简单、最容易验证，也不需要先处理 USB-C 角色切换这一层复杂度。

Radxa A7Z 的下载页当前公开展示的是 Debian 11 桌面镜像，A7Z 仓库则说明公开支持面向的是 Debian Desktop image。这个信号的意思不是“Bookworm 不行”，而是“公开可见的支持范围没有 Orange Pi 那么直接、那么偏向 Bookworm”。

## Orange Pi 的情况

Orange Pi 4 Pro 是 A733 家族里最像“Bookworm 桌面就是主要方向”的板子。它的板级配置里直接写了：

- `BOARDFAMILY="sun60iw2"`
- `BOOT_FDT_FILE="allwinner/sun60i-a733-orangepi-4-pro.dtb"`
- `MODULES="aic8800_fdrv aic8800_btlpm pvrsrvkm"`
- `DISTRIB_TYPE_CURRENT="bookworm jammy bullseye"`
- `DISTRIB_TYPE_LEGACY="bookworm jammy bullseye"`

这件事很重要，因为它说明 Orange Pi 不只是做了 CLI 镜像，而是在把桌面栈和 GPU 模块一起往 Bookworm 路径里塞。

Orange Pi Zero 3W 也走同一个 `sun60iw2` 家族路径，但它不是像 4 Pro 那样强的桌面参考。对我们来说，它仍然值得保留，主要是后续如果关心板子尺寸、功耗或最小化接线，它会有用。

## 对我们项目的意义

1. Radxa A7Z 还是更适合作为基础 HDMI 硬件启动参考。
2. Orange Pi 4 Pro 更适合作为 Debian 12 桌面打包参考。
3. 两家的共同点是 `sun60iw2` 家族支持。
4. 真正要盯住的差距不是“芯片能不能显示”，而是“厂商桌面打包和 Bookworm 下的 GPU 用户态完整不完整”。

## 实用结论

对这个项目来说，最实用的工作假设是：

- 用 Radxa A7Z/Z7A 理解硬件/显示路径。
- 用 Orange Pi 4 Pro 理解 Bookworm 桌面是怎么被串起来的。
- Orange Pi Zero 3W 作为补充参考，除非后面我们特别关心小板细节。
- 目标保持务实：做出 Debian 12 上可用的 HDMI 桌面，不追求做成一个“厂商级完美发行版”。

## 来源

- Radxa A7Z 文档：https://docs.radxa.com/en/cubie/a7z
- Radxa A7Z 下载页：https://docs.radxa.com/en/cubie/a7z/download
- Radxa A7Z 仓库：https://github.com/radxa-build/radxa-cubie-a7z
- Orange Pi 4 Pro 产品页：https://www.orangepi.org/html/hardWare/computerAndMicrocontrollers/details/Orange-Pi-4-Pro.html
- Orange Pi Zero 3W 产品页：https://www.orangepi.org/html/hardWare/computerAndMicrocontrollers/details/Orange-Pi-Zero-3W.html
- Orange Pi build 仓库：https://github.com/orangepi-xunlong/orangepi-build
- Orange Pi 4 Pro 板级配置：https://github.com/orangepi-xunlong/orangepi-build/blob/next/external/config/boards/orangepi4pro.conf
- Orange Pi Zero 3W 板级配置：https://github.com/orangepi-xunlong/orangepi-build/blob/next/external/config/boards/orangepizero3w.conf
- Orange Pi Bookworm 构建问题：https://github.com/orangepi-xunlong/orangepi-build/issues/312

