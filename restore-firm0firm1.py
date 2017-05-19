#!/usr/bin/env python3

import os
import sys
import time


def doexit(msg, errcode=0):
    print(msg)
    input('Press Enter to continue...')
    sys.exit(errcode)


def doexit(msg, errcode=0):
    print(msg)
    input('Press Enter to continue...')
    sys.exit(errcode)


if not os.path.isfile('NAND-patched.bin'):
    doexit('NAND-patched.bin not found.', errcode=1)

if not os.path.isfile('firm0firm1.bak'):
    doexit('firm0firm1.bak was not found.', errcode=1)

if os.path.isfile('NAND-unpatched.bin'):
    doexit('NAND-unpatched.bin was found.\n'
           'In order to prevent writing a good backup with a bad one, the '
           'install has stopped. Please move or delete the old file if you '
           'are sure you want to continue.', errcode=1)

readsize = 0x100000  # must be divisible by 0x3AF00000 and 0x4D800000

print('Trying to open NAND-patched.bin...')
with open('NAND-patched.bin', 'rb+') as nand:
    print('Restoring firm0firm1.back.')
    nand.seek(0xB130000)
    with open('firm0firm1.bak', 'rb') as f:
        firm_final = f.read(0x800000)
    start_time = time.time()
    for curr in range(0x800000 // readsize):
        print('Writing {:06X} ({:>5.1f}%)'.format((curr + 1) * readsize,
              (((curr + 1) * readsize) / 0x800000) * 100), end='\r')
        nand.write(bytes(firm_final[curr * readsize:(curr + 1) * readsize]))

os.rename('NAND-patched.bin', 'NAND-unpatched.bin')

doexit('\nWriting finished in {:>.2f} seconds.'.format(
        time.time() - start_time))
