#!/bin/sh

set -eu

usage()
{
	cat >&2 <<'EOF'
Usage: a733_desktop_soak_test.sh PROFILE [--duration SECONDS] [--interval SECONDS] [--output DIR]

Profiles:
  smoke       10 minutes, samples every minute
  regression  1 hour, samples every 5 minutes
  soak        8 hours, samples every 5 minutes
EOF
	exit 2
}

[ "$#" -ge 1 ] || usage
profile=$1
shift

case "$profile" in
	smoke)
	duration=600
	interval=60
	;;
	regression)
	duration=3600
	interval=300
	;;
	soak)
	duration=28800
	interval=300
	;;
	*) usage ;;
esac

output=
while [ "$#" -gt 0 ]; do
	case "$1" in
		--duration)
		[ "$#" -ge 2 ] || usage
		duration=$2
		shift 2
		;;
		--interval)
		[ "$#" -ge 2 ] || usage
		interval=$2
		shift 2
		;;
		--output)
		[ "$#" -ge 2 ] || usage
		output=$2
		shift 2
		;;
		*) usage ;;
	esac
done

case "$duration:$interval" in
	*[!0-9:]*|0:*|*:0) usage ;;
esac

grep -Fq 'radxa,cubie-a7z' /proc/device-tree/compatible

timestamp=$(date -u +%Y%m%dT%H%M%SZ)
output=${output:-a733-${profile}-${timestamp}}
mkdir -p "$output/samples"
output=$(readlink -f "$output")
start_epoch=$(date +%s)
end_epoch=$((start_epoch + duration))

run_optional()
{
	name=$1
	shift
	if command -v "$1" >/dev/null 2>&1; then
		"$@" > "$name" 2>&1 || true
	else
		printf 'command unavailable: %s\n' "$1" > "$name"
	fi
}

collect_sample()
{
	sequence=$1
	sample=$output/samples/$(printf '%04d' "$sequence")
	mkdir -p "$sample"
	date --iso-8601=seconds > "$sample/time.txt"
	cat /proc/uptime > "$sample/uptime.txt"
	cat /proc/meminfo > "$sample/meminfo.txt"
	ps -eo pid,ppid,rss,vsz,etimes,comm,args > "$sample/processes.txt"
	find /sys/class/drm -maxdepth 2 -type f \
		\( -name status -o -name enabled -o -name modes -o -name mode \) \
		-print -exec cat {} \; > "$sample/drm.txt" 2>&1 || true
	find /sys/class/thermal -maxdepth 2 -type f \
		\( -name type -o -name temp \) -print -exec cat {} \; \
		> "$sample/thermal.txt" 2>&1 || true
	find /sys/class/devfreq -maxdepth 2 -type f \
		\( -name name -o -name cur_freq -o -name min_freq -o -name max_freq \
		-o -name governor -o -name available_frequencies \) \
		-print -exec cat {} \; > "$sample/devfreq.txt" 2>&1 || true
	for process in kwin_wayland Xwayland; do
		for pid in $(pidof "$process" 2>/dev/null || true); do
			ls -l "/proc/$pid/fd" > "$sample/${process}-${pid}-fds.txt" 2>&1 || true
			tr '\0' '\n' < "/proc/$pid/environ" \
				> "$sample/${process}-${pid}-environment.txt" 2>&1 || true
		done
	done
	(
		cd "$sample"
		run_optional pvr-status.txt pvrsrvctl --status
		run_optional vulkan-summary.txt vulkaninfo --summary
		run_optional opencl-summary.txt clinfo --list
	)
}

cat > "$output/metadata.txt" <<EOF
profile=$profile
duration_seconds=$duration
interval_seconds=$interval
started=$(date --iso-8601=seconds)
hostname=$(hostname)
kernel=$(uname -r)
architecture=$(dpkg --print-architecture)
EOF

dpkg-query -W \
	linux-image-5.15.147-21.1-a733 a733-pvr-gpu a733-pvr-xwayland \
	kwin-common kwin-wayland xwayland > "$output/packages.txt" 2>&1 || true
cp /boot/extlinux/extlinux.conf "$output/extlinux.conf" 2>/dev/null || true
journalctl --show-cursor -n 0 > "$output/journal-start.txt" 2>&1 || true

sequence=0
while :; do
	collect_sample "$sequence"
	sequence=$((sequence + 1))
	now=$(date +%s)
	[ "$now" -ge "$end_epoch" ] && break
	remaining=$((end_epoch - now))
	if [ "$remaining" -lt "$interval" ]; then
		sleep "$remaining"
	else
		sleep "$interval"
	fi
done

cursor=$(sed -n 's/^-- cursor: //p' "$output/journal-start.txt" | tail -1)
if [ -n "$cursor" ]; then
	journalctl --after-cursor "$cursor" --no-pager > "$output/journal.txt" 2>&1 || true
else
	journalctl --since "@$start_epoch" --no-pager > "$output/journal.txt" 2>&1 || true
fi

grep -Ei 'pvrsrvkm|pvr|drm|hdmi|hwr|wgp|trp|gpu fault|reset|oom|segfault' \
	"$output/journal.txt" > "$output/graphics-events.txt" || true

cat >> "$output/metadata.txt" <<EOF
finished=$(date --iso-8601=seconds)
samples=$sequence
EOF

tar -C "$(dirname "$output")" -czf "$output.tar.gz" "$(basename "$output")"
printf 'A733 %s test complete: %s.tar.gz\n' "$profile" "$output"
