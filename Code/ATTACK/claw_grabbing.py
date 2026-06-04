from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor, ColorSensor
from pybricks.parameters import Port


claw_motor = Motor(Port.A)
color_sensor = ColorSensor(Port.S1)
ball_caught = False

while True:
    if color_sensor.color() == ColorSensor.COLOR_BLACK: #when switch is performed on the ball, the color sensor will detect black and trigger the claw to close
        ball_caught = True #variable to be used in shooting.py to trigger the shooting mechanism and in 
        claw_motor.run_time(500,5000) #closing the claw and keeping it closed as it is transported to the shooting mechanism, time tbd, may need to be changed after testing