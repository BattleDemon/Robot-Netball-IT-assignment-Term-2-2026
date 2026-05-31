from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor
from pybricks.parameters import Port
from pybricks.iodevices import I2CDevice
import time

ev3 = EV3Brick()
left_motor = Motor(Port.B)
right_motor = Motor(Port.C)
ir_sensor = I2CDevice(Port.S4,0x08)
on_left = [11, 10, 9, 8, 7]
on_right = [1, 2, 3, 4, 5]

ev3.speaker.beep()

BASE_SPEED = 300

while True:
    ball_sensor_data = ir_sensor.read(2,2)
    heading = ball_sensor_data[0]
    distance = ball_sensor_data[1]
    #if ball isnt found, spin until it is
    while heading == 0:
        left_motor.run(100)
        right_motor.run(-100)
        ball_sensor_data = ir_sensor.read(2,2)
        heading = ball_sensor_data[0]
        distance = ball_sensor_data[1]
        time.sleep(0.1)
    #if the ball is on the left, turn left until it is straight ahead
    if heading in on_left:
        left_motor.run(BASE_SPEED * -1)
        right_motor.run(BASE_SPEED)
        while heading != 12:
            ball_sensor_data = ir_sensor.read(2,2)
            heading = ball_sensor_data[0]
            distance = ball_sensor_data[1]
            time.sleep(0.1)
        left_motor.stop()
        right_motor.stop()
    #if the ball is on the right, turn right until it is straight ahead
    elif heading in on_right:
        left_motor.run(BASE_SPEED)
        right_motor.run(BASE_SPEED * -1)
        while heading != 12:
            ball_sensor_data = ir_sensor.read(2,2)
            heading = ball_sensor_data[0]
            distance = ball_sensor_data[1]
            time.sleep(0.1)
        left_motor.stop()
        right_motor.stop()
    #if the ball is straight ahead, beep
    else:
        ev3.speaker.beep()
        time.sleep(0.1)