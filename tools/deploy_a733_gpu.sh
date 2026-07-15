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

exec 9>/run/lock/a7z-gpu-deploy.lock
flock -n 9 || {
	echo "Another A7Z GPU deployment is running." >&2
	exit 1
}

test "$(dpkg-deb -f "$package" Package)" = a733-pvr-gpu
grep -Fq 'radxa,cubie-a7z' /proc/device-tree/compatible
dpkg-query -W -f='${Version}\n' linux-image-5.15.147-21.1-a733 \
	| grep -qx '5.15.147-21.1+display2'

sed -i 's/^default l0$/default l1/' "$extlinux"
apt-get install -y "$package"

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
sed -i 's/^default l0$/default l1/' "$extlinux"
if [ "$activate" = --activate ]; then
	sed -i 's/^default l1$/default l0/' "$extlinux"
fi

sync
echo "A733 PowerVR GPU package installed and verified."
echo "Initramfs size: $initrd_size bytes."
echo "Reboot to load pvrsrvkm and start the accelerated desktop session."
grep '^default' "$extlinux"
