#!/usr/bin/env python
import time
import RPi.GPIO as GPIO
import serial
import binascii

WRITE_OBJ_CMD   = 0x01
TYPE_COOL_GAUGE = 0x08
INDEX_0         = 0x00
gaugeval        = 1
step            = 1

ser = serial.Serial(
	port='/dev/ttyAMA0',
        baudrate = 9600,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS,
        timeout=3
        )
data0 = bytearray([1,8,0,0,50,0])
data1 = bytearray([1,15,0,0,0,0])
reply = bytearray([0,0,0,0,0,0,0])
while True:
	data0[4] = gaugeval
	checksum = WRITE_OBJ_CMD ^ TYPE_COOL_GAUGE ^ INDEX_0 ^ gaugeval	
	data0[5] = checksum
	if gaugeval < 1:
		step = 1
	if gaugeval > 99:
		step = -1
	gaugeval += step
	ser.write(data0)

	numbytesread = ser.inWaiting()
	if numbytesread > 0:
		sliderValue = ser.read()
		sliderValue = binascii.hexlify(sliderValue)
		if sliderValue != '06' :
			reply[0] = int(sliderValue, 16)
			for i in range(1, numbytesread):
				sliderValue = ser.read()
				sliderValue = binascii.hexlify(sliderValue)
				reply[i] = int(sliderValue, 16)
				print reply
			print reply
			checksum = 1 ^ 15 ^ 0 ^ 0 ^ reply[4]
			data1[4] = reply[4]
			data1[5] = checksum
			ser.write(data1) 	
		ser.flushInput()
	time.sleep(0.1)


