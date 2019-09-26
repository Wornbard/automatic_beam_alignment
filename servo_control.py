import threading
import serial
import time
import sys
import numpy as np

port='/dev/ttyUSB1'

def turn(command_motor,angle):
    command='TURN:'+str(command_motor)+':'+str(angle)+'\n'
    sers.write(command.encode())
sers=serial.Serial(port,baudrate=9600)
