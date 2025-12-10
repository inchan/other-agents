#!/usr/bin/env bash
set -euo pipefail

# Usage: ./scripts/install_deps.sh "[dev]"
# The extras argument is optional; defaults to dev deps for CI workflows.
EXTRAS=${1:-"[dev]"}
PYTHON=${PYTHON:-python}
MAX_RETRIES=${MAX_RETRIES:-3}
DELAY_SECONDS=${DELAY_SECONDS:-5}

upgrade_and_install() {
  ${PYTHON} -m pip install --upgrade pip
  ${PYTHON} -m pip install -e ".${EXTRAS}"
}

for attempt in $(seq 1 ${MAX_RETRIES}); do
  if upgrade_and_install; then
    exit 0
  fi

  echo "Dependency installation failed (attempt ${attempt}/${MAX_RETRIES}). Retrying in ${DELAY_SECONDS}s..." >&2
  sleep ${DELAY_SECONDS}
done

echo "Dependency installation failed after ${MAX_RETRIES} attempts." >&2
exit 1
