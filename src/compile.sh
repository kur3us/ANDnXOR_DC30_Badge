#!/bin/bash
#Cross compile python files into native code
for i in *.py; do
    echo "CROSS COMPILING $i"
	../lib/micropython/mpy-cross/mpy-cross $i
done

# main.mpy is ignored by uPY, provision script will manually copy
rm main.mpy