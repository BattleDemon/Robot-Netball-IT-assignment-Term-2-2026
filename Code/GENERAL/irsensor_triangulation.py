import math
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor
from pybricks.parameters import Port
from pybricks.iodevices import I2CDevice
import time

ev3 = EV3Brick()
ir_sensor = I2CDevice(Port.S4,0x08)


class ir_controller:
    def __init__(self,ir_sensor,state_controller):
        self.ir_sensor = ir_sensor
        self.state_controller = state_controller
        self.getting_c = PushAndAim(claw_motor)
        self.my_distance_to_ball
        self.my_angle_to_ball
        self.others_angle_to_ball
    def  ir_sensing (self):
        while True:
            ball_sensor_data = ir_sensor.read(2,2)
            self.my_distance_to_ball = ball_sensor_data[0]
    def get_distance_to_ball(self):
        self.others_angle_to_ball = self.state_controller.get_others_ball_angle()
        my_position = self.state_controller.get_our_position()
        their_position = self.state_controller.get_their_position()

        c = getting_c.get_aim_angle(my_position, their_position)
        a = c - b
        d_angle = 180 - a - self.others_angle_to_ball

        dx = their_position[0] - my_position[0]
        dy = their_position[1] - my_position[1]
        d2 = dx ** 2 + dy ** 2
        d = math.sqrt(d2)

        k = d/math.sin(math.radians(d_angle))
        self.my_distance_to_ball = k * math.sin(math.radians(self.others_angle_to_ball))
        update_ball_angle_and_distance(self.my_angle_to_ball, self.my_distance_to_ball)
