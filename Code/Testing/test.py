#!/usr/bin/env pybricks-micropython
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import (Motor, TouchSensor, ColorSensor, 
                                 InfraredSensor, UltrasonicSensor, GyroSensor)
from pybricks.parameters import Port, Button, Color
from pybricks.tools import wait

ev3 = EV3Brick()

# Helper function to safely connect devices
def try_connect(device_type, port):
    try:
        return device_type(port)
    except OSError:
        print("Port", port, "empty. Skipping...")
        return None

''' ====== DEVICE INITIALISATION ====== '''
motorA = try_connect(Motor, Port.A)
motorB = try_connect(Motor, Port.B)
motorC = try_connect(Motor, Port.C)
motorD = try_connect(Motor, Port.D)

touch = try_connect(TouchSensor, Port.S1)
color = try_connect(ColorSensor, Port.S2)
ultra = try_connect(UltrasonicSensor, Port.S3)
gyro  = try_connect(GyroSensor, Port.S4)

''' ====== START ====== '''
ev3.speaker.beep()
ev3.screen.print("EV3 TEST READY")

if gyro: gyro.reset_angle(0)

while True:
    buttons = ev3.buttons.pressed()

    # ===== MOTOR TEST =====
    if Button.UP in buttons:
        ev3.screen.clear()
        ev3.screen.print("Motors forward")
        for m in [motorA, motorB, motorC, motorD]:
            if m: m.run(500)

    elif Button.DOWN in buttons:
        ev3.screen.clear()
        ev3.screen.print("Motors backward")
        for m in [motorA, motorB, motorC, motorD]:
            if m: m.run(-500)

    elif Button.CENTER in buttons:
        ev3.screen.clear()
        ev3.screen.print("Motors STOP")
        for m in [motorA, motorB, motorC, motorD]:
            if m: m.stop()

    # ===== SENSOR TEST =====
    elif Button.LEFT in buttons:
        ev3.screen.clear()
        ev3.screen.print("SENSORS:")
        if touch: ev3.screen.print("Touch:", touch.pressed())
        if color: ev3.screen.print("Color:", color.color())
        if ultra: ev3.screen.print("Dist:", ultra.distance())
        if gyro:  ev3.screen.print("Gyro:", gyro.angle())
        wait(500)

    # ===== INDIVIDUAL MOTOR TEST =====
    elif Button.RIGHT in buttons:
        ev3.screen.clear()
        motors = [(motorA, "A"), (motorB, "B"), (motorC, "C"), (motorD, "D")]
        for m, name in motors:
            if m:
                ev3.screen.print("Motor " + name + " test")
                m.run_angle(500, 180)
                wait(500)
    
    wait(10)
