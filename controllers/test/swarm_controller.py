# File:          _crabs.py
# Date:          
# Description:   
# Author:        
# Modifications: 

# or to import the entire module. Ex:
#  from controller import *
from controller import *
from search import search
from retrieval import retrieval
from stagnation import stagnation
import epuck_basic

Search = search()
Retrieval = retrieval()
Stagnation = stagnation(Search)

MIN_FEEDBACK = 1
MAX_FEEDBACK = 8
DISTANCE_TRESHOLD = 200
IR_TRESHOLD = 3500

# Here is the main class of your controller.
# This class defines how to initialize and how to run your controller.
# Note that this class derives Robot and so inherits all its functions
class _crabs (epuck_basic.EpuckBasic):

    stagnation_count = 0
    feedback = 5
    timestep = 0  
    
    def grid(self,x,y):
      rs=int ((x+0.6)/0.15) *int((y+0.6)/0.15) 
      return rs

  
#------>7
#|
#|
#|
#|(7)

    def run(self):
    
        self.basic_setup()
        
        while True:
            while self.receiver.getQueueLength()>0 :
                message = self.receiver.getData()
                
                
                print 'I should '+message+'!'  
                x=float(message.split('[')[1].split(',')[0])
                y=float(message.split('[')[1].split(',')[2].split(']')[0])
                states=self.grid(x,y)
                #print ('state',states)
                print ('queue0',self.receiver.getDataSize())
                #while self.receiver.getQueueLength()>2:
                self.receiver.nextPacket()
                    
            
                print ('queue1',self.receiver.getQueueLength())
              
            Search.update_search_speed(self.get_proximities(), DISTANCE_TRESHOLD)
            Retrieval.swarm_retrieval(self.get_lights(), IR_TRESHOLD)     
            self.set_LEDS(Retrieval.get_LED_states())

            if not (Retrieval.converge or Retrieval.push) :
                print "Performing Search Action"
                self.set_wheel_speeds(Search.get_search_left_wheel_speed(), Search.get_search_right_wheel_speed())
     

            elif Retrieval.push:
                if self.timestep >= self.timed_review(self.feedback):
                    print "Push Testing"            
                    pds = self.get_proximities()
                    self.step(10*self.timestep_duration)
                    Stagnation.evaluate_pushing(self.get_proximities(), pds)
                    
                    if Stagnation.get_stagnation_state():  
                        print self.stagnation_count
                        print "Stagnation"   
                        if self.stagnation_count < 2:
                            print "Realigning"
                            Stagnation.stagnation_recovery(self.get_proximities(), DISTANCE_TRESHOLD)
                            self.set_wheel_speeds(Stagnation.get_stagnation_left_wheel_speed(), Stagnation.get_stagnation_right_wheel_speed())
                            self.stagnation_count += 1    
                        else:
                            print "Find New Spot"
                            while True:
                                self.green_LED_blink() 
                                Stagnation.find_new_spot(self.get_proximities(), DISTANCE_TRESHOLD)
                                self.set_wheel_speeds(Stagnation.get_stagnation_left_wheel_speed(), Stagnation.get_stagnation_right_wheel_speed())
                                self.run_timestep()
                                if(Stagnation.twice == 2):
                                    self.green_led.set(0)
                                    self.stagnation_count = 0
                                    break
                        feedback = max(self.feedback -1, MIN_FEEDBACK)
                    else:
                        Stagnation.reset_stagnation()
                        feedback = min(self.feedback+1, MAX_FEEDBACK)
                    self.timestep = 0
                else:
                    self.set_wheel_speeds(Retrieval.get_retrieval_left_wheel_speed(), Retrieval.get_retrieval_right_wheel_speed())
                    self.timestep += 1
            else:
                self.set_wheel_speeds(Retrieval.get_retrieval_left_wheel_speed(), Retrieval.get_retrieval_right_wheel_speed())
            
            self.do_timed_action()    
             
            if self.step(32) == -1:
                break
    
# The main program starts from here

# This is the main program of your controller.
# It creates an instance of your Robot subclass, launches its
# function(s) and destroys it at the end of the execution.
# Note that only one instance of Robot should be created in
# a controller program.
controller = _crabs()
controller.run()
