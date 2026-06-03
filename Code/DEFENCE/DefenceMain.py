#!/usr/bin/env pybricks-micropython

# ++++++++++++++++++++++++++++++++*********
# ======== Work of Hugo and Dexter ========
# ++++++++++++++++++++++++++++++++*********

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
from GENERAL.GroundDetectionSystem import Ground_Observer
from GENERAL.communication import Communicator
from DEFENCE.ActioningStates import StateActions

# Main Robot class for the defending robot
class Defender(): 
    def __init__(self):

        pass
