import os, sys, time
import mechanize

FILE = 'pokemon-sprites.txt'

def getAbilitiesList():
    f = open(FILE, 'r')
    s = f.read()
    f.close()

    lines = s.split('\n')
    pokes = []; abils = {}
    for line in lines:
        if line == '': continue
        parts = line.split('!')
        poke = parts[0]
        num = int(parts[1])

        newStuff = []
        for i in range(num):
            abil = parts[i * 2 + 2]
            url = parts[i * 2 + 3]
            if '&#160' in abil:
                abil = abil[ : abil.index('&#160')].strip()
            abil = abil.replace(',', '').strip()

            if not url in abils or len(abil) < len(abils[url]):
                abils[url] = abil.replace('Hidden Ability', '').strip()
            newStuff.append( (abil, url) )
        rest = '!'.join(parts[num * 2 + 2 :])
        pokes.append( (poke, rest, newStuff) )
    return (abils, pokes)

def openWithRetry(br, url):
    try:
        resp = br.open(url)
        s = resp.read()
        return s
    except:
        print "Sleeping 3 to get %s" % url
        time.sleep(3)
        return openWithRetry(br, url)

def removeTags(s):
    chars = []
    inTag = False
    for char in s:
        if char == '<': inTag = True
        elif char == '>': inTag = False
        elif not inTag: chars.append(char)
    ret = ''.join(chars).strip()
    return '---' if '&#8212;' in ret else ret

def openAbil(br, descrs, url, abil):
    if descrs != None and len(descrs) > 0:
        return descrs[abil]

    url = 'http://bulbapedia.bulbagarden.net' + url
    s = openWithRetry(br, url)

    tag = '<b>Flavor text</b>'
    if not tag in s:
        print 'UHOH: %s' % abil
        return ''
    s = s[s.index(tag) :]
    s = s[s.index('Generation V') :]
    s = s[s.index('\n') :]
    s = s[:s.index('id="toc"')]

    lines = s.split('\n')
    for line in lines:
        name = removeTags(line)
        if name.strip() != '':
            return name.strip()
    print 'UHOH, couldnt find %s' % abil
    return ''

def readDescrs():
    f = open('descrAbilities.txt', 'r')
    lines = f.readlines()
    f.close()
    d = {}
    for line in lines:
        (abil, descr) = line.strip().split('!')
        d[abil] = descr
    return d

def go():
    (abils, pokes) = getAbilitiesList()
    descrs = readDescrs()
    br = mechanize.Browser()

    # Write out the abilities....
    f = open('abilities-sprites.txt', 'w')
    f.write('%d\n' % (len(abils) - 1))
    ind = {}; i = 0
    for key in abils:
        abil = abils[key]
        if abil == 'Sandy Cloak': continue
        descr = openAbil(br, descrs, key, abil)
        print '%s: %s' % (abil, descr)
        f.write('%s!%s\n' % (abil, descr))
        f.flush()
        ind[abil] = str(i); i += 1

    # Write out the pokemon...
    #f.write('%d\n' % len(pokes))
    lastPoke = None
    for (poke, rest, pabils) in pokes:
        poke = poke.strip()
        if lastPoke != None and poke == lastPoke: continue
        lastPoke = poke

        outAbils = []
        for (abilAbil, abilUrl) in pabils:
            abilName = abils[abilUrl]
            if abilName == 'Sandy Cloak': continue
            extra = abilAbil.replace(abilName, '').strip()
            outAbils.append('!'.join([ ind[abilName], extra ]))

        line = '%s!%d!%s!%s\n' % (
            poke, len(outAbils), '!'.join(outAbils), rest)
        f.write(line)
    f.close()

go()
import pdb; pdb.set_trace()
