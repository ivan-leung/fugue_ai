from collections import *
from music21 import *
import util, math, copy
import sys

global DIV
DIV = 8

class NoteEpoch():
    def __init__(self, n, sumQL, m, numQL, numBt):
        self.measure = m
        if n.isChord:
            self.pitch = [p for p in n.pitches][0]
            self.octave = [p.octave for p in n.pitches][0]
        else:
            self.pitch = copy.deepcopy(n.pitch)
            self.octave = n.octave
        self.beat = (n.offset + sumQL - 1 / float(DIV))/ float(numQL) * float(numBt) % float(1)
        # only accurate at upon terminatio of the note
        self.noteStartBeat = ((n.offset+ n.quarterLength- sumQL) / float(numQL) * float(numBt)) % float(1)
        self.sumQL = sumQL
        self.totQL = n.quarterLength

    def getPitchName(self):
        return self.pitch.name

    def printNoteEpoch(self):
        print 'M %s B %s, %s' % (self.measure, self.beat, self.pitch.name)

    def __str__(self):
        return str((str(self.pitch.name) + str(self.octave), self.sumQL))
        

class BachFugue():
    '''
    __init__
    ========================================================
    @param path: path to a Bach fugue .xml file
    @param fugueNum: fugue number of the fugue at path |path|

    Main data storage:
    #########################################################
    self.voices: list of (list of epochs) for each voice
    self.beatNum: list of beat numbers for each epoch in a list of epochs for any voice
    #########################################################

    Auxillary data
    #########################################################
    self.path: path to a Bach fugue .xml file
    self.name: fugue number of this fugue
    self.numM: number of measures in the Bach fugue
    self.epochQL: number of quarterlengths for each epoch. Default to 1/32
    self.measureQL: list of quarterlengths of each measure. 
        Should all be the same, in which case self.measureQL is a float for the quarterlength
    self.measureBeats: list of beats of each measure. S
        hould all be the same, in which case self.measureBeats is a float for the beat
    self.numV: number of voices in this fugue
    #########################################################

    printFugue
    ========================================================
    prints the fugue epoch by epoch
    '''
    def __init__(self, path, name):
        self.path = path
        self.name = name
        f = converter.parse(self.path)
        #f = corpus.parse(path)
        self.ql, self.bt = self.getRhythm(f)
        self.numM = self.getNumM(f)
        self.numE = int(math.ceil(self.numM * self.ql * DIV))
        self.numV, self.vList = self.getNumV(f)
        self.voices = self.getVoices(f) 
        self.epochs = self.getEpochs()
        self.DIV = DIV 
   
    def getRhythm(self, f):
        time = f.recurse().getElementsByClass('Measure')[0].timeSignature
        assert time is not None, 'Time signature not found in the first measure'
        bot = time.denominator / float(4)
        top = time.numerator
        print 'bot in ql: %s, top: %s' % (bot, top)
        ql = top * bot
        bt = time.beatCount
        print 'beatcount', bt
        return (ql, bt)
    
    def getNumM(self, f):
        totM = len(f.recurse().getElementsByClass('Measure'))
        totP = len(f.parts)
        assert totM % totP == 0, 'Unequal number of measures on different parts'
        return totM / totP

    def getNumV(self, f):
        # assume a voice id that is bigger is always a lower voice
        # a meaasure without separate voices is assigned -1 (Treble) and -2 (Bass)
        voiceSet = set()
        for i in range(len(f.parts)):
            nonVoiceID = -(i + 1)
            for m in f.parts[i].getElementsByClass('Measure'):
                vs = m.voices
                if len(vs) == 0:
                    voiceSet.add(nonVoiceID)
                else:
                    for v in vs:                     
                        voiceSet.add(int(v.id))
        voiceList = list(voiceSet)
        voiceList.sort()
        return (len(voiceList), voiceList)    

    def getVoices(self, f):         
        voiceData = [[None for i in range(self.numE)] for j in range(self.numV)]
        for i in range(len(f.parts)):
            nonVoiceID = -(i + 1)
            for m in f.parts[i].getElementsByClass('Measure'):
                sIndex = m.offset * DIV
                eIndex = sIndex + m.quarterLength * DIV
                notesInVoices = m.voices
                if len(notesInVoices) == 0:
                    notes = m.notes
                    self.addNoteList(notes, sIndex, self.vList.index(nonVoiceID), voiceData, int(m.number))
                else:
                    for i in range(len(notesInVoices)):
                        notes = notesInVoices[i].notes
                        self.addNoteList(notes, sIndex, self.vList.index(int(notesInVoices[i].id)), voiceData, int(m.number))
        return voiceData

    def addNoteList(self, notes, sIndex, vIndex, voiceData, mID):
        for n in notes:
            nIndex = int(sIndex + n.offset * DIV)
            self.fillDataPoint(n, nIndex, voiceData, vIndex, mID)
       
    def fillDataPoint(self, n, nIndex, voiceData, vIndex, mID):
        
        sPos = nIndex
        ePos = int(nIndex + n.quarterLength * DIV)
        prev = 0
        if n.tie == tie.Tie('stop') or n.tie == tie.Tie('continue'):
            prevNote = voiceData[vIndex][sPos - 1]
            if prevNote is not None:
                prev = voiceData[vIndex][sPos - 1].sumQL
        assert voiceData[vIndex][sPos] is None, 'Occupied'
        for i in range(sPos, ePos):
            voiceData[vIndex][i] = NoteEpoch(n, prev + ((i + 1 - sPos) / float(DIV)), mID, self.ql, self.bt)

    def getEpochs(self):
        return [[self.voices[v][e] for v in range(self.numV)] for e in range(self.numE)]


    def printData(self):
        for i in range(self.numE):
            L = copy.deepcopy(self.epochs[i])
            M = None
            
            for j in range(self.numV):
                if L[j] is not None:
                    M = L[j].measure
                    L[j] = (str(L[j].pitch.name) +  str(L[j].octave), L[j].beat)
            print 'M: %s, E: %s, %s' % (M, i, L)   
         
                                        
def generateFugueFileNames(args):
    prefix ='data/fugue'
    suffix = '.xml'
    return  [prefix + str(x).zfill(2) + suffix for x in args]

def generateFugueList(args):
    contd = bool(args[0])
    if contd:
        argWarning = 'Arguments: IsContinuous FugueStart FugueEnd'
        assert len(args) > 2, argWarning
        return list(range(int(args[1]), int(args[2]) + 1))
    else:
        return [int(args[i]) for i in range(1, len(args))]

def useFugue(B):
    filterList = [9, 12, 16, 19, 21, 15]
    if B.name in filterList:
        return False
    return True

def main():
    argWarning = 'Arguments: IsContinuous FugueNum1 FugueNum2 ...'
    assert len(sys.argv) > 2, argWarning
    fugueNames = generateFugueList(sys.argv[1: len(sys.argv)])
    fugueFiles = generateFugueFileNames(fugueNames)
    #fugueFiles = ['bach/bwv295', 'bach/bwv296', 'bach/bwv297', 'bach/bwv298']
    #fugueNames = [295, 296, 297, 298]
    fugueInfo = [(fugueFiles[i], fugueNames[i]) for i in range(len(fugueFiles))]
    fugueData = [BachFugue(path, name) for path, name in fugueInfo]
    fugueData = [x for x in fugueData if useFugue(x)]
    #fugueData[0].printData()
    util.writeFile('fugueData.pickle', fugueData, True)

if __name__ == '__main__':
    main()
