#!/usr/bin/env bash

# python path add src/ in CWD
export PYTHONPATH=$PYTHONPATH:$(pwd)/src/

python3 ./src/generate/simple.py