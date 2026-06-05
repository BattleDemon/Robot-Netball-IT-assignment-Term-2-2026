#importing ev3 libraries
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor
from pybricks.parameters import Port
from pybricks.iodevices import I2CDevice
#importing from our files
from DEFENCE.PushAndAim import PushAndAim
from GENERAL.StateController import State_Controller
#importing other libraries
import time
import math

#used only to ensure PushAndAim is working, will not actually be used in this code
claw_motor = Motor(Port.A) #specific port tbd

#creating class so can be called in by main
class ir_controller:
    def __init__(self,ir_sensor,state_controller):
        self.ir_sensor = ir_sensor
        self.state_controller = state_controller
        self.getting_c = PushAndAim(claw_motor)
        self.my_distance_to_ball = 0
        self.my_angle_to_ball = 0
        self.others_angle_to_ball = 0
# function will be called in constantly
    def  ir_sensing (self):

        while True:
            time.sleep(0.2)# rest to ensure we are not overloading the sensor, time tbd, may need to be changed after testing
            ball_sensor_data = self.ir_sensor.read(2,2)
            self.my_angle_to_ball = ball_sensor_data[0] * math.pi / 6 #converting clock to radians, if this is corrects stream is uncertain
            self.get_distance_to_ball() #from PushAndAim

    def get_distance_to_ball(self): #calculations to find distance from ball
        self.others_angle_to_ball = self.state_controller.get_others_ball_angle()
        my_position = self.state_controller.get_our_position()
        their_position = self.state_controller.get_their_position()

        c = self.getting_c.get_aim_angle(my_position, their_position)
        a = c - self.my_angle_to_ball
        a = a % (2 * math.pi) #ensuring a is between 0 and 2pi, as angles can be negative or greater than 360 degrees, but we want to work with radians
        d_angle = math.pi / 2 - a - self.others_angle_to_ball 

        dx = their_position[0] - my_position[0] #x2 - x1
        dy = their_position[1] - my_position[1] #y2 - y1
        d2 = dx ** 2 + dy ** 2 #pythagorean theorem
        d = math.sqrt(d2) #finalising pythagorean theorem to get distance between the two robots

        k = d/math.sin(d_angle) #law of sins, sin(a)/A = sin(b)/B = sin(c)/C, and can flip
        self.my_distance_to_ball = k * math.sin(self.others_angle_to_ball) #final distance calculation, law of sins again
        self.state_controller.update_ball_angle_and_distance(self.my_angle_to_ball, self.my_distance_to_ball) #updating the state controller with the new angle and distance to the ball, so that it can be used in other files
