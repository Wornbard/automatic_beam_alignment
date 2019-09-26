# this script automatically aligns mount according to the signal
# from photodiode
# a file 'motors.pos' with four integer numbers describing positions
# of motors should be in the same folder as this script !!!
import threading
import serial
import time
from pynput import keyboard
import sys
import numpy as np

# === FUNCTIONS ======================================================
port='/dev/ttyACM0'
def is_moving( motor_No ):

    question = 'STPM:' + str(motor_No) + ':ST?\n'
    ser.write( question.encode() )
    answer = ser.readline()
    # boolean variable describing state of the motor
    moving = bool( int(answer[-3])-48 )

    return moving


def set_velocity( vel ):

    # wait to establish connection
    time.sleep(1.0)

    # setting velocity (1 - fast / 10 - slow) for all the four motors
    command = 'STPM:1:VEL:' + str(vel) + '\nSTPM:2:VEL:' + str(vel) + '\nSTPM:3:VEL:' + str(vel) + '\nSTPM:4:VEL:' + str(vel) + '\nSTPM:5:VEL:' + str(vel) + '\nSTPM:6:VEL:' + str(vel) + '\nSTPM:7:VEL:' + str(vel) + '\nSTPM:8:VEL:' + str(vel) + '\n'
    ser.write( command.encode() )

    # checking if the velocity (of the first motor) was set correctly
    question = 'STPM:1:ST?\n'
    ser.write( question.encode() )
    answer = ser.readline()
    vel_ans = int(answer[-5])-48
    if ( vel_ans==vel ):
        print( " velocity set to: ", vel_ans )
    else:
        print( " bad connection with the device!\n check  the connection and run the script again" )
        sys.exit()


def check_positions( ):

# reading positions of motors from file
    file = open('motors.pos', 'r')
    pos = file.readline()
    pos = pos.strip().split(" ")
    positions = [int(pos[0]), int(pos[1]), int(pos[2]), int(pos[3]), int(pos[4]), int(pos[5]), int(pos[6]), int(pos[7]) ]
    file.close()

    return positions

# sending 'move' command
def move( command_motor,command4,command1='STPM:', command3=':REL:'):

    # concatenating command
    command = command1 + str(command_motor) + command3 + str(command4) + '\n'
    #print( command )

    # reading positions from file
    p = check_positions()
    p[command_motor-1] += command4 # 'moving' the motor
    pos = [ str(p[0]), str(p[1]), str(p[2]), str(p[3]), str(p[4]), str(p[5]), str(p[6]), str(p[7])]

    # moving motor if it's allowed
    if ( abs(p[command_motor-1])<rng ):

        # checking if the motor is moving - is it needed?
            moving = is_moving( command_motor )
            if ( not moving ):
                # moving chosen motor
                    ser.write( command.encode() )
                    # saving motors' positions to the file
                    pos = pos[0] + " " + pos[1] + " " + pos[2] + " " + pos[3]+" "+pos[4]+" "+pos[5]+" "+pos[6]+" "+pos[7]
                    file = open('motors.pos', 'w')
                    file.write( pos )
                    file.close()
            else:
                print( ' wait until the motor will stop' )

    else:
        print( ' you wanted to go out of range: [', -rng, ', ', rng, ']!' )

    while is_moving( command_motor ):
        # waiting a moment (?)
            time.sleep(0.01)
            pass


# === MAIN ΡROGRAM ===================================================

rng = 4000		# permitted range of steps; one turn = 4096
vel = 2			# velocity from 1 (fast) to 10 (slow)
motor_No = 1		# default motor

# connecting with the serial
time.sleep(0.5)
ser=serial.Serial(port, baudrate=9600)
print( " serial name : ", ser.name)
set_velocity( vel )
