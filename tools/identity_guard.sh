#!/usr/bin/env bash
# Hard gate run before any push, pull request or merge on this repository.
# Exits non-zero unless the GitHub identity is the automation account
# bubbadog-claude AND it has no admin rights on the repository. Callers must
# use it as a gate (`tools/identity_guard.sh || exit 1`), never just print it.
# Added 2026-11-13 after a hand session pushed a branch with the owner's
# credentials because an identity check printed a value but did not stop.
set -euo pipefail
REPO="${1:-bubbadog/project-2025-tracker}"
EXPECTED="bubbadog-claude"
login="$(gh api user --jq .login 2>/dev/null || true)"
admin="$(gh api "repos/${REPO}" --jq .permissions.admin 2>/dev/null || true)"
if [ "$login" != "$EXPECTED" ]; then
  echo "IDENTITY GUARD: GitHub identity is '${login:-unknown}', not ${EXPECTED}. Push nothing." >&2
  exit 3
fi
if [ "$admin" != "false" ]; then
  echo "IDENTITY GUARD: ${login} reports admin='${admin:-unknown}' on ${REPO}; expected false. Push nothing." >&2
  exit 4
fi
echo "IDENTITY GUARD: ok (${login}, no admin)"
