# uLCD-28PTU 
# Resolution: 240 x 320 pixels

#!/usr/bin/env python
import time
import RPi.GPIO as GPIO
import serial
from math import*

#PIN DEFINITIONS
resetPin = 18 # BroadComm pin # 18, Board Pin #12

#Commands
CLR_SCREEN_CMD	= "FFCD"
PUT_PIXEL_CMD	= "FFC1"
MOVE_ORIGIN_CMD	= "FFCC"
DRAW_LINE_CMD   = "FFC8"

#Arguments for comments
PIXEL_X_MSB 	= "00"
PIXEL_X_LSB 	= "28"
PIXEL_Y_MSB 	= "00"
PIXEL_Y_LSB 	= "64"
PIXEL_CLR_MSB 	= "FF"
PIXEL_CLR_LSB 	= "E0"

PHASE_RESOLUTION = 5

# INITIALIZATION
# Frequency, Sampling rate and Number of samples of sine wave
FS = 8000
F  = 500
SAMPLE = 16

samplePoints = [0]*SAMPLE
yMsb = [0]*SAMPLE
yLsb = [0]*SAMPLE
wave = [0]*SAMPLE
hexWave=[0]*SAMPLE
hexWaveVal=[0]*SAMPLE

phase = 0

#Generate the points on the time axis
def CreateSamplePoints(samplePoints, yMsb, yLsb):
	for j in range(0,16):
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
	return;

#Generate the values for sine wave, convert to hex string and remove '0x' from the string
def GenerateSineWaveValues(wave, hexWave, phase, sides):
	if sides == 'upper' :
		for n in range(SAMPLE):
			wave[n]=int(round(((60*sin((2*pi*F*n/FS)+phase))+180)))
			hexWave[n]=hex(wave[n])[2:]
	else:
		for n in range(SAMPLE):
			wave[n]=int(round(((60*sin((2*pi*F*n/FS)+phase))+60)))
			hexWave[n]=hex(wave[n])[2:]
	
	return;

#Plot the wave as points in the display
def PlotPoints(wave, hexWaveVal, yMsb, yLsb):
	for j in range(0,16):
		if wave[j] < 16:
			hexWaveVal[j]=("0"+hexWave[j]).decode('hex')
		else:
			hexWaveVal[j]=hexWave[j].decode('hex')

		ser.write(PUT_PIXEL_CMD.decode('hex'))
		ser.write("00".decode('hex'))
		ser.write(hexWaveVal[j])
		ser.write(yMsb[j])
		ser.write(yLsb[j])
		ser.write(PIXEL_CLR_MSB.decode('hex'))
		ser.write(PIXEL_CLR_LSB.decode('hex'))		
		if 0 < j < 15:
			ConnectPointsByLine(hexWaveVal, yMsb, yLsb, j-1)	

	return;

# Connect all the points by line together in a single plot
def ConnectPointsByLineTogether(hexWaveVal, yMsb, yLsb):
	for j in range(0,15):
		ser.write(DRAW_LINE_CMD.decode('hex'))
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
		time.sleep(0.01)	
	return;

# Connect all the points by line one by one
def ConnectPointsByLine(hexWaveVal, yMsb, yLsb, idx):
	ser.write(DRAW_LINE_CMD.decode('hex'))
	ser.write("00".decode('hex'))
	ser.write(hexWaveVal[idx])
	ser.write(yMsb[idx])
	ser.write(yLsb[idx])
	ser.write("00".decode('hex'))
	ser.write(hexWaveVal[idx+1])
	ser.write(yMsb[idx+1])
	ser.write(yLsb[idx+1])	
	ser.write(PIXEL_CLR_MSB.decode('hex'))
	ser.write(PIXEL_CLR_LSB.decode('hex'))	
	return;


#INIITIALIZE GPIO PIN
GPIO.setmode(GPIO.BCM)
GPIO.setup(resetPin, GPIO.OUT)
GPIO.output(resetPin, GPIO.HIGH)

#Reset the display before sending commands. This is important as the display might
#not respond (sometimes) if the commands are send before reset
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

# Clear the screen before sending the commands
ser.write(CLR_SCREEN_CMD.decode('hex'))

wave0=[0]*SAMPLE

samplePoints[0] = hex(0)[2:]
for i in range(1,16):
	samplePoints[i]=hex((i*20)-1)[2:]

#Create the sample points to be plotted  on Y-Axis. 
#Here Y Axis means the time axis as the plot is on the tilted LCD
CreateSamplePoints(samplePoints, yMsb, yLsb)

while 1:
	if phase > (2*pi):
		phase = 0
	else:
		phase = phase + (pi/PHASE_RESOLUTION)
	GenerateSineWaveValues(wave, hexWave, phase, 'lower')
	PlotPoints(wave, hexWaveVal, yMsb, yLsb)
	GenerateSineWaveValues(wave, hexWave, phase, 'upper')
	PlotPoints(wave, hexWaveVal, yMsb, yLsb)
#ser.write(CLR_SCREEN_CMD.decode('hex'))
	ser.write("FFC4".decode('hex'))
	ser.write("00000000".decode('hex'))
	ser.write("00f00140".decode('hex'))
	ser.write("0000".decode('hex'))

