#!/usr/bin/env bash
set -euo pipefail

project_dir="$(cd "$(dirname "$0")" && pwd)"
cd "$project_dir"

python3 -m compileall -q livepr run_demo.py tools/mock_event_gateway.py
python3 -m unittest discover -s tests -v
python3 run_demo.py --scenario product_delay_rumor --approve --approved-by verified-demo \
  --output-dir evidence/verified-product-delay
python3 run_demo.py --scenario product_delay_rumor \
  --output-dir evidence/verified-awaiting-approval
python3 run_demo.py --scenario keynote_schedule_change --approve --approved-by verified-demo \
  --output-dir evidence/verified-keynote-change

echo "LivePR verification complete."
