import NoteData, util, Query
from collections import *

def closestTransition(target, transitions):
    targetEval = Eval(target)
    dist = [None for _ in range(len(transitions))]
    for i, t in enumerate(transitions):
        dist[i] = (targetEval.compare(Eval(t)), t)
    return min(dist)[1]    

class EvalConst:
    def __init__(self):
        self.const = Counter()
        self.const['direction'] = 10
        self.const['pitch'] = 2
        self.const['BEGIN'] = 1000
        self.const['newVoice'] = 1000
    
    def getPitch(self):
        return self.const['pitch']

    def getDir(self):
        return self.const['direction']

    def getBegin(self):
        return self.const['BEGIN']
    
    def getNewVoice(self):
        return self.const['newVoice']

class Eval:
    def __init__(self, P):
        self.P = P
        self.features = Counter()
        self.const = EvalConst()
        for v, t in enumerate(P):
            self.addDirection(t)
            self.addIdentity(t, v)
            self.addRule(t)
            self.addPitchDiff(t, v)
            self.addMisc(t)
    
    def getEval(self):
        return self.features

    def compare(self, b):
        bCounter = b.getEval()
        sqSelf = util.dotProduct(self.features, self.features)
        sqB = util.dotProduct(bCounter, bCounter)
        cross = 2 * util.dotProduct(self.features, bCounter)
        return sqSelf - cross + sqB
            
    def addDirection(self, tran):
        direction = tran[-1]
        self.features[direction] += self.const.getDir()
    def addIdentity(self, tran, v):
        self.features[tran + str(v)] += 1
    def addRule(self, tran):
        self.features[tran] += 1
    def estPitchDiff(self, tran):
        if tran[-1] == 'D' or tran[-1] == 'U':
            trimmed = tran[0:(len(tran)-1)]
            if trimmed == 'isChromaticStep':
                return 1
            if trimmed == 'isWholeStep':
                return 2
            if trimmed == 'isSkip':
                return 4
            if trimmed == 'isLeap':
                return 10
        return 0
        
    def addPitchDiff(self, tran, v):
        power = 2
        self.features['PitchDiff'] += pow(self.estPitchDiff(tran), self.const.getPitch())
        self.features['PitchDiff' + str(v)] += pow(self.estPitchDiff(tran), self.const.getPitch())
    def addMisc(self, tran):
        if tran == Query.beginStr:
            self.features['begin'] += self.const.getBegin()
        

