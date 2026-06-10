#!/usr/bin/env pybricks-micropython

import time
from pybricks.ev3devices import Motor, ColorSensor
from pybricks.parameters import Color, Stop


class GrabAndShoot:
    def __init__(
        self,
        claw_motor,
        arm_motor,
        leftwheel_motor,
        rightwheel_motor,
        wind_motor,
        color_sensor,
        ir_sensor,
        com_motor,
    ):
        self.ball_caught = False
        self.ball_loaded = False
        self.claw_motor = claw_motor
        self.arm_motor = arm_motor
        self.leftwheel_motor = leftwheel_motor
        self.rightwheel_motor = rightwheel_motor
        self.wind_motor = wind_motor
        self.color_sensor = color_sensor
        self.ir_sensor = ir_sensor
        self.com_motor = com_motor
        self.com_start_angle = self.com_motor.angle() if self.com_motor is not None else None
        self.shooting = False

    def catching(self):
        pass

    def grabbing(self):
        while True:
            if self.ball_caught:
                time.sleep(0.1)
                continue

            if self.color_sensor.color() == Color.BLACK:
                self.claw_motor.run_time(500, 5000)
                self.claw_motor.hold()
                self.ball_caught = True
                self.ball_loaded = False
                time.sleep(1)

            time.sleep(0.1)

    def loading(self):
        while True:
            if self.ball_caught and not self.ball_loaded:
                self.arm_motor.run_time(-500, 5000)
                time.sleep(2)
                self.arm_motor.run_time(500, 1000)
                time.sleep(1)
                self.arm_motor.hold()
                self.ball_loaded = True
                if self.com_motor is not None:
                    self.com_start_angle = self.com_motor.angle()
            time.sleep(0.2)

    def shoot_once(self):
        if not self.ball_loaded or self.wind_motor is None or self.shooting:
            return False

        self.shooting = True
        self.wind_motor.run_time(2500, 1000)
        time.sleep(1)
        self.claw_motor.run_time(-2000, 500)
        self.claw_motor.hold()
        self.ball_caught = False
        self.ball_loaded = False
        self.wind_motor.run_time(-1000, 5000)
        self.shooting = False
        return True

    def shoot(self):
        while True:
            if self.com_motor is None:
                time.sleep(0.5)
                continue

            if self.com_motor.angle() != self.com_start_angle:
                time.sleep(2)
                if self.wind_motor is not None:
                    self.wind_motor.run_time(2500, 1000)
                    time.sleep(1)
                    self.ball_caught = False
                    self.ball_loaded = False
                    self.wind_motor.run_time(-1000, 5000)
                self.com_start_angle = self.com_motor.angle()

            time.sleep(0.2)
