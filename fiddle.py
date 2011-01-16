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
      
def dewrapper(blob, prepend='', startpos=0):
    """
    This looks for the string : 
    01 46 00 01 | 0X 00 00 00 | 01 03 00 03 | 00 00 YY 09
    where X is either 1 or 2 and YY is either 34 or 48
    in wrapper sections then prints what follows. These 
    sections seem to come in pairs (a 1 followed by a 2)
    they also seem to carry fairly similar payloads
    """
    off = 12 # the first 3 32b words are copied directly
    if len(blob) < 12:
        hexdump(blob, '*')
        return
    
    print str(startpos) + " " + str(off)
    current_four = [0,] + list(unpack('>III', blob[:off]))
    section = 0
    current_start = 0
    
    while off < len(blob):
        current_four.pop(0)
        current_four.append(unpack('>I', blob[off:off + 4])[0])
                # 
                # print current_four
        
        if current_four == [0x01460001,0x01000000,0x01030003,0x00003409] or \
        current_four == [0x01460001,0x02000000,0x01030003,0x00003409] or \
        current_four == [0x01460001,0x01000000,0x01030003,0x00004809] or \
        current_four == [0x01460001,0x02000000,0x01030003,0x00004809]:
            hexdump(blob[current_start: off - 12], "w%d." % section, startpos + current_start)
            current_start = off + 4 # where the next block starts 
            print "%08x %08x %08x %08x" % (current_four[0],current_four[1], current_four[2], current_four[3])
            print "Subsection %d at position %04x" % (section, current_start)
            current_four = [None, None, None, None]
            section += 1
        
        off += 4

        
def chunker(blob, prepend, startpos, stats=True):
  off = 0
  
  while off < len(blob):
    typea, typeb, nullqq, size = unpack('BBBB', blob[off: off + 4])

    print "%02x %02x %02x %02x" % (typea, typeb, nullqq, size)

    if (typea, typeb, nullqq, size) == (0x48, 0x01, 0x60, 0x80):
      new_size = unpack("<I", blob[off+4:off+8])[0]
      print "XXX size fixup, 0x%02x (%d) -> %d" % (new_size, new_size, new_size + 1)
      size = new_size + 1

    # this seems to start a wrapper section; the next 32bit word seem
    # to define how many words are wrapped (eg 0x50 or more)
    if (typea, typeb, nullqq, size) == (0x46, 0x09, 0x00, 0x80):
      new_size = unpack("<I", blob[off+4:off+8])[0]
      print "Wrapper section, size: 0x%02x (%d) -> %d" % (new_size, new_size, new_size + 1)   
      dewrapper(blob[off + 8: off + (new_size*4)], "w", startpos + off)
      off = off + (new_size - 1)*4 # another 4 will be added at bottom


    if (typea, typeb, nullqq) == (0x46, 0x0e, 0x00):
      print "laser power control",
      args = blob[off+4:off + 8 + (size * 4)]
      power = args[0:8]
      power = unpack("II", power)
      power = [p / 100.0 for p in power]
      print power
      hexdump(args, prepend, startpos + off)

    if (typea, typeb, nullqq, size) == (0x48, 0x00, 0x30, 0x01):
      section = unpack('I', blob[off + 4:off + 8])[0]
      print "start section %d" % (section)
#      hexdump(blob[off+8:off+8+128])
#      break
      if prepend == None:
        prepend = 's%d>' % (section)

    if (typea, typeb, nullqq, size) == (0x48, 0x00, 0x40, 0x01):
      print "end section %d at 0x%04x" % (unpack('I', blob[off + 4:off + 8])[0], startpos + off+8)
      print "="*40 + "\n"
      off += 4
      off += size * 4
      break

    if size > 0:
      hexdump(blob[off:off + 4 + (size * 4)], prepend, startpos + off)

    if stats:
      update_stats(typea, typeb, nullqq, size)
    
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
#  hexdump(header, 'header ', 0)
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
    end = chunker(blob[s * 512:], '', s * 512)
#    next = ((end / 512) + 1) * 512


#  dump_stats()

  