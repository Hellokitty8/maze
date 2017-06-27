#   search.py - Search and Avoid behavior.
# 	Made to calculate the speed from distance sensors input.
#	By getting sensor input from the four front distance sensors on the e-puck
# 	it will be determined the speed of the left and right wheel according to
# 	the case script and a threshold. If nothing is in your way - search. 
# 	case script: the four first int's are the sensor input, while the last two are speed

from random import uniform

COUNT_LIMIT = 20

class search(object):

    def __init__(self):
        self.left_wheel_speed = 0
        self.right_wheel_speed = 0
        self.rand_double_left = 0
        self.rand_double_right = 0
        self.counter = 0
        self.case_script = [[0,0,0,0,1,1],[0,0,0,1,1,0],[0,0,1,0,1,0],[0,0,1,1,1,0],[0,1,0,0,0,1],[0,1,0,1,1,0],[0,1,1,0,0,1],[0,1,1,1,1,0],[1,0,0,0,0,1],[1,0,0,1,1,0],[1,0,1,0,0,1],[1,0,1,1,1,0],[1,1,0,0,0,1],[1,1,0,1,1,0],[1,1,1,0,0,1],[1,1,1,1,0,1]];
    
    ### Internal Functions ###

    def __randdouble(self):
        self.rand_double_left = uniform(0, 1)
        self.rand_double_right = uniform(0, 1)

    #Given the input compared to the case script; where do we want to go?
    def __calculate_search_speed(self, threshold_list):
        self.counter = self.counter + 1
        for i in range(16):
            if (threshold_list[0] == self.case_script[i][0]) and (threshold_list[1]==self.case_script[i][1]) and (threshold_list[2]==self.case_script[i][2]) and (threshold_list[3]==self.case_script[i][3]):
                if self.counter == COUNT_LIMIT:
                    self.counter = 0
                    self.__randdouble()
                #Free Path
                if self.case_script[i][4] == self.case_script[i][5]:
                    self.left_wheel_speed = (self.rand_double_left*500) + 500
                    self.right_wheel_speed = (self.rand_double_right*500) + 500
                #Turn Left
                elif self.case_script[i][4] == 1 and self.case_script[i][5]== 0:
                    self.left_wheel_speed=-300
                    self.right_wheel_speed= 700
                #Turn Right
                else:
                    self.left_wheel_speed =700
                    self.right_wheel_speed = -300
       

    #Calculate if there is an obstacle or not, depending on the threshold 
    def __calculate_treshold(self, sensors, distance_treshold):
        treshold_list = [0]*4
        for i in range(4):
            if sensors[i] > distance_treshold:
                treshold_list[i] = 1
            else:
                treshold_list[i] = 0
        self.__calculate_search_speed(treshold_list)

    ### External Functions ###

    #Given the sensor input and threshold, calculates the speed for survival
    def update_search_speed(self, sensor_value, distance_treshold):
        sensors = [sensor_value[6], sensor_value[7], sensor_value[0], sensor_value[1]]
        self.__calculate_treshold(sensors, distance_treshold)

    def get_search_left_wheel_speed(self):
        return self.left_wheel_speed

    def get_search_right_wheel_speed(self):
        return self.right_wheel_speed
