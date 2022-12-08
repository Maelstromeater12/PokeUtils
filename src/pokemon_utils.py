import random

class pType:
    def __init__(self, name, profile):
        self.name = name
        self.offGood = profile['og']
        self.offBad = profile['ob']
        self.defGood = profile['dg']
        self.defBad = profile['db']
        self.inv = profile['inv']
        self.inef = profile['inef']

class MoveSet:
    def __init__(self, moveset=None):
        self.moves = []
        self.coverage = []
        self.bounce = []
        if moveset is not None: self.buildMoveset(moveset.moves)

    def buildMoveset(self, moves):
        for move in moves:
            self.addMove(move)

    def clearState(self):
        self.moves = []
        self.coverage = []
        self.bounce = []
    
    def addMove(self, move):
        self.moves.append(move)
        coverage = move.offGood
        bounce = move.offBad
        for entry in coverage:
            if entry not in self.coverage: self.coverage.append(entry)
            if entry in self.bounce: self.bounce.remove(entry)
        for entry in bounce:
            if entry not in self.coverage and entry not in self.bounce: self.bounce.append(entry)
        for entry in self.bounce:
            if entry not in bounce: self.bounce.remove(entry)
    
    def removeMove(self, move):
        self.moves.remove(move)
        newMoveset = MoveSet()
        for entry in self.moves:
            newMoveset.addMove(entry)
        self.clearState()
        self.buildMoveset(newMoveset.moves)

    def getRating(self):
        return len(self.coverage) - len(self.bounce)

    def getMoveNames(self):
        movenames = []
        for move in self.moves:
            movenames.append(move.name)
        return movenames

    def toString(self):
        rString = self.moves[0].name
        for move in self.moves[1:]:
            rString += ', '+move.name
        return rString

def run(typeDict):
    types = {}
    for entry in typeDict:
        types[entry] = pType(entry, typeDict[entry])
    answer = '0'
    while answer != '8':
        print('What utility would you like to run?')
        print('1. Best Moveset for Type')
        print('2. Best Moveset for Type from collection')
        print('3. Rate Type')
        print('4. Rate Moveset')
        print('5. Rate Composition')
        print('6. Reccomend fill types for current team - STAB Only')
        print('7. Reccomend fill types for current team - Using Best Moveset')
        print('8. Generate best team from a collection')
        print('9. Exit')
        answer = str(input())
        if answer in ['1', '2']:
            ptype = decodeType(input('Enter the pokemon type (split multitypes with a /): '), types)
            if answer == '1': bestMoves(types, ptype, True)
            elif answer == '2': bestMoves(getTypeCollection(types), ptype, True)
        elif answer == '9': return
        else:
            print('Invalid option')

def decodeType(input, types):
    ptype = input.split('/')
    for i in range(len(ptype)): ptype[i] = types[ptype[i].lower()]
    return ptype

# Best moveset for type from collection
def getTypeCollection(types):
    typenames = types.keys()
    tColl = {}
    answer = input('Please enter a comma seperated list of types: ')
    answers = answer.replace(' ','').split(',')
    for a in answers:
        if a.lower() in typenames: tColl[a.lower()] = types[a.lower()]
        else: print(a+' registered as invalid type')
    return tColl

# Best moveset for type
def bestMoves(types, typeCombo, printResult=False):
    stabMoves = []
    ratings = {}
    evaledCombos = []
    moveset = MoveSet()
    if typeCombo[0].name != 'normal': 
        stabMoves = [typeCombo[0].name]
        moveset.addMove(typeCombo[0])
    if len(typeCombo) > 1 and typeCombo[1].name != 'normal':
        moveset.addMove(typeCombo[1])
        stabMoves.append(typeCombo[1].name)

    nestSize = 4-len(stabMoves)
    argsDict = {'types': types, 'stabMoves': stabMoves, 'ts': stabMoves.copy(), 
    'moveset': moveset, 'ratings': ratings, 'evaledCombos': evaledCombos}
    buildMovesetRankings(nestSize, argsDict)

    ratingOrder = []
    for rating in ratings:
        rnum = int(rating)
        if len(ratingOrder) < 1: 
            ratingOrder.append(rnum)
            continue
        idx = 0
        while idx < len(ratingOrder) and ratingOrder[idx] > rnum: idx += 1
        ratingOrder.insert(idx, rnum)
    if printResult:
        top5 = []
        idx = 0
        while len(top5) < 5:
            for ms in ratings[ratingOrder[idx]]: top5.append(ms)
            idx += 1
        for ms in top5:
            print(str(ms.getRating())+': '+ms.toString()+' Eff: '+str(len(ms.coverage))+', Bad: '+str(len(ms.bounce)))
    return random.choice(ratings[ratingOrder[0]])

def buildMovesetRankings(numMoves, argsDict):
    for mtype in argsDict['types']:
        if mtype in argsDict['stabMoves'] or mtype in argsDict['ts']: continue
        if numMoves > 1: 
            argsDict['moveset'].addMove(argsDict['types'][mtype])
            argsDict['ts'].append(argsDict['types'][mtype].name)
            buildMovesetRankings(numMoves-1, argsDict)
            argsDict['moveset'].removeMove(argsDict['types'][mtype])
            argsDict['ts'].remove(argsDict['types'][mtype].name)
        else:
            argsDict['ts'].append(argsDict['types'][mtype].name) 
            checkMoveset(argsDict['stabMoves'], argsDict['types'], argsDict['ts'],
                        argsDict['evaledCombos'], argsDict['moveset'], argsDict['ratings'])
            argsDict['ts'].remove(argsDict['types'][mtype].name)

def checkMoveset(stabMoves, types, ts, evaledCombos, moveset, ratings):
    dupCheck = stabMoves.copy()
    for mtype in ts: dupCheck.append(types[mtype])
    if movesetInList(dupCheck, evaledCombos): return None
    moveset.addMove(types[ts[len(ts)-1]])
    rating = moveset.getRating()
    if rating not in ratings: ratings[rating] = []
    ratings[rating].append(MoveSet(moveset))
    evaledCombos.append(moveset.moves.copy())
    moveset.removeMove(types[ts[len(ts)-1]])

def movesMatch(moves1, moves2):
    movenames1 = getMoveNames(moves1)
    movenames2 = getMoveNames(moves2)
    if 'ice' in movenames2 and 'ground' in movenames2 and \
        'ice' in movenames1 and 'ground' in movenames1:
        x = 1
    for move in movenames1:
        if move not in movenames2: return False
    return True

def movesetInList(moves, mlist):
    movenames = getMoveNames(moves)
    if 'ice' in movenames and 'ground' in movenames:
        x = 1
    for ms in mlist:
        if movesMatch(moves, ms): return True
    return False

def getMoveNames(mlist):
    movenames = []
    for move in mlist:
        movenames.append(move.name)
    return movenames

# Base type rating
def typeRating(type1, type2=None):
    pass

# Best moveset rating
def movesetRating(moveset):
    rating = moveset.getRating()
    pass

# Composition rating
# Best type fills for current team - STAB Only
# Best type fills for current team - Including Best Moveset
# Best team fills from collection
def __main__():
    typeDict = {
        'fire': {'og': ['bug', 'grass', 'ice', 'steel'], 'dg': ['bug', 'fairy', 'fire', 'grass', 'ice', 
            'steel'], 'inv': [], 'ob': ['dragon', 'fire', 'rock', 'water'], 'inef': [], 
            'db': ['ground', 'rock', 'water']},
        'electric': {'og': ['flying', 'water'], 'dg': ['electric', 'flying', 'steel'], 'inv': [] , 
            'ob': ['dragon', 'electric', 'grass'], 'inef': [], 'db': ['ground']},
        'water': {'og': ['fire', 'ground', 'rock'], 'dg': ['fire', 'ice', 'steel', 'water'], 'inv': []
            , 'ob': ['dragon', 'water', 'grass'], 'inef': [], 'db': ['electric', 'grass']},
        'grass': {'og': ['ground', 'rock', 'water'], 'dg': ['electric', 'grass', 'ground', 'water']
            , 'inv': [], 'ob': ['bug', 'dragon', 'fire', 'flying', 'grass', 'poison', 'steel'], 
            'inef': [], 'db': ['bug', 'fire', 'flying', 'ice', 'poison']},
        'flying': {'og': ['bug', 'fighting', 'grass'] , 'dg': ['bug', 'fighting', 'grass'], 'db': []
            , 'inv': ['ground'], 'ob': ['rock', 'electric', 'steel'], 'inef': ['electric', 'ice', 'rock']},
        'ice': {'og': ['dragon', 'flying', 'grass', 'ground'], 'dg': ['ice'], 'inv': [], 'inef': []
            , 'ob': ['fire', 'ice', 'steel', 'water'], 'db': ['fighting', 'fire', 'rock', 'steel']},
        'ghost': {'og': ['ghost', 'psychic'], 'dg': ['bug', 'poison'], 'inv': ['normal', 'fighting']
            , 'ob': ['dark'], 'inef': ['normal'], 'db': ['dark', 'ghost']},
        'psychic': {'og': ['fighting', 'poison'], 'dg': ['fighting', 'psychic'], 'inv': []
            , 'ob': ['psychic', 'steel'], 'inef': ['dark'], 'db': ['dark', 'ghost', 'bug']},
        'dragon': {'og': ['dragon'], 'dg': ['electric', 'fire', 'grass', 'water'], 'inv': []
            , 'ob': ['steel'], 'inef': ['fairy'], 'db': ['dragon', 'fairy', 'ice']},
        'dark': {'og': ['ghost', 'psychic'], 'dg': ['dark', 'ghost'], 'inv': ['psychic'], 
            'ob': ['dark', 'fairy', 'fighting'], 'inef': [], 'db': ['bug', 'fairy', 'fighting']},
        'fairy': {'og': ['dark', 'dragon', 'fighting'], 'dg': ['bug', 'dark', 'fighting'], 'inv': ['dragon']
            , 'ob': ['fire', 'poison', 'steel'], 'inef': [], 'db': ['poison', 'steel']},
        'normal': {'og': [], 'dg': [], 'inv': ['ghost'], 'ob': ['rock', 'steel'], 'inef': ['ghost']
            , 'db': ['fighting']},
        'fighting': {'og': ['dark', 'ice', 'normal', 'rock', 'steel'], 'dg': ['bug', 'dark', 'rock']
            , 'inv': [], 'ob': ['bug', 'fairy', 'flying', 'poison', 'psychic'], 'inef': ['ghost']
            , 'db': ['fairy', 'flying', 'psychic']},
        'poison': {'og': ['fairy', 'grass'], 'dg': ['fighting', 'poison', 'bug', 'grass', 'fairy']
            , 'inv': [], 'ob': ['poison', 'ground', 'rock', 'ghost'], 'inef': ['steel']
            , 'db': ['ground', 'psychic']},
        'ground': {'og': ['electric', 'fire', 'poison', 'rock', 'steel'], 'dg': ['poison', 'rock']
            , 'inv': ['electric'], 'ob': ['bug', 'grass'], 'inef': ['flying'], 'db': ['grass', 'ice', 'water']},
        'rock': {'og': ['bug', 'fire', 'flying', 'ice'], 'dg': ['fire', 'flying', 'normal', 'poison']
            , 'inv': [], 'ob': ['fighting', 'ground', 'steel'], 'inef': []
            , 'db': ['fighting', 'grass', 'ground', 'steel', 'water']},
        'bug': {'og': ['dark', 'grass', 'psychic'], 'dg': ['fighting', 'grass', 'ground'], 'inv': []
            , 'ob': ['fairy', 'fighting', 'fire', 'flying', 'ghost', 'poison', 'steel'], 'inef': []
            , 'db': ['fire', 'flying', 'rock']},
        'steel': {'og': ['ice', 'rock'], 'inv': ['poison'], 'ob': ['electric', 'fire', 'steel', 'water']
            , 'dg': ['bug', 'dark', 'dragon', 'flying', 'ghost', 'grass', 'ice', 'normal', 'psychic', 
            'rock', 'steel'], 'inef': [], 'db': ['fighting', 'fire', 'ground']
        }
    }
    run(typeDict)

__main__()