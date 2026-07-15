#!/bin/sh

set -eu

if [ "$#" -ne 3 ]; then
	echo "Usage: $0 PVRSRVKM.ko VENDOR_USERSPACE.deb OUTPUT.deb" >&2
	exit 2
fi

module=$1
userspace_deb=$2
output=$3
kernel=5.15.147-21.1-a733
ddk=24.2.6603887
prefix=/opt/a733-pvr/$ddk
workdir=$(mktemp -d)
package=$workdir/package

cleanup()
{
	rm -rf "$workdir"
}
trap cleanup EXIT INT TERM

test "$(modinfo -F vermagic "$module" | awk '{print $1}')" = "$kernel"
strings "$module" | grep -Fq '24.2@6603887'
strings "$module" | grep -Fq '36.56.104.183'
test "$(dpkg-deb -f "$userspace_deb" Package)" = \
	'xserver-xorg-img-bxm-1.21.1-2.deb'
test "$(dpkg-deb -f "$userspace_deb" Version)" = 1.0.1

mkdir -p "$package/DEBIAN" "$package/lib/modules/$kernel/updates/a733" \
	"$package/lib/firmware" "$package$prefix/lib" \
	"$package$prefix/share/vulkan/icd.d" \
	"$package$prefix/share/OpenCL/vendors" \
	"$package/usr/local/bin" "$package/usr/local/sbin" \
	"$package/usr/share/doc/a733-pvr-gpu"

dpkg-deb -x "$userspace_deb" "$workdir/vendor"
cp "$module" "$package/lib/modules/$kernel/updates/a733/pvrsrvkm.ko"
cp "$workdir/vendor/lib/firmware/rgx.fw.36.56.104.183" \
	"$package/lib/firmware/"
cp "$workdir/vendor/lib/firmware/rgx.sh.36.56.104.183" \
	"$package/lib/firmware/"
cp -a "$workdir/vendor/usr/lib/"*.so* "$package$prefix/lib/"
cp -a "$workdir/vendor/usr/local/lib/." "$package$prefix/lib/"

cat > "$package$prefix/share/vulkan/icd.d/img_icd.aarch64.json" <<EOF
{
    "file_format_version": "1.0.0",
    "ICD": {
        "library_path": "$prefix/lib/libVK_IMG.so.1",
        "api_version": "1.3.280"
    }
}
EOF
echo "$prefix/lib/libPVROCL.so.1" \
	> "$package$prefix/share/OpenCL/vendors/img.icd"

cat > "$package/usr/local/bin/a733-pvr-run" <<EOF
#!/bin/sh
export LD_LIBRARY_PATH="$prefix/lib\${LD_LIBRARY_PATH:+:\$LD_LIBRARY_PATH}"
export LIBGL_DRIVERS_PATH="$prefix/lib/dri"
export VK_DRIVER_FILES="$prefix/share/vulkan/icd.d/img_icd.aarch64.json"
export OCL_ICD_VENDORS="$prefix/share/OpenCL/vendors"
exec "\$@"
EOF
chmod 0755 "$package/usr/local/bin/a733-pvr-run"

cat > "$package/usr/local/sbin/a733-pvr-control" <<EOF
#!/bin/sh
set -eu
prefix=$prefix

enable()
{
	mkdir -p /etc/modules-load.d /etc/environment.d \
		/etc/profile.d /etc/X11/xorg.conf.d /usr/local/lib/a733-pvr
	echo pvrsrvkm > /etc/modules-load.d/a733-pvr.conf
	cat > /etc/environment.d/90-a733-pvr.conf <<ENV
LD_LIBRARY_PATH=\$prefix/lib
LIBGL_DRIVERS_PATH=\$prefix/lib/dri
VK_DRIVER_FILES=\$prefix/share/vulkan/icd.d/img_icd.aarch64.json
OCL_ICD_VENDORS=\$prefix/share/OpenCL/vendors
KWIN_DRM_DEVICES=/dev/dri/card0
ENV
	cat > /etc/profile.d/a733-pvr.sh <<'ENV'
export LD_LIBRARY_PATH="$prefix/lib\${LD_LIBRARY_PATH:+:\$LD_LIBRARY_PATH}"
export LIBGL_DRIVERS_PATH="$prefix/lib/dri"
export VK_DRIVER_FILES="$prefix/share/vulkan/icd.d/img_icd.aarch64.json"
export OCL_ICD_VENDORS="$prefix/share/OpenCL/vendors"
export KWIN_DRM_DEVICES=/dev/dri/card0
ENV
	if [ -x /usr/bin/kwin_wayland ]; then
		install -m 0755 /usr/bin/kwin_wayland \
			/usr/local/lib/a733-pvr/kwin_wayland.new
		mv /usr/local/lib/a733-pvr/kwin_wayland.new \
			/usr/local/lib/a733-pvr/kwin_wayland
		ln -sfn /usr/local/lib/a733-pvr/kwin_wayland \
			/usr/local/bin/kwin_wayland
	fi
	cat > /etc/X11/xorg.conf.d/20-a733-display.conf <<'ENV'
Section "Device"
    Identifier "A733 HDMI Display"
    Driver "modesetting"
    Option "kmsdev" "/dev/dri/card0"
    Option "PrimaryGPU" "true"
EndSection
ENV
	rm -f /etc/systemd/system/sddm.service.d/90-a733-pvr.conf
	systemctl daemon-reload 2>/dev/null || true
}

disable()
{
	rm -f /etc/modules-load.d/a733-pvr.conf \
		/etc/environment.d/90-a733-pvr.conf \
		/etc/profile.d/a733-pvr.sh \
		/etc/X11/xorg.conf.d/20-a733-display.conf \
		/etc/systemd/system/sddm.service.d/90-a733-pvr.conf
	if [ "$(readlink /usr/local/bin/kwin_wayland 2>/dev/null || true)" = \
		/usr/local/lib/a733-pvr/kwin_wayland ]; then
		rm -f /usr/local/bin/kwin_wayland
	fi
	rm -f /usr/local/lib/a733-pvr/kwin_wayland
	rmdir /usr/local/lib/a733-pvr 2>/dev/null || true
	systemctl daemon-reload 2>/dev/null || true
}

status()
{
	modinfo pvrsrvkm | grep -E '^(filename|version|vermagic):' || true
	lsmod | grep '^pvrsrvkm ' || true
	ls -l /dev/dri 2>/dev/null || true
}

case "\${1:-}" in
	enable) enable ;;
	disable) disable ;;
	status) status ;;
	*) echo "Usage: \$0 {enable|disable|status}" >&2; exit 2 ;;
esac
EOF
chmod 0755 "$package/usr/local/sbin/a733-pvr-control"

cat > "$package/DEBIAN/control" <<EOF
Package: a733-pvr-gpu
Version: 24.2.6603887+gpu4
Section: non-free/kernel
Priority: optional
Architecture: arm64
Maintainer: radxa-a7z-display project
Depends: linux-image-5.15.147-21.1-a733 (= 5.15.147-21.1+display2), kwin-wayland, libxcb-dri2-0, libdrm2, libx11-6, libx11-xcb1, libxcb1, libxcb-dri3-0, libxcb-present0, libxcb-randr0, libxcb-sync1, libxcb-xfixes0, libxshmfence1, libexpat1, libstdc++6, libudev1, zlib1g
Description: A733 PowerVR BXM GPU activation for the verified A7Z kernel
 Installs pvrsrvkm, BVNC 36.56.104.183 firmware, and an isolated vendor
 userspace. It intentionally does not replace Xorg, modesetting, or glamor.
EOF
cat > "$package/DEBIAN/postinst" <<'EOF'
#!/bin/sh
set -e
depmod 5.15.147-21.1-a733
/usr/local/sbin/a733-pvr-control enable
EOF
cat > "$package/DEBIAN/prerm" <<'EOF'
#!/bin/sh
set -e
if [ "$1" = remove ] || [ "$1" = deconfigure ]; then
	/usr/local/sbin/a733-pvr-control disable
fi
EOF
cat > "$package/DEBIAN/postrm" <<'EOF'
#!/bin/sh
set -e
if [ "$1" = remove ] || [ "$1" = purge ]; then
	depmod 5.15.147-21.1-a733 || true
fi
EOF
chmod 0755 "$package/DEBIAN/postinst" "$package/DEBIAN/prerm" \
	"$package/DEBIAN/postrm"

sha256sum "$module" "$userspace_deb" \
	> "$package/usr/share/doc/a733-pvr-gpu/SHA256SUMS.vendor"
find "$package" -path '*/usr/bin/Xorg' -o \
	-path '*/usr/lib/xorg/modules/drivers/modesetting_drv.so' -o \
	-path '*/usr/lib/xorg/modules/libglamoregl.so' | grep -q . && {
	echo "Unsafe Xorg payload entered the package." >&2
	exit 1
}

mkdir -p "$(dirname -- "$output")"
dpkg-deb --build --root-owner-group "$package" "$output"
