# Usage:
# DEVICE_TTY=<micropython_TTY> python ./test_esp.py <TEST_FILTER_STRING>

import sys
import serial
import time
import glob
import os

try:
    TEST_FILTER_STRING = sys.argv[1]
except:
    TEST_FILTER_STRING = None

if 'DEVICE_TTY' in os.environ:
    TTY = os.environ['DEVICE_TTY']
else:
    TTY = '/dev/ttyUSB0'

ser = serial.Serial(TTY, 115200)


def clean_buffer():
    ser.reset_input_buffer()
    ser.reset_output_buffer()


def reboot_machine():
    clean_buffer()
    ser.write(b'import machine\r')
    ser.write(b'machine.reset()\r')


def wait_for_reboot():
    counter = 0
    while True:
        if counter >= 2:
            time.sleep(1)
            break
        data = ser.readline()
        if b'REBOOT_END' in data:
            counter += 1
        if b'Type "help()" for more information.' in data:
            counter += 1


print('Wait for reboot end...')
reboot_machine()
wait_for_reboot()

print('Run tests...')
all_test_files = glob.glob('tests/*.py')


def normailse(in_txt):
    out = in_txt.replace(b'\n', b'')
    out = out.replace(b'\r', b'')
    out = out.replace(b' ', b'')
    return out


for test_file in all_test_files:
    if TEST_FILTER_STRING is not None and TEST_FILTER_STRING not in test_file:
        continue
    print('Test: %s -- ' % test_file, end="")
    test_file_txt_path = test_file[:-2] + 'txt'
    try:
        test_file_txt = open(test_file_txt_path, 'rb').read()
    except FileNotFoundError:
        test_file_txt = b''
    try:
        test_file_wait = float(open(test_file[:-2] + 'wait').read().strip())
    except FileNotFoundError:
        test_file_wait = 0.1
    reboot_machine()
    wait_for_reboot()
    clean_buffer()
    ser.write(b'from %s import *\r' % test_file.replace('/', '.')[:-3].encode('ascii'))
    time.sleep(test_file_wait)
    test_out = ser.read_all()
    if normailse(test_out) != normailse(test_file_txt):
        test_out_path = test_file[:-2] + 'txt_test'
        with open(test_out_path, 'wb') as f:
            f.write(test_out)
        print('FAIL')
        print('check command: diff -w %s %s' % (test_file_txt_path, test_out_path))
    else:
        print('PASS')
