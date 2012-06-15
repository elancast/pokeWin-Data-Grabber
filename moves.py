import json, mechanize, os, sys

MOVES_FILE = 'all-moves.txt'

def findAllMoves(dir):
    files = os.listdir(dir)
    moves = set()
    for file in files:
        f = open(os.path.join(dir, file))
        jsons = json.load(f)
        f.close()
        for move in jsons['tmMoves']:
            moves.add(move['Move'])
        for move in jsons['levelMoves']:
            moves.add(move['Move'])

    f = open(MOVES_FILE, 'w')
    for move in sorted(moves): f.write('%s\n' % move)
    f.close()

def readMove(f, br, url, name):
    # Read data...
    if br == None:
        fr = open(url, 'r')
        s = fr.read()
        fr.close()
    else:
        resp = br.open(url)
        s = resp.read()
        print name

    # Parse and stringify
    descrs = findDesc(s)
    ss = reduce(lambda a, b: a + '\t' + b,
                map(lambda x: x[0] + ': ' + x[1], descrs))
    ss = name + '\t' + ss
    f.write('%s\n' % ss)
    f.flush()

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
    return ''.join(found).strip()

def findDesc(s):
    # Limit
    start = s.index('id="Description"')
    end = s.find('id="Learnset"', start)
    if end < 0:
        end = s.find('<h2', start)
        if end < 0: end = len(s) - 1
    s = s[start : end]

    # Go through td's
    end = 0; strs = []
    last = None
    while end >= 0:
        start = s.find('<td', end)
        if start < 0: break
        end = s.find('</td', start)
        string = s[start:end].strip()
        if '<td' in string[3:]:
            end = start + 3
        elif 'This section is incomplete.' in string:
            continue
        else:
            string = stripTags(string).replace('\t', ' ')
            if string == '': continue
            elif last == None: last = string
            else:
                strs.append( (last, string) )
                last = None
    return strs

def getUrl(br, name):
    name = '%s_(move)' % name.replace(' ', '_')
    if br == None: return 'pgs/%s' % name
    return 'http://bulbapedia.bulbagarden.net/wiki/%s' % name

MOVE_FILE = 'move-descrs.txt'

def go():
    f = open('all-moves.txt', 'r')
    moves = map(lambda x: x.strip(), f.readlines())
    f.close()
    f = open(MOVE_FILE, 'w')

    # Urls
    br = mechanize.Browser()
    urls = map(lambda x: getUrl(br, x), moves)
    for x in range(len(moves)):
        readMove(f, br, urls[x], moves[x])
    f.close()

def testgo():
    moves = [ 'Heal Order', 'Heal Pulse', 'Hidden Power', 'Dig', 'Inferno' ]
    urls = map(lambda x: getUrl(None, x), moves)
    f = open(MOVE_FILE, 'w')
    map(lambda x: readMove(f, None, urls[x], moves[x]),
        range(len(moves)))
    f.close()

if False:
    findAllMoves('./data')
else:
    testgo()
