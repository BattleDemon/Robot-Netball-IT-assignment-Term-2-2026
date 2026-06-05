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

    def __init__(self, PushMotor: Motor, StateController: State_Controller, driver: movement.Driver, ir_sensor:I2CDevice, ev3) -> None:
        # get a reference to the motor used to push the ball
        self.PushMotor = PushMotor
        # get a refeerence to the current state controller
        self.StateController = StateController
        # get a reference to the current driver functions
        self.Driver = driver
        # get a reference to the Pushing code for pushing the ball
        self.pushingCode = PushAndAim(self.PushMotor)
        # Variable to know if the robot was previously in the foul box so we know when to go home.
        self.wasinfoul = False

        self.ir_sensor = ir_sensor

        self.ev3 = ev3


        # create the thread for the main loop
        ActioningStates_t = threading.Thread(target=self.MainLoop)
        # start the thread
        ActioningStates_t.start()
        
        ball_sensor_data = ir_sensor.read(2,2)


    #When foul ends
    def EndOfFoul(self):
        # Drive to home coords
        self.Driver.home_from_foul_box()
        self.StateController.set_idle_state()
        
    # Passing
    def Passing(self):
        # get the angle to our teammate
        #angleToTeamMate = self.pushingCode.get_aim_angle(self.StateController.position, self.StateController.others_position)
        angleToTeamMate = pi/4
        # pivot to face them
        self.Driver.pivot_angle("LEFT", angleToTeamMate) # NEED GABE TO CODE A PIVOT BY ANGLE
        # Push the ball into the spinning wheels
        self.pushingCode.push()
    
    # retrieving
    def Retreiving(self):
        # get the data from the IR sensor
        ball_data = self.ir_sensor.read(2,2)
        # get the angle to the ball in radians from (-pi,pi)
        angle_to_ball = ((ball_data[0] * -1* pi / 6)+pi)%pi-pi
        if 11>= ball_data[0]>=7:
            angle_to_ball = angle_to_ball*-1 
        self.ev3.screen.print(ball_data[0])
        # turn to that angle
        #self.Driver.spin_angle(angle_to_ball)
        # get the heading of the robot
        heading = self.Driver.get_heading() + angle_to_ball
        # calculate a little step forward in the x direction
        forward_x = sin(heading)
        # calculate a little step forward in the y direction
        forward_y = cos(heading)
        # distance modifier
        distanceModifier = 30
        # drive a little increment forward and wait for the next loop
        self.Driver.Drive_angle(angle_to_ball, distanceModifier)
        sleep(1)
    # Locating
    def Locating(self):
        # turn 10 degrees
        self.Driver.spin_angle("LEFT", 10)
        

    # Positioning, needs more complex code. 
    # move to home spot and turn to face partner.
    def Positioning(self):
        # Drive to start position
        self.Driver.reverse_drive_to_point(robot_config.START_DEFENCE_X,robot_config.START_DEFENCE_Y)
        # get the angle to our teammate
        angleToTeamMate = self.pushingCode.get_aim_angle(self.StateController.position, self.StateController.others_position)
        # pivot to face them
        self.Driver.pivot_angle("LEFT",angleToTeamMate) # NEED GABE TO CODE A PIVOT BY ANGLE



    # Receiving
        # Get ready to receive the ball from your teammate
    def Receiving(self):
        # get the angle to our teammate
        angleToTeamMate = self.pushingCode.get_aim_angle(self.StateController.position, self.StateController.others_position)
        # pivot to face them ready for a pass.
        self.Driver.pivot_angle("LEFT", angleToTeamMate) # NEED GABE TO CODE A PIVOT BY ANGLE


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
                self.Receiving
            # if the robot is in the waiting or idle state
            elif Current_state == State.WAITING or Current_state == State.IDLE:
                pass
            # if the robot is in the retreiving state
            elif Current_state == State.RETRIEVING:
                self.Retreiving() # ADD RETREIVING CODE ONCE DONE
            

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