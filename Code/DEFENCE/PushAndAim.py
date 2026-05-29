#!/usr/bin/env pybricks-micropython

# ++++++++++++++++++++++++++++++++
# ======== Work of Dexter ========
# ++++++++++++++++++++++++++++++++

# Import the needed math functions and the motor
from math import atan2, degrees, pi
from pybricks.ev3devices import Motor

# Push and Aim Class
class PushAndAim():
    def __init(self, push_motor: Motor):
        # Locally store the inputed motor
        self.push_motor = push_motor

    # Calculate the angle between us and the other robot
    def get_aim_angle(self,our_position: tuple, others_position: tuple):

        # Locally assign x, y, and angle
        our_x, our_y, our_angle = our_position
        others_x, others_y, _ = others_position

        # Difference between theirs and ours
        dx = others_x - our_x
        dy = others_y - our_y

        # The tangen (with both y and x to find its quadrant)
        target_angle = math.atan2(dy, dx)

        # Angle between
        angle_between = target_angle - our_angle
        # Normilise the angle 
        angle_between = (angle_between ) % (2 * pi)

        return angle_between

    # Push the ball
    def push(self):
        # Push the ball with the motor 
        self.push_motor.run_angle(120,45)

        # wait a short time
        time.sleep(0.5)

        # Return motor to initial place
        self.push_motor.run_angle(-120,45)