#!/bin/sh

set -eu

if [ "$#" -ne 5 ]; then
	echo "Usage: $0 INPUT.deb A7Z.dtb Image KERNEL.config OUTPUT.deb" >&2
	exit 2
fi

input=$1
dtb=$2
image=$3
kernel_config=$4
output=$5
repo_root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
hook="$repo_root/config/initramfs-tools/hooks/zz-a7z-skip-early-fsck"
recovery_postinst="$repo_root/config/kernel/postinst.d/zzz-a7z-repair-recovery-entry"
touchscreen_config="$repo_root/config/kernel/a733-touchscreen.config"
sd_stability_patch="$repo_root/config/kernel/a733-sd-stability.patch"
workdir=$(mktemp -d)

cleanup()
{
	rm -rf "$workdir"
}
trap cleanup EXIT INT TERM

dpkg-deb -R "$input" "$workdir/package"
while IFS= read -r required_config; do
	grep -qx "$required_config" "$kernel_config"
done < "$touchscreen_config"
install -D -m 0755 "$hook" \
	"$workdir/package/etc/initramfs-tools/hooks/zz-a7z-skip-early-fsck"
install -D -m 0755 "$recovery_postinst" \
	"$workdir/package/etc/kernel/postinst.d/zzz-a7z-repair-recovery-entry"
install -D -m 0644 "$sd_stability_patch" \
	"$workdir/package/usr/share/doc/linux-image-5.15.147-21.1-a733/a733-sd-stability.patch"
install -D -m 0644 "$dtb" \
	"$workdir/package/usr/lib/linux-image-5.15.147-21.1-a733/allwinner/sun60i-a733-cubie-a7z.dtb"
install -m 0644 "$image" \
	"$workdir/package/boot/vmlinuz-5.15.147-21.1-a733"
install -m 0644 "$kernel_config" \
	"$workdir/package/boot/config-5.15.147-21.1-a733"

sed -i 's/^Version: 5\.15\.147-21\.1\(+display[0-9][0-9]*\)\?$/Version: 5.15.147-21.1+display5/' \
	"$workdir/package/DEBIAN/control"

(
	cd "$workdir/package"
	find . -path ./DEBIAN -prune -o -type f -print0 \
		| sort -z \
		| xargs -0 md5sum > DEBIAN/md5sums
)

dpkg-deb --build --root-owner-group "$workdir/package" "$output"
