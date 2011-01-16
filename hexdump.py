#!/usr/bin/env python
#
# $Id$
#
# implemented a couple of useful functions for displaying binary data.
#

import sys

def tobin(i):
    """Convert an int to a binary
    
    This function converts an int into a string representing the int
    in binary.
    
    e.g.  tobin(170) would produce 10101010
    
    the string is left padded with 0's to the nearest 32, 16, or 8 bit boundry.
    
    e.g.:
    
      170                          10101010
      342                  0000000101010110
    65537  00000000000000010000000000000001
    """
    s = ""
    max = 8
    if i > 255:
        max = 16
    if i > 65535:
        max = 32
    
    bins = range(max)
    bins = map(lambda a: 2 ** a, bins)
    bins.reverse()
    
    for b in bins:
        if b & i == b:
            s+= "1"
        else:
            s+= "0"
    return s

def hexdump(str, prepend = '', start = 0):
    """Hexdump's things
    
    The prepend arg is prepended to every string thats printed out, 
    useful if you want to indent stuff, it defaults to ''.
    """
    x = y = count = 0
    indent = 16
    out = ''

    print "%s" % (' ' * (len(prepend) + 6)),
    for i in range(start % indent, indent):
#   for i in range(0, indent):
        print "%02x" % (i),
    if start != 0:
        for i in range(0, start % indent):
            print "%02x" % (i),
    print
        
    out = ''

    while (count < len(str)):
        out = "%s%04x : " % (prepend, start + count)
        
        x = 0
        while x < indent:
            if (x + count + 1 ) > len(str):
                break
            out = out + "%02x " % (ord(str[x + count]))
            if (x + count + 1) >= len(str):
                x += 1
                y = 0
                for y in range(indent - x):
                    out = out + '   '
                break
            x += 1
            if (x%4 == 0):
                out += "| "
        
        out = out + ": "
        
        x = 0
        while x < indent:
            if (x + count + 1) > len(str):
                break
            if ord(str[x + count]) >= 32 and ord(str[x + count]) <= 126:
                out = out + str[x + count]
            elif ord(str[x + count]) == 0:
                out = out + ' '
            else:
                out = out + '.'
            
            if (x + count + 1) >= len(str):
                x += 1
                y = 0
                while y < (indent - x):
                    out += ' '
                    y += 1
            
            x += 1
            
        print out
        count += indent
            
    print



if __name__ == "__main__":
    if len(sys.argv) > 1:
        fh = open(sys.argv[1], 'rb')
        blob = fh.read(1024 * 1024 * 1024) # silly
        hexdump(blob)
        fh.close()
        sys.exit()

    s = "lksdhfkahsdflakhjsdflahfalsdfakhfdw98345\000\001\006\077$%$^%$%"
    hexdump(s, "%% ")
    hexdump(s, '', 90)
    for i in [1, 0x24, 0x23, 255, 192, 7, 42, 128, 42 + 128, 342, 65537]:
        print "%5d %33s" % (i, tobin(i))
    