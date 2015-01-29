import serial
import re
import time
import autoSetup
'''
The targetLogLength is 2 because I only want to record the current reading and the previous reading
to check for consistancy, I might want to make the log bigger later to make output to a file easier
'''
targetLogLength = 2

class loadCell(autoSetup.serialAutoSetup):
    'this class wraps a load cell that has been wired up to a london electronics display with rs232 output'
    def __init__(self,port='search'):
        self.inputBuffer = ''
        self.loadLog = []
        self.regex = re.compile(r'\n *[+-]\d+\.\d\r')
        autoSetup.serialAutoSetup.__init__(self,port)
        #self.rawLog = open('Raw data/{} at {}.txt'.format(self.__class__.__name__,time.time()),'w')
        
    def openPort(self,port):
        'this takes a port number and returns a port handle'
        return serial.Serial(port = port-1,timeout = 0)
    
    def isCorrectHardware(self,handleToCheck):
        'this checks if the class is receiving data from a display'
        for i in range (30):
            self.inputBuffer += handleToCheck.read(6000).decode("utf-8",'ignore')
            #print('input buffer: {}'.format(repr(self.inputBuffer)))
            if self.regex.search(self.inputBuffer):
                return True
            time.sleep(0.01)
        return False
    
    def load(self):
        '''this wait until the log has targetLogLength readings, thereafter it
        returns immidiately with the most recent load'''
        while True:
            recievedData = self.comHandle.read(6000).decode("utf-8",'ignore')
            #self.rawLog.write(recievedData)
            #self.rawLog.flush()
            self.inputBuffer += recievedData
            
            for matchObject in self.regex.finditer(self.inputBuffer):
                load = float(matchObject.group())
                self.loadLog.append(load)
                #print(load)       
                self.inputBuffer = self.inputBuffer[matchObject.end():]
            if len(self.loadLog)>= targetLogLength:
                # this reduces the log length to the target log length
                self.loadLog = self.loadLog [-targetLogLength:]
                break
            time.sleep(0.01)
        return self.loadLog[-1] # this is in newtons
    
    def loadIsStable(self):
        'returns True if the load is stable'
        self.load()
        # 5 is the allowable diffrence between consecutive readings
        # this has units of newtons
        return self.loadLog[-2]-5 < self.loadLog[-1] < self.loadLog[-2]+5
        

    def stableLoad(self):
        '''this waits until the load is stable
        then it retuns the most recent load'''
        while not self.loadIsStable():
            time.sleep(0.01)
        return self.loadLog[-1]        
            
if __name__ == '__main__':
    loadCellList = autoSetup.setupListOf(loadCell)
    print(loadCellList)
    for i in range (10):
        for loadCellInstance in loadCellList:
            print('load cell on port: {} load: {} stableLoad: {}'.format(loadCellInstance.comHandle.port,loadCellInstance.load(),loadCellInstance.stableLoad()))
        time.sleep(0.1)
