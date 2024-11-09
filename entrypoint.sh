#!/bin/sh -l

# setting up correct python path to find fabric_agent_action module
export PYTHONPATH="/app:$PYTHONPATH"

# copying fabric configuration to temporary $HOME set by github workflow
if [ ! -z "$GITHUB_WORKSPACE" ]; then
    echo "Detected GitHub runner"
    cp -r /root/.config $HOME/
fi

echo "[start] app.py..."

if [ "$#" -lt 2 ]; then
    ARGS="-h"
else
    ARGS="-f /app/fabric -i $1 -o $2"
fi

if [ "$3" = 'true' ]; then
    ARGS="$ARGS --verbose"
fi

if [ "$4" = 'true' ]; then
    ARGS="$ARGS --debug"
fi

/usr/local/bin/python /app/fabric_agent_action/app.py $ARGS