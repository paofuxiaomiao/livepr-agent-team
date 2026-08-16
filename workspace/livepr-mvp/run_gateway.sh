#!/usr/bin/env bash
set -euo pipefail

project_dir="$(cd "$(dirname "$0")" && pwd)"
cd "$project_dir"
exec python3 tools/mock_event_gateway.py --host 0.0.0.0 --port 18090
