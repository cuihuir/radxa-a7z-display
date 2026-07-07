# A7Z Debian 12 试验检查清单

这是 Radxa Cubie A7Z 上 Debian 12 试验分支的动态检查清单。

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

## 接下来要盯的点

- [ ] `rsdk build radxa-a733` 现在是否默认变成 `bookworm`？
- [ ] A733 上的 KDE 在 `bookworm` 下是否仍然避开 GDM？
- [ ] 生成出来的镜像是否还能保持 Micro HDMI 作为首个可用路径？
- [ ] 有没有任何包钩子默认还在假设 `trixie` 专用行为？
- [ ] 更新后的 A7Z 报告是否还指向真正的下一处阻塞点？

## 已知发现

- `rsdk` 已经有 A733 专属的 KDE 逻辑，包含 GLES 和有限 framebuffer 的处理。
- `rsdk` 已经有 `bookworm` 的桌面包逻辑。
- 公共侧的主要阻塞点就是产品元数据只公开了 `trixie`。
- 本地元数据修改后，剩下的阻塞点应该转向真实的构建/启动验证。

## 下一步

- 做一次 `radxa-a733` 的 `bookworm` 桌面构建试跑，并记录第一条失败或成功信息。

## 备注

- 这份清单保持短。
- 只记录会影响下一步判断的内容。
