#!/usr/bin/env pybricks-micropython

from time import sleep, time
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import (
    Motor,
    TouchSensor,
    ColorSensor,
    InfraredSensor,
    UltrasonicSensor,
    GyroSensor,
)
import random
from pybricks.parameters import Port, Stop, Direction, Button, Color
from pybricks.tools import wait, StopWatch, DataLog
from pybricks.robotics import DriveBase
from pybricks.media.ev3dev import SoundFile, ImageFile, Font
from math import pi, tan, sin, cos
import os
import threading

from GENERAL import movement,IRlocation
from GENERAL.StateController import State_Controller

from DEFENCE.PushAndAim import PushAndAim


class StateActions:
    def __init__(self, PushMotor: Motor, StateController: State_Controller, driver: movement.Driver ) -> None:
        self.PushMotor = PushMotor
        self.State = StateController
        self.Driver = driver
        self.pushingCode = PushAndAim(self.PushMotor)

    #When foul ends

    # Passing
    def Passing(self):
        
        angleToTeamMate = self.pushingCode.get_aim_angle(self.State.position, self.State.others_position)
        self.Driver.pivot("LEFT") # NEED GABE TO CODE A PIVOT BY ANGLE
        self.pushingCode.push()
    
    # retrieving
        #NEEDS ZENS TRIANGULATION CODE
    # Locating
    def Locating(self):
        self.Driver.turn_angle(10)

    # Positioning
    def Positioning(self):
        pass


    # Receiving
        # Get ready to receive the ball from your teammate

    #Waiting

    #Main loop