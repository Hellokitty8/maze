# File:         single_DeepQ_learning.py
# Date:          
# Description:   
# Author:   jia      
# Modifications: 

# or to import the entire module. Ex:
#  from controller import *

import sys 
sys.path.append('/usr/local/lib/python2.7/site-packages')
sys.path[2]='/usr/local/lib/python2.7/site-packages'
import os
from controller import *
from numpy import *
from math import *
from search import search
from retrieval import retrieval
from stagnation import stagnation
import epuck_basic
#from keras.models import Sequential
#from keras.layers.core import Dense, Dropout, Activation
#from keras.optimizers import RMSprop
import math
import time


Search = search()
Retrieval = retrieval()
Stagnation = stagnation(Search)

MIN_FEEDBACK = 1
MAX_FEEDBACK = 8
DISTANCE_TRESHOLD = 200
IR_TRESHOLD = 3500
ACTION=["left","right","go"]
# Here is the main class of your controller.
# This class defines how to initialize and how to run your controller.
# Note that this class derives Robot and so inherits all its functions
class _crabs (epuck_basic.EpuckBasic):

    
    def initialization(self):
        self.emitter = self.getEmitter('emitter')
        self.emitter.setChannel(2)
        self.gps=self.getGPS('gps')
        
        self.speeds=[0.0,0.0]
        self.maxSpeed=1000
        self.setSpeed(500,500)
    
    def getGpsValue(self):
        self.gps.enable(self.timestep)
        gps_values=self.gps.getValues()
        return gps_values
  
   
    
    def scale_data(self,data):
        min_max_scaler = preprocessing.MinMaxScaler()
        X_train = np.array(data) 
        print X_train
        X_train_minmax = min_max_scaler.fit_transform(X_train)
        return X_train_minmax
        
    def get_reward(self,sensor,gps):
        sensorStateCheck=array([int(i>85) for i in sensor])
        mask_sensor=array([1, 0, 0, 0, 0, 0, 0, 1])
        front=sum(sensorStateCheck&mask_sensor)
        
        if (front==2):
            print ("help,I ganna killed!!")
            self.set_wheel_speeds(0, 0)
            reward=-100
        else:
            reward=-1
        if (gps[2]<-0.7):
            print ("wow! I am out!")
            reward=100
        return reward
        
    def makeMove(self,qval):
        if qval==2:
           self.set_wheel_speeds(0.5, 0.5)
        if qval==0:
           self.turn_left()
           
           #self.set_wheel_speeds(1, 1)
           #self.do_timed_action(duration = 5)
        if qval==1:
           self.turn_right()
           
           #self.set_wheel_speeds(1, 1)
           #self.do_timed_action(duration = 5)
           
    def makeMoveDo(self,qval):
        if qval==2:
           self.set_wheel_speeds(0.5, 0.5)
           self.do_timed_action(duration = 2)
        if qval==0:
           self.turn_left()
           self.set_wheel_speeds(0.5, 0.5)
           self.do_timed_action(duration = 2)
        if qval==1:
           self.turn_right()
           self.set_wheel_speeds(0.5, 0.5)
           self.do_timed_action(duration = 2)

        
    def run(self):
        
        
        reward=10
        self.basic_setup()
        i=0
        f1 = open('/Users/jiawang/Data1.txt','w')
        status=1
        flag=0
        replay = []                
        
        while (status == 1):
            action=[]
            epochs = 5
            gamma = 0.9 #since it may take several moves to goal, making gamma high
            epsilon = 1
            batchSize = 10
            buffer = 20
            h = 0
            sensor=self.get_proximities()
            StateCheckA=array([int(i>90) for i in [sensor[0],sensor[7]]])
            StateCheckB=array([int(i>40) for i in [sensor[5],sensor[2],sensor[6],sensor[1],sensor[3],sensor[4]]])
            statesumA=sum(StateCheckA)
            statesumB=sum(StateCheckB)
            StateCheck=concatenate((StateCheckA, StateCheckB), axis=0)
          
            
            for i in range (5) :
                sensor=self.get_proximities()
                self.step(self.timestep)
                if StateCheck[2]==1 and StateCheck[3]==1:
                    continue 
                    
                    
            StateCheckA=array([int(i>90) for i in [sensor[0],sensor[7]]])
            StateCheckB=array([int(i>45) for i in [sensor[5],sensor[2],sensor[6],sensor[1],sensor[3],sensor[4]]])
            statesumA=sum(StateCheckA)
            statesumB=sum(StateCheckB)
            StateCheck=concatenate((StateCheckA, StateCheckB), axis=0)
             
            
            sensor_front=sum([sensor[0],sensor[7]])
            sensor_left=sum([sensor[5],sensor[6]])
            sensor_right=sum([sensor[1],sensor[2]])
             
            sensor_method=[sensor_left,sensor_right,sensor_front]
            norm_a = [float(i)/sum(sensor_method) for i in sensor_method]
            norm_b = sensor_method
            norm = [float(i)/max(sensor_method) for i in sensor_method]
            if norm[0]==1:
                sensor_front=sensor[0]
                
            if norm[1]==1:
                sensor_front=sensor[1]
                
                
            sensor_method=[sensor_left,sensor_right,sensor_front]
            norm = [float(i)/sum(sensor_method) for i in sensor_method]
            
            sensor_std=var(norm)
            print ("norm_a",norm_a)
            print ("norm",norm)
            print ("sensor_std",sensor_std)
            
            
            if sensor_std>0.03:
                big=argmax(norm)
                sma=argmin(norm)
                
                norm.remove(norm[big])
                sensor_std_=var(norm)
                print ("sensor_std_",sensor_std_)
                if sensor_std_>0.006:
                    action=[sma]
                    
                else:
                    action=[0,1,2]
                    action.remove(big)
                    
            else:
                
                action=[0,1,2]
                
            #if statesumA==0: # The front is empty
                #action.append(2)

            #if StateCheckB[0]==0:
                #action.append(0)

            #if StateCheckB[1]==0:
                #action.append(1)
                
            #if action==[]:
                #action.append(random.randint(0,2))
                    #print "here!"
                    #action = 1
                    #self.makeMove(action)
                    #sensor=self.get_proximities()
                    #gps=self.getGpsValue()
                    #reward = self.get_reward(sensor,gps)
                    #replay.append((StateCheck, reward, action))
            
            
            
            doAction=random.choice(action)
            doAction=2
            print action
            print ACTION[doAction]
            self.makeMoveDo(doAction)
            action=[]
            sensor_next=self.get_proximities()
            gps=self.getGpsValue()   
            reward = self.get_reward(sensor_next,gps)   
            replay.append((sensor, reward, doAction))
                 
            if reward == 100:
                status = 0          
                f1.write(str(replay))
            if self.step(32) == -1:
            
                
                break
    
# The main program starts from here

# This is the main program of your controller.
# It creates an instance of your Robot subclass, launches its
# function(s) and destroys it at the end of the execution.
# Note that only one instance of Robot should be created in
# a controller program.


controller = _crabs()
controller.initialization()
controller.run()
#controller.model()
