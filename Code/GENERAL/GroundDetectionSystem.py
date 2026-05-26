#!/usr/bin/env pybricks-micropython

import time
from threading import Thread
from pybricks.ev3devices import ColorSensor
from pybricks.parameters import Color

from state_controller import State, State_Controller


FOUL_TIME = 5

FOUL_COLOUR = "Black"

FIRST_MARKER = "Blue"
SECOND_MARKER = "Red"

BORDER_COLOUR = "White"

class Foul_controller():
    def __init__(self, state_controller: State_Controller, colour_sensor: ColorSensor):
        self.state_controller = state_controller

        self.colour_sensor = colour_sensor
        
        self.observe_ground_thread = Thread(target=self.observe_ground)
        self.observe_ground_thread.daemon = True
        self.observe_ground_thread.start()

        self.observed_colour = None

        self.currently_foul = False
        
        self.on_tape = False

    def observe_ground(self):
        while True:
            self.observed_colour = self.colour_sensor.color_name()

            if self.observed_colour == FOUL_COLOUR and not self.currently_foul:
                self.on_foul_detected()

            elif self.observed_colour == BORDER_COLOUR:
                self.on_tape = True

            elif self.observed_colour == FIRST_MARKER:
                pass

            elif self.observed_colour == SECOND_MARKER:
                pass

            time.sleep(0.75)

    def on_foul_detected(self):
        self.currently_foul = True

        timer_thread = Thread(target=timer)
        timer_thread.deamon = True
        time_thread.start()

        # UPDATE STATE MACHINE

    def foul_timer(self):
        time.sleep(FOUL_TIME)

        # Return to field 

        # UPDATE STATE MACHINE
        
        self.currently_foul = False


# Plan

## Detect Ground colour thread
    # Constantly running
    # Detects if the ground is any non green color
    # Calls other functions to handle that change

