#!/usr/bin/env pybricks-micropython

# ++++++++++++++++++++++++++++++++**********
# ==== Work of Hugo (started by dexter) ====
# ++++++++++++++++++++++++++++++++**********

from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor, ColorSensor, GyroSensor
from pybricks.parameters import Port, Color
from pybricks.iodevices import I2CDevice

from threading import Thread
import time

from GENERAL.IRlocation import irLocator
from GENERAL.StateController import State_Controller
from GENERAL.movement import Driver
from GENERAL.GroundDetectionSystem import Ground_Observer
from GENERAL.communication import Communicator
from ATTACK.ActioningStates import StateActions
from ATTACK.GrabAndShoot import GrabAndShoot


class Attacker():
    def __init__(self):
        self.ev3 = EV3Brick()
        self.team = 'attack'
        self.StateController = State_Controller(self, self.team, 0, 0, 0, 0, 0, 0, 0)
        self.has_ball = False

        # Drive motors
        self.leftMotor = Motor(Port.B)
        self.rightMotor = Motor(Port.A)

        # Manipulator motors
        self.armMotor = Motor(Port.C)
        self.clawMotor = Motor(Port.D)

        # Sensors
        self.GroundDetectionSensor = ColorSensor(Port.S4)
        self.BallSensor = ColorSensor(Port.S2)
        self.gyro = None
        self.ir_sensor = I2CDevice(Port.S3, 0x08)

        # Driver and position tracking
        driver_team = 'ATTACK' if self.team.lower() == 'attack' else 'DEFENCE'
        self.Driver = Driver(
            self.ev3,
            self.leftMotor,
            self.rightMotor,
            self.GroundDetectionSensor,
            driver_team,
            self.gyro,
            self.StateController,
        )

        # Attach grab and shoot behavior
        self.grabber = GrabAndShoot(
            claw_motor=self.clawMotor,
            arm_motor=self.armMotor,
            leftwheel_motor=self.leftMotor,
            rightwheel_motor=self.rightMotor,
            wind_motor=None,
            color_sensor=self.BallSensor,
            ir_sensor=self.ir_sensor,
            com_motor=None,
        )

        # State action thread
        self.stateActioner = StateActions(
            self.armMotor,
            self.StateController,
            self.Driver,
            self.ir_sensor,
            self.ev3,
            grabber=self.grabber,
        )

        # Communication with defender
        self.communicator = Communicator(self.StateController, self.team, self.ev3)
        self.communicationThread = Thread(target=self.communicator.CommunicationLoop)
        self.communicationThread.daemon = True
        self.communicationThread.start()

        # Ball pickup and handling threads
        self.ballSensorThread = Thread(target=self.ball_sensing)
        self.ballSensorThread.daemon = True
        self.ballSensorThread.start()

        self.irThread = Thread(target=irLocator, args=(self, self.ir_sensor))
        self.irThread.daemon = True
        self.irThread.start()

        self.grabThread = Thread(target=self.grabber.grabbing)
        self.grabThread.daemon = True
        self.grabThread.start()

        self.loadThread = Thread(target=self.grabber.loading)
        self.loadThread.daemon = True
        self.loadThread.start()

        self.shootThread = Thread(target=self.grabber.shoot)
        self.shootThread.daemon = True
        self.shootThread.start()

        self.groundObserver = Ground_Observer(self.StateController, self.GroundDetectionSensor)

        self.Start()

    def ball_sensing(self):
        while True:
            has_ball_now = self.BallSensor.color() == Color.BLACK
            if has_ball_now != self.has_ball:
                self.has_ball = has_ball_now
                self.StateController.has_ball = has_ball_now
                if has_ball_now:
                    self.ev3.speaker.beep()
            time.sleep(0.5)

    def Start(self):
        while True:
            self.ev3.screen.clear()
            self.ev3.screen.print('ATTACK', 'state:', self.StateController.get_state())
            self.ev3.screen.print('Ball:', 'YES' if self.has_ball else 'NO')
            time.sleep(0.2)


if __name__ == '__main__':
    attacker = Attacker()
