from BachFugue import BachFugue, NoteEpoch
from collections import *
from music21 import *
import util, math, copy

#####################################################
# FeatureExtractor class
class FeatureExtractor:
    def __init__(self, B, eIndex):
        self.B = B
        self.eIndex = eIndex
        self.features = None

    # extract features from BachFugue B at epoch eIndex
    def extractFeatures(self): raise NotImplementedError("Override me")

    # print feature data extracted by this feature extractor
    def printFeatures(self):
        print self.features
    
    # return the feature counter object
    def getFeatures(self):
        return self.features

    # sort list of NoteEpochs by pitch. Ignore null entires
    def sortEpoch(self, i):
        e = self.B.epochs[i]
        p = [(pEpoch, pIndex) for pIndex, pEpoch in enumerate(e) if pEpoch is not None]
        ps = [(p[i][0].pitch.ps, p[i][1]) for i in range(len(p))]
        ps.sort()
        arg = [t[1] for t in ps]
        return ([e[i] for i in arg], [i for i in arg])      
        

    '''
    Helper functions to evaluate various note epoch quantities
    ===================================================================================
    identity(ne): returns the (ps, duration, offset, elapsed) of ne
    elapsed(ne): returns the elapsed duration of ne
    duration(ne): returns total duration of ne
    pitch(ne): returns pitch of ne, as string
    octave(ne): returns octave on ne, as int
    offset(ne): returns offset of ne relative to measure start
    isContd(ne): returns True if ne at this epoch is a continuation of same note
    '''
    def identity(self, ne):
        if ne is None: return None
        return (ne.pitch.ps, ne.n.quarterLength, ne.n.offset, ne.sumQL)
    def elapsed(self, ne):
        return ne.sumQL
    def duration(self, ne):
        return ne.n.quarterLength
    def octave(self, ne):
        return ne.octave
    def offset(self, ne):
        return ne.n.offset
    # continuity features:
    # the voice in this epoch is continuation of the last
    def isContd(self, pre, cur):
        return (cur is not None) and (cur.sumQL > 1 / float(self.B.DIV))
    # the voice in this epoch marks the beginning of a new voice
    def isNewVoice(self, pre, cur):
        return (cur is not None) and (pre is None)
    # the voice in this epoch is None, marking the termination of the last note
    # only count as termination if the next 2 ql is off
    def isTer(self, pre, cur):         
        return (pre is not None) and (cur is None)
    # the voice in this epoch is a continuation of silence
    def isOff(self, pre, cur):
        return (pre is None) and (cur is None)
    # the voice in this epoch is the beginning of a changed note
    def isNew(self, pre, cur):
        return (pre is not None) and (cur is not None) and (cur.sumQL == 1 / float(self.B.DIV))

    '''
    Helper functions to evaluate various counterpoint quantities
    ===================================================================================
    interval(p1, p2): returns the interval between 2 pitches (ignore octaves)
    pDiff(p1, p2): returns the pitchClass difference between 2 pitches
    isChromaticStepU(p1, p2): returns True if  p2 is 1 semi-tone above p1
    isChromaticStepD(p1, p2): returns True if  p2 is 1 semi-tone below p1
    isWholeStepU(p1, p2): returns True if p2 is 1 whole-tone above p1
    isWholeStepD(p1, p2): returns True if p2 is 1 whole-tone below p1
    isSkipU(p1, p2): returns True if p2 is skip above p1 (m3 to a4)
    isSkipD(p1, p2): returns True if p2 is skip below p1 (m3 to a4)
    isLeapU(p1, p2): returns True if p2 is leap above p1 (>= P5)
    isLeapD(p1, p2): returns True if p2 is leap below p1 (>= P5)
    isConst(p1, p2): returns True if p2 and p1 have the same pitch and same octave
    isOctaveAbove(p1, p2): returns True if p2 and p1 have same pitch, p2 has higher octave
    isOctaveBelow(p1, p2): returns True if p2 and p1 have same pitch, p2 has lower octave
    isU(p1, p2): returns True if p2 is above p1
    isD(p1, p2): returns True if p2 is below p1
    '''
    def pDiff(self, p1, p2):
        return p2.ps - p1.ps
    def interval(self, p1, p2):
        return self.pDiff(p1, p2) % 12
    def isChromaticStepU(self, p1, p2):
        return self.pDiff(p1, p2) == 1
    def isChromaticStepD(self, p1, p2):
        return self.pDiff(p2, p1) == 1
    def isWholeStepU(self, p1, p2):
        return self.pDiff(p1, p2) == 2
    def isWholeStepD(self, p1, p2):
        return self.pDiff(p2, p1) == 2
    def isSkipU(self, p1, p2):
        d = self.pDiff(p1, p2)
        return d > 2 and d <= 6
    def isSkipD(self, p1, p2):
        d = self.pDiff(p2, p1)
        return d > 2 and d <= 6
    def isLeapU(self, p1, p2):
        return self.pDiff(p1, p2) > 6 and p1.name != p2.name
    def isLeapD(self, p1, p2):
        return self.pDiff(p2, p1) > 6 and p1.name != p2.name
    def isConst(self, p1, p2):
        return p1.name == p2.name and p1.octave == p2.octave
    def isOctaveBelow(self, p1, p2):
        return p2.name == p1.name and p2.octave > p1.octave
    def isOctaveAbove(self, p1, p2):
        return p2.name == p1.name and p2.octave < p1.octave
    def isU(self, p1, p2):
        return p2.ps > p1.ps
    def isD(self, p1, p2):
        return p2.ps < p1.ps    
    
    '''
    Helper functions to evaluate various epoch quantities
    ===================================================================================
    onBeat(e): returns True if epoch is on beat
    atBeat(e): returns the beat quantity of the epoch
    numV(e): returns number of sounding voices at the epoch
    '''
    def onBeat(e):
        for n in e:
            if n is not None:
                if n.beat % float(1) == 0:
                    return True
                return False
        return None

    def atBeat(e):
        for n in e:
            if n is not None:
                return n.beat % float(1)
        return None

    def numV(e):
        return sum([1 for n in e if n is not None]) 


    def isType(self, fList, p1, p2):
        for f in fList:
            if f(p1, p2): return f.__name__
        print (p1, p2)
        return None
        

    
class InterVoiceExtractor(FeatureExtractor):

    def __init__(self, B, eIndex):
        FeatureExtractor.__init__(self, B, eIndex)
        self.iv = self.extractFeatures()
    
    def extractFeatures(self):
        sEpoch, sIndex = self.sortEpoch(self.eIndex)
        self.features = tuple(sEpoch[i].pitch.ps - sEpoch[i-1].pitch.ps for i in range(1, len(sEpoch)))
                  

class ContinuityExtractor(FeatureExtractor):

    def __init__(self, B, eIndex):
        FeatureExtractor.__init__(self, B, eIndex)
        self.extractFeatures()

    def extractFeatures(self):
        pre = self.B.epochs[self.eIndex - 1]
        cur = self.B.epochs[self.eIndex]
        pre_cur = [(pre[i], cur[i]) for i in range(self.B.numV)]
        fList = [self.isTer, self.isNew, self.isNewVoice, self.isContd, self.isOff]
        self.features = [self.isType(fList, p[0], p[1]) \
            for p in pre_cur]


class VoiceLeadingExtractor(FeatureExtractor):
    
    def __init__(self, B, eIndex):
        FeatureExtractor.__init__(self, B, eIndex)
        
        self.identityTransition = []
        self.extractFeatures()

    '''
    Helper functions to evaluate various counterpoint quantities
    ===================================================================================
    interval(p1, p2): returns the interval between 2 pitches (ignore octaves)
    pDiff(p1, p2): returns the pitchClass difference between 2 pitches
    isChromaticStepU(p1, p2): returns True if  p2 is 1 semi-tone above p1
    isChromaticStepD(p1, p2): returns True if  p2 is 1 semi-tone below p1
    isWholeStepU(p1, p2): returns True if p2 is 1 whole-tone above p1
    isWholeStepD(p1, p2): returns True if p2 is 1 whole-tone below p1
    isSkipU(p1, p2): returns True if p2 is skip above p1 (m3 to a4)
    isSkipD(p1, p2): returns True if p2 is skip below p1 (m3 to a4)
    isLeapU(p1, p2): returns True if p2 is leap above p1 (>= P5)
    isLeapD(p1, p2): returns True if p2 is leap below p1 (>= P5)
    isConst(p1, p2): returns True if p2 and p1 have the same pitch and same octave
    isOctaveAbove(p1, p2): returns True if p2 and p1 have same pitch, p2 has higher octave
    isOctaveBelow(p1, p2): returns True if p2 and p1 have same pitch, p2 has lower octave
    isU(p1, p2): returns True if p2 is above p1
    isD(p1, p2): returns True if p2 is below p1
    '''

    def getIdentityTransition(self):
        return self.identityTransition           

    def extractFeatures(self):
        pre = self.B.epochs[self.eIndex - 1]
        cur = self.B.epochs[self.eIndex]
        pre_cur = [(pre[i], cur[i]) for i in range(self.B.numV)]

        fList = [self.isTer, self.isOff, self.isNewVoice, self.isContd, self.isNew]
        self.features = [self.isType(fList, p[0], p[1]) for p in pre_cur]
    
        fList = [self.isChromaticStepU, self.isChromaticStepD, \
                     self.isWholeStepU, self.isWholeStepD, self.isSkipU, \
                     self.isSkipD,\
                     self.isLeapU, self.isLeapD, self.isConst, \
                     self.isOctaveAbove, self.isOctaveBelow]
        for i in range(len(self.features)):
            if self.features[i] == 'isNew':
                self.features[i] = self.isType(fList, pre_cur[i][0].pitch, pre_cur[i][1].pitch)
                self.identityTransition.append((pre_cur[i][0].pitch.ps, pre_cur[i][1].pitch.ps))

                               


            
    




