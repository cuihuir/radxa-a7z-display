#!/bin/sh

set -eu

if [ "$#" -ne 3 ]; then
	echo "Usage: $0 IMG_BXM_DKMS.deb KERNEL_TREE OUTPUT.ko" >&2
	exit 2
fi

dkms_deb=$1
kernel_tree=$(CDPATH= cd -- "$2" && pwd)
output=$3
workdir=$(mktemp -d)

cleanup()
{
	rm -rf "$workdir"
}
trap cleanup EXIT INT TERM

for command in dpkg-deb make aarch64-linux-gnu-gcc aarch64-linux-gnu-nm modinfo; do
	command -v "$command" >/dev/null 2>&1 || {
		echo "Missing build command: $command" >&2
		exit 1
	}
done

test -f "$kernel_tree/Module.symvers"
test -f "$kernel_tree/include/generated/utsrelease.h"
dpkg-deb -x "$dkms_deb" "$workdir/package"
source_dir="$workdir/package/usr/src/img-bxm-dkms-0.1.0-3"

make -j"$(getconf _NPROCESSORS_ONLN)" \
	BUILD=release ARCH=arm64 KERNEL_ARCH=arm64 \
	CROSS_COMPILE=aarch64-linux-gnu- \
	KERNEL_CROSS_COMPILE=aarch64-linux-gnu- \
	KERNEL_CC=aarch64-linux-gnu-gcc \
	KERNEL_LD=aarch64-linux-gnu-ld \
	KERNEL_NM=aarch64-linux-gnu-nm \
	KERNEL_OBJCOPY=aarch64-linux-gnu-objcopy \
	KERNELDIR="$kernel_tree" \
	-C "$source_dir/img-bxm/linux/rogue_km/build/linux/sunxi_linux"

module="$source_dir/img-bxm/linux/rogue_km/binary_sunxi_linux_nulldrmws_release/target_aarch64/kbuild/pvrsrvkm.ko"
vermagic=$(modinfo -F vermagic "$module")
release=$(sed -n 's/^#define UTS_RELEASE "\(.*\)"$/\1/p' \
	"$kernel_tree/include/generated/utsrelease.h")

case "$vermagic" in
	"$release "*) ;;
	*) echo "Unexpected vermagic: $vermagic" >&2; exit 1 ;;
esac
strings "$module" | grep -Fq '24.2@6603887'
strings "$module" | grep -Fq '36.56.104.183'

aarch64-linux-gnu-nm -u "$module" | sed -E 's/^ *U //' | sort -u \
	> "$workdir/undefined"
cut -f2 "$kernel_tree/Module.symvers" | sort -u > "$workdir/exported"
if comm -23 "$workdir/undefined" "$workdir/exported" \
	| grep -q .; then
	echo "The module has symbols absent from Module.symvers." >&2
	comm -23 "$workdir/undefined" "$workdir/exported" >&2
	exit 1
fi

mkdir -p "$(dirname -- "$output")"
cp "$module" "$output"
echo "Built $output for $release"

