#!/bin/sh

rm -f /tmp/*.t

for f in ONE.MOL TWO.MOL THREE.MOL FOUR.MOL ; do
./fiddle.py test-files/${f} > /tmp/`basename $f .MOL`.t
done
