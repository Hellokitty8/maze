# retrieval.c - Follow and push behavior.
# Made to make the e-puck converge and push the box.

ON = 1
OFF = 0
NB_LEDS = 8
PUSH_TRESHOLD = 500

class retrieval(object):

    def __init__(self):
        self.left_wheel_speed = 0
        self.right_wheel_speed = 0
        self.LED = [None]*NB_LEDS
        self.converge = False
        self.push = True
    
    ### Internal Functions ###
                
    def __update_speed(self, IR_number):
        if (IR_number == 0):
            self.left_wheel_speed = self.left_wheel_speed + 700            
        elif(IR_number == 7):
            self.right_wheel_speed = self.right_wheel_speed + 700            
        elif(IR_number ==1):
            self.left_wheel_speed = self.left_wheel_speed + 350
        elif(IR_number == 6):
            self.right_wheel_speed = self.right_wheel_speed + 350            
        elif(IR_number == 2):
            self.left_wheel_speed = self.left_wheel_speed + 550
            self.right_wheel_speed = self.right_wheel_speed - 300            
        elif(IR_number == 5):
            self.right_wheel_speed = self.right_wheel_speed + 550
            self.left_wheel_speed = self.left_wheel_speed - 300            
        elif(IR_number == 3):
            self.left_wheel_speed = self.left_wheel_speed + 500
        elif(IR_number == 4):
            self.left_wheel_speed = self.left_wheel_speed - 500
            self.right_wheel_speed += 500


    # The movement for converging to the box
    def __converge_to_box(self,IR_sensor_value, IR_treshold):
        self.left_wheel_speed = 0
        self.right_wheel_speed = 0
        for i in range (NB_LEDS):
            if (IR_sensor_value[i] < IR_treshold):
                self.converge = True
                self.LED[i] = ON
                self.__update_speed(i)
            else:
                self.LED[i] = OFF

    # The behavior when pushing the box                   
    def __push_box(self, IR_sensor_value, IR_threshold):
        self.left_wheel_speed = 0
        self.right_wheel_speed = 0
        # Blink for visual pushing feedback
        for i in range(NB_LEDS):
            if (self.LED[i] == ON):
                self.LED[i] = OFF
            else:
                self.LED[i] = ON      
            if(IR_sensor_value[i] < IR_threshold):
                self.__update_speed(i)

        if(IR_sensor_value[0] < IR_threshold) and (IR_sensor_value[7] < IR_threshold):
            self.left_wheel_speed = 1000
            self.right_wheel_speed = 1000
        

    # Selects the behavior push or converge            
    def __select_behaviour(self, IR_sensor_value):
        self.push = False
        self.converge = False
        for i in range(NB_LEDS):
            if (IR_sensor_value[i] < PUSH_TRESHOLD):
                self.push = True
                break
    
    ### External Functions ###

    # Converge, push, and stagnation recovery
    def swarm_retrieval(self, IR_sensor_value, IR_threshold):
        self.__select_behaviour(IR_sensor_value)
        if (self.push):
            self.__push_box(IR_sensor_value, IR_threshold)
        else:
            self.__converge_to_box(IR_sensor_value, IR_threshold)

    def get_retrieval_left_wheel_speed(self):
        return self.left_wheel_speed

    def get_retrieval_right_wheel_speed(self):
        return self.right_wheel_speed

    def get_LED_states(self):
        return self.LED
