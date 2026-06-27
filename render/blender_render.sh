#!/usr/bin/env bash
# Headless Blender render with a retry guard.
#
# Blender 5.0's bundled OpenColorIO has a ~15% flaky segfault (sscanf in the AgX view-transform
# LUT) on this machine's locale. Each invocation is a fresh process, so retrying clears it.
# LC_ALL=C reduces the rate further.
#
# Usage: blender_render.sh <script.py> [args after -- to the script ...]
set -u
BLENDER="${BLENDER:-/opt/blender-5.0.1-linux-x64/blender}"
ATTEMPTS="${ATTEMPTS:-5}"
script="$1"; shift

for i in $(seq 1 "$ATTEMPTS"); do
    LC_ALL=C "$BLENDER" -b --factory-startup -P "$script" -- "$@"
    rc=$?
    [ "$rc" -eq 0 ] && exit 0
    echo "  ↻ blender exited $rc on $(basename "$script") (attempt $i/$ATTEMPTS) — retrying" >&2
done
echo "  ✗ blender failed after $ATTEMPTS attempts: $script" >&2
exit 1
