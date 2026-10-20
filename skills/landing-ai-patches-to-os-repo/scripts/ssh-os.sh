#!/bin/sh
# SSH to GoldEngle os repo host.
# Password: GOLDENGLE_OS_PASS from the current session (user provides it in chat).
# Do not store secrets in this skill directory.
# Usage: GOLDENGLE_OS_PASS='...' ssh-os.sh 'remote command'
set -eu

HOST="${GOLDENGLE_OS_HOST:-172.18.60.122}"
USER="${GOLDENGLE_OS_USER:-adil}"
if [ "${1:-}" = "" ]; then
  echo "usage: GOLDENGLE_OS_PASS=... $0 'remote-command'" >&2
  exit 2
fi

PASS="${GOLDENGLE_OS_PASS:-}"
if [ -z "$PASS" ]; then
  echo "ssh-os.sh: GOLDENGLE_OS_PASS is empty. Ask the user to send the SSH password in this chat; do not write it into the skill directory." >&2
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
