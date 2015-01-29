import sys
sys.path.append(r'X:\CODE\Reusable')
import serial
from serial.serialutil import SerialException
import time
import re
import loadCell
import autoSetup
from weederRelay import weederRelay

def stableLoads(loadCellList):
    'waits for all the loads to stabilize then return a list of the loads'
    while not all(aLoadCell.loadIsStable() for aLoadCell in loadCellList):
        time.sleep(0.005)
    return [aLoadCell.load() for aLoadCell in loadCellList]

try:
    relay = weederRelay()
except SerialException:
    print("ERROR: The WTDOT-M can't be found, make sure the WTDOT-M is connected to the computer")
    # pause
    input()

# gets a list of load cell objects           
loadCells = autoSetup.setupListOf(loadCell.loadCell)

if loadCells==[]:
    print('ERROR: No load cells found')
    # pause
    input()
    
while True:
    comment = input('Discription of test: ')
    numberOfCycles = int(input('Cycles you want to do: '))
    
    startTimeString = time.strftime('%Y-%B-%d %H.%M.%S',time.localtime())
    fileName = r'Spring test results/Spring test on '+startTimeString+'.txt'
    log = open(fileName,'w')
    log.write('test started on:\t'+startTimeString+'\n')
    log.write('comment:\t'+comment+'\n\n')
    log.write('cycle number\ttime (s)\tlow force (N)\thigh force (N)\n')

    print('Below is the time, the high load and the low load')
    startTime = time.time()
    for cycle in range(numberOfCycles):
        relay.unground()
        time.sleep(0.2)
        lowForces = stableLoads(loadCells)
        
        relay.ground()
        time.sleep(0.2)
        highForces = stableLoads(loadCells)

        forces = zip(lowForces,highForces)

        toRecord = '{}\t{:.3f}\t'.format(cycle+1,time.time()-startTime)
        for forcePair in forces:
            toRecord+='{}\t{}\t'.format(forcePair[0],forcePair[1])
        toRecord+='\n'
        print(toRecord,end='')
        log.write(toRecord)
        log.flush()
        print('{} Cycles remaining'.format(numberOfCycles-cycle-1))
    log.close()
    relay.unground()