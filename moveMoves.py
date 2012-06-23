import os, sys

import convertToNotJson

POKE_FILE = 'YAY-POKEMON-full.txt'
OUT_POKE_FILE = 'POKEMON-moveInd-full.txt'

MOVE_FILE = 'MOVE_DESCRS.txt'
OUT_MOVE_FILE = 'MOVE_INFO.txt'

MOVE_IND_FILE = 'all-moves.txt'

def addToKnown(d, moveParts):
    name = moveParts[4]
    if not name in d:
        d[name] = moveParts[:len(moveParts) - 1]
    else:
        known = d[name]
        if known[6] == None: d[name][6] = moveParts[6]
    return name

def getMoveId(moveInd, move):
    return moveInd[move]

def readMoveInd():
    ind = {}; i = 0
    f = open(MOVE_IND_FILE)
    for line in f.readlines(): ind[line.strip()] = str(i); i+= 1
    f.close()
    return ind

def parseMoves(pokeLine, d, moveInd, newOut):
    def parseMovesInside(parts, start, outParts):
        numLevels = int(parts[start])
        outParts.append(str(numLevels))
        moveF = convertToNotJson.moveFields
        start += 1
        for i in range(numLevels):
            end = start + len(moveF)
            name = addToKnown(d, parts[start : end])
            start = end

            level = parts[start - 1]
            outParts += [ getMoveId(moveInd, name), level ]
        return start

    # Everything before moves...
    parts = pokeLine.split('!')
    start = len(convertToNotJson.infoFields) + len(convertToNotJson.statFields)
    numEvols = int(parts[start])
    start += 1 + len(convertToNotJson.evolutionFields) * numEvols
    outParts = parts[:start]

    # Parse moves
    start = parseMovesInside(parts, start, outParts)
    start = parseMovesInside(parts, start, outParts)
    outParts += parts[start:]

    # Write out
    newOut.write('%s\n' % '!'.join(outParts))

def combineWithMoves(d, moveInd):
    f = open(MOVE_FILE)
    lines = map(lambda x: x.strip(), f.readlines())
    f.close()

    f = open(OUT_MOVE_FILE, 'w')
    for line in lines:
        parts = line.replace('!', '.').split('\t')
        name = parts[0]; rest = parts[1:]
        out = [name] + d[name][:4] + d[name][5:] + rest
        f.write('%s\n' % '!'.join(out))
    f.close()

def go():
    ind = readMoveInd()
    d = {}
    f = open(POKE_FILE)
    lines = f.readlines()
    f.close()
    f = open(OUT_POKE_FILE, 'w')

    for line in lines:
        parseMoves(line.strip(), d, ind, f)
    f.close()
    combineWithMoves(d, ind)

go()
