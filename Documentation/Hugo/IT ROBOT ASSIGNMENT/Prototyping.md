# Building Catcher and thrower for defence
## Issue with not enough power
When first designing the catch and throw system I used a combination of gears connected to 1 motor to power two wheels. This ended up overloading the motor and not giving enough power for the wheels to launch the ball.
![[FirstThrower.jpg|696]]
This was the first iteration and the gap was too small.
![[SecondThrower.jpg]]
This was the second iteration and the gear system was too complex and didn't fit.
![[ThridThrower.jpg]]
This was the third iteration with the same problems at the Second.

To solve the power issue I replaced the single medium motor with two large motors.


## Issue with catcher speed
The next issue was the motors not having enough speed. To solve this I added a small to large gear ratio as in this image:
![[BaseAndThrower2.jpg]]


## Issue with catcher friction
The next issue was the torque created by the large revolutions per minute. The torque created friction in the shafts holding the wheels and the pieces intended on keeping the shafts upright.
To solve this I added supports further down to decrease the overall friction. (The white connectors to the side)
![[baseAndThrower.jpg]]




## Final catcher
The final catcher had the wheels moved and the supports slightly changed to better accommodate for the ball and fit within the size constraints. The shafts holding the wheels were also shortened to keep within the height limit.
PUT IMAGE HERE

## Code for catcher
```
#!/usr/bin/env pybricks-micropython

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

IN = -2000
OUT = 2000

ev3 = EV3Brick()

def Catch_throw():
    motor = Motor(Port.B)
    motor2 = Motor(Port.C)
    cs = ColorSensor(Port.S4)
    ballwasthere = False
    while True:
        if cs.color() == Color.BLACK:
            motor.run(OUT)
            motor2.run(OUT)
            ballwasthere = True
        else:
            if ballwasthere:
                sleep(1)
                ballwasthere=False
            motor.run(IN)
            motor2.run(IN)
```
# Communication

## First (and last) Iteration
Using my knowledge obtained from my past asssignment involving network communication I was able to easily code this section on my first try and it didn't change for the rest of the project.
```
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

#the hostname / network name of the Server Ev3Brick
SERVERNAME = "ev3dev"

class Communicator():
    """
    Class for the two robots to communicate between eachother
    """

    
    def __init__(self, stateController: State_Controller, team: str, ev3: EV3Brick) -> None:
        """
        #initialise the Mailboxes of the robots
        """
        # get the state controller for later access
        self.State_Controller = stateController
        # "Defence" or "Attack" depending on if it is the defending or attacking robot
        self.team = team

        # If the robot is the defending robot.
        if self.team == "Defence":
            # Initialise the bluetooth Server
            self.server = BluetoothMailboxServer()
            # Define the Mailbox for the server "# type: ignore" is appended to the end because VS code prints an error that doesnt effect the actual robot.
            self.mailBox = TextMailbox("Hey Teammate", self.server) # type: ignore
            # Wait for the Attack robot to connect to the bluetooth
            self.server.wait_for_connection()
            # Play a cheery connection sound.
            ev3.speaker.play_notes(['C4/8','E4/8','G4/8'])

        # If the robot is the attacking robot
        if self.team == "Attack":
            # Initialise the bluetooth client
            self.client = BluetoothMailboxClient()
            # Define the Mailbox for the client "# type: ignore" is appended to the end because VS code prints an error that doesnt effect the actual robot.
            self.mailBox = TextMailbox("Hey Teammate", self.client) # type: ignore
            # Connect to the Defending robots Bluetooth server.
            self.client.connect(SERVERNAME)
            # Play a cheery connection sound.
            ev3.speaker.play_notes(['C4/8','E4/8','G4/8'])


    def sendState(self):
        """
        Send the Current state Snapshot to the other robot.
        """

        # Get a snapshot of the current state
        currentStateSnapshot = self.State_Controller.get_snapshot()
        # Get a json string version of the current snapshot.
        snapshotJsonString = json.dumps(currentStateSnapshot)
        # send the Snapshot to the other robot.
        self.mailBox.send(snapshotJsonString)
        


    def recieveState(self):
        """
        Revieve the stateSnapshot of and from the other robot.
        """

        # Wait for a snapshot string from the other robot
        self.mailBox.wait()

        # Read the snapShot string from the other robot.
        teammateSnapshotStr = self.mailBox.read()
        # Turn the snapshot string into a snapshot object
        self.teammateSnapshot = json.loads(teammateSnapshotStr)
        # Update the state_controller's other robot snapshot.
        self.State_Controller.update_incoming(self.teammateSnapshot)
        # sleep as to not fry the cpu accidentally
        sleep(0.1)
        
    
    def CommunicationLoop(self):
        """
        Main loop for the communication of the robots.
        """

        # If it is the defending robot
        if self.team == "Defence":
            # start the loop
            while True:
                # First wait for the attacking robot to send it's snapshot.
                self.recieveState()
                # Then send the current Defending state Snapshot back
                self.sendState()
        # If it is the attacking robot.
        elif self.team == "Attack":
            # Start the loop
            while True:
                # First send the current Attacking state Snapshot
                self.sendState()
                # Then wait for the attacking robot to send it's snapshot
                self.recieveState()
                
```