from motor_control import *
from servo_control import *
from gaussian_fit import *
from ccd_time_snap import *
import numpy as np
import sys
import serial
import time
import threading
import copy
exposure=0.7
gain=1
pc=20#pixel_clock
goaldis=100
def step_size():
    return 100
    #sets how far each engine moves for every iteration of gradient descent
def image_center(arr):
    return {'x':int(arr.shape[0]/2),'y':int(arr.shape[1]/2)}
def distance(pos,goalpos):
    dis=(pos['x']-goalpos['x'])**2+(pos['y']-goalpos['y'])**2
    return dis
def optimal_movement(light):#calculates the movement of motors along the "gradient"
    step=step_size()
    dist0=np.array([distance(d.center,d.goalpos)for d in light.dots])
    dist=np.zeros([light.motors.size,light.dots.size])
    derivative=np.zeros([light.motors.size,light.dots.size])#initialize what will become the gradient
    for index,motor in enumerate(light.motors):
        move(motor,int(step))
        for i,d in enumerate(light.dots):
            d.take_picture()
            dist[index][i]=distance(d.center,d.goalpos)
        move(motor,-int(step))#find how distance varies with each parameter
    for k in range(light.motors.size):
        for l in range(light.dots.size):
            derivative[k,l]=(dist[k,l]-dist0[l])/step
    derivative=np.sum(derivative,axis=1)#sum the contrubutions of both dots
    movement=(-1)*(derivative*(step/(np.sum(np.absolute(derivative)))))
    movement=np.rint(movement).astype(int)
    return movement
def optimize(light):
    for d in light.dots:
           d.take_picture()
    while(max([distance(d.center,d.goalpos)for d in light.dots]) >goaldis):#ta skladnia pewnie tak nie dziala
       movement=optimal_movement(light)
       for i,m in enumerate(movement):
               print("motor: ",light.motors[i],"movement: ",m,"\n" )
               print("\n")
       for index,motor in enumerate(light.motors):
           move(motor,movement[index])
       for d in light.dots:
           d.take_picture()
           id=(d.servos[0].id-1)*2+(d.servos[1].id-3)+1
           f=open("center"+str(id)+".pos","a+")
           f.write(str(d.center['x'])+" "+str(d.center['y'])+"\n")
           f.close()
def run_experiment(beams):
    for light in beams:
        for d in light.dots:
            d.take_picture()
        optimize(light)
class servo(object):
    def __init__(self,num,openpos,closedpos):
        self.id=num
        self.op=openpos
        self.cp=closedpos#angle which cuts off the beam corresponding to this dot at some point
class dot(object):
    def __init__(self,servos,image=None,goalpos=None):
        if(image is not None):
            self.image=image
        else:
            self.image=np.empty([1280,1024,3])
        self.center=find_center(self.image)
        self.servos=servos
        if(goalpos is None):
            self.goalpos=image_center(self.image)
        else:
            self.goalpos=goalpos   
    def take_picture(self):
        for s in servos:
            if s in self.servos:
                print("turning: ",s.id," to open position: ",s.op)
                turn(s.id,s.op)
                time.sleep(0.1)
            else:
                print("turning: ",s.id," to closed  position: ",s.cp)
                turn(s.id,s.cp)
                time.sleep(0.1)
        time.sleep(0.5)
        UEye420_Snapper(Exposure=exposure,Gain=gain,File_Location="./photo_tmp.bmp", pixel_clock=pc)
        self.image=np.array(Image.open("./photo_tmp.bmp"))
        self.center=find_center(self.image)
class beam(object):
    def __init__(self,motors,servos,prev_pos=None,goalpos=None):
       self.motors=np.array(motors)
       self.dots=[]
       self.dots.append(dot([servos[0],servos[1]]))
       self.dots.append(dot([servos[0],servos[2]]))
       self.dots=np.array(self.dots)
servos=[servo(1,90,0),servo(2,60,150),servo(3,0,90),servo(4,180,90)]
#to zdjecie jest tymczasowe i nic nigdzie nie robi
moved_beams=[beam(motors=[1,2,3,4],servos=[servos[0]]+servos[2:4]),beam(motors=[5,6,7,8],servos=[servos[1]]+servos[2:4])]
for d in moved_beams[0].dots:
    d.take_picture()
moved_beams[1].dots[0].goalpos=moved_beams[0].dots[0].center
moved_beams[1].dots[1].goalpos=moved_beams[0].dots[1].center
moved_beams[0].dots[0].goalpos=moved_beams[0].dots[0].center
moved_beams[0].dots[1].goalpos=moved_beams[0].dots[1].center
#this way the first beam is assumed to be centered
run_experiment([moved_beams[1]])

