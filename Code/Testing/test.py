#!/usr/bin/env pybricks-micropython

from pybricks.hubs import EV3Brick
from pybricks.ev3devices import (
    Motor, TouchSensor, ColorSensor,
    InfraredSensor, UltrasonicSensor, GyroSensor
)
from pybricks.parameters import Port, Button, Color
from pybricks.tools import wait


ev3 = EV3Brick() # Simplified for ease of use lol

''' ====== MOTORS ====== '''
motorA = Motor(Port.A)
motorB = Motor(Port.B)
motorC = Motor(Port.C)
motorD = Motor(Port.D)

''' ====== SENSORS ====== '''
touch = TouchSensor(Port.S1)
color = ColorSensor(Port.S2)
ultra = UltrasonicSensor(Port.S3)
gyro = GyroSensor(Port.S4)

''' ====== START ====== '''
ev3.speaker.beep()
ev3.screen.print("EV3 TEST READY")

# Reset gyro
gyro.reset_angle(0)

while True:
    buttons = ev3.buttons.pressed()

    ''' ===== MOTOR TEST ===== '''
    if Button.UP in buttons:
        ev3.screen.clear()
        ev3.screen.print("Motors forward")

        motorA.run(500)
        # motorB.run(500)
        # motorC.run(500)
        # motorD.run(500)

    elif Button.DOWN in buttons:
        ev3.screen.clear()
        ev3.screen.print("Motors backward")

        motorA.run(-500)
        # motorB.run(-500)
        # motorC.run(-500)
        # motorD.run(-500)

    elif Button.CENTER in buttons:
        ev3.screen.clear()
        ev3.screen.print("Motors STOP")

        motorA.stop()
        # motorB.stop()
        # motorC.stop()
        # motorD.stop()

        ''' ===== SENSOR TEST ===== '''
    elif Button.LEFT in buttons:
        ev3.screen.clear()
        ev3.screen.print("SENSORS:")

        # Touch
        ev3.screen.print("Touch:", touch.pressed())

        # Color
        ev3.screen.print("Color:", color.color())

        # Distance
        ev3.screen.print("Dist:", ultra.distance())

        # Gyro
        ev3.screen.print("Gyro:", gyro.angle())

        wait(500)

        ''' ===== INDIVIDUAL MOTOR TEST ===== '''
    elif Button.RIGHT in buttons:
        ev3.screen.clear()
        ev3.screen.print("Motor A test")

        motorA.run_angle(500, 180)
        wait(500)

        ev3.screen.print("Motor B test")
        motorB.run_angle(500, 180)
        wait(500)

        ev3.screen.print("Motor C test")
        motorC.run_angle(500, 180)
        wait(500)

        ev3.screen.print("Motor D test")
        motorD.run_angle(500, 180)

    wait(100)
