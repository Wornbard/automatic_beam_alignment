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
def step_size():#light is an instance of dot
    return 100
    #tymczasowe
def image_center(arr):
    return {'x':int(arr.shape[0]/2),'y':int(arr.shape[1]/2)}
def distance(pos,goalpos):
    dis=(pos['x']-goalpos['x'])**2+(pos['y']-goalpos['y'])**2
    return dis
def dis_x(pos,goalpos):
    return (pos['x']-goalpos['x'])**2
def dis_y(pos,goalpos):
    return (pos['y']-goalpos['y'])**2
def axis_center(motor, dis, d):
    totalsteps=0
    step=step_size()
    d.take_picture()
    while(dis(d.center,d.goalpos)>goaldis):
        dist0=distance(d.center,d.goalpos)
        dist=0
        move(motor,step)
        d.take_picture()
        move(motor,-step)
        dist=dis(d.center,d.goalpos)
        direction=np.sign((dist-dist0))*(-1)
        movement=direction*step
        movement=np.rint(movement).astype(int)
        print("motor: ",motor,"movement: ",movement,"\n" )
        print("\n")
        move(motor,int(movement))
        totalsteps+=movement
        d.take_picture()
    print("The center dot is in position wrt one axis with goalpos of ",d.goalpos['x']," ",d.goalpos['y']," and actual pos of ",d.center['x']," ",d.center['y'])
    return totalsteps 
def center_dot(light,dotnum):
    step=step_size()
    d=light.dots[dotnum]#dotnum to 0 albo 1
    d.take_picture()
    while(distance(d.center,d.goalpos)>goaldis):
        dist0=distance(d.center,d.goalpos)
        dist=np.empty([light.motors.size])
        for index,motor in enumerate(light.motors):
            move(motor,int(step))
            d.take_picture()
            dist[index]=distance(d.center,d.goalpos)
            move(motor,-int(step))
        derivative=(dist-np.array([dist0]*light.motors.size))/step
        movement=(-1)*(derivative*(step/(np.sum(np.absolute(derivative)))))
        movement=np.rint(movement).astype(int)
        for i,m in enumerate(movement):
           print("motor: ",light.motors[i],"movement: ",m,"\n" )
           print("\n")
        for index,motor in enumerate(light.motors):
           move(motor,int(movement[index]))
        d.take_picture()
    print("The center dot is in position with goalpos of ",d.goalpos['x']," ",d.goalpos['y']," and actual pos of ",d.center['x']," ",d.center['y'])
def dumb_optimize(light):
    #najpierw centrujemy jedną kropkę, np. pierwszą
    center_dot(light,0)
    #pierwsze silniki obu kropek odpowiadają za ruch w pionie, a drugie w poziomie
    #zapisujemy polozenie, w ktorym przynajmniej jedna kropka jest na srodku
    motorpos=np.zeros([4])#przyjmijmy, że zaczynają w zerze
    maxranges=[400,400,400,400]#tzn abs z połozenia każdego silnika nie może tego przekroczyć
    #tbh wystaczy jak nie wylecimy z pierwszymi dwoma parametrami, bo reszta jakoś się sama dostosuje, żeby działać
    d_ref=light.dots[0]
    d=light.dots[1]
    d_ref.take_picture()
    d.take_picture()
    bestpos=np.zeros([4])
    bestdis=dis_y(d.center,d.goalpos)
    while(np.abs(motorpos[0])<maxranges[0]):
        move(light.motors[0],50)
        motorpos[0]+=50
        motorpos[2]+=axis_center(light.motors[2],dis_y,d_ref)
        #przekazywanie tych argumentów jest zrobione jakoś super idiotycznie, ale whatever
        d.take_picture()
        if(dis_y(d.center,d.goalpos)<bestdis):
            bestpos=copy.deepcopy(motorpos)
        if(np.sqrt(dis_y(d.center,d.goalpos))>300):
            #to znaczy, że serio jest słabo
            break
    move(light.motors[0],int(-motorpos[0]))
    while(np.abs(motorpos[0])<maxranges[0]):
        move(light.motors[0],-50)
        motorpos[0]-=50
        motorpos[2]+=axis_center(light.motors[2],dis_y,d_ref)
        #przekazywanie tych argumentów jest zrobione jakoś super idiotycznie, ale whatever
        d.take_picture()
        if(dis_y(d.center,d.goalpos)<bestdis):
            bestpos=copy.deepcopy(motorpos)
        if(np.sqrt(dis_y(d.center,d.goalpos))>300):
            #to znaczy, że serio jest słabo
            break
    bestdis=dis_x(d.center,d.goalpos)
    while(np.abs(motorpos[1])<maxranges[1]):
        move(light.motors[1],50)
        motorpos[1]+=50
        motorpos[3]+=axis_center(light.motors[3],dis_x,d_ref)
        #przekazywanie tych argumentów jest zrobione jakoś super idiotycznie, ale whatever
        d.take_picture()
        if(dis_x(d.center,d.goalpos)<bestdis):
            bestpos=copy.deepcopy(motorpos)
        if(np.sqrt(dis_x(d.center,d.goalpos))>300):
            break
    move(light,motors[1],-int(motorpos[1]))
    while(np.abs(motorpos[1])<maxranges[1]):
        move(light.motors[1],-50)
        motorpos[1]-=50
        motorpos[3]+=axis_center(light.motors[3],dis_x,d_ref)
        #przekazywanie tych argumentów jest zrobione jakoś super idiotycznie, ale whatever
        d.take_picture()
        if(dis_x(d.center,d.goalpos)<bestdis):
            bestpos=copy.deepcopy(motorpos)
        if(np.sqrt(dis_x(d.center,d.goalpos))>300):
            break
    print("Found the optimal position\n")#hehe jasne, to nigdy nie zadziała
    for index,motor in enumerate(light.motors):
        move(motor,int(bestpos[index]-motorpos[index]))
    #krecimy o jakiś ustalony krok pierwszym silnikiem pierwszej kropki
    #dla kazdego polozenia obracamy drugi silnik do momentu, w którym ta pierwsza kropka powróci do położenia centralnego(powiedzmy, że tylko w osi y)
    #liczymy, że znajdziemy położenie, w którym przy okazji druga kropka się wycentruje w osi y (po przeszukaniu wszystkich stanów zapisujemy pozycje silników, w których było najlepiej
    #przeszukiwanie w danej osi kończymy kiedy? wstepnie ustalmy jakis maksymalny zakres ruchu dla sliników i tyle
    #potem to samo w drugiej osi i patrzymy na rezultat
def optimal_movement(light):
    step=step_size()
    dist0=np.array([distance(d.center,d.goalpos)for d in light.dots])
    dist=np.zeros([light.motors.size,light.dots.size])
    derivative=np.zeros([light.motors.size,light.dots.size])
    for index,motor in enumerate(light.motors):
        move(motor,int(step))
        for i,d in enumerate(light.dots):
            d.take_picture()
            dist[index][i]=distance(d.center,d.goalpos)
        move(motor,-int(step))
    for k in range(light.motors.size):
        for l in range(light.dots.size):
            derivative[k,l]=(dist[k,l]-dist0[l])/step
    #derivative=np.sum(derivative,axis=1)#bo optymalizujemy sume kwadratow oldeglosci na obu obrazach
    derivative=derivative[:,0]
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
        #optimize(light)
        dumb_optimize(light)
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
run_experiment([moved_beams[1]])

