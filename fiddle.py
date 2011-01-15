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
qgrams = {}

def update_a_stat(d, k):
  if k not in d:
    d[k] = 1
  else:
    d[k] += 1
  
def update_stats(a, b, nq, s):
  update_a_stat(tas, a)
  update_a_stat(tbs, b)
  update_a_stat(nullqs, nq)

  bkey = "%02x %02x" % (a, b)
  update_a_stat(bis, bkey)

  trikey = "%02x %02x %02x" % (a, b, nq)
  update_a_stat(tris, trikey)

  qkey = "%02x %02x %02x %02x" % (a, b, nq, s)
  update_a_stat(qgrams, qkey)

def dump_stats():
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

  print "qgrams"
  sort_n_dump(qgrams)



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
  
  ks.sort(cmp=lambda x,y: cmp(x, y))
  for k in ks:
    if type(k) == type(42):
      print "%02x (%d): %d" % (k, k, d[k])
    else:
      print "%s: %s" % (k, d[k])

def chunker(blob, prepend, startpos, stats=True):
  off = 0
  
  while off < len(blob):
    typea, typeb, nullqq, size = unpack('BBBB', blob[off: off + 4])
#    if typea == typeb == nullqq == size == 0:
#      break

    print "%02x %02x %02x %02x" % (typea, typeb, nullqq, size)

    if stats:
      update_stats(typea, typeb, nullqq, size)

    if (typea, typeb, nullqq, size) == (0x48, 0x01, 0x60, 0x80):
      print "XXX size fixup, 0x%02x (%d) -> 10" % (size, size)
      size = 10

    if (typea, typeb, nullqq, size) == (0x48, 0x00, 0x30, 0x01):
      section = unpack('I', blob[off + 4:off + 8])[0]
      print "start section %d" % (section)
      # keep stats about the start of the section
      if prepend == None:
        prepend = 's%d>' % (section)

    if (typea, typeb, nullqq, size) == (0x48, 0x00, 0x40, 0x01):
      print "end section %d at 0x%04x" % (unpack('I', blob[off + 4:off + 8])[0], startpos + off+8)
      # append the addr of the end of the section
      off += 4
      off += size * 4
      break
    
    if size > 0:
      hexdump(blob[off:off + 4 + (size * 4)], prepend, startpos + off)

#    if typeb == 9:
#      chunker(blob[off+8:off + (size * 4)], prepend + '*> ', startpos + off + 8)
    off += 4
    off += size * 4

  return startpos + off

if __name__ == "__main__":
  if len(sys.argv) != 2:
    print "%s: <filename.mol>" % (sys.argv[0])
  
  filename = sys.argv[1]

  fh = open(filename, 'rb')
  s = os.stat(filename)
  filesize = s.st_size

  blob = fh.read(filesize)
  
  fh.close()

  # header stuff?
  print "header:"
  header = blob[0:512]
  hexdump(header, 'header ', 0)
  print "sections at:",
  sections = unpack("4I", header[0x70:0x70 + (4*4)])
  print sections,
  print ["%04x" % (s * 512) for s in sections]
  print
  
  # something at 0x200

  print "next stuff:"
  stuff = blob[0x200:0x200 + 512]
  hexdump(stuff, 'header2 ', 0x200)
  print

  # start at offset 0x400
  #
  # won't work with long .mol files, need to find out how the
  # section lengths work.
  #
  for i,s in enumerate(sections[1:]):
    print "Section %d: offset: %d (0x%04x)" % (i, s, s * 512) 
    end = chunker(blob[s * 512:], None, s * 512)
#    next = ((end / 512) + 1) * 512


#  dump_stats()

  