#!/usr/bin/python
# -*- coding: utf-8 -*-
import os, sys, time
import mechanize
import json

from convertToNotJson import convertPokeJson

BASE_URL = 'http://bulbapedia.bulbagarden.net'

THINGS = [
    ('Species', '<span style="color:#000;">Species</span>',
     '<td class="roundy"', '>', None),
    ('Ability', '<a href="/wiki/Ability" title="Ability">',
     '<td width="50%" class="roundy"', '"color:#000;">', '<'),
    ('Experience', '<a href="/wiki/Experience" title="Experience">',
     'style="background: #FFFFFF; border', '>', None),
    ('Height', '<span style="color:#000;">Height</span>',
     '<br /><small>Metric</small>', '>', '<'),
    ('Weight', '<span style="color:#000;">Weight</span>',
     '<br /><small>Metric</small>', '>', '<'),
    ('Egg group', '<span style="color:#000;">Breeding</span>',
     '(Egg group)', '<span style="color:#000;">', '<'),
]

"""
    ('Baby form name', '<td> <small>Baby form</small>',
     '<span style="color:#000;">', '<span style="color:#000;">', '<'),
    ('Baby form method', '<td> <small>Baby form</small>',
     '<td rowspan="1"> ', 'style="color:#000;">', '<', True),

    ('Unevolved', '<td> <small>Unevolved</small>',
     '<span style="color:#000;">', '<span style="color:#000;">', '<'),
    ('Unevolved method', '<td> <small>Unevolved</small>',
     '<td rowspan="1"> ', 'style="color:#000;">', '<', True),

    ('First evolution', '<td> <small>First evolution</small>',
     '<span style="color:#000;">', '<span style="color:#000;">', '<'),
    ('First evolution method', '<td> <small>First evolution</small>',
     '<td> <a href="', 'style="color:#000;">', '<', True),

    ('Second evolution', '<td> <small>Second evolution</small>',
     '<span style="color:#000;">', '<span style="color:#000;">', '<'),
"""

PROB_FILE = 'problems.txt'

def getEvolutions(s):
    # Fix the string...
    tag = 'id="Evolution"'
    if not tag in s: return {}
    s = s[s.index(tag):]
    end = s.find('id="Sprites"')
    s = s if end < 0 else s[:end]

    # Find all tds
    end = 0
    strs = []
    while True:
        start = s.find('<td', end)
        if start < 0: break
        end = s.find('</td', start)
        string = s[start:end].strip()
        if '<td' in string[3:]:
            end = start + 3
        else:
            string = continueTilEnd(string)
            if string != '': strs.append(string)

    # Assign aprts
    if not 'evol' in strs[0] and not 'Baby' in strs[0]: return {}
    all = []
    methods = []
    i = 0
    while i < len(strs):
        x = strs[i]
        if 'evol' in x or 'Baby' in x:
            form = x
            poke = strs[i + 1]
            method = None if len(methods) == 0 else methods[0]
            methods = methods[1:]
            if '&#160;' in poke:
                poke = poke[:poke.index('&#160;')].strip()
            #print '%s / %s / %s' % (method, form, poke)
            all.append( { 'method' : method, 'form' : form, 'poke' : poke} )
            i += 2
        else:
            methods.append(x)
            i += 1
    return all

def readPokes(fname="out-pokemon.txt"):
    f = open(fname, 'r')
    lines = f.readlines()
    return map(lambda x: x.strip().split('\t'), lines)

def getPart(s, starttag, endtag):
    start = s.index(starttag) + len(starttag)
    end = len(s) if endtag == None else s.index(endtag, start)
    return s[start : end].strip()

def getStats(s):
    #tag = '<h4> <span class="mw-headline" id="Base_stats">'#Base stats</span></h4>'
    tag = 'id="Base_stats"'
    if not tag in s and not tag.lower() in s.lower(): return []
    parts = s.split('\n')

    statname = 'title="Stats"><span style="color:#000;">'
    basename = 'width: 30px;"> '
    othername = '<th> <small>'
    endname = '</th></tr>'
    stat = None; num1 = None; num2 = None; num3 = None
    stats = []
    json = {}

    for x in parts:
        if statname in x:
            stat = getPart(x, '<span style="color:#000;">', '<')
        elif basename in x:
            num1 = getPart(x, basename, None)
        elif othername in x:
            thing = getPart(x, othername, '<')
            if num2 == None: num2 = thing
            else: num3 = thing
        elif stat != None and num1 != None and endname in x:
            stats.append( (stat,num1,num2,num3) )
            json[stat] = num1
            #print "%s\t%s\t%s\t%s" % (stat, num1, num2, num3)
            stat = None; num1 = None; num2 = None; num3 = None
        else: continue
    return json

# Strip tags
def stripTags(x):
    found = [' ']
    i = 0
    while i < len(x):
        c = x[i]
        if c == '<':
            while i < len(x) and x[i] != '>': i += 1
            i += 1
            if not found[len(found) - 1] == ' ': found.append(' ')
        elif c == '\n': break
        #elif ord(c) >= 128: i += 1
        elif (c == '.' or c == ' ') and found[len(found) - 1] == ' ': i += 1
        elif c == '*': i += 1
        else: found.append(c); i += 1
    return ''.join(found).strip().replace('!', '.')

# Strips out tags
def continueTilEnd(x):
    found = [' ']
    i = 0
    while i < len(x):
        c = x[i]
        if c == '<':
            while i < len(x) and x[i] != '>': i += 1
            i += 1
            if not found[len(found) - 1] == ' ': found.append(' ')
        elif c == '\n': break
        elif ord(c) >= 128: i += 1
        else: found.append(c); i += 1
    return ''.join(found).strip()

def findRightAfter(s, before, tag, start, end, tilEnd=False):
    if not before in s: return None
    s = s[s.index(before):]
    parts = s.split('\n')
    for x in parts:
        if not tag in x: continue
        if not start in x: continue
        startit = x.index(start) + len(start)
        endit = len(x) if end == None else x.index(end, startit)
        if not tilEnd: return x[startit : endit].strip()
        else: return continueTilEnd(x[startit:])

def removeTags(s):
    chars = []
    inTag = False
    for char in s:
        if char == '<': inTag = True
        elif char == '>': inTag = False
        elif not inTag: chars.append(char)
    ret = ''.join(chars).strip()
    return '---' if '&#8212;' in ret else ret

def findNextTagVal(s, end, tag, closeTag):
    ERR_RET = (-1, None)
    while end >= 0:
        start = s.find(tag, end)
        if start < 0: return ERR_RET
        end = s.find(closeTag, start)
        string = s[start:end].strip()
        if tag in string[len(tag) : ]:
            end = start + len(tag)
        elif 'This section is incomplete.' in string:
            continue
        else:
            string = stripTags(string).replace('\t', ' ')
            if string == '': continue
            return (end, string)
    return ERR_RET

def mergeHdrsSprites(d, hdrs, sprites):
    for i in range(min(len(hdrs), len(sprites))):
        d[hdrs[i]] = sprites[i]

def getSprites(s):
    tag = 'id="Sprites"'
    if not tag in s: tag = tag.lower()
    if not tag in s: return {}
    s = s[s.index(tag) :]
    s = s[:s.index('</table>')]

    lines = s.split('\n')
    hdrs = []
    sprites = []
    d = {}
    for line in lines:
        if '<th' in line:
            if 'Generation' in line: continue
            hdrs.append(stripTags(line))
        elif '<td' in line and '<img' in line:
            start = line.index('src="') + 5
            end = line.index('"', start)
            url = line[start : end]
            if '_s.' in url: continue
            if 'colspan="' in line:
                start = line.index('colspan="') + len('colspan="')
                end = line.index('"', start)
                cols = int(line[start : end])
            else: cols = 1
            for c in range(cols): sprites.append(url)
        elif '</td></tr' in line:
            mergeHdrsSprites(d, hdrs, sprites)
            hdrs = []; sprites = []
    return d

def getSpritesByDescr(name, sprites, descrs):
    f = []
    for descr in descrs:
        (game, _) = descr
        if ' 2' in game: continue
        if game == 'Stadium': game = 'Red / Blue'
        opts = game.split(' / ')
        chosen = ''

        for opt in opts:
            if not opt in sprites: continue
            chosen = sprites[opt]; break

        if chosen == '':
            print "CANNOT FIND SPRITE for %s / %s" % (name, game)
        f.append(chosen.replace('!', ''))
        print '%s: %s' % (game, chosen)
    return f

def getDescription(s):
    start = s.index('id="Game_data"')
    s = s[start:]
    tags = [ 'id="Pok.C3.A9dex_entries_2"', 'id="Pok.C3.A9dex_entries_3"', 'id="Pok.C3.A9dex_entries"' ]
    for tag in tags:
        if tag in s: break
    start = s.index(tag)
    start = s.index('<small>', start)
    end = s.index('id="Game_locations"', start)
    focus = s[start : end]

    # Run through and alternate th and td
    tags = [ '<th', '<td' ]
    endTags = [ '</th', '</td' ]
    strs = []; end = 0
    while end >= 0:
        (fend, first) = findNextTagVal(focus, end, tags[0], endTags[0])
        (send, secon) = findNextTagVal(focus, end, tags[1], endTags[1])

        # There can be multiple firsts...so check for more
        vals = []; end = 0
        while first != None:
            if not 'Generation' in first: vals.append(first)
            (end, first) = findNextTagVal(focus[fend : send], end,
                                          tags[0], endTags[0])

        # Append the values and move on
        if len(vals) > 0 and secon != None and not '{{{' in secon:
            if not 'data is available' in secon:
                if not 'entry is unav' in secon:
                    strs.append((' / '.join(vals), secon))
        end = send
    return strs
    #import pdb; pdb.set_trace()

def getMoves(s, startTag, endTag):
    begin = '<td style'; kill = '</td></tr>'

    start = s.index(startTag) + len(startTag)
    end = s.index(endTag, start)
    s = s[start : end]
    parts = s.split('\n')

    moves = []
    move = []
    for line in parts:
        if len(move) > 0 and line == kill:
            moves.append(move)
            #print ' '.join(move)
            move = []
        elif not line.startswith(begin): continue
        else: move.append(removeTags(line))
    return moves

def getObj(keys, values):
    obj = {}
    for i in range(len(values)):
        obj[keys[i]] = values[i]
    return obj

def getLevelMoves(s):
    moves = getMoves(s, '<h4> <span class="mw-headline" id="By_leveling_up">', '<h4>')
    names = [ 'Level', 'Move', 'Type', 'Category', 'Power', 'Accuracy', 'PP' ]
    return map(lambda x : getObj(names, x), moves)

def getTmMoves(s):
    moves = getMoves(s, '<h4> <span class="mw-headline" id="By_TM.2FHM">', '<h4>')
    names = [ 'TM', 'Move', 'Type', 'Category', 'Power', 'Accuracy', 'PP' ]
    return map(lambda x : getObj(names, x), moves)

def openWithRetry(br, url):
    try:
        resp = br.open(url)
        s = resp.read()
        return s
    except:
        print "Sleeping 3 to get %s" % url
        time.sleep(3)
        openWithRetry(br, url)

def readPokemon(br, outf, url, pname, bigNum, inNum, type1, type2):
    if br != None:
        s = openWithRetry(br, url)
    else:
        f = open('./pgs/' + pname, 'r')
        s = f.read()
        f.close()
    preJson = {
        'url' : url,
        'name' : pname,
        'allNum' : bigNum,
        'regionNum' : inNum,
        'type1' : type1
    }
    if type2 != None: preJson['type2'] = type2

    desr = getDescription(s)
    preJson['description'] = desr

    if True:
        sprites = getSprites(s)
        sprs = [ pname ] + getSpritesByDescr(pname, sprites, desr)
        outf.write("%s\n" % ('!'.join(sprs)))
        return

    # Fields
    for thing in THINGS:
        (name, before, tag, start, end) = thing[:5]
        it = findRightAfter(s, before, tag, start, end, len(thing) > 5)
        if it == None: continue
        preJson[name] = it

    # Evolutions
    evs = getEvolutions(s)
    preJson['evolutions'] = evs

    # Stats
    stats = getStats(s)
    preJson['stats'] = stats

    # Level up moves
    levelMoves = getLevelMoves(s)
    tmMoves = getTmMoves(s)
    preJson['levelMoves'] = levelMoves
    preJson['tmMoves'] = tmMoves

    # Write to file and print
    if False:
        outs = json.dumps(preJson)
        fname = urlToName(pname, type1, type2)
        f = open(fname, 'w')
        f.write(outs)
        f.close()
        print '\t' + fname
    else:
        convertPokeJson(outf, preJson)
        outf.flush()
        print 'P\t' + pname

    # Note something if empty...
    noteIfEmpty(FPROB, evs, pname, '  evolutions')
    noteIfEmpty(FPROB, desr, pname, 'description')
    noteIfEmpty(FPROB, stats, pname, 'stats')
    noteIfEmpty(FPROB, levelMoves, pname, 'levelMoves')
    noteIfEmpty(FPROB, tmMoves, pname, 'tmMoves')

def noteIfEmpty(f, struct, poke, type):
    if struct != None and len(struct) != 0: return
    f.write('%s: %s\n' % (type, poke))
    print '%s: %s' % (type, poke)

def urlToName(name, type1, type2):
    ret = name + "_" + type1
    if type2 != None: ret += "_" + type2
    return 'dataTest/' + ret + ".txt"

def readAllPokemon(br, outf, info):
    (url, name, bigNum, inNum, type1) = info[:5]
    type2 = None
    if len(info) == 6: type2 = info[5]
    url = BASE_URL + url
    readPokemon(br, outf, url, name, bigNum, inNum, type1, type2)

def go(lower=0, upper=2000):
    br = mechanize.Browser()
    pokes = readPokes()
    limited = filter(lambda l : int(l[2]) >= lower and int(l[2]) <= upper, pokes)
    f = open("YAY-POKEMON-spr.txt", 'w')
    map(lambda x:readAllPokemon(br, f, x), limited)
    f.close()
    """readPokemon(br, 'http://bulbapedia.bulbagarden.net/wiki/Charizard_(Pok%C3%A9mon)', '', '', '', '', '')
    readPokemon(br, 'http://bulbapedia.bulbagarden.net/wiki/Pichu_(Pok%C3%A9mon)', 'Pichu', 0,0, 'A', 'B')
    readPokemon(br, 'http://bulbapedia.bulbagarden.net/wiki/Throh_(Pok%C3%A9mon)')
    readPokemon(br, 'http://bulbapedia.bulbagarden.net/wiki/Elekid_(Pok%C3%A9mon)')
    readPokemon(br, 'http://bulbapedia.bulbagarden.net/wiki/Arceus_(Pok%C3%A9mon)')"""

def testgo(lower=0, upper=2000):
    pokes = [ 'Bulbasaur', 'Charizard', 'Beedrill', 'Eevee', 'Happiny', 'Meloetta', 'Unown' ]
    #pokes = [ 'Meloetta' ]
    allPokes = readPokes()
    pokesInfo = filter(lambda x: x[1] in pokes, allPokes)
    f = open('YAY-POKEMON-spr-test.txt', 'w')
    map(lambda x: readAllPokemon(None, f, x), pokesInfo)
    f.close()

lower = 0 if len(sys.argv) < 2 else int(sys.argv[1])
upper = 2000 if len(sys.argv) < 3 else int(sys.argv[2])
FPROB = open(PROB_FILE, 'w')
go(lower, upper)
FPROB.close()
