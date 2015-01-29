import serial
import time
import re

settings = open("spring tester settings.txt")
arduinoPort = int(settings.readline().split()[0])
loadCellPort = int(settings.readline().split()[0])
cycleTime = 1.3 #float(input('Enter the cycle time in seconds: '))

class loadCell():
    def __init__(self,givenPort):
        self.inputBuffer = ''
        self.comHandle = serial.Serial(
            port=givenPort-1,
            baudrate=9600,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=0,
            interCharTimeout=0xffffffff# this causes read to return instantly
            )
        assert(self.comHandle.isOpen())
    def load(self):
        # ToDo: record readings until two consecutive readings are within 5N of each other then use the second one
        dataRecived = False
        while(True):
            recivedData = self.comHandle.read(6000)
            self.inputBuffer += recivedData.decode("utf-8")
            for matchObject in re.finditer(r'[+-]\d+\.\d',self.inputBuffer):
                load = float(matchObject.group())
                dataRecived= True         
            if(dataRecived):
                self.inputBuffer = self.inputBuffer[matchObject.end():]
                return load # this is in newtons
            time.sleep(0.001)
            
myLoadCell=loadCell(loadCellPort)

arduino = serial.Serial(
            port=arduinoPort-1,
            baudrate=9600,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=0,
            interCharTimeout=0xffffffff# this causes read to return instantly
            )

while True:
    numberOfCycles = int(input('Enter the number of cycles you want to do: '))
    springNumber = int(input('Enter the spring number: '))
    runNumber = int(input('Enter the run number: '))
    material = input('Enter the spring material: ')
    comment = input('Enter a comment: ')
    
    #This loop finds a log file that is not yet in use
    for i in range(1000):
        try:
            log = open('MyLog{}.txt'.format(i),'r')
        except FileNotFoundError:
            break
    log = open('MyLog{}.txt'.format(i),'w')
    
    log.write('spring number: {}\n'.format(springNumber))
    log.write('run number: {}\n'.format(runNumber))
    log.write('spring material: {}\n'.format(material))
    log.write('comment: {}\n'.format(comment))
    
    print('Below is the time, the high load and the low load')

    time.perf_counter()
    for cycle in range(numberOfCycles):
        print('Cycle {} of {}, there are {} minutes remaining'.format(cycle,numberOfCycles,(numberOfCycles-cycle)*cycleTime/60))
        arduino.write(b'H')
        time.sleep(cycleTime/2)
        highForce = myLoadCell.load()
        
        arduino.write(b'L')
        time.sleep(cycleTime/2)
        lowForce = myLoadCell.load()
        
        toRecord = '{:.3f}\t{}\t{}\n'.format(time.perf_counter(),highForce,lowForce)
        print(toRecord,end='')
        log.write(toRecord)
        
    log.close()
arduino.close()