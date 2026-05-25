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

        if self.state == State.FOUL:
            return

        if self.state == State.WAITING:
            if self.incoming_request == Request.DECLINE:
                self.request = Request.NONE

            if self.incoming_request == self.request:
                if self.request == Request.PASS:
                    self.state = State.PASSING
                elif self.request == Request.RECIEVE:
                    self.state = State.RECIEVING

                return
            else:
                return
    
        if self.incoming_request != Request.NONE:
            if self.incoming_request == Request.PASS:
                if not self.has_ball and self.state not in (State.FOUL, State.SHOOTING):
                    self.state = State.RECIEVING
                    self.request = Request.RECIEVE  # echo confirmation back
                    return
                else:
                    self.request = Request.DECLINE
                    return

            if self.incoming_request == Request.RETRIEVE:
                if self.has_ball or self.state == State.FOUL:
                    self.request = Request.DECLINE
                    return

            if self.incoming_request == Request.REPOSITION:
                if self.state not in  (State.FOUL, State.PASSING, State.SHOOTING): 
                    self.state = State.POSITIONING
                    self.request = Request.NONE
                    return



        if self.has_ball and self.owner_type == "attack":
            # Some how determin if near hoop

            self.state = State.SHOOTING
            self.request = Request.NONE
            return

        if self.has_ball:
            self.request = Request.PASS
            self.state = State.WAITING
            return

        if not self.has_ball and not self.others_has_ball:
            if self.ball_distance is not None:
                if self.ball_distance <= self.others_ball_dist or self.others_state in (State.FOUL, State.POSITIONING):
                    self.state = State.RETRIEVING
                    self.request = Request.NONE

                # Else
                # determing if self or other is retreiving

                return

        if not self.has_ball and not self.others_has_ball:
            if self.ball_distance is None and self.others_ball_dist is None:
                self.state = State.LOCATING
                self.request = Request.NONE
                return

        self.state = State.IDLE
        self.request = Request.NONE
        

# State Calculations

# State calculated every few seconds or after a state has done its thing (You have opassed the ball, your foul has elapsed and you've returned to the location)

## Foul
    # Have recieved foul condition
    # THis is a special state since its triggered after been picked up and placed in the foul box, 
    # it also has a individual way of returning to idle since it needs to return to the field after the foul has elapsed

## Retreive 
    # If you don't have ball, and other doesn't have ball, and the ball has a know location
    # If your closest
    # Not nessisary but can be influnce by if you've been asked to recieve 

## Locating
    # if neither you nor the other robot know where the ball is 
    # neither robot has the ball
    # Neither robot's is in state passing or shooting

## Passing
    # If you have the ball, have requested to pass and gotten back a confiormation recieving
    # if other logic works but have not requested to pass, request to pass

## Positioning 
    # if other has ball and you need to get out of its way, or if your just moving around

## Recieving 
    # iF OTHER IS REQUESTING TO PASS 
    # and doesn't have the ball
    # other has the ball

## SHOOTING
    # IF HAVE CAPABILITIES TO SHOOT AND HAS BALL ( NOT DEFENDING RBOOT)
    # has ball 
    # is near hoop (we will have hoop locations i mightr need to make a local varaible )


## Waiting 
    # if waiting for a request to come back (stay in until you get a declined or the correct one back (NONE is default and not a decline))
'''if self.state == State.WAITING:
            if self.incoming_request == self.request:
                match self.request:
                    case Request.
            elif self.incoming_request == Request.DECLINE:
                pass
'''