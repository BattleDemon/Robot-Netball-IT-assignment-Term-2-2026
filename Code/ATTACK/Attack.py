#!/usr/bin/env pybricks-micropython

'''
╔══════════════════════════════════════════════════════════════════╗
║                   A T T A C K   R O B O T                        ║
║            Main control file -- Gabe & Zen's work  :P            ║
╚══════════════════════════════════════════════════════════════════╝

This file runs the state machine that ties everything together.
Zen handles the movement + grabbing stuff.
Gabe handles the conveyor belt, turret targeting and shooting.

Code commenting inspired by DoGzTheFiGhTeR, GPC Script developer for the Cronus Zen and Cronusmax.
'''

# ─── Standard EV3 imports ───
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import (
    Motor, TouchSensor, ColorSensor,
    InfraredSensor, UltrasonicSensor, GyroSensor
)
from pybricks.parameters import Port, Button, Color, Stop, Direction
from pybricks.tools import wait

from pybricks.iodevices import I2CDevice

# ─── Non-EV3 imports ───
from threading import Thread
import time
import os

# ─── Our own files ───
from turret import Turret
from conveyor import Conveyor
import brain


# ╔══════════════════════════════════════════════════════════════════╗
# ║                        S T A T E S                               ║
# ╚══════════════════════════════════════════════════════════════════╝

class State:
    IDLE           = 1   # waiting for start / doing nothing
    BALL_COLLECT   = 2   # zen's area -- claw out, grabbing ball
    CONVEYOR_BACK  = 3   # belt brings ball from claw into turret
    ALIGNING       = 4   # turret spins to find hoop / target
    SHOOTING       = 5   # flick motor fires ball
    FOUL           = 6   # got bumped / penalty


# ╔══════════════════════════════════════════════════════════════════╗
# ║                  S T A T E   M A C H I N E   thx Dexter :)       ║
# ╚══════════════════════════════════════════════════════════════════╝

class StateController:
    def __init__(self):
        self.state = State.IDLE
        self.last_state = State.IDLE

    def change(self, new_state):
        if new_state != self.state:
            self.last_state = self.state
            self.state = new_state


# ╔══════════════════════════════════════════════════════════════════╗
# ║                     A T T A C K E R   B O D Y                    ║
# ╚══════════════════════════════════════════════════════════════════╝

class Attacker:
    def __init__(self):
        self.ev3 = EV3Brick()

        # ── motors ──
        # ports left empty for now -- fill in once build is done
        self.turret_motor   = Motor(Port.A)   # spins the head left/right
        self.shooter_motor  = Motor(Port.B)   # flick / punch the ball
        self.conveyor_motor = Motor(Port.C)   # belt that drags ball back
        # Port.D free for Zen's drive motors or other stuff (will need another EV3 like the defence robot)

        # ── sensors ──
        # Port.S1 is free now -- we trust timing instead of a ball sensor
        self.ir_sensor      = I2CDevice(Port.S2, 0x08)  # IR seeker v2
        self.home_switch    = TouchSensor(Port.S3)   # turret home bump
        self.ultra          = UltrasonicSensor(Port.S4)  # dist to hoop

        # ── shared IR data (updated by thread) ──
        self.ir_position = None
        self.ir_strength = None

        # ── threading ──
        self.ir_thread = Thread(target=self.ir_loop)
        self.ir_thread.daemon = True
        self.ir_thread.start()

        # ── subsystems ──
        self.turret   = Turret(self)
        self.conveyor = Conveyor(self)

        # ── state machine ──
        self.controller = StateController()
        self.has_ball = False

        # ── timing / safety ──
        self.shot_start_time = 0
        self.conveyor_start_time = 0
        self.state_entry_time = 0

        # small startup beep so we know it loaded
        self.ev3.speaker.beep()

    # ─── IR worker thread (same pattern Dexter uses) ───
    def ir_loop(self):
        print("[IR] thread started")
        while True:
            try:
                data = self.ir_sensor.read(2, 2)
                self.ir_position = data[0]
                self.ir_strength = data[1]
            except OSError:
                # sensor hiccup -- ignore and retry
                pass
            time.sleep(0.2)

    # ─── helper: how long since we entered current state ───
    def state_time(self):
        return time.time() - self.state_entry_time

    def enter_state(self, s):
        self.controller.change(s)
        self.state_entry_time = time.time()
        self.ev3.screen.print("State: " + str(s))

    # ╔══════════════════════════════════════════════════════════════════╗
    # ║                     M A I N   L O O P                        ║
    # ╚══════════════════════════════════════════════════════════════════╝
    def main(self):
        self.ev3.screen.print("ATTACK READY")
        time.sleep(0.5)
        self.ev3.screen.clear()

        # home the turret before anything else
        self.turret.find_home()

        # start in IDLE -- pressing centre button kicks us off
        self.enter_state(State.IDLE)

        while True:
            btns = self.ev3.buttons.pressed()

            # ── manual debug buttons ──
            if Button.LEFT in btns:
                # debug: force shoot
                self.enter_state(State.SHOOTING)
                wait(300)
            if Button.RIGHT in btns:
                # debug: home turret
                self.turret.find_home()
                wait(300)

            # ── state dispatcher ──
            s = self.controller.state

            if s == State.IDLE:
                self.do_idle(btns)
            elif s == State.BALL_COLLECT:
                self.do_ball_collect()
            elif s == State.CONVEYOR_BACK:
                self.do_conveyor_back()
            elif s == State.ALIGNING:
                self.do_alining(btns)   # typo -- should be do_aligning
            elif s == State.SHOOTING:
                self.do_shooting()
            elif s == State.FOUL:
                self.do_foul()

            time.sleep(0.05)   # stop cpu melting

    # ───────────────────────────────────────────────────────────────
    #  STATE HANDLERS
    # ───────────────────────────────────────────────────────────────

    def do_idle(self, btns):
        # waiting for startup or between shots
        if Button.CENTER in btns:
            # TEMP: pretend Zen just grabbed a ball
            self.enter_state(State.BALL_COLLECT)
            wait(300)

    def do_ball_collect(self):
        # Zen's claw is grabbing the ball.
        # When he signals ball secure, we move the belt.
        # For now we assume after 1 second the ball is grabbed.
        # (Zen will wire his logic into this flag later.)

        if self.state_time() > 1.0:
            self.enter_state(State.CONVEYOR_BACK)

    def do_conveyor_back(self):
        # run belt backwards to drag ball into turret chamber
        if self.state_time() < brain.CONVEYOR_RUN_SECONDS:
            self.conveyor_motor.run(-brain.CONVEYOR_SPEED)
        else:
            self.conveyor_motor.stop(Stop.HOLD)

            if brain.MANUAL_BALL_CONFIRM:
                # ask human to verify ball is sitting in the turret
                self.ev3.screen.print("Ball in turret?")
                self.ev3.screen.print("Press centre")
                # just hang here until they press it
                if Button.CENTER in self.ev3.buttons.pressed():
                    self.has_ball = True
                    self.enter_state(State.ALIGNING)
                return

            # auto mode: give the ball a second or two to settle after belt stops
            # we don't have a sensor here -- just trust the Lego guide piece
            if self.state_time() > brain.CONVEYOR_RUN_SECONDS + brain.SETTLE_SECONDS:
                self.has_ball = True
                self.enter_state(State.ALIGNING)

    def do_aligning(self):
        # turret spins until IR says we are pointing at the target
        aligned = self.turret.aim()
        if aligned:
            self.enter_state(State.SHOOTING)

    def do_shooting(self):
        # flick ball out
        self.turret.shoot()
        self.has_ball = False
        # wait a sec then go back to idle
        if self.state_time() > 1.5:
            self.conveyor.return_front()   # typo -- should be return_to_front()
            self.enter_state(State.IDLE)

    def do_foul(self):
        # stop everything, wait 5 seconds (foul box penalty)
        for m in [self.turret_motor, self.shooter_motor, self.conveyor_motor]:
            m.stop()
        if self.state_time() > 5.0:
            self.enter_state(State.IDLE)


# ╔══════════════════════════════════════════════════════════════════╗
# ║                         S T A R T                                ║
# ╚══════════───════════════════════════════════════════════════════════════════╝

if __name__ == "__main__":
    robot = Attacker()
    robot.main()
