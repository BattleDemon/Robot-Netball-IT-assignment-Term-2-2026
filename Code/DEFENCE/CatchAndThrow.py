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

IN = -2000
OUT = 2000

ev3 = EV3Brick()

def Catch_throw():
    motor = Motor(Port.B)
    motor2 = Motor(Port.C)
    cs = ColorSensor(Port.S4)
    ballwasthere = False
    while True:
        if cs.color() == Color.BLACK:
            motor.run(OUT)
            motor2.run(OUT)
            ballwasthere = True
        else:
            if ballwasthere:
                sleep(1)
                ballwasthere=False
            motor.run(IN)
            motor2.run(IN)