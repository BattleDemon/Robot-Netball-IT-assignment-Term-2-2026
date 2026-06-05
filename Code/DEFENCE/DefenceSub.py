#!/usr/bin/env pybricks-micropython

''' This File is a combination of Hugo and Dexter's work '''

from pybricks.hubs import EV3Brick
from pybricks.ev3devices import (
    Motor, TouchSensor, ColorSensor,
    InfraredSensor, UltrasonicSensor, GyroSensor
)
from pybricks.parameters import Port, Button, Color


from pybricks.iodevices import I2CDevice

# Non Ev3 Imports
from threading import *
import time
import CatchAndThrow


class SubDefence():
    def __init__(self) -> None:
        self.CatchAndThrowThread = Thread(target=CatchAndThrow.Catch_throw)
        self.CatchAndThrowThread.start()
        while True:
            time.sleep(1)


SubDefence()