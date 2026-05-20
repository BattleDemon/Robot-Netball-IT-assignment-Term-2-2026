#!/usr/bin/env pybricks-micropython

''' This File is a combination of Hugo and Dexter's work '''

# Import things from the other files so we can use them from one file

from pybricks.hubs import EV3Brick
from pybricks.ev3devices import (
    Motor, TouchSensor, ColorSensor,
    InfraredSensor, UltrasonicSensor, GyroSensor
)
from pybricks.parameters import Port, Button, Color
from pybricks.tools import wait

from pybricks.iodevices import I2CDevice

# Non Ev3 Imports
from threading import *
import os
import time
import random

from IRlocation import irLocator

ev3 = EV3Brick()

# States
class State():
    IDLE = 1
    FOUL = 2
    PASSING = 3
    RETRIEVING = 4
    LOCATING = 5
    POSITIONING = 6

# State Machine
class State_Controller():
    def __init__(self):
        self.state = State.IDLE

class Defender(): 
    def __init__(self):
        self.stateMachine = State_Controller()
        self.has_ball = False

        self.IR_sensor = I2CDevice(Port.S2,0x08)

        self.IR_position = None
        self.IR_strength = None

        self.IR_thread = Thread(target=irLocator, args=(self,self.IR_sensor))
        self.IR_thread.daemon = True
        self.IR_thread.start()

    def main(self):
        ev3.screen.print("EV3 TEST READY")
        time.sleep(1)
        ev3.screen.clear()

        while True:
            ev3.screen.print(self.IR_position) 

            time.sleep(0.4)

defender = Defender()
defender.main()
