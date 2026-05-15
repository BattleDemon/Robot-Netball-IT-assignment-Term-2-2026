#!/usr/bin/env pybricks-micropython

from pybricks.hubs import EV3Brick
from pybricks.ev3devices import (
    Motor, TouchSensor, ColorSensor,
    InfraredSensor, UltrasonicSensor, GyroSensor
)
from pybricks.parameters import Port, Button, Color
from pybricks.tools import wait

from pybricks.iodevices import I2CDevice

ev3 = EV3Brick()

ir_sensor = I2CDevice(Port.S4,0x08)

ball_sensor_data = ir_sensor.read(2,2)

ball_position = ball_sensor_data[0]
ball_sig_strength = ball_sensor_data[1]

print(ball_position)

print(ball_sig_strength)
