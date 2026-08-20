#!/bin/bash
# Kill the running fraud_pipeline serve process and restart it so the
# latest fraud_pipeline.py is picked up by the next Quick Run trigger.
set -u
cd /root/code/prefect

# Kill any prior serve loop (matches on the module path).
pkill -f 'fraud_pipeline' 2>/dev/null || true
sleep 2

# Relaunch in the background. The serve() call upserts the deployment
# named `fraud-pipeline` and blocks as a worker loop.
nohup python3 /root/code/prefect/fraud_pipeline.py \
  > /var/log/prefect-serve.log 2>&1 &

echo "Redeployed fraud-pipeline. Check /var/log/prefect-serve.log"