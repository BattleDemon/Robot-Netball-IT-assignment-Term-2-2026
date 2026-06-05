#!/usr/bin/env pybricks-micropython

# ++++++++++++++++++++++++++++++++**********
# ==== Work of Hugo (started by dexter) ====
# ++++++++++++++++++++++++++++++++**********

from pybricks.hubs import EV3Brick
from pybricks.ev3devices import (
    Motor, TouchSensor, ColorSensor,
    InfraredSensor, UltrasonicSensor, GyroSensor
)
from pybricks.parameters import Port, Button, Color

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

from GENERAL.GroundDetectionSystem import Ground_Observer
from GENERAL.communication import Communicator
from DEFENCE.ActioningStates import StateActions

# Main Robot class for the defending robot
class Defender(): 
    def __init__(self):
        

        self.ev3 = EV3Brick()
        self.team = 'defence'
        self.StateController = State_Controller(self,self.team, 0,0,0,0,0,0,0)
        self.has_ball = False
        
        self.leftMotor = Motor(Port.C)
        self.rightMotor = Motor(Port.D)
        self.pushMotor = Motor(Port.A)

        self.GroundDetectionSensor = ColorSensor(Port.S1)
        self.BallSensor = ColorSensor(Port.S4)
        self.gyro = GyroSensor(Port.S2)
        self.ir_sensor = I2CDevice(Port.S4,0x08)

        #self.communicator = Communicator(self.StateController, self.team, self.ev3)
        #self.communicationThread = Thread(target=self.communicator.CommunicationLoop)
        #self.communicationThread.start()

        self.ballSensorThread = Thread(target=self.ball_sensing)
        self.ballSensorThread.start()

        self.Driver = Driver(self.ev3, self.leftMotor,self.rightMotor,self.GroundDetectionSensor,self.team, self.gyro)


        self.stateActioner = StateActions(self.pushMotor, self.StateController, self.Driver,self.ir_sensor)

        self.groundObserver = Ground_Observer(self.StateController, self.GroundDetectionSensor)

        #IR detection initialisation code goes here.
        #self.irLocator = ir_controller(self.ir_sensor,self.StateController)
        #self.irThread = Thread(target=self.irLocator.ir_sensing)
        #self.irThread.start()
        self.Start()
        
    def ball_sensing(self):
        while True:
            if self.BallSensor.color() == Color.BLACK:
                self.has_ball = True
            else:
                self.has_ball = False
            time.sleep(0.5)

    def Start(self):
        while True:
            self.ev3.screen.print("WEEEE I am defending")
            time.sleep(0.2)


defender = Defender()
defender.start()