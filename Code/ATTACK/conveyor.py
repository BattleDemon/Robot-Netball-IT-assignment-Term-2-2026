#!/usr/bin/env pybricks-micropython

'''
╔══════════════════════════════════════════════════════════════════╗
║                 C O N V E Y O R . P Y                            ║
║        Moves the ball from the front claw into the turret        ║
╚══════════════════════════════════════════════════════════════════╝

Logic:
- When ball is grabbed, run belt backwards for X seconds
- Ball should roll / get dragged into the turret chamber
- After shooting, run belt forwards again to reset and wait for if the ball is found again

We use a motor and just time it because we don't have a second sensor
on the belt itself (yet...). Adjust CONVEYOR_RUN_SECONDS in brain.py.
'''

from pybricks.ev3devices import Motor
from pybricks.parameters import Port, Stop, Direction
from pybricks.tools import wait
import time

import brain


class Conveyor:
    def __init__(self, owner):
        self.owner = owner
        self.motor = owner.conveyor_motor

    # ───────────────────────────────────────────────────────────────
    def run_back(self):
        '''Start the belt moving backward (ball toward turret). Non-blocking.'''
        self.motor.run(-brain.CONVEYOR_SPEED)

    def run_forward(self):
        '''Start the belt moving forward (ball toward claw). Non-blocking.'''
        self.motor.run(brain.CONVERYOR_SPEED)   # typo: CONVERYOR_SPEED

    def stop(self):
        '''Stop belt.'''
        self.motor.stop(Stop.BRAKE)

    # ───────────────────────────────────────────────────────────────
    def return_to_front(self):
        '''After shooting, send belt back to front so we can grab again.'''
        self.motor.run(brain.CONVEYOR_SPEED)
        time.sleep(brain.CONVEYOR_RETURN_SECONDS)
        self.motor.stop(Stop.BRAKE)
