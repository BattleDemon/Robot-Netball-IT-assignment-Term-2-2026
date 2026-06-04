import math
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor
from pybricks.parameters import Port

leftwheel_motor = Motor(Port.A)#port tbd
rightwheel_motor = Motor(Port.B)#port tbd

tolerance = 2 #tolerance for angle adjustment, may need to be changed after testing, in degrees
dx = 79 - my_x
dy = 0 - my_y

angle_rad = math.atan2(dy, dx)
angle_deg = (math.degrees(math.atan2(dy, dx)) + 360) % 360

wind_motor = Motor(Port.A)

while True:
    if ball_caught == True: #if the ball is caught, as seen in claw grabbing, then we can shoot it
        time.sleep(7) #waiting for ball to reach slot, time tbd, may need to be changed after testing
        rotation_needed = (angle_deg - my_angle + 180) % 360 - 180
        while abs(rotation_needed) > tolerance:
            if rotation_needed > 0: #is the target to the right of the robot?
                leftwheel_motor.run(100) #turning right, speed needs testing
            else: #is the target to the left of the robot?
                rightwheel_motor.run(100) #turning left, speed needs testing
            # Read current angle sensor
           # my_angle = get_current_angle() how will we know this?
            rotation_needed = (angle_deg - my_angle + 180) % 360 - 180
        leftwheel_motor.stop()
        rightwheel_motor.stop()
        wind_motor.run_time(2500, 1000) #quick release of trebuchet
        time.sleep(1) #wait after release to ensure the ball has left the trebuchet
        ball_caught = False #disarming arm and triggering return to normal position
        wind_motor.run_time(-1000, 5000) #rewinding trebuchet, time tbd, may need to be changed after testing

        