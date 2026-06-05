#!/usr/bin/env pybricks-micropython

'''
╔══════════════════════════════════════════════════════════════════╗
║                M O V E M E N T   T E S T . P Y                   ║
║                                                                  ║
║  Tests movement.py and robot_config without shooting / catching. ║
║                                                                  ║
║  1. Spins until IR ball is detected.                             ║
║  2. Drives toward the ball in small steps.                       ║
║  3. When close → ball dance (wiggle + beep).                     ║
║  4. Faces the hoop → hoop dance.                                 ║
║  5. Repeats.                                                     ║
╚══════════════════════════════════════════════════════════════════╝
'''

from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor, ColorSensor, GyroSensor
from pybricks.iodevices import I2CDevice
from pybricks.parameters import Port, Stop, Button
from pybricks.tools import wait
from threading import Thread
import time
from math import pi

# Our own files
from robot_config import *
from movement import Driver
from IRlocation import irLocator


# ---------- Hardware setup ----------
# Adjust ports to match robot :)
ev3 = EV3Brick()
left_motor = Motor(Port.B)
right_motor = Motor(Port.A)
ground_sensor = ColorSensor(Port.S1)   # not used for IR tracking, but required by Driver
ir_sensor = I2CDevice(Port.S3, 0x08)    # HiTechnic IR seeker

# Optional gyro (unplug if not used)
try:
    gyro = GyroSensor(Port.S2)
except:
    gyro = None

# ---------- Create the Driver ----------
# Team can be "ATTACK" or "DEFENCE" – we use attack so it faces the correct hoop.
robot = Driver(ev3, left_motor, right_motor, ground_sensor, team="ATTACK", gyro=gyro)

# ---------- Start IR locator in background ----------
# This thread writes robot.IR_position (0‑9) and robot.IR_strength (0‑255) continuously.
ir_thread = Thread(target=irLocator, args=(robot, ir_sensor))
ir_thread.daemon = True
ir_thread.start()

# Give sensors a moment to initialise
wait(500)


# ---------- Little dance functions ----------
def ball_dance():
    """Celebrate finding the ball – wiggle and beep."""
    ev3.speaker.beep(880, 200)  # high beep
    for _ in range(3):
        robot.spin_angle(0.3)   # turn ~17° clockwise
        wait(200)
        robot.spin_angle(-0.3)  # turn back
        wait(200)
    ev3.speaker.beep(440, 400)  # lower beep

def hoop_dance():
    """Celebrate facing the hoop – spin 360° and beep twice."""
    ev3.speaker.beep(1000, 100)
    robot.spin_angle(2 * pi)    # full turn
    ev3.speaker.beep(1200, 100)
    wait(300)
    ev3.speaker.beep(1000, 100)


# ---------- Main test loop ----------
ev3.screen.print("Movement Test")
ev3.screen.print("Press centre to start")
while Button.CENTER not in ev3.buttons.pressed():
    wait(50)
ev3.screen.clear()

# State machine for the test
# 0 = searching, 1 = approaching ball, 2 = ball reached, 3 = facing hoop, 4 = done
state = 0
ball_dance_done = False

while True:
    # Allow emergency stop with back button
    if Button.UP in ev3.buttons.pressed():
        robot.stop()
        ev3.screen.print("Stopped")
        break

    # Get latest IR data
    pos = robot.IR_position
    strength = robot.IR_strength

    # ---- State 0: Searching for the ball ----
    if state == 0:
        ev3.screen.print("Searching...")
        # If we see a strong enough signal, switch to approach
        if strength is not None and strength > IR_BALL_CLOSE_THRESHOLD:
            state = 1
        else:
            # Slowly spin in place to scan
            robot.spin_angle(0.2)  # ~11° per step
            wait(100)

    # ---- State 1: Approaching the ball ----
    elif state == 1:
        ev3.screen.print("Approaching...")
        if strength is None or strength < 10:
            # Lost the signal, go back to searching
            state = 0
            continue

        # Convert IR direction (0‑9) to angle from robot's nose
        # 5 = straight ahead, 0 = far left, 9 = far right
        # Each step is about 10° – we convert to radians
        angle_to_ball = (pos - 5) * (pi / 18)   # positive = right

        # Turn toward the ball (spin, not pivot – we don't have it yet)
        robot.spin_angle(angle_to_ball / 2.0)   # turn half the error to avoid overshoot

        # Drive a small step forward (5 cm)
        robot.move_distance(5.0, SLOW_SPEED)

        # If the ball is very close (strong signal and centered), we've reached it
        if strength > 60 and 4 <= pos <= 6:
            state = 2

    # ---- State 2: Ball reached – dance! ----
    elif state == 2:
        robot.stop()
        ev3.screen.print("Ball found!")
        ball_dance()
        state = 3
        ball_dance_done = True

    # ---- State 3: Face the hoop – then dance again ----
    elif state == 3:
        ev3.screen.print("Facing hoop...")
        robot.face_hoop()
        hoop_dance()
        state = 4
        ev3.screen.print("Test complete!")
        ev3.speaker.beep(200, 500)
        break

    wait(50)

# Clean up
robot.stop()
robot.shutdown()