#!/usr/bin/env pybricks-micropython

# ++++++++++++++++++++++++++++++++*********
# ========      Work of Hugo       ========
# ++++++++++++++++++++++++++++++++*********

from pybricks.hubs import EV3Brick
from pybricks.ev3devices import (
    Motor, TouchSensor, ColorSensor,
    InfraredSensor, UltrasonicSensor, GyroSensor
)
from pybricks.parameters import Port, Button, Color
from pybricks.tools import wait
from pybricks.messaging import BluetoothMailboxClient, BluetoothMailboxServer, TextMailbox
from pybricks.iodevices import I2CDevice

# Non Ev3 Imports
from threading import *
import os
from time import sleep
import random
import json

from GENERAL.StateController import State, State_Controller


SERVERNAME = "ev3dev"

class Communicator():
    def __init__(self, stateController: State_Controller, team: str, ev3 = EV3Brick) -> None:
        self.State_Controller = stateController
        self.team = team
        if self.team == "Defence":
            self.server = BluetoothMailboxServer()
            self.mailBox = TextMailbox("Hey Teammate", self.server) # type: ignore
            self.server.wait_for_connection()
            ev3.speaker.play_notes(['C4/8','E4/8','G4/8'])
        if self.team == "Attack":
            self.client = BluetoothMailboxClient()
            self.mailBox = TextMailbox("Hey Teammate", self.client) # type: ignore
            self.client.connect(SERVERNAME)
            ev3.speaker.play_notes(['C4/8','E4/8','G4/8'])


    def sendState(self):
        currentStateSnapshot = self.State_Controller.get_snapshot()
        snapshotJsonString = json.dumps(currentStateSnapshot)
        self.mailBox.send(snapshotJsonString)
        


    def recieveState(self):
        self.mailBox.wait()
        teammateSnapshotStr = self.mailBox.read()
        self.teammateSnapshot = json.loads(teammateSnapshotStr)
        self.State_Controller.update_incoming(self.teammateSnapshot)
        sleep(0.1)
        
    
    def CommunicationLoop(self):
        if self.team == "Defence":
            while True:
                self.recieveState()
                self.sendState()
        elif self.team == "Attack":
            while True:
                self.sendState()
                self.recieveState()
                