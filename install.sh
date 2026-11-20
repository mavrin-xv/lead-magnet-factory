#!/usr/bin/env bash
# lead-magnet-factory installer.
#
#   ./install.sh             skills into ~/.claude/skills (all projects)
#   ./install.sh --project   skills into ./.claude/skills (this project only)
#                            and the format templates into ./magnets/_templates
#
# Each installed skill gets a copy of templates/, so its template paths resolve.
# Existing skills with the same name are backed up to <name>.bak.<timestamp> first.
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
DEST="$HOME/.claude"; PROJECT=0
while [ $# -gt 0 ]; do
  case "$1" in
    --project) DEST="$(pwd)/.claude"; PROJECT=1 ;;
    -h|--help) sed -n 2,9p "$0"; exit 0 ;;
    *) echo "unknown option: $1" >&2; exit 1 ;;
  esac
  shift
done

mkdir -p "$DEST/skills"
for s in "$HERE"/skills/*/; do
  name="$(basename "$s")"
  if [ -d "$DEST/skills/$name" ]; then
    mv "$DEST/skills/$name" "$DEST/skills/$name.bak.$(date +%s)"
    echo "backed up existing $name"
  fi
  cp -R "$s" "$DEST/skills/$name"
  mkdir -p "$DEST/skills/$name/templates"
  cp -n "$HERE"/templates/* "$DEST/skills/$name/templates/" 2>/dev/null || true
  find "$DEST/skills/$name" -name __pycache__ -type d -prune -exec rm -r {} + 2>/dev/null || true
  echo "installed skill $name"
done

if [ "$PROJECT" = 1 ]; then
  mkdir -p "$(pwd)/magnets/_templates"
  cp -n "$HERE"/templates/* "$(pwd)/magnets/_templates/" 2>/dev/null || true
  echo "templates copied to ./magnets/_templates (existing files kept)"
fi

command -v python3 >/dev/null || command -v py >/dev/null || \
  echo "note: the scripts need Python 3.8+ (standard library only)."
echo "done. Try: \"turn this article into a lead magnet\""
