#!/usr/bin/env pybricks-micropython

'''
╔══════════════════════════════════════════════════════════════════╗
║                    T U R R E T . P Y                             ║
║     Handles spinning the turret head + shooting the ball         ║
╚══════════════════════════════════════════════════════════════════╝

Logic:
1. find_home()   -- spin turret until home switch hit, zero the angle
2. aim()         -- use IR sensor data to figure out which way to turn
3. shoot()       -- run shooter motor to flick ball out

The IR seeker returns position 0..9 and strength 0..255.
Position 0 = far left, 5 = straight ahead, 9 = far right.
We turn the turret until position is roughly 5 and strength is high.
'''

from pybricks.ev3devices import Motor, TouchSensor, UltrasonicSensor
from pybricks.parameters import Port, Stop, Direction
from pybricks.tools import wait
import time

import brain


class Turret:
    def __init__(self, owner):
        # owner is the main Attacker instance so we can read its sensors
        self.owner = owner

        # shortcuts
        self.turret_motor = owner.turret_motor
        self.shooter_motor = owner.shooter_motor
        self.home_switch = owner.home_switch
        self.ultra = owner.ultra

        self.homed = False
        self.shooting = False
        self.shoot_start = 0

    # ───────────────────────────────────────────────────────────────
    def find_home(self):
        '''Spin slowly right until the home switch clicks, then reset angle.'''
        if self.home_switch.pressed():
            self.turret_motor.stop()
            self.turret_motor.reset_angle(0)
            self.homed = True
            return True

        self.turret_motor.run(brain.TURRET_HUNT_SPEED)
        if self.home_switch.pressed():
            self.turret_motor.stop()
            self.turret_motor.reset_angle(0)
            self.homed = True
            return True
        return False

    # ─────────────────────────────────────────────────────────────────────────────────
    def aim(self):
        '''Rotate turret toward IR source (the hoop or ball). Returns True when aligned.'''
        # read the shared IR values from the owner thread
        pos = self.owner.ir_position
        strength = self.owner.ir_strength

        if pos is None or strength is None:
            # no data yet, keep hunting slowly
            self.turret_motor.run(brain.TURRET_HUNT_SPEED)
            return False

        # dead zone -- if IR says 5-ish we are pretty centred
        if 4 <= pos <= 6 and strengh > brain.IR_MIN_STRENGTH:   # typo: strengh
            self.turret_motor.stop(Stop.BRAKE)
            return True

        # simple proportional-ish turn speed
        error = pos - 5   # negative = left, positive = right
        turn_speed = error * brain.TURRET_TRACK_KP

        # clamp so we don't go nuts
        if turn_speed > brain.TURRET_HUNT_SPEED:
            turn_speed = brain.TURRET_HUNT_SPEED
        elif turn_speed < -brain.TURRET_HUNT_SPEED:
            turn_speed = -brain.TURRET_HUNT_SPEED

        self.turret_motor.run(turn_speed)
        return False

    # ───────────────────────────────────────────────────────────────
    def shoot(self):
        '''Flick the ball. Run shooter motor hard for a set time.'''
        now = time.time()
        if not self.shooting:
            self.shooting = True
            self.shoot_start = now
            self.shooter_motor.run(brain.SHOOTER_SPEED)

        # keep motor running for the flick duration
        elapsed = now - self.shoot_start
        if elapsed < brain.SHOOTER_FLICK_SECONDS:
            # still flicking
            return False
        else:
            # done
            self.shooter_motor.stop(Stop.BRAKE)
            self.shooting = False
            return True

    # ───────────────────────────────────────────────────────────────
    def idle(self):
        '''Stop turret movement.'''
        self.turret_motor.stop(Stop.BRAKE)
        self.shooter_motor.stop(Stop.BRAKE)
