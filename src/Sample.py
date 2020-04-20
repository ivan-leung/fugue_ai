from NoteData import *
from Eval import *
import random

def wrapStatement(s):
    top = '==========================================='
    mid = '**** ' + s + ' ****'
    bot = '-------------------------------------------'
    return top + '\n' + mid + '\n' + bot + '\n'

def ending():
    top = '================= END ====================='
    return top

def transitionCount(tProb):
    print wrapStatement('Summary for Transition Count')
    for nAct in tProb:
        print '# Active Voices:', nAct
        print '# Prev:', len(tProb[nAct].keys())
        currCount = [len(tProb[nAct][prev].keys()) for prev in tProb[nAct]]
        print '# Curr:', sum(currCount)
    print ending()

def sampleIntervals(iProb, n):
    print wrapStatement(str(n) + ' Samples from Interval Count')
    for nPresent in iProb:
        print '# Present Voices:', nPresent + 1
        intervals = iProb[nPresent].keys()
        random.shuffle(intervals)
        print 'choosing', n, 'intervals from', len(intervals),'choices:'
        printed = 1
        for interval in intervals:
            if printed > n:
                break
            print str(interval) + ': ' + str(iProb[nPresent][interval])
            printed += 1
    print ending()

def sampleNoteData(nProb):
    print wrapStatement(' Printning All Note Count')
    print nProb
    print ending()

def sampleTransitions(tProb, n):
    print wrapStatement(str(n) + ' Samples from Transition Count')
    for nAct in tProb:
        print '# Active Voices:', nAct
        nPrev = len(tProb[nAct].keys())    
        print '# Prev:', nPrev
        sCount = 1
        prevList = tProb[nAct].keys()
        random.shuffle(prevList)
        for prev in prevList:
            if sCount > n:
                break
            print '   P:', prev
            currs = tProb[nAct][prev].keys()
            print '   choosing 1 from ', len(currs), 'transitions given prev:'
            chosen = random.choice(currs)
            print '   C:', chosen, ':', tProb[nAct][prev][chosen]
            sCount += 1
    print ending()

def printChangeProb(changeProb):
    for t in changeProb:
        print 'Transition type:', t
        for x in changeProb[t]:
            print x, changeProb[t][x]        
                        

def main():
    durationProb, transitionProb, intervalProb, noteProb, changeProb = util.readFile('noteData.pickle')

    print durationProb
    if sys.argv[1] == 't':
        transitionCount(transitionProb)
    if len(sys.argv) > 2:
        if sys.argv[1] == 's':
            nSamples = int(sys.argv[2])
            sampleTransitions(transitionProb, nSamples)
        if sys.argv[1] == 'i':
            nSamples = int(sys.argv[2])
            sampleIntervals(intervalProb, nSamples)
    if sys.argv[1] == 'n':
        sampleNoteData(noteProb)
    if sys.argv[1] == 'd':
        dKeys = durationProb.keys()
        dKeys.sort()
        for duration in dKeys:
            print '=============================='
            print str(duration) + ':'
            print durationProb[duration]
            print '==============================='
    if sys.argv[1] == 'c':
        printChangeProb(changeProb)
    if sys.argv[1] == 'help':
        print 's num: sample |num| transitions'
        print 'i num: sample |num| intervals'
        print 'n: print note probabilities'
                    

if __name__ == '__main__':
    main()
    
    
