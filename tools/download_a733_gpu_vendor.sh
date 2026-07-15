#!/bin/sh

set -eu

if [ "$#" -ne 1 ]; then
	echo "Usage: $0 OUTPUT_DIR" >&2
	exit 2
fi

output_dir=$1
base=https://radxa-repo.github.io/a733-bullseye/pool/main
dkms=img-bxm-dkms_0.1.0-3_all.deb
userspace=xserver-xorg-img-bxm_1.21.1-2_arm64.deb

mkdir -p "$output_dir"
curl -fL --retry 5 -o "$output_dir/$dkms" \
	"$base/a/aw-drivers-dkms/$dkms"
curl -fL --retry 5 -o "$output_dir/$userspace" \
	"$base/x/xserver-xorg-img-bxm-1.21.1-2.deb/$userspace"

cat > "$output_dir/SHA256SUMS" <<EOF
923ed2039cc97e9c36b147493345f2d048bdf8ebe828444195bf84c476dd1b89  $dkms
c8e606db1abdea40a5b97f7905ea86901b50c5fe1b76a55356ab70dde3304c3a  $userspace
EOF

(cd "$output_dir" && sha256sum -c SHA256SUMS)

