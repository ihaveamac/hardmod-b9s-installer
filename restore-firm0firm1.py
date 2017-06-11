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

use_separate = True  # use separate firm(0/1)_enc.bak
if os.path.isfile('firm0firm1.bak'):
    print('Using firm0firm1.bak.')
elif os.path.isfile('firm0_enc.bak') and os.path.isfile('firm1_enc.bak'):
    print('Using firm0_enc.bak and firm1_enc.bak')
    use_separate = True
else:
    doexit('FIRM backup was not found.\n'
           'This can be in a single "firm0firm1.bak" file, or\n'
           'two "firm0_enc.bak" and "firm1_enc.bak" files.', errcode=1)

if os.path.isfile('NAND-unpatched.bin'):
    doexit('NAND-unpatched.bin was found.\n'
           'In order to prevent writing a good backup with a bad one, the '
           'install has stopped. Please move or delete the old file if you '
           'are sure you want to continue.', errcode=1)

readsize = 0x100000  # must be divisible by 0x3AF00000 and 0x4D800000

print('Trying to open NAND-patched.bin...')
with open('NAND-patched.bin', 'rb+') as nand:
    print('Restoring FIRM0FIRM1.')
    nand.seek(0xB130000)
    if use_separate:
        with open('firm0_enc.bak', 'rb') as f:
            firm_final = f.read(0x400000).ljust(0x400000, b'\0')
        with open('firm1_enc.bak', 'rb') as f:
            firm_final += f.read(0x400000).ljust(0x400000, b'\0')
    else:
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
