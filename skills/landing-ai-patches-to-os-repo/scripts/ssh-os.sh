#!/bin/sh
# SSH to GoldEngle os repo host as adil (password auth).
# Usage: ssh-os.sh 'remote command'
#        ssh-os.sh                 # interactive not supported; require a command
set -eu

HOST="${GOLDENGLE_OS_HOST:-172.18.60.122}"
USER="${GOLDENGLE_OS_USER:-adil}"
PASS="${GOLDENGLE_OS_PASS:-zxr19840223}"

if [ "${1:-}" = "" ]; then
  echo "usage: $0 'remote-command'" >&2
  exit 2
fi

ASK="$(mktemp "${TMPDIR:-/tmp}/askpass-os.XXXXXX")"
trap 'rm -f "$ASK"' EXIT INT TERM
umask 077
printf '%s\n' '#!/bin/sh' "echo '$PASS'" > "$ASK"
chmod 700 "$ASK"

export SSH_ASKPASS="$ASK" SSH_ASKPASS_REQUIRE=force DISPLAY="${DISPLAY:-:0}"
# Password only; do not let a local key confuse the server.
exec setsid ssh \
  -o StrictHostKeyChecking=accept-new \
  -o PreferredAuthentications=password \
  -o PubkeyAuthentication=no \
  "${USER}@${HOST}" \
  "$@"
