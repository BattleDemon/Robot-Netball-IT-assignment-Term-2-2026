#!/usr/bin/env pybricks-micropython

from enum import Enum

# States
class State(Enum):
    IDLE = 0
    FOUL = 1
    PASSING = 2
    RETRIEVING = 3
    LOCATING = 4
    POSITIONING = 5
    RECIEVING = 6

class Request(Enum):
    PASS = 0
    RECIEVE = 1
    RETRIEVE = 2
    NONE = 3


# State Machine
class State_Controller():
    def __init__(self, owner):
        self.owner = owner

        self.state = State.IDLE
        self.other_state: State

        self.x_pos: float
        self.y_pos: float
        self.angle: float

        self.position: tuple
        self.other_position: tuple

        self.ball_position: tuple
        self.other_ball_position: tuple

        self.has_ball: bool
        self.other_has_ball: bool

        self.request: Request
        self.incoming_request: Request

    def update_self_position(self, x, y, angle):
        pass

    def update_other_position(self, x, y, angle):
        pass

    def get_snapshot(self, ):
        # Gather all info the communication manager needs
        pass

    def alerted_of_foul(self):
        pass