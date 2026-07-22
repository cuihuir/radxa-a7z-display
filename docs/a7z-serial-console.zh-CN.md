# Radxa A7Z 串口控制台

在修改镜像之前，优先用串口控制台诊断启动、HDMI 或网络故障。当显示无法使用或 Wi-Fi 不可用时，它是最可靠的恢复路径。

## 所需设备

- 一个 3.3 V TTL USB 转串口适配器（如 CP2102、CH340 或 FTDI）。
- 三根母对母杜邦线。
- A7Z 仍通过 USB-C 正常供电。

不要使用 RS-232 适配器，其电平可能损坏开发板。不要将适配器的 VCC、3.3 V 或 5 V 引脚连接到 A7Z；只需要 TX、RX 和 GND。

## 排针位置与接线

调试控制台使用 A7Z 40 针 GPIO 排针上的 UART0（官方板卡文档中为 GPIO 接口 #12）。按照标准 40 针物理针脚编号：

| A7Z 物理针脚 | A733 信号 | 连接到 USB 转串口适配器 |
| --- | --- | --- |
| 8 | PB9 / UART0-TX | RX |
| 10 | PB10 / UART0-RX | TX |
| 6 | GND | GND |

TX 与 RX 必须交叉连接。针脚 6 是方便使用的地线；针脚 9、14、20、25、30、34 和 39 也都是地线。

## 终端参数

使用 `115200 8N1`，关闭流控。给开发板上电或重启前先打开终端，才能捕获 U-Boot 和内核早期日志。

在 Linux 主机上，先识别适配器：

```bash
ls /dev/ttyUSB* /dev/ttyACM*
```

2026 年 7 月 21 日实机验证的适配器为 CH341/CH340，USB ID 是
`1a86:7523`，设备路径为：

```text
/dev/ttyUSB0
/dev/serial/by-id/usb-1a86_USB_Serial-if00-port0
```

脚本中优先使用稳定的 `/dev/serial/by-id/` 路径。如果设备权限是
`root:dialout`，可将当前用户加入 `dialout` 组，然后重新登录：

```bash
sudo usermod -aG dialout "$USER"
```

再打开串口，例如：

```bash
picocom -b 115200 /dev/ttyUSB0
```

或：

```bash
screen /dev/ttyUSB0 115200
```

如需只读抓取日志、确保不向开发板发送字符，可使用：

```bash
stty -F /dev/serial/by-id/usb-1a86_USB_Serial-if00-port0 \
  115200 cs8 -cstopb -parenb -ixon -ixoff -crtscts raw -echo
timeout 120 cat /dev/serial/by-id/usb-1a86_USB_Serial-if00-port0 \
  | tee a7z-serial-boot.log
```

实机验证镜像使用 `console=ttyAS0,115200n8` 配置内核控制台，并使用
`earlyprintk=sunxi-uart,0x02500000` 输出早期日志。因此正常启动时会先看到引导加载器输出，随后是内核日志，最后出现登录提示符。

2026 年 7 月 21 日的验证成功捕获了正常关机、随后一次 `l1` 启动、systemd
服务启动、Wi-Fi 初始化、SDDM 启动，以及最终登录提示：

```text
Debian GNU/Linux 12 radxa-cubie-a7z ttyAS0
radxa-cubie-a7z login:
```

## 当前恢复用途

针对当前 Debian 12 镜像排障，串口日志可以区分以下表面上难以判断的问题：

- SD 镜像没有启动，还是小 HDMI 屏幕无法正确显示。
- 开发板从其他存储设备启动，而不是 SD 卡。
- 自定义内核已启动，但 AIC8800 Wi-Fi DKMS 模块加载失败。
- 系统已到达登录提示符，但 HDMI 模式选择不正确。

请从上电开始一直捕获到登录提示符，并避免粘贴账户密码或 Wi-Fi 密钥。最有价值的内容包括启动设备、内核命令行、根文件系统挂载、DRM/HDMI 日志，以及 Wi-Fi/DKMS 错误。

## 可选的早期 fsck 恢复启动项

正常 `l0` initramfs 继续使用已验证的 `display3` 策略，不直接修改。应在 A7Z 上独立生成恢复镜像：

```bash
sudo ./tools/build_a733_recovery_initramfs.sh \
  5.15.147-21.1-a733 \
  /boot/initrd.img-5.15.147-21.1-a733.a7z-recovery.new
sudo ./tools/install_a733_recovery_entry.sh \
  5.15.147-21.1-a733 \
  /boot/initrd.img-5.15.147-21.1-a733.a7z-recovery.new
```

安装脚本会增加 `a7z-recovery`，保持现有默认项不变，并生成带时间戳的 extlinux 备份。通过 UART U-Boot 菜单输入数字选择恢复项。该启动项保留详细内核输出，并在挂载根文件系统前检查 ext4。

可先在不接触块设备和已挂载文件系统的情况下验证修复策略：

```bash
./tools/test_a733_recovery_fsck.sh
```

测试会创建一次性的普通文件 ext4 镜像，构造块组描述符不一致，要求 `e2fsck -p` 返回 `1`，然后要求只读复检通过。整个过程不会访问当前 SD 卡。

## 依据与来源

- 官方 GPIO 针脚表：<https://docs.radxa.com/en/cubie/a7z/hardware-use/pin-gpio>
- 官方 A7Z 板卡页面：<https://docs.radxa.com/en/cubie/a7z>
- A733 设备配置：`radxa/device-a733` 的 `configs/cubie_a7z/sys_config.fex`
  指定 `uart_debug_port = 0`、TX 为 `PB09`、RX 为 `PB10`。
- A733 启动环境：`radxa/device-a733` 的 `configs/cubie_a7z/debian/env.cfg`
  指定 `console=ttyS0,115200`。
