from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor, ColorSensor
from pybricks.parameters import Port
import time
arm_motor = Motor(Port.B)

while True:
    if ball_caught == True: #if the ball is caught, as seen in claw grabbing, then we can raise the arm to place in ramp for trebuchet loading
        arm_motor.run_time(-500, 5000) #raising the arm, time tbd, may need to be changed after testing
        time.sleep(1) #wait after raising to math.degrees(angle_rad)ensure the arm is in position
        arm_motor.run_time(500, 1000) #lowering the arm, time tbd, may need to be changed after testing
        time.sleep(1) #wait after lowering to ensure the arm is in position 
    while color_sensor.color() != ColorSensor.COLOR_GREEN: #if the color sensor does not detect green even after resetting then we can assume that the arm has not yet reached the ground
        arm_motor.run(100) #lowering the arm, speed needs testing