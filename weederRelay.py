import serial
from serial.serialutil import SerialException
import time
import autoSetup

class weederRelay(autoSetup.serialAutoSetup):
    '''this class wraps a WTDOT-M circuit board'''
    
    def __init__(self,port = 'search'):
        autoSetup.serialAutoSetup.__init__(self,port)
        
    def openPort(self,port):
        return serial.Serial(port=port-1,timeout=0.5)
    
    def isCorrectHardware(self,handleToCheck):
        '"A$" is not a valid command so it returns A followed by a ? meaning that it was not understood'
        handleToCheck.write(b'A$\r')
        recieved = handleToCheck.read(3)
        return recieved==b'A?\r'
    
    def ground(self,channel = 'A'):
        'this connects the output channel ot ground with a high current connection'
        toSend = bytes('AL{}\r'.format(channel),'utf-8')
        self.comHandle.write(toSend)
        recieved = self.comHandle.read(4)
        assert(recieved == toSend)
    
    def unground(self,channel = 'A'):
        'this disconnects the output channel from ground so that it is a floating pin'
        toSend = bytes('AH{}\r'.format(channel),'utf-8')
        self.comHandle.write(toSend)
        recieved = self.comHandle.read(4)
        assert(recieved == toSend)
    
if __name__ == '__main__':
    valves = weederRelay()
    valves.ground('E')
    #the pause is only so that you can hear two seperate events
    time.sleep(0.2)
    valves.unground('E')
    print('it worked')
        
        