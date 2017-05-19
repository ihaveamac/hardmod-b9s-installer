#!/usr/bin/env python3

import hashlib
import os
import shutil
import subprocess
import sys
import time


def doexit(msg, errcode=0):
    print(msg)
    input('Press Enter to continue...')
    sys.exit(errcode)


if not os.path.isfile('NAND.bin'):
    doexit('NAND.bin not found.', errcode=1)

if os.path.isfile('firm0firm1.bak'):
    doexit('firm0firm1.bak was found.\n'
           'In order to prevent writing a good backup with a bad one, the '
           'install has stopped. Please move or delete the old file if you '
           'are sure you want to continue. If you would like to restore, use '
           '`restore-firm0firm1`.',
           errcode=1)

if os.path.isfile('NAND-patched.bin'):
    doexit('NAND-patched.bin was found.\n'
           'Please move or delete the patched NAND before patching another.',
           errcode=1)

if not os.path.isfile('current.firm'):
    doexit('current.firm not found.', errcode=1)

if not os.path.isfile('boot9strap.firm'):
    doexit('boot9strap.firm not found.', errcode=1)

if not os.path.isfile('boot9strap.firm.sha'):
    doexit('boot9strap.firm.sha not found.', errcode=1)

print('Verifying boot9strap.firm.')
with open('boot9strap.firm.sha', 'rb') as f:
    b9s_hash = f.read(0x20)
with open('boot9strap.firm', 'rb') as f:
    if hashlib.sha256(f.read(0x400000)).digest() != b9s_hash:
        doexit('boot9strap.firm hash check failed.', errcode=1)
    print('boot9strap.firm hash check passed.')

readsize = 0x100000  # must be divisible by 0x3AF00000 and 0x4D800000

shutil.rmtree('work', ignore_errors=True)
os.makedirs('work', exist_ok=True)


def runcommand(cmdargs):
    proc = subprocess.Popen(cmdargs, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    proc.wait()
    procoutput = proc.communicate()[0]
    # return(procoutput)
    if proc.returncode != 0:
        print('{} had an error.'.format(cmdargs[0]))
        print('Full command: {}'.format(' '.join(cmdargs)))
        print('Output:')
        print(procoutput)


overall_time = time.time()
print('Trying to open NAND.bin...')
with open('NAND.bin', 'rb+') as nand:
    print('Backing up FIRM0FIRM1 to firm0firm1.bin...')
    nand.seek(0xB130000)
    start_time = time.time()
    with open('firm0firm1.bak', 'wb') as f:
        for curr in range(0x800000 // readsize):
            f.write(nand.read(readsize))
            print('Reading {:06X} ({:>5.1f}%)'.format((curr + 1) * readsize,
                  (((curr + 1) * readsize) / 0x800000) * 100), end='\r')
    print('\nReading finished in {:>.2f} seconds.\n'.format(
        time.time() - start_time))

    print('Creating FIRMs to xor from boot9strap.firm.')
    start_time = time.time()
    with open('current.firm', 'rb') as f:
        with open('work/current_pad.bin', 'wb') as b9s:
            b9s.write(f.read(0x400000).ljust(0x400000, b'\0') * 2)
    with open('boot9strap.firm', 'rb') as f:
        with open('work/boot9strap_pad.bin', 'wb') as b9s:
            b9s.write(f.read(0x400000).ljust(0x400000, b'\0') * 2)
    print('Creation finished in {:>.2f} seconds.\n'.format(
        time.time() - start_time))

    print('XORing FIRM0FIRM1 with current.firm.')
    start_time = time.time()
    runcommand(['tools/lazyxor-' + sys.platform, 'firm0firm1.bak',
                'work/current_pad.bin', 'work/xored.bin'])
    print('XORing finished in {:>.2f} seconds.\n'.format(
        time.time() - start_time))

    print('XORing FIRM0FIRM1 with boot9strap.firm.')
    start_time = time.time()
    runcommand(['tools/lazyxor-' + sys.platform, 'work/xored.bin',
                'work/boot9strap_pad.bin', 'work/final.bin'])
    print('XORing finished in {:>.2f} seconds.\n'.format(
        time.time() - start_time))

    print('Writing final FIRMs to NAND.bin.')
    with open('work/final.bin', 'rb') as f:
        firm_final = f.read(0x800000)
    nand.seek(0xB130000)
    start_time = time.time()
    for curr in range(0x800000 // readsize):
        print('Writing {:06X} ({:>5.1f}%)'.format((curr + 1) * readsize,
              (((curr + 1) * readsize) / 0x800000) * 100), end='\r')
        nand.write(bytes(firm_final[curr * readsize:(curr + 1) * readsize]))
    print('\nWriting finished in {:>.2f} seconds.'.format(
        time.time() - start_time))

os.rename('NAND.bin', 'NAND-patched.bin')

doexit('boot9strap install process finished in {:>.2f} seconds.'.format(
       time.time() - overall_time))
