#!/usr/bin/python
# -*- coding: latin-1 -*-
import os, sys

def getNumber(line, numbers):
    # <td style="font-family:Monospace;"> #007
    start = line.index('#') + 1
    try:
        return int( line[start:].strip() )
    except:
        return -1

def getPokemon(line, poke):
    # <td> <a href="/wiki/Squirtle_(Pok%C3%A9mon)" title="Squirtle (Pokémon)">Squirtle</a>
    start = line.index('"/wiki') + 1
    end = line.index('"', start)
    url = line[start : end]

    start = line.index('>', end) + 1
    end = line.index('<', start)
    mon = line[start : end]
    return '%s\t%s' % (url, mon)

def getType(line, typeStr):
    start = line.index(typeStr) + len(typeStr)
    end = line.index('<', start)
    return line[start:end]

def grabPoke(br, fname="out-pokemon.txt"):
    resp = br.open("http://bulbapedia.bulbagarden.net/wiki/List_of_Pok%C3%A9mon_by_National_Pok%C3%A9dex_number")
    s = resp.read()

    numbers = '<td style="font-family:Monospace;">'
    poke = '<td> <a href="/wiki/'
    typeStr = '<span style="color:#FFFFFF">'
    endStr = '</td></tr>'
    types = []
    pokemons = []
    f = open(fname, "w")

    currNum1 = None; currNum2 = None; currPoke = None
    for line in s.split('\n'):
        if numbers in line:
            num = getNumber(line, numbers)
            if currNum1 == None: currNum1 = num
            else: currNum2 = num
        elif poke in line:
            currPoke = getPokemon(line, poke)
        elif typeStr in line:
            types.append(getType(line, typeStr))
        elif endStr in line:
            if currPoke == None: continue
            pokemons.append( (currPoke, currNum2, currNum1) )
            myTypes = '\t'.join(types)
            f.write("%s\t%d\t%d\t%s\n" % (currPoke, currNum2, currNum1, myTypes))
            print "%s\t%d\t%d\t%s" % (currPoke, currNum2, currNum1, myTypes)
            currNum1 = None; currNum2 = None; currPoke = None
            types = []
        else: continue


    f.close()

import mechanize
br = mechanize.Browser()
grabPoke(br)
