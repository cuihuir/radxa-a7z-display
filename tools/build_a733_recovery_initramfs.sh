#!/bin/sh

set -eu

PATH=/usr/sbin:/usr/bin:/sbin:/bin:$PATH
export PATH

usage()
{
	echo "Usage: sudo $0 KERNEL_VERSION OUTPUT_INITRD" >&2
	exit 2
}

[ "$#" -eq 2 ] || usage
[ "$(id -u)" -eq 0 ] || usage

kernel=$1
output=$2
repo_root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
recovery_config=$repo_root/config/initramfs-tools/recovery

command -v mkinitramfs >/dev/null 2>&1 || {
	echo "mkinitramfs is required; install initramfs-tools." >&2
	exit 1
}
command -v lsinitramfs >/dev/null 2>&1 || {
	echo "lsinitramfs is required; install initramfs-tools-core." >&2
	exit 1
}
[ -d "/usr/lib/modules/$kernel" ] || {
	echo "Kernel modules not found: /usr/lib/modules/$kernel" >&2
	exit 1
}

workdir=$(mktemp -d)
temporary_output=$output.tmp.$$

cleanup()
{
	rm -rf "$workdir"
	rm -f "$temporary_output"
}
trap cleanup EXIT INT TERM

cp -a /etc/initramfs-tools/. "$workdir/"
rm -f "$workdir/hooks/zz-a7z-skip-early-fsck"
install -D -m 0644 "$recovery_config/conf.d/a7z-recovery" \
	"$workdir/conf.d/a7z-recovery"
install -D -m 0755 "$recovery_config/hooks/a7z-recovery-fsck" \
	"$workdir/hooks/a7z-recovery-fsck"

mkdir -p "$(dirname -- "$output")"
mkinitramfs -d "$workdir" -o "$temporary_output" "$kernel"

for required in usr/sbin/fsck usr/sbin/fsck.ext4 usr/sbin/e2fsck; do
	lsinitramfs "$temporary_output" | grep -qx "$required" || {
		echo "Recovery initramfs is missing $required." >&2
		exit 1
	}
done

size=$(stat -c %s "$temporary_output")
if [ "$size" -gt 20971520 ]; then
	echo "Recovery initramfs exceeds the 20 MiB safety limit: $size bytes." >&2
	exit 1
fi

chmod 0644 "$temporary_output"
mv "$temporary_output" "$output"
trap - EXIT INT TERM
rm -rf "$workdir"

echo "Recovery initramfs created: $output"
echo "size=$size"
sha256sum "$output"
