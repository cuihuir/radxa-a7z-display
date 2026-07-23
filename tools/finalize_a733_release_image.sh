#!/bin/sh

set -eu

kernel=5.15.147-21.1-a733

if [ "$#" -ne 1 ]; then
	echo "Usage: sudo $0 IMAGE.img" >&2
	exit 2
fi

image=$1

if [ "$(id -u)" -ne 0 ]; then
	echo "This command must run as root." >&2
	exit 1
fi

if [ ! -f "$image" ] || [ -L "$image" ]; then
	echo "Refusing non-regular image: $image" >&2
	exit 1
fi

case $image in
	*.img) ;;
	*)
		echo "Image filename must end in .img: $image" >&2
		exit 1
		;;
esac

image=$(readlink -f "$image")
workdir=$(mktemp -d)
loop=

cleanup()
{
	if mountpoint -q "$workdir/root"; then
		umount "$workdir/root"
	fi
	if [ -n "$loop" ]; then
		losetup -d "$loop" 2>/dev/null || true
	fi
	rm -rf "$workdir"
}
trap cleanup EXIT INT TERM

mkdir "$workdir/root"
loop=$(losetup --find --show --partscan "$image")
root_partition="${loop}p3"

for unused in 1 2 3 4 5; do
	[ -b "$root_partition" ] && break
	sleep 1
done

if [ ! -b "$root_partition" ]; then
	echo "Root partition did not appear: $root_partition" >&2
	exit 1
fi

if [ "$(blkid -s LABEL -o value "$root_partition")" != rootfs ]; then
	echo "Partition 3 is not the expected rootfs." >&2
	exit 1
fi

e2fsck -pf "$root_partition" || status=$?
case ${status:-0} in
	0|1) ;;
	*) exit "$status" ;;
esac

mount "$root_partition" "$workdir/root"
root="$workdir/root"

if [ ! -d "$root/lib/modules/$kernel" ]; then
	echo "Missing kernel modules for $kernel" >&2
	exit 1
fi

rm -f \
	"$root/etc/systemd/system/sysinit.target.wants/a7z-kernel-metadata.service" \
	"$root/etc/systemd/system/a7z-kernel-metadata.service" \
	"$root/usr/local/sbin/a7z-finalize-kernel-metadata" \
	"$root/var/lib/a7z/kernel-metadata-ready"

depmod -b "$root" "$kernel"
setcap cap_net_raw+ep "$root/usr/bin/ping"

modinfo -b "$root" -k "$kernel" pvrsrvkm >/dev/null
modinfo -b "$root" -k "$kernel" aic_load_fw_usb >/dev/null
modinfo -b "$root" -k "$kernel" aic8800_fdrv_usb >/dev/null

if [ "$(getcap "$root/usr/bin/ping")" != "$root/usr/bin/ping cap_net_raw=ep" ]; then
	echo "Failed to preserve ping capability." >&2
	exit 1
fi

sync
umount "$root"
e2fsck -fn "$root_partition"
losetup -d "$loop"
loop=

echo "Finalized A733 release image: $image"
