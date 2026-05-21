#!/usr/bin/env pybricks-micropython

''' Work of Dexter '''

#User Presses touch sensor once (tells machine it is being moved to foul)

#User Presses again to signify the machine is in the foul zone.abs

# Wait until foul has elapsed

# Leave foul zone 

# return to normal state

class Foul_controller():
    def __init__(self,colour_sensor):
        self.colour_sensor = colour_sensor
        
        self.see_ground_thread = Thread(target=see_ground)

    def see_ground(self):
        pass

    def foul(self):
        pass