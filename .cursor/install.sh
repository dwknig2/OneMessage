#!/usr/bin/env bash
# Idempotent environment bootstrap for the Unified Jess Timeline (OneMessage) pipeline.
# Safe to run repeatedly: installs the system venv package, then (re)installs the
# Python dependencies into a project-local virtual environment at .venv.
set -euo pipefail

cd "$(dirname "$0")/.."

# ensurepip / venv support is not present in the base image by default.
if ! python3 -c "import ensurepip" >/dev/null 2>&1; then
  sudo apt-get update -qq
  sudo apt-get install -y --no-install-recommends python3-venv
fi

# Create the virtual environment only if it does not already exist.
if [ ! -x .venv/bin/python ]; then
  python3 -m venv .venv
fi

.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt

echo "OneMessage environment ready. Activate with: source .venv/bin/activate"
