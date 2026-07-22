#!/bin/sh

set -eu

if [ "$#" -ne 2 ]; then
	echo "Usage: $0 KWIN.dsc OUTPUT_DIR" >&2
	exit 2
fi

dsc=$(readlink -f "$1")
output=$(readlink -m "$2")
root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
patch_file=$root/patches/kwin/0001-linux-dmabuf-use-egl-render-node.patch
workdir=$(mktemp -d)
source_dir=$workdir/kwin

cleanup()
{
	rm -rf "$workdir"
}
trap cleanup EXIT INT TERM

test "$(dpkg --print-architecture)" = arm64
test -f "$dsc"
test -f "$patch_file"
grep -Fq 'Source: kwin' "$dsc"
grep -Fq 'Version: 4:5.27.5-3' "$dsc"

case " ${DEB_BUILD_OPTIONS:-} " in
	*" noopt "*)
		echo "Release KWin builds must use Debian's default optimization." >&2
		exit 1
		;;
esac

dpkg-source -x "$dsc" "$source_dir"
patch -d "$source_dir" -p1 < "$patch_file"

{
	cat <<'EOF'
kwin (4:5.27.5-3+a7331) bookworm; urgency=medium

  * Advertise the EGL render node in linux-dmabuf feedback.

 -- cuihuir <cuihuir@163.com>  Fri, 17 Jul 2026 00:00:00 -0500

EOF
	cat "$source_dir/debian/changelog"
} > "$workdir/changelog"
mv "$workdir/changelog" "$source_dir/debian/changelog"

mkdir -p "$output"
(
	cd "$source_dir"
	DEB_BUILD_OPTIONS="${DEB_BUILD_OPTIONS:-nocheck parallel=1}" \
		dpkg-buildpackage -b -uc -us -j"${JOBS:-1}"
)
cp "$workdir"/*.deb "$output/"
(
	cd "$output"
	sha256sum ./*.deb | sed 's#  \./#  #' > SHA256SUMS
)
