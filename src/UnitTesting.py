import random, collections, sys, Query
#from constants import *

class UnitTest:
    '''
    Abstract Class for unit testing.
    '''
    def __init__(self, subjectName=None):
        self.passed = None
        self.testName = None
        self.testStr = ''
        self.subjectName = subjectName

    def runTest(self):
        raise Exception('Implement runTest')


    def getResult(self):
        intro =  'Unit Test ' + self.testName
        if self.subjectName is not None:
            intro += ' on ' + self.subjectName + ': '
        else:
            print 'subject name', self.subjectName
            intro += ': '
        if self.passed:
            intro += 'PASS'
        else:
            intro += 'FAIL'
        intro = self.wrapStatement(intro)
        print intro
        print self.testStr
        print self.ending()        

    def ending(self):
        top = '-------------- End of Test ---------------'
        bot = '=========================================='
        return top + '\n' + bot + '\n'

    def wrapStatement(self, s):
        top = '=========================================='
        mid = '**** ' + s + ' ****'
        bot = '------------------------------------------'
        return top + '\n' + mid + '\n' + bot + '\n'
            



class TimeConsistencyTest(UnitTest):
    def __init__(self, epochs, subjectName=None):
        UnitTest.__init__(self)
        self.epochs = epochs
        self.testName = 'Time Consistency Test'
        self.subjectName = subjectName

    def validate(self, v, i):
        dStr, ql = self.epochs[i][v]
        end = int(i + ql * Query.DIV)
        for j in range(i + 1, end):
            curDStr, curQL = self.epochs[j][v]       
            if curQL is not None:
                return str([self.epochs[k][v] for j in range(i, end)])
        if len(self.epochs) < end and self.epochs[end][v] is not None:
            return str([self.epochs[k][v] for j in range(i, end + 1)])
        return ''

    def runTest(self):
        wrongStr = ''
        for i in range(len(self.epochs)):            
            for v in range(Query.VOICES):
                dStr, ql = self.epochs[i][v]    
                if ql is not None:
                    wrongStr += self.validate(v, i)
                    
        if wrongStr != '':
            self.testStr = wrongStr
            return
        self.passed = True

class PitchFilterTest(UnitTest):
    def __init__(self, epoch, pitchSet, subjectNae=None):
        UnitTest.__init__(self)
        self.epoch = epoch
        self.pitchSet = pitchSet
        self.testName = 'Pitch Filter Test'
        self.subjectName = subjectName

    def runTest(self):
        print self.epoch
        print self.pitchSet        
        


