## Combines all of the pokemon files into one

import json, os, sys

DIR = './whoo/dataTest'

OUT_FILE = 'ALL_POKEMON.txt'

def fixAllFiles():
    files = os.listdir(DIR)
    all = []
    outf = open(OUT_FILE, 'w')
    for fname in files:
        f = open(os.path.join(DIR, fname))
        s = f.read()
        outf.write('%s\n' % s.strip())
        f.close()
    outf.close()

fixAllFiles()
