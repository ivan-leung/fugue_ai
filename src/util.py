import random, copy, math, random
try:
    import cpickle as pickle
except:
    import pickle
from collections import Counter


def sign(x):
    if x < 0:
        return -1
    if x == 0:
        return 0
    if x > 0:
        return 1 

def listProduct(x):
    result = 1
    for elem in x:
        result *= elem
    return result
    

def dotProduct(d1, d2):
    """
    COPIED FROM util.py FROM SENTIMENT ASSIGNMENT
    @param dict d1: a feature vector represented by a mapping from a feature (string) to a weight (float).
    @param dict d2: same as d1
    @return float: the dot product between d1 and d2
    """
    if len(d1) < len(d2):
        return dotProduct(d2, d1)
    else:
        return sum(d1.get(f, 0) * v for f, v in d2.items())

def increment(d1, scale, d2):
    """
    COPIED FROM util.py FROM SENTIMENT ASSIGNMENT
    Implements d1 += scale * d2 for sparse vectors.
    @param dict d1: the feature vector which is mutated.
    @param float scale
    @param dict d2: a feature vector.
    """
    for f, v in d2.items():
        d1[f] = d1.get(f, 0) + v * scale

def kmeans(examples, K, maxIters, verbose):
    '''
    WRAPPER CODE COPIED FROM submission.py FROM SENTIMENT ASSIGNMENT
    examples: list of examples, each example is a string-to-double dict representing a sparse vector.
    K: number of desired clusters. Assume that 0 < K <= |examples|.
    maxIters: maximum number of iterations to run for (you should terminate early if the algorithm converges).
    Return: (length K list of cluster centroids,
            list of assignments, (i.e. if examples[i] belongs to centers[j], then assignments[i] = j)
            final reconstruction loss)
    '''
    numSamples = len(examples)
    print 'numsamples', numSamples        
    if verbose > 0:
            print changed

    # Initialize K random points as centroids
    centroids = [examples[i] for i in random.sample(range(numSamples), K)]
    # Initialize assignments
    assignments = [random.sample(range(K), 1)[0] for _ in range(numSamples)]
    # Initialize distance
    distance = None
    # precompute dot product of training example with itself
    sqDat = [dotProduct(ex, ex) for ex in examples]
    # precompute dot product of centroid with itself
    sqCen = [dotProduct(c, c) for c in centroids]

    def getAvg(exampleIndexes):
        group = [examples[i] for i in exampleIndexes]
        result = Counter()
        for ex in group:
            result.update(ex)
        for f in result:
            result[f] = result[f] / float(len(group))
        return result
    numIter = 0
    while numIter <= maxIters:
        if verbose > 0: print 'Iteration: ', numIter
        sqCen = [dotProduct(c, c) for c in centroids]
        # centroid sq dist = (ex - u_i)(ex- u_i) = dot(ex, ex) - 2 dot(ex, u_i) + dot(u_i, u_i)
        distance = [[sqDat[e] - 2 * dotProduct(examples[e], centroids[c]) + sqCen[c] \
                    for c in range(K)] for e in range(numSamples)]
        minDist = [min(sqDist) for sqDist in distance]
        newCluster = [distance[i].index(minDist[i]) for i in range(numSamples)]
        changed = sum([1 for ex in range(numSamples) if assignments[ex] != newCluster[ex]])
        if changed == 0: break
        assignments = newCluster
        centroids = [getAvg([i for i in range(numSamples) if newCluster[i] == cluster]) for cluster in range(K)]
        if verbose > 0: print 'Distance: ', sum(minDist)
        numIter += 1

    print 'Iters: %s, TotalLoss: %s' % (numIter, sum(minDist))
    clusterList = [[examples[i] for i in range(numSamples) if assignments[i] == k] for k in range(K)]
    if verbose > 1:
        for k in clusterList:
            print '======= new cluster ======'
            for i in k:
                print i
    return (assignments, centroids)

def predictCluster(centroids, ex):
    distance = [dotProduct(ex, ex) - 2 * dotProduct(ex, c) + dotProduct(c, c) for c in centroids]
    minDist = min(distance)
    return distance.index(minDist)

class Const:
    def __init__(self):
        self.DIV = 8
    
    



# Funtion: Weighted Random Choice 
# [COPIED FROM util.py IN cars ASSIGNMENT
# --------------------------------
# Given a dictionary of the form element -> weight, selects an element
# randomly based on distribution proportional to the weights. Weights can sum
# up to be more than 1. 
def weightedRandomChoice(weightDict):
    weights = []
    elems = []
    for elem in weightDict:
        weights.append(weightDict[elem])
        elems.append(elem)
    total = sum(weights)
    key = random.uniform(0, total)
    runningTotal = 0.0
    chosenIndex = None
    for i in range(len(weights)):
        weight = weights[i]
        runningTotal += weight
        if runningTotal > key:
            chosenIndex = i
            return elems[chosenIndex]
    print weightDict
    raise Exception('Should not reach here')

def writeFile(filename, data, verbose=False):
    out_s = open(filename, 'wb')
    for obj in data:
        if verbose:
            print obj
        pickle.dump(obj, out_s)
    out_s.close()

def readFile(filename, verbose=False):
    in_s = open(filename, 'rb')
    result = []
    while True:
        try:
            obj = pickle.load(in_s)
            result.append(obj)
        except EOFError:
            break
        else:
            if verbose:
                print 'READ: %s' % (obj)
    return result



def argSort(L, desc=False):
    indexList = list(range(len(L)))
    newL = [(L[i], indexList[i]) for i in range(len(L))]
    newL.sort()
    if desc:
        newL.reverse()
    sortedIndex = [index for elem, index in newL]
    sortedArray = [elem for elem, index in newL]
    return (sortedArray, sortedIndex)

def categoricalTemplate(data, categories):
    vec = [0 for _ in categories]
    for i in range(len(categories)):
        if data == categories[i]: 
            vec[i] = 1  
    return vec

def printNestedDict(d, pre):
    line = '==================================='
    under = '___________________________________'
    print pre + line
    for key in d:
        if isinstance(d[key], dict):
            print pre, 'Dict: ', key
            printNestedDict(d[key], pre + '  ')
        else:
            print str(pre + '  '), key, ':', d[key]

PITCH_CLASS = range(0, 12)
OCTAVE = range(0, 9)




    

