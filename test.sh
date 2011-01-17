#!/bin/sh

rm -f /tmp/*.t

for f in ONE.MOL TWO.MOL THREE.MOL FOUR.MOL ; do
./fiddle.py test-files/${f} > /tmp/`basename $f .MOL`.t
done

for f in 1X1CM.MOL 2X2CM.MOL 4X4CM.MOL ; do
./fiddle.py test-files/squares_mol_files/${f} > /tmp/`basename $f .MOL`.t
done
