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
from GENERAL.state_controller import State, State_Controller
from GENERAL.movement import Driver
import CatchAndThrow
from GENERAL.GroundDetectionSystem import Ground_Observer


# Main Robot class for the defending robot
class Defender(): 
    def __init__(self):

        self.ev3 = EV3Brick()

        self.state_controller = State_Controller()
        
        self.team = "Defence"

        self.left_wheel
        self.right_wheel

        self.gyro

        self.driver = Driver(self.ev3, self.left_wheel, self.right_wheel, self.team, self.gyro)

        self.has_ball

        self.ball_sensor = ColorSensor() # add port
        self.colour_sensor_thread = Thread(target=ball_sensing)
        self.ball_sensor_thread.start()

        self._ground_colour_sensor = ColorSensor() # Add port

        self.ground_observer = Ground_Observer()

        self.IR_sensor = I2CDevice(Port.s2,0x08)

        self.IR_position
        self.IR_strength
        self.IR_thread = Thread(target=irLocator, args=(self,self.IR_sensor))
        self.IR_thread.start()


    def ball_sensing(self):
        while True:
            if self.ball_sensor.color() == Color.BLACK:
                self.has_ball = True
                while True:
                    if self.ball_sensor.color() != Color.BLACK:
                        break
                time.sleep(0.5)
            time.sleep(0.5)

    def main(self):
        self.ev3.screen.print("EV3 TEST READY")
        time.sleep(1)
        self.ev3.screen.clear()

        while True:
            self.ev3.screen.print(self.IR_position) 

            time.sleep(0.4)

defender = Defender()
defender.main()
