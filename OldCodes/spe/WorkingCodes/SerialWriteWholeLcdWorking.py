# uLCD-28PTU 
# Resolution: 240 x 320 pixels

#!/usr/bin/env python
import time
import RPi.GPIO as GPIO
import serial
import binascii

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
pixelVal =["00","00","00","00","00","00"]
hexYMsb="00"
for i in range(0, 239):
	if i < 16:
		hexX=("0"+hex(i)[2:]).decode('hex')
	else:
		hexX=hex(i)[2:].decode('hex')
	for j in range(0, 319):
		
		if j < 16:
			hexYMsb = "00".decode('hex')
			hexY=("0"+hex(j)[2:]).decode('hex')
		elif j > 255:
			hexYMsb =("0"+hex(j/255)[2:]).decode('hex')
			if (j-255) < 16 :
				hexY=("0"+hex(j-255)[2:]).decode('hex')
			else:
				hexY=hex(j-255)[2:].decode('hex')
		else:
			hexYMsb = "00".decode('hex')
			hexY=hex(j)[2:].decode('hex')
		WritePixel(ser, PUT_PIXEL)
		ser.write("00".decode('hex'))
		ser.write(hexX)
		ser.write(hexYMsb)
		ser.write(hexY)
		ser.write(PIXEL_CLR_MSB.decode('hex'))
		ser.write(PIXEL_CLR_LSB.decode('hex'))	
		time.sleep(0.001)

