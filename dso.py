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
PIXEL_COLOR_MSB	= "FF"
PIXEL_COLOR_LSB	= "E0"

PHASE_RESOLUTION = 5

# INITIALIZATION
# Frequency, Sampling rate and Number of samples of sine wave
X_SIZE = 240
Y_SIZE = 320
FS = 8000
F  = 500
SAMPLE = 64
SAMPLE_WIDTH = (Y_SIZE/SAMPLE)

samplePoints = [0]*SAMPLE
yMsb = [0]*SAMPLE
yLsb = [0]*SAMPLE
wave = [0]*SAMPLE
hexWave=[0]*SAMPLE
hexWaveVal=[0]*SAMPLE

phase = 0
########################################################################################################
#Generate the points on the time axis.
#Algorithm: The sample points are for the Y-Axis of the display. These points are to be transferred
#           as MSB and LSB of 8 bits each. Since python deals with strings each of the string needs
#           to be converted to hex value. "0" is a nibble and "00" is 8-bit value.
#           (1) If the sample point value is less than 0xF then "0" is to be appended to it for LSB
#               and MSB will be "00".
#           (2) If the sample point value is greater than 255 (for example the Y-axis can have a maximum 
#               value of 320 as it is a 240 x 320 display) then it needs to be split into MSB and LSB.
#               The MSB is obtained by dividing the sample point value by 255 and the LSB by subtracting 
#               the sample point value from 255. Again the logic (1) is applied.
#           (3) If the sample point value is between 0 and 255 then MSB is zero and the LSB is the
#               corresponding hex value.
########################################################################################################
def CreateSamplePoints(samplePoints, yMsb, yLsb):
	for j in range(0,SAMPLE):
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

########################################################################################################
#Generate the values for sine wave, convert to hex string and remove '0x' from the string
#Algorithm: The 240 x 320 display is divided into two sections along the X-axis (i.e along the 240
#           side). The sine wave can be displayed either in the upper half or in the lower half. 
#            If in the upper half it has to be shifted such that the lowest point point of the wave
#           is at 120. Since the sine function generates values between [-1 1] it is scaled by 60 
#           and shifted by 180 so the lower most point is -60+180=120 and the upper most point is 
#           60+180=240. For the lower wave the scaling is 60 and shifting is 60 so that the minimum 
#           value is 0 and maximum value is 120.
########################################################################################################
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

########################################################################################################
#Plot the wave as points in the display
#Algorithm: Since the maximum value of the sine wave be 240 the value can be contained in the LSB.
#           The MSB will be zero. The corresponding pixel of the sine value is marked as a point 
#           in the display. Refer the command manual to know more about the command format.
########################################################################################################
def PlotPoints(wave, hexWaveVal, yMsb, yLsb):
	for j in range(0,SAMPLE):
		if wave[j] < 16:
			hexWaveVal[j]=("0"+hexWave[j]).decode('hex')
		else:
			hexWaveVal[j]=hexWave[j].decode('hex')

		ser.write(PUT_PIXEL_CMD.decode('hex'))
		ser.write("00".decode('hex'))
		ser.write(hexWaveVal[j])
		ser.write(yMsb[j])
		ser.write(yLsb[j])
		ser.write(PIXEL_COLOR_MSB.decode('hex'))
		ser.write(PIXEL_COLOR_LSB.decode('hex'))		
		if 0 < j < SAMPLE:
			ConnectPointsByLine(hexWaveVal, yMsb, yLsb, j-1)	

	return;

########################################################################################################
#Connect all the points by line together in a single plot
#Algorithm: Scan through all the points and draw a line connecting them.
########################################################################################################
def ConnectPointsByLineTogether(hexWaveVal, yMsb, yLsb):
	for j in range(0,SAMPLE):
		ser.write(DRAW_LINE_CMD.decode('hex'))
		ser.write("00".decode('hex'))
		ser.write(hexWaveVal[j])
		ser.write(yMsb[j])
		ser.write(yLsb[j])
		ser.write("00".decode('hex'))
		ser.write(hexWaveVal[j+1])
		ser.write(yMsb[j+1])
		ser.write(yLsb[j+1])	
		ser.write(PIXEL_COLOR_MSB.decode('hex'))
		ser.write(PIXEL_COLOR_LSB.decode('hex'))	
		time.sleep(0.01)	
	return;

########################################################################################################
#Connect all the points by line one by one
#Algorithm: Once the pixels are marked, a straight line is drawn from the old pixel to the new one.
########################################################################################################
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
	ser.write(PIXEL_COLOR_MSB.decode('hex'))
	ser.write(PIXEL_COLOR_LSB.decode('hex'))	
	return;


########################################################################################################
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

#Since there are 320 pixels along Y-Axis divide it number of sample points to plot.
for i in range(1,SAMPLE):
	samplePoints[i]=hex((i*SAMPLE_WIDTH)-1)[2:]

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

    # Clearing the screen is important to plot the next set of points
	ser.write(CLR_SCREEN_CMD.decode('hex'))

    # Instead of clearing the screen draw a black rectangle to fill the screen. It is a bit more
    # faster.
#	ser.write("FFC4".decode('hex'))
#	ser.write("00000000".decode('hex'))
#	ser.write("00f00140".decode('hex'))
#	ser.write("0000".decode('hex'))

