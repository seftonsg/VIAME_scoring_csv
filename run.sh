#!/bin/bash
ARGS=""
ARGS="$ARGS -truth=tracks/truths/TRUTHS_5img.csv" 
ARGS="$ARGS -computed=tracks/5img/12c_tracks_CRNN_v0915_5img_0.002.csv" 
ARGS="$ARGS -images=5images.txt" 
ARGS="$ARGS -output=12c_CRNN_0.002"

echo "python expander.py $ARGS" >> cmds.txt

