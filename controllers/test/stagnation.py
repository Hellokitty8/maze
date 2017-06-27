#   stagnation.py - Stagnation recovery behavior
#   Whenever the e-puck reason about his push behavior not being effective,
#   the stagnation behavior should trigger. This behavior will reposition the
#   robot, hopefully getting a spot which will result

from random import randint
import math

ON = 1
OFF = 0
NEUTRAL = 3
IR_DIFF_TRESHOLD = 4
DISTANCE_DIFF_TRESHOLD = 300
REVERSE_LIMIT = 30
TURN_LIMIT = 10
FORWARD_LIMIT = 30
NEIGHBOR_LIMIT = 120
OBJECT_LIMIT = 2200
OBJECT_THRESHOLD = 2600

ALIGN_STRAIGHT_TRESHOLD = 100 # If larger, align straight
LOW_DIST_VALUE = 10 # If lower (and detecting IR), the sensor is close

class stagnation(object):

    def __init__(self, srch):
        self.left_wheel_speed = 0
        self.right_wheel_speed = 0
        self.has_recovered = False
        self.turn_left = NEUTRAL
        self.green_LED_state = OFF
        self.reverse_counter = 0
        self.turn_counter = 0
        self.forward_counter = 0
        self.twice = 0
        self.align_counter = 0
        self.Search = srch  

    ### Internal Functions ### 

    def LED_blink(self):
        if(self.green_LED_state == ON):
            self.green_LED_state = OFF
        else:
            self.green_LED_state = ON
    
    def __realign(self, distance_value):

        # Find the difference of the two front IR sensors
        dist_diff_front = distance_value[7] - distance_value[0]
        # Are we pushing straight? If not, maybe we should try. If we are, maybe we should
        # try pushing from another angle.
        if (abs(dist_diff_front) > ALIGN_STRAIGHT_TRESHOLD):
            print "NOT STRAIGHT"
            # Lets push straight, but which way are we angled?
            if (distance_value[0] < LOW_DIST_VALUE):
                self.right_wheel_speed = -500
                self.left_wheel_speed = 500
            elif(distance_value[7] <  LOW_DIST_VALUE):
                self.left_wheel_speed = 500
                self.right_wheel_speed = -500
            elif(distance_value[1] < LOW_DIST_VALUE):
                self.right_wheel_speed = -1000
                self.left_wheel_speed = 700
            elif(distance_value[6] < LOW_DIST_VALUE):
                self.right_wheel_speed = 700
                self.left_wheel_speed = -1000
        # We are standing straight, lets try pushing with another angle.   
        else:
            # Roll a dice, left angle or right angle?
            if (randint(0,1) == 1): #50/50
                self.right_wheel_speed = -500
                self.left_wheel_speed = 500
            else:
                self.right_wheel_speed = 500
                self.left_wheel_speed = -500
        
        self.has_recovered = True
        self.green_LED_state = OFF
   
    ### External Functions ###

    def find_new_spot(self, distance_value, DIST_TRESHOLD):
        if (self.twice == 2):
            self.has_recovered = True
            self.green_LED_state = OFF
            self.align_counter = 0

        elif(self.reverse_counter != REVERSE_LIMIT): # Make Space by moving away
            self.reverse_counter = self.reverse_counter + 1
            self.left_wheel_speed = -800
            self.right_wheel_speed = -800

        elif(self.turn_counter != TURN_LIMIT): # Line up with one of the sides of the box
            self.turn_counter = self.turn_counter +  1
            self.forward_counter = 0
            if self.turn_left == NEUTRAL:
                if (randint(0,1) == 1): # 50/50
                    self.turn_left = OFF
                else:
                    self.turn_left = ON
                    
            if (self.turn_left == ON):
                self.left_wheel_speed = -300
                self.right_wheel_speed = 700
            else:
                self.left_wheel_speed = 700
                self.right_wheel_speed = -300

        elif self.forward_counter != FORWARD_LIMIT:
            self.forward_counter = self.forward_counter + 1
            if (self.forward_counter == FORWARD_LIMIT -1):
                self.twice =  self.twice + 1
                self.turn_counter = 0
                if (self.turn_left == ON):
                    self.turn_left = OFF
                else:
                    self.turn_left = ON
                    
            self.Search.update_search_speed(distance_value, DIST_TRESHOLD)
            self.left_wheel_speed = self.Search.get_search_left_wheel_speed()
            self.right_wheel_speed = self.Search.get_search_right_wheel_speed()
            
            if (self.left_wheel_speed > 0) and (self.right_wheel_speed > 0):
                self.left_wheel_speed = 1000
                self.right_wheel_speed = 1000
           
    def reset_stagnation(self):
        self.has_recovered = False
        self.reverse_counter = 0
        self.turn_counter = 0 
        self.forward_counter = 0
        self.turn_left = NEUTRAL;
        self.twice = 0

    def stagnation_recovery(self, distance_sensors_value, DIST_THRESHOLD):
        if self.align_counter < 2: # Align
            self.align_counter = self.align_counter + 1;
            self.__realign(distance_sensors_value);
        elif self.align_counter > 0: # Reposition
            self.LED_blink();
            self.find_new_spot(distance_sensors_value, DIST_THRESHOLD);
    
    # To keep pushing or not to keep pushing, that is the question
    def evaluate_pushing(self, dist_value, prev_dist_value):
        # The Front IR Sensors Pushing against the box
        dist_diff7 = prev_dist_value[7] - dist_value[7]
        dist_diff0 = prev_dist_value[0] - dist_value[0]
        if abs(dist_diff7) > DISTANCE_DIFF_TRESHOLD and abs(dist_diff0) > DISTANCE_DIFF_TRESHOLD:# and not(abs(accelerometer_value[0]) > ACCELEROMETER_X_THRESHOLD or abs(accelerometer_value[0]) > ACCELEROMETER_Y_THRESHOLD):
            self.has_recovered = True
            self.green_LED_state = OFF
            self.align_counter = 0
        elif (dist_value[5] > NEIGHBOR_LIMIT and dist_value[2] > NEIGHBOR_LIMIT) and (dist_value[5] < OBJECT_THRESHOLD or dist_value[2] < OBJECT_THRESHOLD): #and (dist_value[5] < OBJECT_LIMIT or dist_value[2] < OBJECT_LIMIT)    : # Has Neighbors
            self.has_recovered = True
            self.green_LED_state = OFF
            self.align_counter = 0

        elif (dist_value[5] > NEIGHBOR_LIMIT or dist_value[2] > NEIGHBOR_LIMIT) and not(dist_value[5] > OBJECT_THRESHOLD or dist_value[2] > OBJECT_THRESHOLD): # Has Neighbors
            # Roll a Dice, do i trust just one team mate?
            if randint(0, 1) == 1:
                self.has_recovered = True
                self.green_LED_state = OFF
                self.align_counter = 0

    # Return the boolean value of whether or not to continue with this behavior
    def get_stagnation_state(self):
        if self.has_recovered == True:
            return False
        return True
    
    # Returns the state (ON/OFF) for green LED
    def get_green_LED_state(self):
        return self.green_LED_state

    def get_stagnation_left_wheel_speed(self):
        return self.left_wheel_speed

    def get_stagnation_right_wheel_speed(self):
        return self.right_wheel_speed
