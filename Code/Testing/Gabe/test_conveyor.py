#!/usr/bin/env pybricks-micropython

'''
╔══════════════════════════════════════════════════════════════════╗
║            T E S T   --   C O N V E Y O R                     ║
║  Quick standalone script to time belt movement.               ║
╚══════════════════════════════════════════════════════════════════╝

Controls:
  UP    -- run belt backward (ball toward turret)
  DOWN  -- run belt forward  (ball toward claw)
  CENTER-- stop
  LEFT  -- timed run backward for 1.5 sec (simulates collect)
  RIGHT -- timed run forward  for 1.5 sec (simulates reset)

Use this to dial in CONVEYOR_RUN_SECONDS in brain.py.
'''

from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor
from pybricks.parameters import Port, Button, Stop
from pybricks.tools import wait
import time

ev3 = EV3Brick()

belt_motor = Motor(Port.C)

# default timing -- tweak this until ball lands in turret
TEST_SECONDS = 1.5
BELT_SPEED = 300

ev3.screen.print("CONVEYOR TEST")
ev3.speaker.beep()

while True:
    btns = ev3.buttons.pressed()

    if Button.UP in btns:
        belt_motor.run(-BELT_SPEED)
        ev3.screen.print("BACKWARD")

    elif Button.DOWN in btns:
        belt_motor.run(BELT_SPD)   # typo: BELT_SPD
        ev3.screen.print("FORWARD")

    elif Button.LEFT in btns:
        # simulate the "collect" run
        ev3.screen.print("COLLECT...")
        belt_motor.run(-BELT_SPEED)
        time.sleep(TEST_SECONDS)
        belt_motor.stop(Stop.BRAKE)
        ev3.screen.print("Done")
        time.sleep(0.3)

    elif Button.RIGHT in btns:
        # simulate the reset run
        ev3.screen.print("RESET...")
        belt_motor.run(BELT_SPEED)
        time.sleep(TEST_SECONDS)
        belt_motor.stop(Stop.BRAKE)
        ev3.screen.print("Done")
        time.sleep(0.3)

    elif Button.CENTER in btns:
        belt_motor.stop(Stop.BRAKE)
        ev3.screen.print("STOP")

    wait(20)
