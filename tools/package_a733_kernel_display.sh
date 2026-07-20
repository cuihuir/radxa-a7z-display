#!/bin/sh

set -eu

if [ "$#" -ne 3 ]; then
	echo "Usage: $0 INPUT.deb A7Z.dtb OUTPUT.deb" >&2
	exit 2
fi

input=$1
dtb=$2
output=$3
repo_root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
hook="$repo_root/config/initramfs-tools/hooks/zz-a7z-skip-early-fsck"
workdir=$(mktemp -d)

cleanup()
{
	rm -rf "$workdir"
}
trap cleanup EXIT INT TERM

dpkg-deb -R "$input" "$workdir/package"
install -D -m 0755 "$hook" \
	"$workdir/package/etc/initramfs-tools/hooks/zz-a7z-skip-early-fsck"
install -D -m 0644 "$dtb" \
	"$workdir/package/usr/lib/linux-image-5.15.147-21.1-a733/allwinner/sun60i-a733-cubie-a7z.dtb"

sed -i 's/^Version: 5\.15\.147-21\.1$/Version: 5.15.147-21.1+display3/' \
	"$workdir/package/DEBIAN/control"

(
	cd "$workdir/package"
	find . -path ./DEBIAN -prune -o -type f -print0 \
		| sort -z \
		| xargs -0 md5sum > DEBIAN/md5sums
)

dpkg-deb --build --root-owner-group "$workdir/package" "$output"
