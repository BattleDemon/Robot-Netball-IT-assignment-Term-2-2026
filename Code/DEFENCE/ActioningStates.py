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
from GENERAL.StateController import State_Controller, State

from DEFENCE.PushAndAim import PushAndAim


class StateActions:
    def __init__(self, PushMotor: Motor, StateController: State_Controller, driver: movement.Driver ) -> None:
        self.PushMotor = PushMotor
        self.StateController = StateController
        self.Driver = driver
        self.pushingCode = PushAndAim(self.PushMotor)

    #When foul ends
    def EndOfFoul(self):
        self.Driver.home_from_foul_box()
    # Passing
    def Passing(self):
        
        angleToTeamMate = self.pushingCode.get_aim_angle(self.StateController.position, self.StateController.others_position)
        self.Driver.pivot("LEFT") # NEED GABE TO CODE A PIVOT BY ANGLE
        self.pushingCode.push()
    
    # retrieving
        #NEEDS ZENS TRIANGULATION CODE
        
    # Locating
    def Locating(self):
        self.Driver.turn_angle(10)
        

    # Positioning
    def Positioning(self):
        self.Driver.drive_to_point(100,100)


    # Receiving
        # Get ready to receive the ball from your teammate
    def Receiving(self):
        angleToTeamMate = self.pushingCode.get_aim_angle(self.StateController.position, self.StateController.others_position)
        self.Driver.pivot("LEFT") # NEED GABE TO CODE A PIVOT BY ANGLE


    #Waiting
    def Waiting(self):
        pass

    #Main loop
    def MainLoop(self):
        while True:
            Current_state = self.StateController.get_state()
            
            
            