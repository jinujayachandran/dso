#!/usr/bin/env python
import time
import RPi.GPIO as GPIO
import serial

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
        timeout=1
        )
time.sleep(0.001)
#ser.write("01".decode('hex'))
#ser.write("08".decode('hex'))
#ser.write("00".decode('hex'))
#ser.write("00".decode('hex'))
#ser.write("0A".decode('hex'))
#ser.write("03".decode('hex'))

ser.write("010f00000f01".decode('hex'))

'''
# Working Code
gaugeval = 50
checksum = WRITE_OBJ_CMD ^ TYPE_COOL_GAUGE ^ INDEX_0 ^ gaugeval
data0 = bytearray([1,8,0,0,50,0])
data0[5]= checksum
ser.write(data0)
time.sleep(0.001)
'''

data0 = bytearray([1,8,0,0,50,0])
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
	time.sleep(0.1)
