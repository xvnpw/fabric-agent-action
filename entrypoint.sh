#!/bin/sh -l

export PYTHONPATH="/app:$PYTHONPATH"

echo "[start] app.py..."

/usr/local/bin/python /app/fabric_agent_action/app.py -f /app/fabric -i $1 -o $2