#!/usr/bin/env pybricks-micropython

# ++++++++++++++++++++++++++++++++
# ======== Work of Dexter ========
# ++++++++++++++++++++++++++++++++

# Imports
import time  # To use timer
from threading import Thread  # For the constant ground detection thread and the timer
from pybricks.ev3devices import ColorSensor  # To detect the ground colour

# Allow use to take in the state_controller and know what it is, to set a few variables
from StateController import State, State_Controller

# Constant foul time, might add to Gabe's constants file
FOUL_TIME = 5

# Colour constants for field objects
FOUL_COLOUR = "Black"
FIRST_MARKER = "Blue"
SECOND_MARKER = "Red"
BORDER_COLOUR = "White"


# Ground Observer Class
class Ground_Observer:
    def __init__(self, state_controller: State_Controller, colour_sensor: ColorSensor):
        # Local refrence to state controller, as to allow for variable setting
        self.state_controller = state_controller
        self.state = State.IDLE

        # Allow any ports colour_sensor to work with it as an argument
        self.colour_sensor = colour_sensor

        # Observe Ground thread set up
        self.observe_ground_thread = Thread(target=self.observe_ground)
        # self.observe_ground_thread.daemon = True
        self.observe_ground_thread.start()

        # The currently observed colour
        self.observed_colour = None

        # If we are currenty fouled
        self.currently_foul = False

    # Observe the ground thread
    def observe_ground(self):
        # Loop forever
        while True:
            # Set the observed colour
            self.observed_colour = self.colour_sensor.color_name()

            # Start the foul detected if in foul and not fouling
            if self.observed_colour == FOUL_COLOUR and not self.currently_foul:
                self.on_foul_detected()

            # If fouling update if no longer
            if self.currently_foul:
                # Check state
                if self.state_controller.get_state() != State.FOUL:
                    # turn currently foul off
                    self.currently_foul = False

            # Updated state contellers local ground colour (so Gabe can use that as secondary navigation checker, and foul)
            self.state_controller.set_ground_colour(self.observed_colour)

            # Don't want to kill the CPU
            time.sleep(0.75)

    # When the foul is detected
    def on_foul_detected(self):
        # Set currently_foul local and state
        self.currently_foul = True
        self.state_controller.set_foul_state()

        # Start a timer thread
        timer_thread = Thread(target=self.foul_timer)
        # timer_thread.deamon = True
        timer_thread.start()

    # The foul timer, so we don't stay fouled forever
    def foul_timer(self):
        # Sleep for the foul time
        time.sleep(FOUL_TIME)

        # Tell state controller foul is over but don't change state (Need to return to field)
        self.state_controller.toggle_foul_elapsed()
