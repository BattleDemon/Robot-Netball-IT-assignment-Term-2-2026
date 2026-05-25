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
    SHOOTING = 7

class Request(Enum):
    PASS = 0
    RECIEVE = 1
    RETRIEVE = 2
    REPOSITION = 3
    NONE = 4


# State Machine
class State_Controller():
    def __init__(self, owner):
        self.owner = owner

        self.state = State.IDLE
        self.others_state: State

        self.x_pos: float
        self.y_pos: float
        self.angle: float

        self.position: tuple
        self.others_position: tuple

        self.ball_position: tuple
        self.others_ball_position: tuple

        self.has_ball: bool
        self.others_has_ball: bool

        self.request: Request
        self.incoming_request: Request

    def update_self_position(self, x, y, angle):
        pass

    def update_other_position(self, x, y, angle):
        pass

    def get_snapshot(self):
        # Create a snap shot dictionary to send to the communication manager

        snapshot = {
            "state" : self.state,
            "position" : self.position,
            "ball position": self.ball_position,
            "has ball": self.has_ball,
            "request" : self.request
        }

        return snapshot

    def alerted_of_foul(self):
        pass

# State Calculations

## Foul
    # If have been placed on the foul colour 

## Retreive 
    # If you don't have ball, and other doesn't have ball, and the ball has a know location

## Locating
    # if neither you nor the other robot know where the ball is 

## Passing
    # If you have the ball, have requested to pass and gotten back a revieving

## Positioning 
    # if other has ball and you need to get out of its way

## Recieving 
    # iF OTHER IS REQUESTING TO PASS 

## SHOOTING
    # IF HAVE CAPABILITIES TO SHOOT AND HAS BALL ( NOT DEFENDING RBOOT)