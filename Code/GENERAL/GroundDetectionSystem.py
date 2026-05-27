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

    def observe_ground(self):
        while True:
            self.observed_colour = self.colour_sensor.color_name()

            if self.observed_colour == FOUL_COLOUR and not self.currently_foul:
                self.on_foul_detected()

            self.state_controller.set_ground_colour(self.observed_colour)

            time.sleep(0.75)

    def on_foul_detected(self):
        self.currently_foul = True
        self.state_controller.set_foul_state()

        timer_thread = Thread(target=timer)
        timer_thread.deamon = True
        time_thread.start()


    def foul_timer(self):
        time.sleep(FOUL_TIME)

        self.state_controller.toggle_foul_elapsed()

        self.currently_foul = False
