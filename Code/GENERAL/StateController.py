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
    WAITING = 8

class Request(Enum):
    PASS = 0
    RECIEVE = 1
    RETRIEVE = 2
    REPOSITION = 3
    DECLINE = 4 # Refuse to do the request, might need one one or two occassion s
    NONE = 5


# State Machine
class State_Controller():
    def __init__(self, owner, x_pos, y_pos, angle, ball_angle, ball_dist):
        self.owner = owner

        self.state = State.IDLE
        self.others_state: State = State.IDLE

        self.position: tuple = (x_pos, y_pos, angle)
        self.others_position: tuple

        self.ball_position: int = ball_angle
        self.ball_distance: float = ball_dist
        self.others_ball_position: int
        self.others_ball_dist: float 
        self.has_ball: bool = False
        self.others_has_ball: bool = False

        self.request: Request = Request.NONE
        self.incoming_request: Request = Request.NONE

    def update_position(self,x,y,angle):
        self.position = (x,y,angle)

    def update_ball_position(self, angle):
        self.ball_position = (angle)

    def update_have_ball(self):
        self.has_ball = not self.has_ball

    def get_snapshot(self):
        # Create a snap shot dictionary to send to the communication manager

        snapshot = {
            "state" : self.state,
            "position" : self.position,
            "ball position": self.ball_position,
            "ball distance": self.ball_distance,
            "has ball": self.has_ball,
            "request" : self.request
        }

        return snapshot

    def update_incoming(self, snapshot):

        self.others_state = snapshot["state"]
        self.others_position = snapshot["position"]
        self.others_ball_position = snapshot["ball position"]
        self.others_ball_dist = snapshot["ball distance"]
        self.others_ball_position = snapshot["has ball"]
        self.incoming_request = snapshot["request"]


    def determine_state(self):
        if self.has_ball:
            pass
        elif self.others_has_ball:
            pass
        


# State Calculations

## Foul
    # If have been placed on the foul colour 

## Retreive 
    # If you don't have ball, and other doesn't have ball, and the ball has a know location
    # If your closest

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

## Waiting 
    # if waiting for a request 
'''if self.state == State.WAITING:
            if self.incoming_request == self.request:
                match self.request:
                    case Request.
            elif self.incoming_request == Request.DECLINE:
                pass
'''