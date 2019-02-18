#!/usr/bin/env bash

if [ "$1" == "" ]; then
    TTY=/dev/ttyUSB0
else
    TTY="$1"
fi
set -x
ampy --port ${TTY} rmdir /scron
ampy --port ${TTY} put ./build/scron/ /scron/

