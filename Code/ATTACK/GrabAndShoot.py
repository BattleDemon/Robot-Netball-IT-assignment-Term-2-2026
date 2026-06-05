#!/usr/bin/env pybricks-micropython

import time
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import (
    Motor,
    ColorSensor,
    InfraredSensor,
)
from pybricks.parameters import Stop
from 

ev3 = EV3Brick()

class GrabAndShoot:
    def __init__(self, claw_motor, arm_motor, leftwheel_motor, rightwheel_motor, wind_motor, color_sensor, ir_sensor, com_motor):
        self.ball_caught = False
        self.claw_motor = claw_motor
        self.arm_motor = arm_motor
        self.leftwheel_motor = leftwheel_motor
        self.rightwheel_motor = rightwheel_motor
        self.wind_motor = wind_motor
        self.color_sensor = color_sensor
        self.ir_sensor = ir_sensor
        self.com_motor = com_motor
        self.com_start_angle = self.com_motor.angle()

    def catching(self):
        pass

    def grabbing(self):

        while True:
            if self.color_sensor.color() == ColorSensor.COLOR_BLACK: #when switch is performed on the ball, the color sensor will detect black and trigger the claw to close
                self.ball_caught = True #variable to be used in shooting.py to trigger the shooting mechanism and in 
                self.claw_motor.run_time(500,5000) #closing the claw and keeping it closed as it is transported to the shooting mechanism, time tbd, may need to be changed after testing
                time.sleep(6) #wait after closing to ensure the ball is securely caught
                self.claw_motor.run_time(-2000,500) #opening the claw to release ball
                self.claw_motor.hold() #holding the claw open after releasing the ball, to make it re enter the neutral position

    def loading(self):

        while True:
            if self.ball_caught == True: #if the ball is caught, as seen in claw grabbing, then we can raise the arm to place in ramp for trebuchet loading
                self.arm_motor.run_time(-500, 5000) #raising the arm, time tbd, may need to be changed after testing
                time.sleep(2) #wait after raising to ensure the arm is in position
                self.arm_motor.run_time(500, 1000) #lowering the arm, time tbd, may need to be changed after testing
                time.sleep(1) #wait after lowering to ensure the arm is in position 
            while self.color_sensor.color() != ColorSensor.COLOR_GREEN: #if the color sensor does not detect green even after resetting then we can assume that the arm has not yet reached the ground
                self.arm_motor.run(100) #lowering the arm, speed needs testing
            self.arm_motor.hold() #holding the arm in place after it has reached the ground, to make it re enter the neutral position
            self.com_start_angle = self.com_motor.angle() #resetting the start angle of the com motor to the new angle, so that we can detect the next signal to shoot

        
    def shoot(self):
        while True:
            if self.com_motor.angle() != self.com_start_angle: #if the communication motor has turned, then we can assume that we have received a signal to shoot
                time.sleep(2) #waiting for ball to reach slot, time tbd, may need to be changed after testing
                self.wind_motor.run_time(2500, 1000) #quick release of trebuchet
                time.sleep(1) #wait after release to ensure the ball has left the trebuchet
                self.ball_caught = False #disarming arm and triggering return to normal position
                self.wind_motor.run_time(-1000, 5000) #rewinding trebuchet, time tbd, may need to be changed after testing
