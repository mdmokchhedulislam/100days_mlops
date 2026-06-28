#!/bin/bash
# Materialize the fraud-detection feature views into the online
# store. Feast's materialize-incremental command writes every
# event whose timestamp is between the view's last-materialized
# watermark (or the TTL-based fallback) and the given end date.
#
# Run from /root/code/fraud-detection/feature_repo/.
set -euo pipefail

cd "$(dirname "$0")"

END_DATE="2025-12-31T23:59:59"

feast materialize-incremental "$END_DATE"