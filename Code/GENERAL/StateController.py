#!/usr/bin/env pybricks-micropython

'''
    This file is the work of Dexter
'''

from enum import Enum

# --- Enums ---

# All possible states a robot can be in
class State(Enum):
    IDLE = 0        # No tasks
    FOUL = 1        # Robot has been fouled and is in the foul box or leaving it
    PASSING = 2     # Passing the ball to the other robot
    RETRIEVING = 3  # Moving to collect ball
    LOCATING = 4    # Searching for ball
    POSITIONING = 5 # Moving out of the way
    RECEIVING = 6   # Waiting to recieve a pass
    SHOOTING = 7    # Attempting to shoot at the hoop
    WAITING = 8     # Waiting for the other robot to respond to a request

# Requests that can be sent between the robots
class Request(Enum):
    PASS = 0        # Asking the other robot to pass the ball
    RECEIVE = 1     # Asking the other robot to recieve a pass
    RETRIEVE = 2    # Asking the other robot to collect the ball
    REPOSITION = 3  # Ask other robot to move
    DECLINE = 4     # Refusing the incoming request
    NONE = 5        # No active request


# --- State Machine ---

class State_Controller():
    def __init__(self, owner, robot_type, x_pos, y_pos, angle, ball_angle, ball_dist, hoop_x, hoop_y):
        self.owner = owner # Local stored refrence to owner
        self.owner_type: str = robot_type # Robot role: "attack" or "defence"

        self.hoop_position: tuple = (hoop_x, hoop_y) # Fixed hoop cords on the field, taken in value because it depends on how movement works

        # This robot's state and the last know state of the other
        self.state: State = State.IDLE
        self.others_state: State = State.IDLE

        # This robots and the other's positions
        self.position: tuple = (x_pos, y_pos, angle)
        self.others_position: tuple = None

        # Ball tracking for this robot and the other
        self.ball_position: int = ball_angle
        self.ball_distance: float = ball_dist
        self.others_ball_position: int = None
        self.others_ball_dist: float = None

        # Ball posession
        self.has_ball: bool = False
        self.others_has_ball: bool = False

        # Outgoing and latest incoming requests
        self.request: Request = Request.NONE
        self.incoming_request: Request = Request.NONE

        # IR Ground detected
        self.ground_colour: str  = None

    # update local robot position and heading
    def update_position(self,x,y,angle):
        self.position = (x,y,angle)

    # Update the angle and distance to ball from us
    def update_ball_angle_and_dist(self, angle, distance):
        self.ball_position = angle
        self.ball_distance = distance

    # toggle ball possession
    def update_have_ball(self):
        self.has_ball = not self.has_ball

    # Allow foul controller to set foul
    def set_foul_state(self):
        self.state = State.FOUL

    # Allow foul controller to return to idle
    def set_idle_state(self):
        self.state = State.IDLE

    def get_ground_colour(self, colour):
        self.ground_colour = colour

    # Create a snapshot dictionary to send to the communication manager, which then sends to other robot
    def get_snapshot(self):

        snapshot = {
            "state" : self.state,
            "position" : self.position,
            "ball position": self.ball_position,
            "ball distance": self.ball_distance,
            "has ball": self.has_ball,
            "request" : self.request
        }

        return snapshot

    # Unpack the received snapshot and store it
    def update_incoming(self, snapshot):

        self.others_state = snapshot["state"]
        self.others_position = snapshot["position"]
        self.others_ball_position = snapshot["ball position"]
        self.others_ball_dist = snapshot["ball distance"]
        self.others_has_ball = snapshot["has ball"]
        self.incoming_request = snapshot["request"]

    # Return's true if the robot is near us
    def _near_hoop(self, dist_threshold=20):
        dist_to_hoop_x = self.position[0] - self.hoop_position[0]
        dist_to_hoop_y = self.position[1] - self.hoop_position[1]

        dist_to_hoop = (dist_to_hoop_x**2 + dist_to_hoop_y**2) ** 0.5

        return dist_to_hoop < dist_threshold

    def determine_state(self):

        # --- Foul --- 
        # Is triggered by foul controller and turned off 
        if self.state == State.FOUL:

            return

        # --- Waiting ---
        # Stays waiting until the other robot responsd to our request

        if self.state == State.WAITING:
            # Other robot declined our request
            if self.incoming_request == Request.DECLINE:
                # Resets our request
                self.request = Request.NONE

                # Does not return so it can redetermine state

            # Confirmed request and assing state
            if self.incoming_request == self.request:
                if self.request == Request.PASS:
                    self.state = State.PASSING
                elif self.request == Request.RECEIVE:
                    self.state = State.RECEIVING

                return
            else:
                # No responce yet
                return
    
        # --- Handle Incoming requests from other robot ---
        if self.incoming_request != Request.NONE:

            if self.incoming_request == Request.PASS:
                # Other robot wants to pass, accept if don't have ball
                if not self.has_ball and self.state not in (State.FOUL, State.SHOOTING):
                    self.state = State.RECEIVING
                    self.request = Request.RECEIVE # Return confirmation

                    return
                else:
                    # Decline if don't meet requirments
                    self.request = Request.DECLINE

                    return

            if self.incoming_request == Request.RETRIEVE:
                # Other robot wants you to get ball
                # Decline if have ball or are in foul
                if self.has_ball or self.state == State.FOUL:
                    self.request = Request.DECLINE

                    return

                self.state = State.RETRIEVING
                self.request = Request.NONE

            if self.incoming_request == Request.REPOSITION:
                # other robot need you to move from its path or reposition in some way
                if self.state not in  (State.FOUL, State.PASSING, State.SHOOTING): 
                    self.state = State.POSITIONING
                    self.request = Request.NONE

                    return


        # --- Self Determined State ---
        # Ordered in priority order

        if self.has_ball and self.owner_type == "attack" and self._near_hoop():
            # Can only shoot if has ball is the attacker, and if close enough to hoop

            self.state = State.SHOOTING
            self.request = Request.NONE

            return

        # Passing
        # Have ball and wants to pass to other
        if self.has_ball:
            self.request = Request.PASS
            self.state = State.WAITING

            return

        # Neither robot has the ball
        if not self.has_ball and not self.others_has_ball:

            # The Ball has a known location
            if self.ball_distance is not None:

                # This robot is closer, or the other robot is occupied
                if self.ball_distance <= self.others_ball_dist or self.others_state in (State.FOUL, State.POSITIONING):

                    # Attacker is near the hoop, better to hold its positon and let defence retreive
                    if self.owner_type == "attack" and self._near_hoop():
                        self.state = State.POSITIONING
                        self.request = Request.RETRIEVE

                    # Go get ball
                    else:
                        self.state = State.RETRIEVING
                        self.request = Request.NONE
                
                # other robot is closer, stay still and let it retrieve
                else:
                    self.state = State.WAITING
                    self.request = Request.RETRIEVE

                return

            # neither robot knows where the ball is, lets find it
            if self.others_ball_dist is None and self.others_ball_dist is None:
                self.state = State.LOCATING
                self.request = Request.NONE
                return

        # My logic has failed and there is no state that fits
        self.state = State.IDLE
        self.request = Request.NONE
        
