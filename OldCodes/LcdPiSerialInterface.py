#!/usr/bin/env python
import time
import RPi.GPIO as GPIO
import serial

#LCD COMMANDS
ClrScreen = 65485
PutChar = 65534
writeobj=01

#PIN DEFINITIONS
DtrPin = 17 # Broadcomm pin # 17, Board Pin # 11

#INIITIALIZE GPIO PIN
GPIO.setmode(GPIO.BCM)
GPIO.setup(DtrPin, GPIO.OUT)
GPIO.output(DtrPin, GPIO.HIGH)
GPIO.output(DtrPin, GPIO.LOW)
time.sleep(0.00001)
GPIO.output(DtrPin, GPIO.HIGH)
ser = serial.Serial(
	port='/dev/ttyAMA0',
        baudrate = 9600,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS,
        timeout=1
        )
ser.write("010800".decode('hex'))
ser.write("005059".decode('hex'))
ser.write("010f00000f01".decode('hex'))
'''
while True:
	if ser.inWaiting():
		rcv=ser.read(ser.inWaiting())
		print rcv
'''
time.sleep(0.01)
