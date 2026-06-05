#!/usr/bin/env pybricks-micropython

''' This File is a combination of Hugo and Dexter's work '''

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

# Local Imports
from GENERAL.IRlocation import irLocator
from GENERAL.StateController import State, State_Controller
from GENERAL.movement import Driver
import CatchAndThrow


class SubDefence():
    def __init__(self) -> None:
        self.CatchAndThrowThread = Thread(target=CatchAndThrow.Catch_throw)
        self.CatchAndThrowThread.start()