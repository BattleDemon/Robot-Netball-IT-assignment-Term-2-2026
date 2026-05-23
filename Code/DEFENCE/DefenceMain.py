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
from IRlocation import irLocator
from state_controller import State, State_Controller
from movement import Driver
from Foul_Controller import Foul_controller

#rgeogeo

class Defender(): 
    def __init__(self):
        self.ev3 = EV3Brick()
        self.driver = "Make a Drive Base Like Class that controls motors (handles turns ect)"
        
        self.has_ball = False
        self.ball_sensor = ColorSensor() # Add Port
        self.ball_sensor_thread = Thread(target=ball_sensing)
        self.ball_sensor_thread.daemon = True
        self.ball_sensor_thread.start()

        self.bottom_color_sensor = ColorSensor() # Add Port
        self.Foul_controller = Foul_controller()

        self.stateMachine = State_Controller()

        self.IR_sensor = I2CDevice(Port.S2,0x08)
        self.IR_position = None
        self.IR_strength = None
        self.IR_thread = Thread(target=irLocator, args=(self,self.IR_sensor))
        self.IR_thread.daemon = True
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
