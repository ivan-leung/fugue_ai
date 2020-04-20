from music21 import *
from Eval import *
from collections import Counter
import collections, copy, util, random, UnitTesting, Query, Melody

def composeOneVoiceRhythms():
    totQL = 0
    rhythms = []
    prev = (1.0, 0.0)
    #prev = Query.BEGIN_RHYTHM
    while totQL < Query.MAX_QL:        
        prevQL, prevBT = prev
        currQL, currBT = util.weightedRandomChoice(dProb[prev])
        if currBT == Query.OFF_RHYTHM[1]:
            prev = Query.OFF_RHYTHM
            rhythms.append((Query.OFF_RHYTHM, totQL))            
            totQL += Query.OFF_RHYTHM[0]
            continue
        if totQL % 1 < currBT: # insert rest to catch up
            deficit = currBT - (totQL % 1)
            totQL += deficit
        elif totQL % 1 > currBT: # need to catch up ACROSS the beat line
            deficit = currBT + 1 - (totQL % 1)
            totQL += deficit
        prev = (currQL, currBT)
        rhythms.append(((currQL, currBT), totQL))        
        totQL += currQL
    return rhythms 

def fillRhythm(epochs, v, s, e, ql, bt):
    if bt == Query.OFF_BEAT:
        return
    numE = Query.MAX_QL * Query.DIV
    if s >= numE:
        return
    ql = min(ql, Query.MAX_QL - float(s) / Query.DIV)
    prevEpochs = [epochs[i][v] is None for i in range(max(0, s - Query.DIV), s)]
    if False in prevEpochs:
        epochs[s][v] = (Query.noteStr, ql)
    else:    
        epochs[s][v] = (Query.newVStr, ql)
    for i in range(s + 1, min(e, numE)):
        epochs[i][v] = (Query.nConStr, None)

def fillRest(epochs, v, s, e):
    epochs[s][v] = (Query.restStr, float(e - s) / Query.DIV)
    for i in range(s + 1, e):
        epochs[i][v] = (Query.rConStr, None)    

def elimNewV(epochs, i, chosen, numE):
    ql = epochs[i][chosen][1]
    fillRest(epochs, chosen, i, int(i + ql * Query.DIV))
    cur = int(i + ql * Query.DIV)
    while cur < numE and epochs[cur][chosen][0] != Query.noteStr:
        cur += 1
    if cur != numE:
        #print 'should be', (Query.newVStr, epochs[cur][chosen][1])
        newQL = epochs[cur][chosen][1]
        epochs[cur][chosen] = (Query.newVStr, newQL)
    #print 'voice', chosen, 'post change', cur, epochs[cur]

def rhythmsToEpochs(R):
    numE = Query.MAX_QL * Query.DIV
    epochs = [[None for v in range(Query.VOICES)] for e in range(numE)]
    for v in range(Query.VOICES):
        voiceLine = R[v]
        for (ql, bt), start in voiceLine:
            sEpoch = int(start * Query.DIV)
            eEpoch = int(sEpoch + ql * Query.DIV)
            fillRhythm(epochs, v, sEpoch, eEpoch, ql, bt)

    for i in range(numE):
        for v in range(Query.VOICES):
            if epochs[i][v] is None:
                j = i
                while j < numE and epochs[j][v] is None:
                    j += 1
                fillRest(epochs, v, i, j)

    for i, e in enumerate(epochs):
        newVoiceList = [j for j, (vStr, ql) in enumerate(e) if vStr == Query.newVStr]
        if len(newVoiceList) > 1:
            #print 'amending epoch', i
            #print 'pre change', e
            chosenList = random.sample(newVoiceList, len(newVoiceList) - 1)
            for chosen in chosenList:
                elimNewV(epochs, i, chosen, numE)  
            #print 'post chanage', e          
                    
    #for i, e in enumerate(epochs):
    #    print i, e
    
    return epochs
    
                    
def composeRhythms():
    rhythms = [composeOneVoiceRhythms() for v in range(Query.VOICES)]
    epochs = rhythmsToEpochs(rhythms)
    #test1 = UnitTesting.TimeConsistencyTest(epochs)
    #test1.runTest()
    #test1.getResult()
    return epochs

def getRequiredIntervals(epoch, pIndex, fIndex):
    result = [None for _ in range(len(fIndex) - 1)]
    for i in range(len(fIndex) - 1):
        diff = epoch[fIndex[i + 1]][0] - epoch[fIndex[i]][0]
        result[i] = (diff, pIndex.index(fIndex[i]), pIndex.index(fIndex[i + 1]))
    return result

def match(req, full):
    for psDiff, vLow, vHigh in req:
        if sum(full[vLow: vHigh]) != psDiff:
            return False
    return True    
        
def filterIntervals(iProb, pIndex, fIndex, epoch):
    if len(fIndex) < 2:
        return iProb[len(pIndex) - 1]
    requiredIntervals = getRequiredIntervals(epoch, pIndex, fIndex)
    filteredDict = Counter()
    for x in iProb[len(pIndex) - 1]:
        if match(requiredIntervals, x):
            filteredDict[x] = pow(iProb[len(pIndex) - 1][x], Query.EXP)
    return filteredDict 

def intervalsToPitch(intervals, lowest):
    return tuple(lowest + sum(intervals[0:i]) for i in range(len(intervals) + 1))

def inRange(pitchSet, rangeList):
    for i, n in enumerate(pitchSet):
        if n not in rangeList[i]:
            return False
    return True

def expandPitchSet(intervals, pIndex, fIndex, epoch):
    voiceRangeList = [Query.voiceRange(v) for v in pIndex]
    if len(fIndex) == 0: # no constraints on pitch
        result = Counter()
        for x in intervals:
            pitches = [intervalsToPitch(x, i) for i in voiceRangeList[0]]
            filteredPitches = [p for p in pitches if inRange(p, voiceRangeList)]
            for p in filteredPitches:
                result[p] = intervals[x]
        return result
    else: # every interval is anchored
        result = Counter()
        anchor = pIndex.index(fIndex[0])
        for x in intervals:
            pitch = [epoch[fIndex[0]][0] for _ in range(len(pIndex))]
            for i in reversed(range(0, anchor)):
                pitch[i] = pitch[i + 1] - x[i]
            for i in range(anchor + 1, len(pIndex)):
                pitch[i] = pitch[i - 1] + x[i - 1]
            if inRange(pitch, voiceRangeList):
                result[tuple(pitch)] = intervals[x]
        return result
        
def calculateTransition(preTran, pre2, pitchSetDict, pIndex, aIndex):
    hasBegin = [pre2[i] == Query.beginStr for i in pIndex]
    for pitches in pitchSetDict:
        curTran = tuple(Query.isType(pre2[aI], pitches[pIndex.index(aI)]) for aI in aIndex)
        pitchSetDict[pitches] *= pow((Query.LAPLACE + tProb[len(aIndex)][preTran][curTran]), Query.EXP)
        for j, aI in enumerate(aIndex):
            if curTran[j] not in cProb:
                continue
            cKey = (pre2[aI] % 12, pitches[pIndex.index(aI)] % 12) 
            pitchSetDict[pitches] *= pow((Query.LAPLACE + 10 * cProb[curTran[j]][cKey]), Query.EXP)

def singleVoiceSim(pre1, pre2, epoch, v):
    preTran = Query.isType(pre1[v], pre2[v])
    nRange = Query.voiceRange(v)
    result = Counter()
    for n in nRange:
        result[n] = pow(nProb[n] + Query.LAPLACE, Query.EXP)
        if preTran in cProb:
            cKey = (pre2[v] % Query.TONES, n % Query.TONES)
            result[n] *= pow((cProb[preTran][cKey] + Query.LAPLACE), Query.EXP)
    chosen = util.weightedRandomChoice(result)
    pre1[v] = pre2[v]
    origQL = epoch[v][1]
    epoch[v] = (chosen, origQL)
    return (pre1, pre2)

def fillEpoch(pre1, pre2, epoch):
    lost = False
    aIndex = [i for i, (vStr, ql) in enumerate(epoch) if Query.isActive(vStr)]    
    if len(aIndex) == 0:
        #print 'return earlly'
        return (pre1, pre2, lost) 
    pIndex = [i for i, (vStr, ql) in enumerate(epoch) if Query.isPresent(vStr)]
    if len(pIndex) == 1:
        # implicitly, len(aIndex) == 1
        pre1, pre2 = singleVoiceSim(pre1, pre2, epoch, pIndex[0])
        return (pre1, pre2, lost)       
    fIndex = [i for i, (vStr, ql) in enumerate(epoch) if isinstance(vStr, int) or isinstance(vStr, float)]
    if len(aIndex) + len(fIndex) != len(pIndex):
        print 'a', len(aIndex), 'p', len(pIndex), 'f', len(fIndex)
        print epoch
        raise Exception('does not sum correctly')
    interVoiceDict = filterIntervals(iProb, pIndex, fIndex, epoch)
    pitchSetDict = expandPitchSet(interVoiceDict, pIndex, fIndex, epoch)
    preTran = tuple(Query.isType(pre1[i], pre2[i]) for i in aIndex)
    if preTran not in tProb[len(aIndex)]:
        #print 'not found'
        lost = True
        #print 'before', preTran,
        preTran = closestTransition(preTran, tProb[len(aIndex)].keys())
        #print 'after', preTran
    calculateTransition(preTran, pre2, pitchSetDict, pIndex, aIndex)
    chosen = tuple(util.weightedRandomChoice(pitchSetDict))
    for i, pI in enumerate(pIndex):
        origQL = epoch[pI][1]
        epoch[pI] = (chosen[i], origQL)
    for aI in aIndex:
        pre1[aI] = pre2[aI]
        pre2[aI] = chosen[pIndex.index(aI)]
    return (pre1, pre2, lost)

def limitBegins(epochs, i, pre1, pre2):
    aIndex = [j for j, (vStr, ql) in enumerate(epochs[i]) if Query.isActive(vStr)] 
    preTran = [Query.isType(pre1[j], pre2[j]) for j in aIndex]
    beginList = [j for j, tran in enumerate(preTran) if tran == Query.beginStr]
    if sum(beginList) > 1:
        #print 'beginList > 1', i, epochs[i]
        #print 'beginList, aIndex', aIndex
        chosenList = random.sample(beginList, len(beginList) - 1)
        for chosen in chosenList:
            elimNewV(epochs, i, chosen, int(Query.MAX_QL * Query.DIV))
        #print 'post adjust', i, epochs[i]

def fillNote(epochs, i, v):
    note = epochs[i][v][0]
    numE = Query.MAX_QL * Query.DIV
    end = i + int(epochs[i][v][1] * Query.DIV)     
    for j in range(i + 1, min(end, numE)):
        epochs[j][v] = (note, None)  
    
def composeNoteEpochs(epochs):
    missedTransition = 0
    pre1 = [None for v in range(Query.VOICES)]
    pre2 = [Query.beginStr for v in range(Query.VOICES)]
    for i, e in enumerate(epochs):
        limitBegins(epochs, i, pre1, pre2)
        pre1, pre2, lost = fillEpoch(pre1, pre2, e)
        if lost:
            missedTransition += 1
        for v in range(Query.VOICES):
            if e[v][1] is not None and Query.isPresent(e[v][0]):
                fillNote(epochs, i, v)
        #print i, e  
    print 'missed transition', missedTransition
    return epochs

def appendNoteRest(part, data):
    vStr, ql = data
    if ql is None:
        return
    assert vStr == Query.restStr or isinstance(vStr, int) or isinstance(vStr, float)
    if vStr == Query.restStr:
        rest = note.Rest(quarterLength = ql)
        part.append(rest)
    else:
        N = note.Note(ps=vStr, quarterLength = ql)
        part.append(N)

def epochsToScore(epochs):
    score = stream.Score()
    partList = [stream.Part() for v in range(Query.VOICES)]
    numE = Query.MAX_QL * Query.DIV
    for i in range(numE):
        for v in range(Query.VOICES):
            appendNoteRest(partList[v], epochs[i][v])
    partList = list(reversed(partList))
    for part in partList:
        score.append(part)
    score.show()


def initProbs():
    global dProb, tProb, iProb, nProb, cProb
    dProb, tProb, iProb, nProb, cProb = util.readFile('noteData.pickle')


def main():
    initProbs()
    rhythms = composeRhythms()
    noteEpochs = composeNoteEpochs(rhythms)
    score = epochsToScore(noteEpochs)

if __name__ == '__main__':
    main()
