#!/bin/sh

set -eu

if [ "$#" -ne 2 ]; then
	echo "Usage: $0 XWAYLAND OUTPUT.deb" >&2
	exit 2
fi

xwayland=$1
output=$2
version=24.1.6
prefix=/opt/a733-xwayland/$version
expected_sha256=a58c2908da43d45bdf28f63b692c260452b9f455ce9aa36cd52a33190f389135
workdir=$(mktemp -d)
package=$workdir/package

cleanup()
{
	rm -rf "$workdir"
}
trap cleanup EXIT INT TERM

test "$(dpkg --print-architecture)" = arm64
test -x "$xwayland"
echo "$expected_sha256  $xwayland" | sha256sum -c -
file "$xwayland" | grep -Fq 'ARM aarch64'
"$xwayland" -version 2>&1 | grep -Fq "Xwayland Version $version"

mkdir -p "$package/DEBIAN" "$package$prefix" \
	"$package/usr/share/doc/a733-pvr-xwayland"
install -m 0755 "$xwayland" "$package$prefix/Xwayland"
sha256sum "$package$prefix/Xwayland" \
	> "$package/usr/share/doc/a733-pvr-xwayland/SHA256SUMS"

cat > "$package/DEBIAN/control" <<EOF
Package: a733-pvr-xwayland
Version: $version+a7331
Section: non-free/x11
Priority: optional
Architecture: arm64
Maintainer: cuihuir <cuihuir@163.com>
Depends: a733-pvr-gpu (>= 24.2.6603887+gpu7), kwin-common (>= 4:5.27.5-3+a7331), xwayland, libc6, libdrm2, libepoxy0, libgbm1, libpixman-1-0, libwayland-client0, libwayland-egl1, libxau6, libxdmcp6, libxfont2, libxshmfence1
Description: GPU-accelerated XWayland GLES glamor integration for A733
 Installs XWayland 24.1.6 under /opt. The a733-pvr-gpu wrapper activates it
 only with a compatible patched KWin and scopes the PowerVR environment to
 XWayland with the supported GLES glamor backend.
EOF
cat > "$package/DEBIAN/postinst" <<'EOF'
#!/bin/sh
set -e
if [ -x /usr/local/sbin/a733-pvr-control ]; then
	/usr/local/sbin/a733-pvr-control enable
fi
EOF
cat > "$package/DEBIAN/postrm" <<'EOF'
#!/bin/sh
set -e
if [ -x /usr/local/sbin/a733-pvr-control ]; then
	/usr/local/sbin/a733-pvr-control enable
fi
EOF
chmod 0755 "$package/DEBIAN/postinst" "$package/DEBIAN/postrm"

mkdir -p "$(dirname -- "$output")"
dpkg-deb --build --root-owner-group "$package" "$output"
