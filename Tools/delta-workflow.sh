#!/usr/bin/env bash
# Shared forwarding logic for the themes repository's Bash entry points.
set -euo pipefail
THEMES_ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)
mode=${RIVE_WORKFLOW_MODE:?Missing workflow mode}
delta=${DELTA_DIR:-$(dirname "$THEMES_ROOT")/Delta}
forwarded=(); offline=false; help_requested=false
while [[ $# -gt 0 ]]; do
    case "$1" in
        --delta)
            [[ $# -ge 2 && -n "$2" ]] || { printf 'Error: --delta needs a path.\n' >&2; exit 1; }
            delta=$2; shift 2 ;;
        --help|-h) help_requested=true; forwarded+=("$1"); shift ;;
        --offline) offline=true; forwarded+=("$1"); shift ;;
        *) forwarded+=("$1"); shift ;;
    esac
done
case "$delta" in "~") delta=$HOME ;; "~/"*) delta="$HOME/${delta#\~/}" ;; esac
if [[ "$help_requested" == true && ! -d "$delta" ]]; then
    entry=setup; if [[ "$mode" == import ]]; then entry=import_simulator; fi
    printf "Usage: Tools/%s.sh [--delta PATH] [Delta workflow options]\n" "$entry"
    printf "Uses the sibling Delta rive checkout. Setup can clone it when missing.\n"
    exit 0
fi
if [[ "$mode" == setup && ! -e "$delta" ]]; then
    [[ "$offline" == false ]] || { printf 'Error: Delta is missing; clone dskuza/Delta on rive first.\n' >&2; exit 1; }
    git clone --branch rive git@github.com:dskuza/Delta.git "$delta"
fi
case "$mode" in setup) command=setup-rive.sh ;; import) command=import-rive-themes.sh ;; *) exit 1 ;; esac
command="$delta/Scripts/$command"
[[ -f "$command" ]] || { printf 'Error: %s not found; check out Delta’s rive branch or pass --delta PATH.\n' "$command" >&2; exit 1; }
# The conditional expansion keeps an empty array compatible with Bash 3.2 + nounset.
exec /bin/bash "$command" ${forwarded[@]+"${forwarded[@]}"} --themes "$THEMES_ROOT"
