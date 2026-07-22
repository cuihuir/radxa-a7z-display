#!/bin/sh

set -eu

PATH=/usr/sbin:/usr/bin:/sbin:/bin:$PATH
export PATH

for command in truncate mke2fs debugfs e2fsck; do
	command -v "$command" >/dev/null 2>&1 || {
		echo "Missing required command: $command" >&2
		exit 1
	}
done

workdir=$(mktemp -d)

cleanup()
{
	rm -rf "$workdir"
}
trap cleanup EXIT INT TERM

image=$workdir/recovery-fsck.img
truncate -s 64M "$image"
mke2fs -q -t ext4 -F "$image"

e2fsck -fn "$image" >/dev/null 2>&1
debugfs -w -R 'set_bg 0 free_blocks_count 1' "$image" >/dev/null 2>&1

set +e
e2fsck -p "$image" > "$workdir/repair.log" 2>&1
repair_status=$?
set -e

[ "$repair_status" -eq 1 ] || {
	cat "$workdir/repair.log" >&2
	echo "Expected e2fsck repair status 1, got $repair_status." >&2
	exit 1
}

grep -Fq 'FIXED' "$workdir/repair.log" || {
	cat "$workdir/repair.log" >&2
	echo "e2fsck did not report a repaired inconsistency." >&2
	exit 1
}

e2fsck -fn "$image" > "$workdir/post-check.log" 2>&1 || {
	cat "$workdir/post-check.log" >&2
	echo "The repaired image did not pass the read-only follow-up check." >&2
	exit 1
}

echo "A733 recovery fsck image test passed: repair status 1, follow-up status 0."
