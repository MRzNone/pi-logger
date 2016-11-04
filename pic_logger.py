import sys
import time
import picamera
import os.path
import datetime
import RPi.GPIO as GPIO
import ftplib

#If TURN
IFMOVE = False

addr = "/home/pi/Desktop/logger/" + "{0}"

#FTP setup
session = ftplib.FTP('ftp server','username','passcode')
#upload
def ftpUpload(name, dire):
        #upload others
        file = open (dire, 'rb')
        if name in session.nlst():
                session.delete(name)
        session.storbinary("STOR " + name, file)
        file.close()
        #upload logger
        file.close()

def timeElaspe(check):
        global last
        result = time.time() - last
        if check == 1:
                last = time.time()
        return result

#take a picture at logger foder with a name name
def takePic(name):
        fAddr = addr.format(name) + ".jpg"
        with picamera.PiCamera() as camera:
                camera.resolution = (1080,720)
                camera.capture(fAddr)
        ftpUpload(name + ".jpg", fAddr)
        readNum(1)

#add the new line into logger file
def logger(line, num):
        #read and add new line if exist
        if(os.path.isfile(addr.format("log.txt"))):
                with open (addr.format("log.txt"), 'a') as f:
                        f.write(line)

        #create file and write line and number if NOT exist
        else:
                f = open (addr.format("log.txt"), 'w')
                f.write(line + "\n")

    #upload to server is time elapse is greater than 10 seconds
        if (timeElaspe(0) > 10):
                print("uploading log.txt")
                ftpUpload("log.txt", addr.format("log.txt"))
                timeElaspe(1)

#red num/ update numbe by 1 is check == 1 after read
def readNum(check):
        if(os.path.isfile(addr.format("num.txt"))):
                with open (addr.format("num.txt"), 'r+') as f:
                        num = int(f.readline())

                #update num
                if check == 1:
                        with open (addr.format("num.txt"), 'w') as f:
                                f.write(str(num+1))

                return num
        else:
                f = open(addr.format("num.txt"), 'w')
                f.write("0")
                f.close()
                return 0

# Servo SetUp
GPIO.setmode(GPIO.BOARD)
GPIO.setup(7,GPIO.OUT)
servo = GPIO.PWM(7,50)
GPIO.setwarnings(False)
servo.start(7.5)

#turn to a degree
def turnTo(degree):  # 0-180
        frequency = (degree/180.0)*(10.0) + 2.5
        servo.ChangeDutyCycle(frequency)
        time.sleep(0.3)


last = time.time()
num = readNum(0) + 1
i = num;
positon_1 = 120
position_2 = 160
turned = False
try:
        while True:
                info = str(i) + "_" + str(datetime.datetime.now())
                if (IFMOVE == True):
                        if(turned == True):
                                turnTo(positon_1)
                                turned = False
                        else:
                                turnTo(position_2)
                                turned = True
                        time.sleep(0.7)
                else:
                        turnTo(positon_1)
                        servo.stop()
                        time.sleep(0.5)
                logger(info, i)
                takePic(info)
                print(str(i) + "\n")
                i = i+1

except KeyboardInterrupt:
        GPIO.cleanup()
        session.stop()
        servo.stop()

GPIO.cleanup()
session.stop()
servo.stop()
