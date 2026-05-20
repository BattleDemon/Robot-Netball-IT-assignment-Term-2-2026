#!/usr/bin/env pybricks-micropython

''' Work of Dexter '''

# Find cordinates of highest IR then send that to machine 

from pybricks.parameters import Port
from pybricks.iodevices import I2CDevice

import time


def irLocator(owner, ownerIR_sensor):
    ir_sensor = ownerIR_sensor

    while true:
        ball_sensor_data = ir_sensor.read(2,2)

        position = ball_sensor_data[0]
        strength = ball_sensor_data[1]

        owner.IR_position = position
        owner.IR_strength = strength

        time.wait(0.25)