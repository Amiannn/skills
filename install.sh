#!/usr/bin/env bash
# Copy the two reviewed skills; no network, authentication, or GPU side effects.
set -euo pipefail
ROOT=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
TARGET=codex
DEST=''
usage() {
  echo 'Usage: bash install.sh [--target codex|claude] [skills-directory]'
}
while (( $# )); do
  case "$1" in
    --target)
      if (( $# < 2 )); then usage >&2; exit 2; fi
      TARGET="$2"
      shift 2
      ;;
    -h|--help) usage; exit 0 ;;
    -*) usage >&2; exit 2 ;;
    *)
      if [[ -n "$DEST" || -z "$1" ]]; then usage >&2; exit 2; fi
      DEST="$1"
      shift
      ;;
  esac
done
case "$TARGET" in
  codex) DEST="${DEST:-${HOME}/.agents/skills}"; CLIENT='Codex' ;;
  claude) DEST="${DEST:-${HOME}/.claude/skills}"; CLIENT='Claude Code' ;;
  *) usage >&2; exit 2 ;;
esac
SKILLS=(nano4-workflow qwen-sglang-mtp)
for skill in "${SKILLS[@]}"; do
  test -f "${ROOT}/skills/${skill}/SKILL.md"
  if [[ -e "${DEST}/${skill}" || -L "${DEST}/${skill}" ]]; then
    echo "Refusing to overwrite existing skill: ${DEST}/${skill}" >&2
    exit 1
  fi
done
# Use copytree with its default dirs_exist_ok=False to also reject destination
# collisions occurring after the shell preflight. Filter local Python caches.
python3 - "${ROOT}" "${DEST}" "${TARGET}" <<'PY'
import shutil
import sys
from pathlib import Path
root, dest = map(Path, sys.argv[1:3])
target = sys.argv[3]
ignored = ['__pycache__', '*.pyc', '*.pyo']
if target == 'claude':
    # These skills' agents/ directories contain only Codex UI metadata.
    ignored.append('agents')
dest.mkdir(parents=True, exist_ok=True)
for name in ('nano4-workflow', 'qwen-sglang-mtp'):
    shutil.copytree(root / 'skills' / name, dest / name,
                    ignore=shutil.ignore_patterns(*ignored))
    print(f'Installed: {dest / name}')
PY
echo "Restart ${CLIENT} if the skills do not appear. No Nano4 jobs were submitted."
