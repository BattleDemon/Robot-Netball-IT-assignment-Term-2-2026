#!/usr/bin/env pybricks-micropython

import time

''' Work of Dexter '''

#User Presses touch sensor once (tells machine it is being moved to foul)

#User Presses again to signify the machine is in the foul zone.abs

# Wait until foul has elapsed

# Leave foul zone 

# return to normal state

FOUL_TIME = 5

class Foul_controller():
    def __init__(self, owner, colour_sensor):
        self.colour_sensor = colour_sensor
        
        self.observe_ground_thread = Thread(target=observe_ground)
        self.observe_ground_thread.daemon = True
        self.observe_ground_thread.start()

        self.observed_colour = None

        self.currently_foul = False
        
        self.on_tape = False

    def observe_ground(self):
        while True:
            self.observed_colour = self.colour_sensor.color_name()

            if self.colour_sensor == "White" and not self.currently_foul:
                self.on_white_detected()

            if self.colour_sensor == "Black" and not self.currently_foul:
                self.on_tape = True

            if self.colour_sensor != "Black" and self.on_tape:
                self.on_tape = False

            time.sleep(0.75)

    def on_white_detected(self):
        self.currently_foul = True

        timer_thread = Thread(target=timer)
        timer_thread.deamon = True
        time_thread.start()

        # UPDATE STATE MACHINE

        # STOP DRIVER

    def timer(self):
        time.wait(FOUL_TIME)

        # Return to field 

        # UPDATE STATE MACHINE
        
        self.currently_foul = False