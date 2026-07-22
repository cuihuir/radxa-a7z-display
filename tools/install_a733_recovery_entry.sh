#!/bin/sh

set -eu

PATH=/usr/sbin:/usr/bin:/sbin:/bin:$PATH
export PATH

usage()
{
	echo "Usage: sudo $0 KERNEL_VERSION RECOVERY_INITRD" >&2
	exit 2
}

[ "$#" -eq 2 ] || usage
[ "$(id -u)" -eq 0 ] || usage

kernel=$1
source_initrd=$2
extlinux=/boot/extlinux/extlinux.conf
target_initrd=/boot/initrd.img-$kernel.a7z-recovery
kernel_image=/boot/vmlinuz-$kernel
dtb_dir=/usr/lib/linux-image-$kernel

[ -f "$source_initrd" ] || usage
[ -f "$extlinux" ] || {
	echo "Missing extlinux configuration: $extlinux" >&2
	exit 1
}
[ -f "$kernel_image" ] || {
	echo "Missing kernel image: $kernel_image" >&2
	exit 1
}
[ -d "$dtb_dir" ] || {
	echo "Missing kernel DTB directory: $dtb_dir" >&2
	exit 1
}

root_source=$(findmnt -n -o SOURCE /)
root_uuid=$(blkid -s UUID -o value "$root_source")
[ -n "$root_uuid" ] || {
	echo "Unable to determine root filesystem UUID." >&2
	exit 1
}

default_before=$(sed -n 's/^default[[:space:]]\+//p' "$extlinux" | head -1)
[ -n "$default_before" ] || {
	echo "The extlinux configuration has no default entry." >&2
	exit 1
}

backup=$extlinux.before-a7z-recovery-$(date -u +%Y%m%dT%H%M%SZ)
temporary=$extlinux.tmp.$$
cp -a "$extlinux" "$backup"
install -m 0644 "$source_initrd" "$target_initrd.tmp.$$"
mv "$target_initrd.tmp.$$" "$target_initrd"

awk '
$1 == "label" { skip = ($2 == "a7z-recovery") }
!skip { print }
' "$extlinux" > "$temporary"

cat >> "$temporary" <<EOF

label a7z-recovery
	menu label A7Z recovery: early ext4 fsck (UART recommended)
	linux $kernel_image
	initrd $target_initrd
	fdtdir $dtb_dir/
	append root=UUID=$root_uuid console=ttyAS0,115200n8 earlyprintk=sunxi-uart,0x2500000 rootwait clk_ignore_unused loglevel=7 ro earlycon consoleblank=0 console=tty1 coherent_pool=2M irqchip.gicv3_pseudo_nmi=0 kasan=off
EOF

default_after=$(sed -n 's/^default[[:space:]]\+//p' "$temporary" | head -1)
[ "$default_after" = "$default_before" ] || {
	echo "Refusing to change default entry from $default_before to $default_after." >&2
	exit 1
}

chmod --reference="$extlinux" "$temporary"
chown --reference="$extlinux" "$temporary"
mv "$temporary" "$extlinux"
sync

echo "Installed optional recovery entry: a7z-recovery"
echo "Default entry remains: $default_before"
echo "Configuration backup: $backup"
