# A733 串口启动恢复验证

## 目标

在多次异常断电恢复、initramfs 实验和误导性的 SSH 超时之后，建立可靠的启动失败判断边界。

## 串口配置

- 适配器：CH341/CH340，USB ID `1a86:7523`；
- 主机设备：`/dev/serial/by-id/usb-1a86_USB_Serial-if00-port0`；
- 参数：`115200 8N1`，关闭流控；
- 开发板控制台：UART0，A7Z 针脚 8 TX 接适配器 RX，针脚 10 RX 接适配器 TX，针脚 6 接 GND。

## 恢复过程

离线执行 `e2fsck -fy`，修复了多次非正常断电造成的 ext4 orphan 链和分配 bitmap 不一致。启动配置恢复为默认 `l1`，并恢复显式原厂 A7Z DTB 和 `module_blacklist=pvrsrvkm`。

未经验证的 14 MB `MODULES=dep` initramfs 已从正常启动路径撤销。`l0` initramfs 从已知可启动备份逐字节恢复：

```text
size=42251056
sha256=395d50f38d752d978d4070cf371e3ee4ec99e23e9ff45f1a6b1b79f5274d7574
```

## 串口结果

保存的 UART 日志显示：

1. U-Boot 加载 `/boot/extlinux/extlinux.conf`；
2. 第 1 项选择 `5.15.147-21.1-a733`；
3. U-Boot 成功加载精确 initramfs、kernel 和 A7Z DTB；
4. 约 15 秒时启动 kernel；
5. NetworkManager、WPA supplicant、SSH 和 SDDM 启动；
6. 系统在 `ttyAS0` 到达 `radxa-cubie-a7z login:`。

随后 SSH 确认 kernel 为 `5.15.147-21.1-a733`、默认项为 `l0`、systemd 健康、`wlan0` 地址为 `192.168.123.210`、`pvrsrvkm` 已加载、DRM 提供 `card0`、`card1` 和 `renderD128`，HDMI 为 connected/enabled。

## 隔离早期 fsck 复测

在不修改 `default l0` 的前提下追加了独立 `fscktest` extlinux 启动项，并通过 UART 数字键选择菜单第 7 项。U-Boot 成功加载：

```text
/boot/initrd.img-5.15.147-21.1-a733.fsck-final-test
size=14701871
sha256=367883cd00c9b0781e3ba97767cd50a1ee19955033c94b247309383e0e41762c
```

启动日志随后显示预期的挂载前检查：

```text
Begin: Will now check root file system ... fsck from util-linux 2.38.1
[/sbin/fsck.ext4 (1) -- /dev/mmcblk0p3] fsck.ext4 -a -C0 /dev/mmcblk0p3
rootfs: clean, 199656/3786960 files, 2092429/15228411 blocks
```

同一次启动继续完成 NetworkManager、SSH、SDDM，并到达 `ttyAS0` 登录提示。本机保留 ignored artifacts 时，原始日志位于 `artifacts/serial/2026-07-21-fsck-final-isolated-boot.log`。

## 可复现的 recovery 构建

仓库中的 recovery 配置和构建脚本已在开发板上复现相同结果，且没有修改正常 `l0` initramfs：

```text
path=/boot/initrd.img-5.15.147-21.1-a733.a7z-recovery
size=14701537
sha256=5f536ec77e793cd4d79687eeb46279923b0df870d1db761191d76df4366fa1ce
```

带保护的安装脚本新增 `label a7z-recovery`，同时保留 `default l0`。通过 UART 选择菜单第 7 项后，新生成镜像执行了相同的挂载前 `fsck.ext4 -a` 检查，到达登录提示，并恢复 Wi-Fi 地址 `192.168.123.210`。生成镜像的串口记录位于 `artifacts/serial/2026-07-21-generated-a7z-recovery-boot.log`。

主机端普通文件测试还构造了块组描述符不一致，观察到 `e2fsck -p` 返回 `1`，并在只读复检时返回 `0`。这在不接触当前 SD 卡的情况下验证了自动修复行为，但仍不能替代未来在备用介质上的完整启动修复测试。

## 备用介质修复启动

使用一张容量略小的 58.2 GiB 备用卡进行了完整测试：保留启动前缀和两个 FAT 分区，重建较小的 ext4 根分区，并按文件恢复根文件系统。备用卡首次正常 `l0` 启动成功到达登录提示，Wi-Fi 正常。

备用卡离线时，使用 `debugfs` 修改块组 0 的空闲块计数。只读 `e2fsck -fn` 返回 `4`，同时报告块组描述符校验和无效、空闲块计数错误；主机端没有执行修复。

随后正常 `l0` 无法挂载根分区并进入 initramfs。再次上电后，通过 UART 选择 `a7z-recovery`，恢复 initramfs 输出：

```text
rootfs: One or more block group descriptor checksums are invalid.  FIXED.
rootfs: Group descriptor 0 checksum is 0x99ce, should be 0x54c2.  FIXED.
fsck exited with status code 1
```

系统继续启动到 `ttyAS0` 登录提示。SSH 确认 systemd 为 running、Wi-Fi 恢复到 `192.168.123.210`、`default l0` 未改变，并且 `tune2fs` 报告根文件系统状态为 `clean`。UART 证据位于 `artifacts/serial/2026-07-21-spare-sd-fault-recovery-prearmed.log`。

## 最终发布镜像

2026 年 7 月 22 日将发布源重新构建为 12 GiB 紧凑 GPT 镜像。通过移除不使用的
AMD/NVIDIA PCI GPU 模块和固件，正常 initramfs 降到 19,768,890 字节，连续
两次正常重启均通过。镜像完成净化和 XZ 压缩后重新写回备用 SD 卡，并使用
`radxa/radxa` 到达串口登录提示。首次启动生成了新的 machine ID。随后在实机
验证专用 systemd unit 可在 SSH 启动前生成唯一 host key，从而在不发布共享
密钥的情况下修复净化镜像的 SSH 启动问题。

## 结论

历史精确 `l0` initramfs 在本次有串口记录的测试中可以启动。更早的故障还包含已确认的文件系统损坏和启动项破坏，因此不能把原因简化为 SSH 时序。以后所有早期启动结论必须以 UART 证据为准。early-fsck recovery 现已在备用介质上修复可复现的 ext4 元数据故障，并继续完成系统启动；对于 `e2fsck -a` 无法自动修复的错误，离线 fsck 仍是后备方案。
