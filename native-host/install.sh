#!/usr/bin/env bash
# 사용법: ./install.sh --browser firefox
#         ./install.sh --browser chrome --extension-id <ID>
set -euo pipefail
python3 "$(dirname "$0")/install.py" "$@"
