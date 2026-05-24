#!/usr/bin/env pybricks-micropython

'''
╔══════════════════════════════════════════════════════════════════╗
║                       ==== MOEVEMENT ====                        ║
║   This will be movement for both Defence and Attack.             ║
║   Base code writen by Hugo, changes made and added on by Gabe    ║
╚══════════════════════════════════════════════════════════════════╝
'''

from time import sleep, time
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import (
    Motor,
    TouchSensor,
    ColorSensor,
    InfraredSensor,
    UltrasonicSensor,
    GyroSensor,
)
import random
from pybricks.parameters import Port, Stop, Direction, Button, Color
from pybricks.tools import wait, StopWatch, DataLog
from pybricks.robotics import DriveBase
from pybricks.media.ev3dev import SoundFile, ImageFile, Font
from math import pi, tan, sin, cos
import os
import threading

os.system("setfont Lat15-TerminusBold14")
# os.system('setfont Lat15-TerminusBold32x16')  # Try this larger font

WHEEL_RADIUS = 5.6 / 2
WHEEL_CIRCUMFERENCE = 2 * pi * WHEEL_RADIUS
BASE_RADIUS = 12.3 / 2
WHEEL_BASE_RATIO = WHEEL_RADIUS / BASE_RADIUS


class MyTank:
    def __init__(
        self,
        ev3: EV3Brick,
        Lmotor: Motor,
        Rmotor: Motor,
        csL: ColorSensor,
        usF: UltrasonicSensor,
        csR: ColorSensor,
        usS: UltrasonicSensor,
    ):
        self.Lmotor = Lmotor
        self.Rmotor = Rmotor
        self.csL = csL
        self.ev3 = ev3
        self.usF = usF
        self.csR = csR
        self.usS = usS
        self.x = 0
        self.y = 0
        self.angle = 0
        self.dy = sin(self.angle) * 97.73843811168245
        self.dx = cos(self.angle) * 97.73843811168245
        self.speed = 200
        self.movestart = time()
        self.fractionComplete = 0

    def Move_for_seconds(self, Sleep_time: int, speed: int = 200):
        self.Lmotor.run(speed)
        self.Rmotor.run(speed)
        curTime = time()
        dist = (Sleep_time * WHEEL_CIRCUMFERENCE * speed) / 360
        startx = self.x
        starty = self.y

        self.movestart = curTime
        endTime = curTime + Sleep_time
        while time() < endTime:
            self.fractionComplete = (time() - curTime) / Sleep_time
            self.x = startx + (self.dx * self.fractionComplete)
            self.y = starty + (self.dy * self.fractionComplete)

        self.Lmotor.stop()
        self.Rmotor.stop()
        self.Lmotor.brake()
        self.Rmotor.brake()

    def Move_dist(self, distance, speed=200):
        rotations = distance / WHEEL_CIRCUMFERENCE
        degrees_to_turn = rotations * 360
        seconds_to_turn = degrees_to_turn / speed
        self.Move_for_seconds(seconds_to_turn, speed)

    def turn(self, angle, speed=200):
        wheel_degrees = angle / WHEEL_BASE_RATIO
        self.angle += angle
        self.angle = self.angle % 360
        self.dy = sin(self.angle) * 97.73843811168245
        self.dx = cos(self.angle) * 97.73843811168245
        seconds_to_turn = abs(wheel_degrees) / speed
        self.Lmotor.run(speed * (-wheel_degrees / abs(wheel_degrees)))
        self.Rmotor.run(speed * (wheel_degrees / abs(wheel_degrees)))
        sleep(seconds_to_turn)
        self.Lmotor.stop()
        self.Rmotor.stop()
        self.Lmotor.brake()
        self.Rmotor.brake()

    def move(self, speedL=200, speedR=100):
        self.Lmotor.run(speedL)
        self.Rmotor.run(speedR)
        self.movestart = time()

    def stopAndBrake(self):
        self.Lmotor.stop()
        self.Rmotor.stop()
        self.Lmotor.brake()
        self.Rmotor.brake()

    def followBlackLine(self):
        while True:
            if self.csL.color() == Color.BLACK:
                self.move(100, 200)

            elif self.csR.color() == Color.BLACK:
                self.move(200, 100)

            else:
                self.move(200, 200)

    def randommov(self):
        Distance = 200
        speed = 1000
        self.move(speed, speed)
        while True:

            rand = random.randrange(-360, 360)
            self.stopAndBrake()

            self.Move_for_seconds(10)
            self.turn(rand)

    def follow_leftWall(self):
        while True:
            fDist = self.usF.distance()
            sDist = self.usS.distance()
            if fDist < 200:
                self.move(200, 0)
            else:
                if sDist < 20:
                    self.move(200, 0)
                elif 20 < sDist < 70:
                    self.move(200, 120)
                elif 70 < sDist < 100:  # if too close
                    self.move(200, 170)
                elif 100 < sDist < 130:  # if just right
                    self.move(200, 200)
                elif 130 < sDist < 170:  # if too far
                    self.move(170, 200)
                elif 170 < sDist < 250:
                    self.move(130, 200)
                else:  # if no wall
                    self.move(50, 200)

    def updateCoords(self):
        while True:

            self.ev3.screen.clear()
            coordstring = "%f, %f" % (self.x, self.y)

            # self.ev3.screen.set_font(Font("Lucida", 8))
            self.ev3.screen.draw_text(0, 20, coordstring)
            sleep(0.1)

    def startCoords(self):
        t1 = threading.Thread(target=self.updateCoords)
        t1.start()
        self.randommov()


ev3 = EV3Brick()
ev3.screen.clear()
motorR = Motor(Port.C)
motorL = Motor(Port.B)
csL = ColorSensor(Port.S1)
usF = UltrasonicSensor(Port.S4)
csR = ColorSensor(Port.S3)
usS = UltrasonicSensor(Port.S2)

tank = MyTank(ev3, motorL, motorR, csL, usF, csR, usS)
ev3.screen.set_font(Font("Lucida", 15))
ev3.speaker.beep()
tank.startCoords()