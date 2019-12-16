#!/usr/bin/env python3

from diggicamp import *
from clint.arguments import Args
from clint.textui import puts, colored, indent

puts(colored.blue('Grouped Arguments: ') + str(dict(args.grouped)))

print()
