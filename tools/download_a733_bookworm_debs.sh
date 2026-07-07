#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
dest="${1:-"$repo_root/sources/rsdk/debs/a733-bookworm"}"

mkdir -p "$dest"

urls=(
  "https://github.com/radxa-pkg/linux-a733/releases/download/5.15.147-21/linux-headers-5.15.147-21-a733_5.15.147-21_arm64.deb"
  "https://github.com/radxa-pkg/linux-a733/releases/download/5.15.147-21/linux-headers-radxa-a733_5.15.147-21_all.deb"
  "https://github.com/radxa-pkg/linux-a733/releases/download/5.15.147-21/linux-image-5.15.147-21-a733_5.15.147-21_arm64.deb"
  "https://github.com/radxa-pkg/linux-a733/releases/download/5.15.147-21/linux-image-radxa-a733_5.15.147-21_all.deb"
  "https://github.com/radxa-pkg/u-boot-aw2501/releases/download/2018.07-17/u-boot-aw2501_2018.07-17_all.deb"
  "https://github.com/radxa-pkg/u-boot-aw2501/releases/download/2018.07-17/u-boot-radxa-a733_2018.07-17_all.deb"
)

for url in "${urls[@]}"; do
  file="$dest/$(basename "$url")"
  if [[ -s "$file" ]]; then
    echo "exists: $file"
    continue
  fi
  echo "download: $url"
  curl -fL --connect-timeout 15 --max-time 180 --retry 3 --retry-delay 2 -o "$file" "$url"
done

echo "A733 Bookworm local deb cache: $dest"
