#!/bin/sh

set -eu

usage()
{
	echo "Usage: sudo $0 PACKAGE.deb [--activate]" >&2
	exit 2
}

[ "$#" -ge 1 ] && [ "$#" -le 2 ] || usage
[ "$(id -u)" -eq 0 ] || usage

package=$1
activate=${2:-}
[ -f "$package" ] || usage
[ -z "$activate" ] || [ "$activate" = "--activate" ] || usage

kernel=5.15.147-21.1-a733
extlinux=/boot/extlinux/extlinux.conf
initrd=/boot/initrd.img-$kernel
recovery_initrd=/boot/initrd.img-5.15.147-21-a733.vendor
recovery_dtb=/usr/lib/linux-image-5.15.147-21-a733-vendor/allwinner/sun60i-a733-cubie-a7z.dtb

repair_recovery_entry()
{
	sed -i '/^label l1$/,/^label l2$/{/^[[:space:]]*fdt .*linux-image-5\.15\.147-21-a733-vendor/d}' "$extlinux"
	sed -i "\\|^[[:space:]]*initrd $recovery_initrd\$|a\\\tfdt $recovery_dtb" "$extlinux"
	sed -i '/^label l1$/,/^label l2$/{/^[[:space:]]*append /{/module_blacklist=pvrsrvkm/!s/$/ module_blacklist=pvrsrvkm/}}' "$extlinux"
}

exec 9>/run/lock/a7z-display-kernel-deploy.lock
flock -n 9 || {
	echo "Another A7Z kernel deployment is running." >&2
	exit 1
}

sed -i 's/^default l0$/default l1/' "$extlinux"
dpkg -i "$package"

dpkg-query -W -f='${db:Status-Abbrev}\n' linux-image-5.15.147-21.1-a733 \
	| grep -qx 'ii '
dkms status | grep -Fq "aic8800-usb/5.0+git20260123.5f7be68d-6, $kernel, aarch64: installed"
dkms status | grep -Fq "radxa-overlays/0.2.25, $kernel, aarch64: installed"

gzip -t "$initrd"
if lsinitramfs "$initrd" \
	| grep -Eq 'usr/(sbin/(fsck|e2fsck|fsck.ext4)|lib/.*/(libext2fs|libe2p|libcom_err))'; then
	echo "Unexpected fsck payload remains in $initrd." >&2
	exit 1
fi

initrd_size=$(stat -c %s "$initrd")
if [ "$initrd_size" -gt 42300000 ]; then
	echo "Initramfs is too large for the verified A7Z boot path: $initrd_size bytes." >&2
	exit 1
fi

u-boot-update
repair_recovery_entry
sed -i 's/^default l0$/default l1/' "$extlinux"

if [ "$activate" = "--activate" ]; then
	sed -i 's/^default l1$/default l0/' "$extlinux"
fi

sync
echo "Kernel package verified; initramfs size: $initrd_size bytes."
grep '^default' "$extlinux"
