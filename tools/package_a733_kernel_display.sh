#!/bin/sh

set -eu

if [ "$#" -ne 2 ]; then
	echo "Usage: $0 INPUT.deb OUTPUT.deb" >&2
	exit 2
fi

input=$1
output=$2
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

sed -i 's/^Version: 5\.15\.147-21\.1$/Version: 5.15.147-21.1+display2/' \
	"$workdir/package/DEBIAN/control"

(
	cd "$workdir/package"
	find . -path ./DEBIAN -prune -o -type f -print0 \
		| sort -z \
		| xargs -0 md5sum > DEBIAN/md5sums
)

dpkg-deb --build --root-owner-group "$workdir/package" "$output"
