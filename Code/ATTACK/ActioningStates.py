#!/usr/bin/env pybricks-micropython

# +++++++++++++++++++++++++++++++++++++++++
# ========      Work of Hugo       ========
# +++++++++++++++++++++++++++++++++++++++++


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
import time
from pybricks.iodevices import I2CDevice

from GENERAL import movement,IRlocation
from GENERAL.StateController import State_Controller, State
from GENERAL import robot_config

from DEFENCE.PushAndAim import PushAndAim


class StateActions:

    """
    Class to manage what the robot does when a specific state is on.
    """

    def __init__(self, PushMotor: Motor, StateController: State_Controller, driver: movement.Driver, ir_sensor:I2CDevice, ev3, grabber=None ) -> None:
        # get a reference to the motor Can be any random motor, will not be used
        self.PushMotor = PushMotor
        # get a refeerence to the current state controller
        self.StateController = StateController
        # get a reference to the current driver functions
        self.Driver = driver
        # get a reference to the Pushing code for the defence robot but it is only used for getting the angle to our teammate
        self.pushingCode = PushAndAim(self.PushMotor)
        # Variable to know if the robot was previously in the foul box so we know when to go home.
        self.wasinfoul = False

        self.ir_sensor = ir_sensor
        self.ev3 = ev3
        self.grabber = grabber

        
        # create the thread for the main loop
        ActioningStates_t = threading.Thread(target=self.MainLoop)
        # start the thread
        ActioningStates_t.daemon = True
        ActioningStates_t.start()


    #When foul ends
    def EndOfFoul(self):
        # Drive to home coords
        self.Driver.home_from_foul_box()
        self.StateController.set_idle_state()
        

    # Shooting
    def Shooting(self):
        if self.grabber is None:
            return

        if self.grabber.shoot_once():
            self.StateController.has_ball = False
            self.StateController.set_idle_state()
            try:
                self.ev3.speaker.beep()
            except Exception:
                pass

    # Passing
    def Passing(self):
        # get the angle to our teammate
        angleToTeamMate = self.pushingCode.get_aim_angle(self.StateController.position,
                                                        self.StateController.others_position)
        # pivot to face them, left foot planted (netball legal)
        self.Driver.pivot_angle("LEFT", angleToTeamMate)

        # TODO: CODE TO PASS BALL (claw release etc.)
    
    # retrieving
    def Retreiving(self):
        # get the data from the IR sensor
        ball_data = self.ir_sensor.read(2,2)
        # get the angle to the ball in radians from (-pi,pi)
        angle_to_ball = ((ball_data[0] * pi / 6)+pi)%pi-pi
        # turn to that angle
        self.Driver.spin_angle(angle_to_ball)
        # get the heading of the robot
        heading = self.Driver.get_heading()
        # calculate a little step forward in the x direction
        forward_x = cos(heading)
        # calculate a little step forward in the y direction
        forward_y = sin(heading)
        # distance modifier
        distanceModifier = 5
        # drive a little increment forward and wait for the next loop
        self.Driver.drive_to_point(self.Driver.x+forward_x,self.Driver.y+forward_y)

        
    # Locating
    def Locating(self):
        # turn 10 degrees
        self.Driver.spin_angle(10)
        

    # Positioning
    def Positioning(self):
        # Drive to start position
        self.Driver.drive_to_point(robot_config.START_ATTACK_X,
                                robot_config.START_ATTACK_Y)
        # get the angle to our teammate
        angleToTeamMate = self.pushingCode.get_aim_angle(self.StateController.position,
                                                        self.StateController.others_position)
        # pivot to face them, left foot planted
        self.Driver.pivot_angle("LEFT", angleToTeamMate)


    # Receiving
    def Receiving(self):
        # get the angle to our teammate
        angleToTeamMate = self.pushingCode.get_aim_angle(self.StateController.position,
                                                        self.StateController.others_position)
        # pivot to face them ready for a pass, left foot planted
        self.Driver.pivot_angle("LEFT", angleToTeamMate)


    #Waiting
    def Waiting(self):
        pass

    #Main loop
    def MainLoop(self):
        # main loop
        while True:
            # get the current state
            Current_state = self.StateController.get_state()

            # if the robot is in the foul state
            if Current_state == State.FOUL:
                if self.wasinfoul == False:
                    self.wasinfoul =  True
            # if the robot is in the Locating state
            elif Current_state == State.LOCATING:
                self.Locating()
            # if the robot is in the passing state
            elif Current_state == State.PASSING:
                self.Passing()
            # if the robot is in the positioning state
            elif Current_state == State.POSITIONING:
                self.Positioning()
            # if the robot is in the receiving state
            elif Current_state == State.RECEIVING:
                self.Receiving()
            # if the robot is in the waiting or idle state
            elif Current_state == State.WAITING or Current_state == State.IDLE:
                pass
            # if the robot is in the retreiving state
            elif Current_state == State.RETRIEVING:
                self.Retreiving() # ADD RETREIVING CODE ONCE DONE
            # if the robot is in the shooting state
            elif Current_state == State.SHOOTING:
                self.Shooting()
            

            # if the robot is not in a foul state
            if Current_state != State.FOUL:
                # if the robot previously was in a foul state 
                if self.wasinfoul == True:
                    # set the variable to false
                    self.wasinfoul = False
                    # Drive home from the foul box
                    self.Driver.home_from_foul_box()
            # Refresh and recalculate the state.
            self.StateController.determine_state() 
            time.sleep(0.1)    