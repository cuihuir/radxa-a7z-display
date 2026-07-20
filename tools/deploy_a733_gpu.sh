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
package=$(readlink -f "$package")
[ -z "$activate" ] || [ "$activate" = --activate ] || usage

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

exec 9>/run/lock/a7z-gpu-deploy.lock
flock -n 9 || {
	echo "Another A7Z GPU deployment is running." >&2
	exit 1
}

test "$(dpkg-deb -f "$package" Package)" = a733-pvr-gpu
grep -Fq 'radxa,cubie-a7z' /proc/device-tree/compatible
kernel_package_version=$(dpkg-query -W -f='${Version}\n' \
	linux-image-5.15.147-21.1-a733)
dpkg --compare-versions "$kernel_package_version" ge 5.15.147-21.1+display2
dpkg --compare-versions "$kernel_package_version" lt 5.15.147-21.2

sed -i 's/^default l0$/default l1/' "$extlinux"
apt-get install --fix-broken -y "$package"

module=/lib/modules/$kernel/updates/a733/pvrsrvkm.ko
test "$(modinfo -F vermagic "$module" | awk '{print $1}')" = "$kernel"
strings "$module" | grep -Fq '24.2@6603887'
strings "$module" | grep -Fq '36.56.104.183'
test -s /lib/firmware/rgx.fw.36.56.104.183
modprobe -n pvrsrvkm >/dev/null
gzip -t "$initrd"
initrd_size=$(stat -c %s "$initrd")
if [ "$initrd_size" -gt 42300000 ]; then
	echo "Initramfs is too large for the verified A7Z boot path: $initrd_size bytes." >&2
	exit 1
fi

u-boot-update
repair_recovery_entry
sed -i 's/^default l0$/default l1/' "$extlinux"
if [ "$activate" = --activate ]; then
	sed -i 's/^default l1$/default l0/' "$extlinux"
fi

sync
echo "A733 PowerVR GPU package installed and verified."
echo "Initramfs size: $initrd_size bytes."
echo "Reboot to load pvrsrvkm and start the accelerated desktop session."
grep '^default' "$extlinux"
