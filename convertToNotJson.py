import json, os, sys

fileName = "ALL_POKEMON2.txt"
outFile = "ConvertedPokemon.txt"

infoFields = [ "Ability", "regionNum", "Weight", "Experience", "name",
               "Egg group", "Species", "Height", "type1", "type2",
               "allNum" ]
biggerFields = [ "stats", "tmMoves", "levelMoves", "evolutions", "description" ]

evolutionFields = [ "poke", "method", "form" ]
moveFields = [ "Accuracy", "Category", "PP", "Power", "Move", "Type",
               "TM", "Level" ]
statFields = [ "Sp.Atk", "Sp.Def", "HP", "Attack", "Defense", "Speed" ]

def convertPoke(outf, line):
    convertPokeJson(outf, json.loads(line))

def convertPokeJson(outf, poke):
    results = []

    # Go through all normal fields...
    for f in infoFields:
        if not f in poke: poke[f] = ''
        results.append(poke[f])

    # Go through stats...
    stats = poke[biggerFields[0]]
    for f in statFields:
        results.append(stats[f])

    # Append number of evolutions and each evolution
    evols = poke[biggerFields[3]]
    results.append(str(len(evols)))
    for evol in evols:
        for f in evolutionFields:
            if not f in evol or evol[f] == None: evol[f] = ''
            results.append(evol[f])

    # Append moves
    levels = poke[biggerFields[2]]
    results.append(str(len(levels)))
    for level in levels:
        for f in moveFields:
            if not f in level: level[f] = ''
            results.append(level[f])

    # Append tms
    tms = poke[biggerFields[1]]
    results.append(str(len(tms)))
    for tm in tms:
        for f in moveFields:
            if not f in tm: tm[f] = ''
            results.append(tm[f])

    # Append description
    descr = poke[biggerFields[4]]
    results.append(str(len(descr)))
    for des in descr:
        results += des

    # That's all. Write to the file
    s = '%s\n' % '!'.join(results)
    try:
        s = s.encode('utf-8')
    except:
        #import pdb; pdb.set_trace()
        pass
    outf.write(s)

def go():
    f = open(fileName, 'r')
    lines = f.readlines()
    f.close()

    f = open(outFile, 'w')
    map(lambda line: convertPoke(f, line), lines)
    f.close()

if __name__ == '__main__':
    go()
