# Radxa RSDK 与 Orange Pi A733 对比

## 对比对象

- Radxa 真正的构建框架：`sources/rsdk`
- Orange Pi 真正的板级构建树：`sources/orangepi-build`

Radxa 的 `radxa-cubie-a7z` 仓库只是发布和 workflow 外壳，真正的 A733 构建逻辑在 `rsdk` 里，所以这里对比的是 `rsdk` 和 Orange Pi 的 build tree。

## 先说结论

- Orange Pi 把 Debian 12 桌面路径暴露得更直接。
- Radxa 把 A733 的限制说明得更明确，也更诚实。
- 对我们自己的移植工作来说，Orange Pi 更适合做 Bookworm 桌面参考。
- 对理解 A733 桌面为什么脆弱来说，Radxa RSDK 更有价值。

## 对照总结

| 主题 | Radxa RSDK | Orange Pi 构建树 | 含义 |
| --- | --- | --- | --- |
| 公共 A733 产品 | `radxa-a733` | `orangepi4pro`、`orangepizero3w` | 都是 A733，但发布方式不同 |
| 桌面目标 | `kde` 和 `cli` | 直接提供桌面镜像 | Orange Pi 更直接地把桌面路径摆出来 |
| 支持发行版 | `trixie` | `bookworm`、`jammy`、`bullseye` | Orange Pi 对 Debian 12 更有参考价值 |
| GPU 说明 | A733 只支持 OpenGL ES | 板级树直接集成 `pvrsrvkm` | Orange Pi 更明确地把 GPU 模块串进去 |
| 默认终端/显示路径 | A733 在 `trixie` 上切到 `kmscon` + DRM | 以桌面镜像和 BSP 模块为主 | Radxa 更明显地写出了 framebuffer 限制 |
| 板级 overlay | 主要是产品元数据 | A733 走 `sun60i-a733` overlay | Orange Pi 的板级拼装更完整 |

## Radxa 发现

Radxa 的构建框架里，`radxa-a733` 的信息是：

- 产品名：`Generic A733 Image for Radxa products`
- 支持的 suite：`trixie`
- 支持的 edition：`kde`、`cli`
- SoC：`a733`

同一套框架还说明 Allwinner 家族里有 `a733`，并且 `bullseye` 和 `trixie` 都在安装推荐里，但产品级发布仍然是 `trixie`。

最关键的是 KDE 相关逻辑：

- Radxa 明确说 A733 GPU 只支持 OpenGL ES。
- KDE 通过 `libqt5gui5-gles` 走硬件加速。
- Radxa 明确写了 A733 GPU 驱动当前不支持 GDM。
- 在 `trixie` 上，A733 默认终端换成 `kmscon` + DRM，因为 framebuffer 支持有限。

这基本就是 A733 图形栈的真实边界说明。

## Orange Pi 发现

Orange Pi 的 A733 板级配置更偏向 Debian 12：

- `orangepi4pro.conf` 和 `orangepizero3w.conf` 都用 `BOARDFAMILY="sun60iw2"`。
- 两块板都用 `BOOTCONFIG="sun60iw2p1_t736_defconfig"`。
- 两块板都设置了 A733 DTB。
- 两块板都把 `bookworm` 放进 `DISTRIB_TYPE_CURRENT` 和 `DISTRIB_TYPE_LEGACY`。

Orange Pi 4 Pro 还直接把这些模块写进来了：

- `aic8800_fdrv`
- `aic8800_btlpm`
- `pvrsrvkm`

`sun60iw2` 家族配置也更进一步：

- `orangepi4pro` 和 `orangepizero3w` 使用 `sun60i-a733` overlay。
- 两块板都用 A733 对应的 Linux config。
- 镜像生成时会安装 `pvrsrvkm.ko`。
- 还会带上 `libAWIspApi` 和桌面媒体相关包。

所以 Orange Pi 不只是“写了 Bookworm”，而是真的把桌面和 GPU 链路放进了板级构建里。

## 对我们移植的意义

1. Orange Pi 更适合当 Debian 12 桌面镜像的参考。
2. Radxa 更适合当 A733 图形限制和风险的参考。
3. 两边都说明 A733 桌面仍然是 BSP 驱动的，不是纯主线就能自动成立。
4. 目前最该盯住的差异还是图形路径：
   - Radxa 直接写出了 framebuffer 和 GDM 的限制。
   - Orange Pi 更积极地把 `pvrsrvkm` 和桌面包串起来。

## 最直接的结论

如果目标是“在 A733 上做 Debian 12 + HDMI 桌面”，Orange Pi 是更直接的构建参考。

如果目标是“搞清楚为什么 A733 桌面仍然脆”，Radxa RSDK 更有参考价值。

这两棵树是互补的，不是重复的。

## 来源

- [Radxa Cubie A7Z 仓库](../../sources/radxa-cubie-a7z/README.md)
- [Radxa RSDK 产品元数据](../../sources/rsdk/src/share/rsdk/configs/products.json)
- [Radxa RSDK SoC 元数据](../../sources/rsdk/src/share/rsdk/configs/socs.json)
- [Radxa RSDK KDE 包逻辑](../../sources/rsdk/src/share/rsdk/build/mod/packages/kde.libjsonnet)
- [Radxa RSDK 核心包逻辑](../../sources/rsdk/src/share/rsdk/build/mod/packages/categories/core.libjsonnet)
- [Orange Pi 4 Pro 板级配置](../../sources/orangepi-build/external/config/boards/orangepi4pro.conf)
- [Orange Pi Zero 3W 板级配置](../../sources/orangepi-build/external/config/boards/orangepizero3w.conf)
- [Orange Pi sun60iw2 家族配置](../../sources/orangepi-build/external/config/sources/families/sun60iw2.conf)

