from BachFugue import *
from music21 import *
import util, math, collections, copy, Query
from FeatureExtractor import *

STANDARD_NOTE_QL = 0.25
OFF = (float(1) / 8, 'OFF')

class NoteData():
    def __init__(self, B, eIndex):
        self.eIndex = eIndex
        self.numE = B.numE - 1
        self.BnumV = B.numV
        self.Bbt = B.bt
        self.Bql = B.ql
        self.DIV = B.DIV
        self.e = B.epochs[eIndex]
        self.m = self.getMeasure()
        self.beat = self.eIndexToBeat()
        self.f = Counter()
        self.featureSet = set([ContinuityExtractor, \
            VoiceLeadingExtractor, InterVoiceExtractor])
        self.iv = InterVoiceExtractor(B, eIndex).getFeatures()
        self.cn = ContinuityExtractor(B, eIndex).getFeatures()
        self.vl = VoiceLeadingExtractor(B, eIndex).getFeatures()
        self.it = VoiceLeadingExtractor(B, eIndex).getIdentityTransition()
        #self.addFeature(InterVoiceExtractor, B, eIndex, self.iv)
        #self.addFeatureSets(self.featureSet, B, eIndex)
   
    def addFeature(self, extractor, B, eIndex, obj):
        obj += extractor(B, eIndex).getFeatures()       

    def addFeatureSets(self, extractorFnSet, B, eIndex):
        for extractorFn in extractorFnSet:
            self.f += extractorFn(B, eIndex).getFeatures()

    def getMeasure(self):
        for ne in self.e:
            if ne is not None:
                return ne.measure
        return None

    def eIndexToBeat(self):
        extraEpochs = self.eIndex % float(self.DIV)
        extraBeats = extraEpochs * (self.Bbt / float(self.Bql * self.DIV))
        return extraBeats

    def __str__(self):
        eString = ' '
        for i in range(len(self.e)):
            eString += ' ' + str(self.e[i])
        ndString = 'M %s B %s: %s' % (self.m, self.beat, eString)
        return ndString

def countPitchChange(Bname):
    noteDataList = Data[Bname]
    totV = noteDataList[0].BnumV 
    numE = noteDataList[0].numE  
    DIV = noteDataList[0].DIV
    for i in range(0, numE - 1):
        it = noteDataList[i].it
        for x in it:
            t = Query.isType(x[0], x[1])  
            if t not in changeProb:
                changeProb[t] = Counter()
            pname, cname = x
            pname = pname % 12
            cname = cname % 12
            changeProb[t][(pname, cname)] += 1

                       
def countDuration(Bname):
    ## need to take care of terminating and new voices
    noteDataList = Data[Bname]
    totV = noteDataList[0].BnumV 
    numE = noteDataList[0].numE  
    DIV = noteDataList[0].DIV
    s = scalingFactor[Bname]
    pre = [Query.BEGIN_RHYTHM for _ in range(totV)]
    for i in range(numE - 1):
        cnNext = noteDataList[i + 1].cn
        for v in range(totV):
            if cnNext[v] == 'isContd': continue
            if cnNext[v] == 'isTer' or cnNext[v] == 'isNew':
                note = noteDataList[i].e[v]
                cur = (note.sumQL, note.noteStartBeat)
            elif cnNext[v] == 'isNewVoice' or cnNext[v] == 'isOff':
                
                if i + DIV > numE:
                    cnNextQl = noteDataList[i : numE]
                else:
                    cnNextQl = noteDataList[i : (i + DIV)]
                isOff = [x.cn[v] == 'isNewVoice' or x.cn[v] == 'isOff' for x in cnNextQl]
                if False in isOff:
                    continue
                else:
                    cur = Query.OFF_RHYTHM     
            if pre[v] not in durationProb:
                durationProb[pre[v]] = Counter()
            
            durationProb[pre[v]][cur] += 1
            pre[v] = cur
    # manually subtracting 'redundant' ('OFF', 'OFF') entries because of extra voices
    # assuming a fugue normally would not exceed 4 running voices
    
    redundance = (totV - 4) * numE
    durationProb[Query.OFF_RHYTHM][Query.OFF_RHYTHM] = \
        max(durationProb[Query.OFF_RHYTHM][Query.OFF_RHYTHM] - redundance, 0)
     
    for prev in durationProb:
        if prev != Query.BEGIN_RHYTHM and prev != Query.OFF_RHYTHM\
                 and Query.OFF_RHYTHM in durationProb[prev]:
            durationProb[prev][Query.OFF_RHYTHM] = durationProb[prev][Query.OFF_RHYTHM] / 8
    
                   
           
     
            
                        
def initTransition():

    maxV = max([Data[Bname][0].BnumV for Bname in Data])
     
    for totV in range(maxV + 1):
        transitionProb[totV] = dict()
               
    
def shortEpochStr(e):
    result = ''
    for n in e:
        if n is None:
            result += 'NA, '
        else:
            result += str(n.pitch.name) + str(n.pitch.octave) + ', '
    return result

def countTransition(Bname):
    noteDataList = Data[Bname]
    totV = noteDataList[0].BnumV
    numE = noteDataList[0].numE
    DIV = noteDataList[0].DIV

    prevTrans = [Query.beginStr for _ in range(totV)]
    for i in range(numE):
        vl = noteDataList[i].vl
        ep = noteDataList[i].e
        numPresent = sum([n is not None for n in ep])
        actIndex = [v for v in range(totV) if \
            (vl[v] != 'isContd' and vl[v] != 'isOff' and vl[v] != 'isTer')]
        if len(actIndex) == 0:
            continue
        selectPrev = [prevTrans[v] for v in actIndex]
        selectCurr = [vl[v] for v in actIndex]

        if tuple(selectPrev) not in transitionProb[len(actIndex)]:
            transitionProb[len(actIndex)][tuple(selectPrev)] = Counter()
        transitionProb[len(actIndex)][tuple(selectPrev)][tuple(selectCurr)] += 1
        for v in actIndex:
            prevTrans[v] = vl[v]

             
def countInterval(Bname):
    noteDataList = Data[Bname]  
    totV = noteDataList[0].BnumV
    numE = noteDataList[0].numE
    for i in range(numE):
        numV = len(noteDataList[i].iv)
        if numV not in intervalProb:
            intervalProb[numV] = Counter()
        iv = noteDataList[i].iv
        intervalProb[numV][iv] += 1


def countNote(Bname):
    noteDataList = Data[Bname]
    totV = noteDataList[0].BnumV
    numE = noteDataList[0].numE
    for i in range(numE):
        epoch = noteDataList[i].e
        for v in range(totV):
            if epoch[v] is not None:
                n = epoch[v].pitch.ps
                noteProb[n] += 1

def getScalingFactor(B):
    noteList = converter.parse(B.path).recurse().getElementsByClass('Note')
    #noteList = corpus.parse(B.path).recurse().getElementsByClass('Note')
    qlCount = Counter()
    for n in noteList:
        qlCount[n.quarterLength] += 1
    print qlCount
    print 'QL Counter ends'
   
    return STANDARD_NOTE_QL / float(qlCount.most_common(1)[0][0])
    
    

def main():
    BachFugueList = util.readFile('fugueData.pickle', False)

    global Data
    global durationProb
    global transitionProb
    global intervalProb
    global noteProb
    global changeProb
    global scalingFactor
    
     
    Data = dict()
    scalingFactor = dict()
    durationProb = dict()
    transitionProb = dict()
    changeProb = dict()
    noteProb = Counter()

    intervalProb = Counter()
    for B in BachFugueList:      
        Data[B.name] = [NoteData(B, eIndex) for eIndex in range(1, B.numE)]
        scalingFactor[B.name] = getScalingFactor(B)

    initTransition()
    
    for Bname in Data:
        countDuration(Bname)
        countTransition(Bname)
        countInterval(Bname)
        countNote(Bname)
        countPitchChange(Bname)
        
    util.writeFile('noteData.pickle', (durationProb, transitionProb, intervalProb, noteProb, changeProb), False)    

if __name__ == '__main__':
    main()
