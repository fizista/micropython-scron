#!/usr/bin/env bash

function title() {
    echo "##########################################################"
    echo "$1"
    echo "##########################################################"
}

title "Tests for Micropython unix port"
MICROPYPATH=$MICROPYPATH:./modules/:./mock/ micropython test_scron.py

title "Tests for Python 3"
PYTHONPATH=$PYTHONPATH:./modules/:./mock/ python3 test_scron.py


find . -name "__pycache__" -exec rm -r {} \; &> /dev/null
