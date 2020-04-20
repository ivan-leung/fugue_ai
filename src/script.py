import sys
import Compose


def composeOne():
    trials = 0
    while True:
        try:
            Compose.main()
        except:
            trials += 1
            pass
        else:
            break
    print 'total trials', trials

runs = int(sys.argv[1])
for i in range(runs):
    composeOne()


