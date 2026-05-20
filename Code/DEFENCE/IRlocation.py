#!/usr/bin/env pybricks-micropython

''' Work of Dexter '''
# Find cordinates of highest IR then send that to machine 

from pybricks.iodevices import I2CDevice
import time

def irLocator(owner, ownerIR_sensor):
    # Set local refrence to IR_sensor
    ir_sensor = ownerIR_sensor

    # Debug Message
    print("IR thread started")

    # IR Loop
    while True:
        ball_sensor_data = ir_sensor.read(2,2)

        # Update local 
        position = ball_sensor_data[0]
        strength = ball_sensor_data[1]

        # Update parent
        owner.IR_position = position
        owner.IR_strength = strength

        # Prevent CPU from dieing 
        time.sleep(0.25)