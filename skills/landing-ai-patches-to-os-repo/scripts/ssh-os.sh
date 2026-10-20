#!/bin/sh
# SSH to GoldEngle os repo host. Password is never stored in this skill directory.
# Provide GOLDENGLE_OS_PASS, or a 0600 file GOLDENGLE_OS_PASS_FILE
# (default: ~/.config/goldengle-os/ssh-password).
# Usage: ssh-os.sh 'remote command'
set -eu

HOST="${GOLDENGLE_OS_HOST:-172.18.60.122}"
USER="${GOLDENGLE_OS_USER:-adil}"
PASS_FILE="${GOLDENGLE_OS_PASS_FILE:-${HOME}/.config/goldengle-os/ssh-password}"

if [ "${1:-}" = "" ]; then
  echo "usage: $0 'remote-command'" >&2
  exit 2
fi

PASS="${GOLDENGLE_OS_PASS:-}"
if [ -z "$PASS" ] && [ -f "$PASS_FILE" ]; then
  PASS="$(cat "$PASS_FILE")"
fi
if [ -z "$PASS" ]; then
  echo "ssh-os.sh: no password. Set GOLDENGLE_OS_PASS or write one line to $PASS_FILE (chmod 600). Do not put secrets under ~/.cursor/skills/landing-ai-patches-to-os-repo/" >&2
  exit 1
fi

ASK="$(mktemp "${TMPDIR:-/tmp}/askpass-os.XXXXXX")"
trap 'rm -f "$ASK"' EXIT INT TERM
umask 077
# Askpass reads env; do not embed the secret in the skill tree.
printf '%s\n' '#!/bin/sh' 'printf "%s\n" "$GOLDENGLE_OS_PASS"' > "$ASK"
chmod 700 "$ASK"

export GOLDENGLE_OS_PASS="$PASS"
export SSH_ASKPASS="$ASK" SSH_ASKPASS_REQUIRE=force DISPLAY="${DISPLAY:-:0}"
exec setsid ssh \
  -o StrictHostKeyChecking=accept-new \
  -o PreferredAuthentications=password \
  -o PubkeyAuthentication=no \
  "${USER}@${HOST}" \
  "$@"
