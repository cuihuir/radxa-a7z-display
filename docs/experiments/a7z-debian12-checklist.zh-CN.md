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
- [x] 第一次 dry run 失败后，已初始化 RSDK 子模块。
- [x] 确认当前宿主需要 Debian/Ubuntu 构建环境。
- [x] 使用本地已有的 Debian 12 distrobox 安装依赖并验证 dry run。
- [x] 增加 Debian 12 适用的 Jsonnet 0.18 兼容补丁。
- [x] 确认 Debian 12 distrobox 可以完成 `radxa-a733 bookworm kde` dry run。

## 接下来要盯的点

- [x] `rsdk build radxa-a733` 现在是否默认变成 `bookworm`？
- [ ] A733 上的 KDE 在 `bookworm` 下是否仍然避开 GDM？
- [ ] 生成出来的镜像是否还能保持 Micro HDMI 作为首个可用路径？
- [ ] 有没有任何包钩子默认还在假设 `trixie` 专用行为？
- [ ] 更新后的 A7Z 报告是否还指向真正的下一处阻塞点？
- [x] 在 Debian/Ubuntu 构建环境里 dry run 能否跑完？
- [x] 确认当前 distrobox 真实镜像构建会失败，原因是宿主缺少 `qemu-aarch64` binfmt。
- [ ] 宿主机是否已经通过 `binfmt_misc` 注册 `qemu-aarch64`？

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

## 下一步

- 先在宿主机安装/注册 `qemu-aarch64` binfmt，然后回到 Debian 12 distrobox 重试 `src/bin/rsdk build radxa-a733`。

## 备注

- 这份清单保持短。
- 只记录会影响下一步判断的内容。
