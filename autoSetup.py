'''
History:

First I wrote my code in C++ and I expected the user to enter the correct port number.
If the user did not then I got error messages and crashes.Then I rewrote in python.
Each piece of equipment had it's own equipment autodetection algorithem.
This saved hassle for the program user. The problem was that each piece of equipment was
diffrent and it required a diffrent autodetection stratagy. When I got up to 7 classes,
each with it's own autodetection stratagy I decided that I had enough cases to write a
general algorithem.


'''

import serial
from serial.serialutil import SerialException
import time

class wrongDeviceException(SerialException):
    pass

class serialAutoSetup:
    '''
    this class contains a general algorithm for finding
    a piece of hardware on a serial port and opening a connection to it
    '''
    
    '''
    how it works:
        if a port is given it attempts to setup with it, no errors are caught
        if no port is given it attempts to setup from file
        if the setup from file throws an error then
        try opening every port with the overridden open file command
        then there is a user specified wait (default 0)
        then the handles to the ports are checked with isCorrectHardware
        the first handle on which hardware is found becomes the handle of the class
        all other handles are closed. This means it is possible
        to get for example 5 alicats by useing the autosetup 5 times
    '''
    
    def __init__(self,port = 'search',delayAfterOpening = 0):
        '''this is an efficent but complex port opening stratagy'''
        self.portFileName = b'Ports\\' + bytes(self.__class__.__name__,'utf-8')+ b' port.txt'
            
        # if a port is given then setup with it
        if port!='search':
            self.comHandle = self.setup(port,delayAfterOpening)
            return

        # else try the port that worked last time
        try:
            port=self.loadPortNumber()
            self.comHandle = self.setup(port,delayAfterOpening)
            return
        # there are at least 4 failure modes possible in the above try statement.
        # all should pass silently as the portFile is just a performance enhancement and recovery is easy
        except FileNotFoundError:
            pass
        except ValueError:
            pass
        except wrongDeviceException:
            pass
        except SerialException:
            pass
            
        # try scanning all the ports
        print('Attempting automatic setup of ' + self.__class__.__name__)
        handleStore = []
        for port in range (100):
            #print(port)
            try:
                handle = self.openPort(port=port)
                handleStore.append(handle)
            except SerialException:
                pass
        #there needs to be a 2 second wait between opening a connection to an arduino and using it
        time.sleep(delayAfterOpening)
        hardwareIsFound = False
        for handle in handleStore:
            # if there are multiple pieces of matching hardware this will
            # find the one on the lowest numbered port
            if (not hardwareIsFound) and self.isCorrectHardware(handle):
                hardwareIsFound = True
                self.comHandle = handle
                #The +1 below is to conteract the funny way that pySerial numbers ports
                self.savePortNumber(self.comHandle.port+1)
            else:
                handle.close()
        if not hardwareIsFound:
            # I don't print the below message because the class name may make sense to me
            # but it might not make sense to the user
            # I can use the stack trace to understand what is going on.
            # For end user software the exception should be caught.
            #print('No {} found on the first {} ports'.format(self.__class__.__name__,port))
            raise SerialException

    def setup (self,port,delayAfterOpening):
        '''given a port number and an optional delay after opening the port
        this returns a handle on sucsess and throws an exception on failure'''
        handle = self.openPort(port)
        time.sleep(delayAfterOpening)
        if not self.isCorrectHardware(handle):
            raise wrongDeviceException
        'if the port is correct then save it for next time'
        #The +1 below is to conteract the funny way that pySerial numbers ports
        self.savePortNumber(handle.port+1)
        return handle
    
    def openPort(self,port):
        'to be overwritten in subclasses with a method that returns a handle'
        raise NotImplementedError
    
    def isCorrectHardware(self,handleToCheck):
        'to be overwritten in subclasses with a method that returns a boolean'
        raise NotImplementedError

    def loadPortNumber(self):
        '''this tries to return the number of the port that worked last time,
        it can throw lots of diffrent errors'''
        portFileHandle = open(self.portFileName,'r')
        return int(portFileHandle.read())

    def savePortNumber(self,port):
        '''this tries to save the given port for next time,
        this should save time when setting up'''
        portFileHandle = open(self.portFileName,'w')
        portFileHandle.write(str(port))

    def close(self):
        '''I know that closing a port is not strictly part of automatic setup
        but putting the code here saves code duplication'''
        self.comHandle.close()

def setupListOf(hardwareClass):
    'this returns a list of class instances'
    # this setup routine could be made faster by parelleliseing the search
    # this would require a more complex algorythem though
    # A smarter algorythem would probably either require copying most of the __init__ method of autosetup
    # or rewriting this file in a more functional style to enable greater reuse of the components from outside the class
    hardwareList = []
    for port in range (1,100):
        try:
            hardwareList.append(hardwareClass(port))
        except SerialException:
            pass
    return hardwareList
    
if __name__ == '__main__':
    import alicatFlowMeter
    alicats = setupListOf(alicatFlowMeter.alicat)
    for alicat in alicats:
        print(alicat.comHandle.port)
    #alicat = alicatFlowMeter.alicat()
    #print(alicat.massFlow())