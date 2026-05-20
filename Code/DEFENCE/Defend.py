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
from enum import Enum
from threading import *
import os
import time
import random

# States
class State(Enum):
    IDLE
    FOUL
    PASSING
    COLLECTING
    POSITIONING
    MOVING


# State Machine
class State_Machine():
    pass

class Defender(): 
    def __init__(self):
        pass