#!/bin/sh -l

# setting up correct python path to find fabric_agent_action module
export PYTHONPATH="/app:$PYTHONPATH"

# copying fabric configuration to temporary $HOME set by github workflow
if [ -n "$GITHUB_WORKSPACE" ]; then
    echo "Detected GitHub runner"
    cp -r /root/.config $HOME/
fi

if [ -n "$INPUT_FILE" -a -n "$OUTPUT_FILE" ]; then
    ARGS="-f /app/fabric -i $INPUT_FILE -o $OUTPUT_FILE"
else
    ARGS="-h"
fi

if [ "$VERBOSE" = 'true' ]; then
    ARGS="$ARGS --verbose"
fi

if [ "$DEBUG" = 'true' ]; then
    ARGS="$ARGS --debug"
fi

echo "[start] app.py..."

echo "[debug] $ARGS"

/usr/local/bin/python /app/fabric_agent_action/app.py $ARGS