#!/usr/bin/env pybricks-micropython

import time

''' Work of Dexter '''

#User Presses touch sensor once (tells machine it is being moved to foul)

#User Presses again to signify the machine is in the foul zone.abs

# Wait until foul has elapsed

# Leave foul zone 

# return to normal state

class Foul_controller():
    def __init__(self, owner, colour_sensor):
        self.colour_sensor = colour_sensor
        
        self.observe_ground_thread = Thread(target=observe_ground)
        self.observe_ground_thread.daemon = True
        self.observe_ground_thread.start()

        self.observed_colour = None

        self.currently_foul = False

    def observe_ground(self):
        while True:
            self.observed_colour = self.colour_sensor.color_name()

            if self.colour_sensor == "White" and self.currently_foul == False:
                self.currently_foul = True
                foul()

            ## Checks for tape on ground that send to owner

            time.sleep(0.75)

    def foul(self):
        pass