#!/usr/bin/env bash
#
# run_tests_esp.sh <action> <TTY>
#
# Actions:
#   upload
#   upload_combined
#   run

ACTION=$1
if [ "$2" != "" ]
then
    TTY=$2
else
  TTY=/dev/ttyUSB0
fi

if [ "${ACTION}" = "upload" ] || [ "${ACTION}" = "upload_combined" ]
then
    ./compile.sh

    ampy --port ${TTY} rmdir scron &>/dev/null
    ampy --port ${TTY} rmdir lib &>/dev/null
    ampy --port ${TTY} rmdir tests &>/dev/null

    ampy --port ${TTY} mkdir scron
    ampy --port ${TTY} mkdir tests

    for file in ./tests/upload/*.py
    do
        echo Upload $file
        ampy --port ${TTY} put $file
    done

    for file in ./build/scron/*.mpy
    do
        echo Upload $file ${file/.\/build/}
        ampy --port ${TTY} put $file ${file/.\/build/}
    done

    for file in ./tests/*.py
    do
        echo Upload $file ${file/./}
        ampy --port ${TTY} put $file ${file/./}
    done
fi

if [ "${ACTION}" = "upload_combined" ]
then
    echo Upload and replace ./build/scron/cweek.mpy /scron/week.mpy
    ampy --port ${TTY} put ./build/scron/cweek.mpy /scron/week.mpy
    ampy --port ${TTY} rm /scron/cweek.mpy
    ampy --port ${TTY} rm /scron/scount.mpy
    ampy --port ${TTY} rm /scron/base.mpy
fi

if [ "${ACTION}" = "run" ]
then
    DEFICE_TTY=$TTY python ./test_esp.py
fi
