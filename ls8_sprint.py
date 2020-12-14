#!/usr/bin/env python3

"""Main."""

import sys
from cpu_sprint import *

if len(sys.argv) != 2:
    print("Wrong number of arguments passed in.")
    print(sys.argv)
else:
    cpu = CPU()

    cpu.load(sys.argv[1])
    cpu.run()
