# uLCD-28PTU 
# Resolution: 240 x 320 pixels

#!/usr/bin/env python
import time
import RPi.GPIO as GPIO
import serial
import binascii
from math import*

#PIN DEFINITIONS
resetPin = 18 # BroadComm pin # 18, Board Pin #12

CLEAR_SCREEN="FFCD"
PUT_PIXEL="FFC1"
PIXEL_X_MSB = "00"
PIXEL_X_LSB = "28"
PIXEL_Y_MSB = "00"
PIXEL_Y_LSB = "64"
PIXEL_CLR_MSB = "FF"
PIXEL_CLR_LSB = "E0"

FS = 8000
F  = 500
SAMPLE = 16

def WritePixel(ser,pixelCmdData):
	ser.write(pixelCmdData.decode('hex'))
	return;

#INIITIALIZE GPIO PIN
GPIO.setmode(GPIO.BCM)
GPIO.setup(resetPin, GPIO.OUT)
GPIO.output(resetPin, GPIO.HIGH)
GPIO.output(resetPin, GPIO.LOW)
time.sleep(0.0001)
GPIO.output(resetPin, GPIO.HIGH)

time.sleep(5)
ser = serial.Serial(
	port='/dev/ttyAMA0',
        baudrate = 9600,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS,
        timeout=1
	)
ser.write(CLEAR_SCREEN.decode('hex'))

samplePoints = [0]*SAMPLE
yMsb = [0]*SAMPLE
yLsb = [0]*SAMPLE
wave = [0]*SAMPLE
hexWave=[0]*SAMPLE
hexWaveVal=[0]*SAMPLE
for n in range(SAMPLE):
	wave[n]=int(round(((100*sin(2*pi*F*n/FS))+100)))
	hexWave[n]=hex(wave[n])[2:]

samplePoints[0] = hex(0)[2:]
for i in range(1,16):
	samplePoints[i]=hex((i*20)-1)[2:]

print hexWave
print samplePoints

print samplePoints
for j in range(0,16):
	if wave[j] < 16:
		hexWaveVal[j]=("0"+hexWave[j]).decode('hex')
	else:
		hexWaveVal[j]=hexWave[j].decode('hex')

	if int(samplePoints[j],16)<16:
		yMsb[j]="00".decode('hex')
		yLsb[j]=("0"+samplePoints[j]).decode('hex')
	elif int(samplePoints[j],16)>255:
		yMsb[j]=("0"+hex(int(samplePoints[j],16)/255)[2:]).decode('hex')
		if (int(samplePoints[j],16)-255) < 16 :
			yLsb[j]=("0"+hex(int(samplePoints[j],16)-255)[2:]).decode('hex')
		else:
			yLsb[j]=hex(int(samplePoints[j],16)-255)[2:].decode('hex')
	else:
		yMsb[j] = "00".decode('hex')
		yLsb[j]=samplePoints[j].decode('hex')

	ser.write(PUT_PIXEL.decode('hex'))
	ser.write("00".decode('hex'))
	ser.write(hexWaveVal[j])
	ser.write(yMsb[j])
	ser.write(yLsb[j])
	ser.write(PIXEL_CLR_MSB.decode('hex'))
	ser.write(PIXEL_CLR_LSB.decode('hex'))	
	time.sleep(0.001)	

for j in range(0,15):
	ser.write("FFC8".decode('hex'))
	ser.write("00".decode('hex'))
	ser.write(hexWaveVal[j])
	ser.write(yMsb[j])
	ser.write(yLsb[j])
	ser.write("00".decode('hex'))
	ser.write(hexWaveVal[j+1])
	ser.write(yMsb[j+1])
	ser.write(yLsb[j+1])	
	ser.write(PIXEL_CLR_MSB.decode('hex'))
	ser.write(PIXEL_CLR_LSB.decode('hex'))	
	time.sleep(0.0001)	



