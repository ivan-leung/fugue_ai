DIV = 8

noteStr = 'New Note--'
restStr = 'New Rest--'
nConStr = '--------n-'
rConStr = '--------r-'
newVStr = 'New Voice-'
beginStr = '--BEGIN---'
BEGIN_RHYTHM = (0, 0)
OFF_RHYTHM = (1/float(DIV), 'OFF')
OFF_BEAT = 'OFF'
LAPLACE = 0.01 # laplace smoothing param

EXP = 1
MAX_QL = 40 # a composition of |TOT_QL| quarterlengths
VOICES = 4  # a composition of |VOICES| voices
TONES = 12 # 12 tones per octave


def isPresent(vStr):
    return vStr != restStr and vStr != rConStr
def isActive(vStr):
    return vStr == noteStr or vStr == newVStr

def isConst(p, c):
    return p == c
def isChromaticStep(p, c):
    return abs(p - c) == 1
def isWholeStep(p, c):
    return abs(p - c) == 2
def isSkip(p, c):
    return abs(p - c) > 2 and abs(p - c) <= 6
def isLeap(p, c):
    return abs(p - c) > 6 and abs(p - c) % 12 != 0
def isOctave(p, c):
    return abs(p - c) == 12
def U(p, c):
    return c > p
def D(p, c):
    return p > c
def isType(p, c):
    if p == beginStr or c == beginStr:
        return beginStr
    fnList = [isConst, isChromaticStep, isWholeStep, isSkip, isLeap, isOctave, U, D]
    result = ''
    for fn in fnList:
        if fn(p, c):
            result += fn.__name__
    return result

def voiceRange(i):
    sDict = {0: 40, 1: 48, 2:55, 3:60}
    span = 2 * TONES + 8
    return range(sDict[i], sDict[i] + span)





