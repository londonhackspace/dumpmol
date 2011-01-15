#!/usr/bin/env python
#
#
#

import sys, os
from struct import *
from hexdump import *

tas = {}
tbs = {}
nullqs = {}
bis = {}
tris = {}

def update_stats(a,b,nq):
  if a not in tas:
    tas[a] = 1
  else:
    tas[a] += 1

  if b not in tbs:
    tbs[b] = 1
  else:
    tbs[b] += 1

  if nq not in nullqs:
    nullqs[nq] = 1
  else:
    nullqs[nq] += 1
    
  bkey = "%02x %02x" % (a, b)
  if bkey not in bis:
    bis[bkey] = 1
  else:
    bis[bkey] += 1

  trikey = "%02x %02x %02x" % (a, b, nq)
  if trikey not in tris:
    tris[trikey] = 1
  else:
    tris[trikey] += 1

def sort_n_dump(d):
  ks = d.keys()
  print "len", len(ks)
  ks.sort(cmp=lambda x,y: cmp(d[x], d[y]))
  for k in ks:
    if type(k) == type(42):
      print "%02x (%d): %d" % (k, k, d[k])
    else:
      print "%s: %s" % (k, d[k])
  
  print

def chunker(blob, prepend, startpos):
  off = 0
  
  while off < len(blob):
    typea, typeb, nullqq, size = unpack('BBBB', blob[off: off + 4])
    if typea == typeb == nullqq == size == 0:
      break
    print "%02x %02x %02x %02x" % (typea, typeb, nullqq, size)

    update_stats(typea, typeb, nullqq)

    hexdump(blob[off:off + 4 + (size * 4)], prepend, startpos + off)
    if typeb == 9:
      chunker(blob[off+8:off + (size * 4)], prepend + '*> ', startpos + off + 8)
    off += 4
    off += size * 4

if __name__ == "__main__":
  if len(sys.argv) != 2:
    print "%s: <filename.mol>" % (sys.argv[0])
  
  filename = sys.argv[1]

  fh = open(filename, 'rb')
  s = os.stat(filename)
  filesize = s.st_size

  blob = fh.read(filesize)
  
  fh.close()
  
  # something at 0x200

  stuff = blob[0x200:0x200 + 512]

  chunker(stuff, 'H>', 0x200)
  
  # start at offset 0x400
  # of 0xa00 ...
  things = blob[0xa00:]
  
  chunker(things, '', 0xa00)

  print "typea:"
  sort_n_dump(tas)

  print "typeb:"
  sort_n_dump(tbs)

  print "nullqq:"
  sort_n_dump(nullqs)

  print "bigrams"
  sort_n_dump(bis)

  print "trigrams"
  sort_n_dump(tris)



