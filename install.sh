#!/usr/bin/env bash
# Copy the two reviewed skills; no network, authentication, or GPU side effects.
set -euo pipefail
ROOT=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
DEST="${1:-${HOME}/.agents/skills}"
if (( $# > 1 )); then
  echo 'Usage: bash install.sh [skills-directory]' >&2
  exit 2
fi
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
python3 - "${ROOT}" "${DEST}" <<'PY'
import shutil
import sys
from pathlib import Path
root, dest = map(Path, sys.argv[1:])
dest.mkdir(parents=True, exist_ok=True)
for name in ('nano4-workflow', 'qwen-sglang-mtp'):
    shutil.copytree(root / 'skills' / name, dest / name,
                    ignore=shutil.ignore_patterns('__pycache__', '*.pyc', '*.pyo'))
    print(f'Installed: {dest / name}')
PY
echo 'Restart Codex if the skills do not appear. No Nano4 jobs were submitted.'
