#!/usr/bin/env bash
# Sync official lark-* skills: ~/.agents/skills -> ~/.cursor/skills
# Does not touch cursor-only names (e.g. lark-whiteboard-cli).
set -euo pipefail

SRC="${HOME}/.agents/skills"
DST="${HOME}/.cursor/skills"

if [[ ! -d "$SRC" ]]; then
  echo "lark-cli-skills-sync: missing source $SRC" >&2
  exit 1
fi
if [[ ! -d "$DST" ]]; then
  echo "lark-cli-skills-sync: missing dest $DST" >&2
  exit 1
fi

if ! command -v rsync >/dev/null 2>&1; then
  echo "lark-cli-skills-sync: rsync not found" >&2
  exit 1
fi

shopt -s nullglob
synced=()
for src in "$SRC"/lark*; do
  [[ -d "$src" ]] || continue
  name=$(basename "$src")
  rsync -a --delete "$src/" "$DST/$name/"
  synced+=("$name")
done

if [[ ${#synced[@]} -eq 0 ]]; then
  echo "lark-cli-skills-sync: no lark* dirs in $SRC" >&2
  exit 1
fi

printf 'lark-cli-skills-sync: synced %d skill(s) %s -> %s\n' \
  "${#synced[@]}" "$SRC" "$DST"
printf '  %s\n' "${synced[@]}"
