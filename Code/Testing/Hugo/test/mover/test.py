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


ev3 = EV3Brick()

motorL = Motor(Port.C)
motorR = Motor(Port.D)
pusher = Motor(Port.A)

motorL.run(1000)
motorR.run(1000)
sleep(2)