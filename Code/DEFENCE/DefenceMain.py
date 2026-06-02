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


# Main Robot class for the defending robot
class Defender(): 
    def __init__(self):

        self.ev3 = EV3Brick()
        self.team = "Defence"
        self.state_controller = State_Controller(self, self.team, 0,0,0,0,0,0,0)
        
        

        self.Communicator = Communicator(self.state_controller,self.team, self.ev3)
        self.Communication_Thread= Thread(target= self.Communicator.CommunicationLoop())
        self.Communication_Thread.start()

        self.left_wheel = Motor(Port.A)# not sure if correct
        self.right_wheel= Motor(Port.B)# not sure if correct

        self.gyro = GyroSensor(Port.S1)

        self.ball_sensor = ColorSensor(Port.S4) # add port
        self.ball_sensor_thread = Thread(target=self.ball_sensing)
        self.ball_sensor_thread.start()
        self.has_ball = False

        self.driver = Driver(self.ev3, self.left_wheel, self.right_wheel,self.ball_sensor, self.team, self.gyro)

        

        

        self._ground_colour_sensor = ColorSensor(Port.S3) # Add port

        self.ground_observer = Ground_Observer(self.state_controller,self._ground_colour_sensor)

        self.IR_sensor = I2CDevice(Port.S2,0x08)

        irData = self.IR_sensor.read(2,2)

        self.IR_position = irData[0]
        self.IR_strength = irData[1]
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
