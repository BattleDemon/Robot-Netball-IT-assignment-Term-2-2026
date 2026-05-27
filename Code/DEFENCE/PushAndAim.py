#!/usr/bin/env pybricks-micropython

# ++++++++++++++++++++++++++++++++
# ======== Work of Dexter ========
# ++++++++++++++++++++++++++++++++

from math import atan2, degrees, pi
from pybricks.ev3devices import Motor

class PushAndAim():
    def __init(self, push_motor: Motor):
        self.push_motor = push_motor

    def get_aim_angle(self,our_position: tuple, others_position: tuple):

        our_x, our_y, our_angle = our_position
        others_x, others_y, _ = others_position

        dx = others_x - our_x
        dy = others_y - our_y

        target_angle = math.atan2(dy, dx)

        angle_between = target_angle - our_angle
        angle_between = (angle_between + pi) % (2 * pi) - pi

        return angle_between

    def push(self):
        pass
        # Push motor 45 degrees 
        # wait a min then turn back