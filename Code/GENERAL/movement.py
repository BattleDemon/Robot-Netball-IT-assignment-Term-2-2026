#!/usr/bin/env pybricks-micropython

'''
╔══════════════════════════════════════════════════════════════════╗
║                     M O V E M E N T . P Y                        ║
║   Shared navigation module for Attack & Defence robots.          ║
║   Handles wheel odometry, field mapping, boundary checks,        ║
║   foul box homing, and pivot movement.                           ║
║                                                                  ║
║   Written by Gabe                                                ║
║                                                                  ║
║   Code ASCII art inspired by DoGzTheFiGhTeR,                     ║
║   GPC Script developer for the Cronus Zen and Cronusmax.         ║
╚══════════════════════════════════════════════════════════════════╝
'''

from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor, ColorSensor, GyroSensor
from pybricks.parameters import Port, Stop, Direction
from pybricks.tools import wait

from math import pi, sin, cos, radians, degrees, atan2, sqrt
from threading import Thread, Lock
import time

from robot_config import (
    TEAM, WHEEL_DIAMETER, WHEEL_RADIUS, WHEEL_CIRCUM, TRACK_WIDTH,
    FIELD_WIDTH, FIELD_LENGTH, HOOP_X, HOOP_Y_ATTACK, HOOP_Y_DEFENCE,
    FOUL_BOX_WIDTH, FOUL_BOX_HEIGHT,
    FOUL_BOX_TOP_LEFT_X, FOUL_BOX_TOP_LEFT_Y,
    FOUL_BOX_BOTTOM_RIGHT_X, FOUL_BOX_BOTTOM_RIGHT_Y,
    START_ATTACK_X, START_ATTACK_Y, START_DEFENCE_X, START_DEFENCE_Y,
    START_ATTACK_HEADING, START_DEFENCE_HEADING,   # must be in radians!
    DEFAULT_SPEED, SLOW_SPEED, TURN_SPEED, ODO_SLEEP,
    FOUL_PROBE_STEP_CM, FOUL_PROBE_SPEED, FOUL_PROBE_ANGLE,
    FOUL_PROBE_MAX_CM, FOUL_BACKUP_CM, BOUNDARY_MARGIN,
    IR_BALL_CLOSE_THRESHOLD,
)

from StateController import State, State_Controller


class Driver:
    '''
    Differential-drive controller with wheel odometry.
    Tracks theoretical (x, y, heading) in radians.
    Heading 0 = +y, pi/2 = +x, pi = -y, 3pi/2 = -x.

    Integrates with Dexter's State_Controller:
      - Odometry position is pushed to the SC automatically (in radians).
      - Foul and ground colour are ONLY read from the SC.
      - Foul homing is triggered when the SC reports foul elapsed.
    '''

    def __init__(self, ev3, left_motor, right_motor, colour_sensor,
                 team=TEAM, gyro=None, state_controller=None):
        self.ev3 = ev3
        self.lm = left_motor
        self.rm = right_motor
        self.cs = colour_sensor
        self.team = team
        self.gyro = gyro
        self.state_controller = state_controller

        # //////// Pose (all in radians) ////////
        if self.team == "ATTACK":
            self.x = START_ATTACK_X
            self.y = START_ATTACK_Y
            self.heading = START_ATTACK_HEADING   # radians
            self.hoop_x = HOOP_X
            self.hoop_y = HOOP_Y_ATTACK
        else:
            self.x = START_DEFENCE_X
            self.y = START_DEFENCE_Y
            self.heading = START_DEFENCE_HEADING   # radians
            self.hoop_x = HOOP_X
            self.hoop_y = HOOP_Y_DEFENCE

        # //////// Encoder bookkeeping ////////
        self._last_l = self.lm.angle()
        self._last_r = self.rm.angle()

        # //////// Gyro offset ////////
        if self.gyro is not None:
            # Store gyro's current value (degrees) as offset to match initial heading
            self._gyro_offset = self.gyro.angle()  # degrees
        else:
            self._gyro_offset = 0

        # //////// External data placeholders ////////
        self._other_robot_pos = None
        self.IR_strength = 0
        self.IR_position = 0

        # //////// Threads ////////
        self._running = True
        self._odo_thread = Thread(target=self._odometry_loop)
        self._odo_thread.daemon = True
        self._odo_thread.start()

    # ─── State listener helpers ───
    def is_foul_active(self):
        if self.state_controller:
            return self.state_controller.get_state() == State.FOUL
        return False

    # ─── External data setters ───
    def set_other_robot_position(self, x, y, heading):
        self._other_robot_pos = (x, y, heading)

    def get_ball_data(self):
        return (self.IR_strength, self.IR_position)

    # ─── Internal odometry thread (radians) ───
    def _odometry_loop(self):
        while self._running:
            l_now = self.lm.angle()
            r_now = self.rm.angle()

            dl = l_now - self._last_l
            dr = r_now - self._last_r

            if dl != 0 or dr != 0:
                d_left  = (dl / 360.0) * WHEEL_CIRCUM
                d_right = (dr / 360.0) * WHEEL_CIRCUM

                d_centre = (d_left + d_right) / 2.0
                # Change in heading in radians
                d_theta = (d_right - d_left) / TRACK_WIDTH  # radians

                self.heading += d_theta
                self.heading %= 2 * pi   # keep in [0, 2π)

            

                # Update position using current heading in radians
                self.x += d_centre * sin(self.heading)
                self.y += d_centre * cos(self.heading)

                self._last_l = l_now
                self._last_r = r_now

                # Push to state controller (radians)
                if self.state_controller:
                    self.state_controller.update_position(
                        self.x, self.y, self.heading
                    )

            time.sleep(ODO_SLEEP)

    # ─── Basic movement commands ───
    def move(self, left_speed=DEFAULT_SPEED, right_speed=DEFAULT_SPEED):
        self.lm.run(left_speed)
        self.rm.run(right_speed)

    def stop(self, brake=True):
        self.lm.stop()
        self.rm.stop()
        if brake:
            self.lm.brake()
            self.rm.brake()

    def move_distance(self, distance_cm, speed=DEFAULT_SPEED):
        rotations = distance_cm / WHEEL_CIRCUM
        target_deg = rotations * 360.0

        start_l = self.lm.angle()
        start_r = self.rm.angle()

        direction = 1 if distance_cm >= 0 else -1
        self.lm.run(speed * direction)
        self.rm.run(speed * direction)

        while True:
            travelled_l = abs(self.lm.angle() - start_l)
            travelled_r = abs(self.rm.angle() - start_r)
            if travelled_l >= abs(target_deg) and travelled_r >= abs(target_deg):
                break
            time.sleep(0.01)

        self.stop()

    # ╔══════════════════════════════════════════════════════════════════╗
    # ║                    T U R N I N G   (radians)                     ║
    # ╚══════════════════════════════════════════════════════════════════╝

    def spin_angle(self, angle_rad, speed=TURN_SPEED):
        '''
        Rotate in place (both wheels opposite).
        Positive angle_rad = clockwise.
        '''
        # Distance each wheel travels = angle_rad * (TRACK_WIDTH / 2)
        wheel_dist = abs(angle_rad) * TRACK_WIDTH / 2.0
        target_deg = (wheel_dist / WHEEL_CIRCUM) * 360.0

        direction = 1 if angle_rad >= 0 else -1
        self.lm.run(speed * direction)
        self.rm.run(-speed * direction)

        start_l = self.lm.angle()
        start_r = self.rm.angle()

        while True:
            done_l = abs(self.lm.angle() - start_l) >= target_deg
            done_r = abs(self.rm.angle() - start_r) >= target_deg
            if done_l and done_r:
                break
            time.sleep(0.01)

        self.stop()
        # Update heading (radians)
        self.heading = (self.heading + angle_rad) % (2*pi)
        self._last_l = self.lm.angle()
        self._last_r = self.rm.angle()

    def pivot_angle(self, pivot_side, angle_rad, speed=TURN_SPEED):
        '''
        Pivot around one braked wheel (netball legal).
        Position and heading tracked by odometry thread.
        Positive angle_rad = clockwise.
        '''
        # Moving wheel travels arc length = angle_rad * TRACK_WIDTH
        wheel_dist = abs(angle_rad) * TRACK_WIDTH
        target_deg = (wheel_dist / WHEEL_CIRCUM) * 360.0

        if pivot_side == "LEFT":
            self.lm.brake()
            direction = -1 if angle_rad >= 0 else 1   # clockwise = right motor backward
            self.rm.run(speed * direction)
            motor = self.rm
        elif pivot_side == "RIGHT":
            self.rm.brake()
            direction = 1 if angle_rad >= 0 else -1    # clockwise = left motor forward
            self.lm.run(speed * direction)
            motor = self.lm
        else:
            return

        start = motor.angle()
        while abs(motor.angle() - start) < target_deg:
            time.sleep(0.01)

        self.stop()
        self._last_l = self.lm.angle()
        self._last_r = self.rm.angle()

    # ─── Position / pose getters ───
    def get_position(self):
        return (self.x, self.y)

    def get_heading(self):
        return self.heading   # radians

    def reset_position(self, x=0.0, y=0.0, heading=0.0):
        '''heading in radians'''
        self.x = x
        self.y = y
        self.heading = heading % (2*pi)
        if self.gyro is not None:
            # Store new gyro offset so blended heading matches
            self._gyro_offset = self.gyro.angle() - degrees(self.heading)
        self._last_l = self.lm.angle()
        self._last_r = self.rm.angle()

    # ─── Field awareness ───
    def distance_to_hoop(self):
        hoop_dx = self.hoop_x - self.x
        hoop_dy = self.hoop_y - self.y
        return sqrt(hoop_dx * hoop_dx + hoop_dy * hoop_dy)

    def angle_to_hoop(self):
        '''Returns heading (radians) to hoop. 0 = +y, pi/2 = +x, etc.'''
        hoop_dx = self.hoop_x - self.x
        hoop_dy = self.hoop_y - self.y
        angle_from_x = atan2(hoop_dy, hoop_dx)   # radians from +x axis
        target_heading = (pi/2 - angle_from_x) % (2*pi)
        return target_heading

    def is_in_bounds(self):
        return (BOUNDARY_MARGIN <= self.x <= FIELD_WIDTH - BOUNDARY_MARGIN and
                BOUNDARY_MARGIN <= self.y <= FIELD_LENGTH - BOUNDARY_MARGIN)

    def is_in_foul_area(self):
        if self.state_controller:
            if self.state_controller.get_ground_colour() == "White":
                return True
        if (FOUL_BOX_TOP_LEFT_X <= self.x <= FOUL_BOX_TOP_LEFT_X + FOUL_BOX_WIDTH and
            FOUL_BOX_TOP_LEFT_Y <= self.y <= FOUL_BOX_TOP_LEFT_Y + FOUL_BOX_HEIGHT):
            return True
        if (FOUL_BOX_BOTTOM_RIGHT_X <= self.x <= FOUL_BOX_BOTTOM_RIGHT_X + FOUL_BOX_WIDTH and
            FOUL_BOX_BOTTOM_RIGHT_Y <= self.y <= FOUL_BOX_BOTTOM_RIGHT_Y + FOUL_BOX_HEIGHT):
            return True
        return False

    def sees_black_tape(self):
        if self.state_controller:
            return self.state_controller.get_ground_colour() == "Black"
        return False

    # ─── Higher-level helpers ───
    def face_hoop(self, speed=TURN_SPEED):
        target = self.angle_to_hoop()   # radians
        # shortest angular difference (radians)
        error = (target - self.heading + pi) % (2*pi) - pi
        self.spin_angle(error, speed)

    def drive_to_point(self, target_x, target_y, speed=DEFAULT_SPEED):
        target_dx = target_x - self.x
        target_dy = target_y - self.y
        forward_heading = (pi/2 - atan2(target_dy, target_dx)) % (2*pi)
        error = (forward_heading - self.heading + pi) % (2*pi) - pi
        self.spin_angle(error, TURN_SPEED)
        distance = sqrt(target_dx*target_dx + target_dy*target_dy)
        self.move_distance(distance, speed)

    def reverse_drive_to_point(self, target_x, target_y, speed=DEFAULT_SPEED):
        target_dx = target_x - self.x
        target_dy = target_y - self.y
        forward_heading = (pi/2 - atan2(target_dy, target_dx)) % (2*pi)
        reverse_heading = (forward_heading + pi) % (2*pi)
        error = (reverse_heading - self.heading + pi) % (2*pi) - pi
        self.spin_angle(error, TURN_SPEED)
        distance = sqrt(target_dx*target_dx + target_dy*target_dy)
        self.move_distance(-distance, speed)

    # ╔══════════════════════════════════════════════════════════════════╗
    # ║              F O U L   B O X   H O M I N G                       ║
    # ╚══════════════════════════════════════════════════════════════════╝

    def guess_foul_box(self):
        ir_strength, _ = self.get_ball_data()
        if ir_strength > IR_BALL_CLOSE_THRESHOLD:
            return "TOP_LEFT"
        elif ir_strength > 0:
            return "BOTTOM_RIGHT"
        if self._other_robot_pos is not None:
            other_x, other_y, _ = self._other_robot_pos
            if other_y > FIELD_LENGTH / 2:
                return "BOTTOM_RIGHT"
            else:
                return "TOP_LEFT"
        if self.y > FIELD_LENGTH / 2:
            return "TOP_LEFT"
        else:
            return "BOTTOM_RIGHT"

    def _snap_position_after_foul_exit(self, box, exit_heading):
        '''exit_heading in radians, snapped to cardinal directions'''
        # Convert to degrees for easy cardinal comparison, then back
        heading_deg = round(degrees(exit_heading)) % 360
        if box == "TOP_LEFT":
            if heading_deg == 0:
                self.x = FOUL_BOX_TOP_LEFT_X + FOUL_BOX_WIDTH / 2.0
                self.y = FOUL_BOX_TOP_LEFT_Y + FOUL_BOX_HEIGHT + 2.0
            elif heading_deg == 90:
                self.x = FOUL_BOX_TOP_LEFT_X + FOUL_BOX_WIDTH + 2.0
                self.y = FOUL_BOX_TOP_LEFT_Y + FOUL_BOX_HEIGHT / 2.0
            elif heading_deg == 180:
                self.x = FOUL_BOX_TOP_LEFT_X + FOUL_BOX_WIDTH / 2.0
                self.y = FOUL_BOX_TOP_LEFT_Y - 2.0
            else:
                self.x = FOUL_BOX_TOP_LEFT_X - 2.0
                self.y = FOUL_BOX_TOP_LEFT_Y + FOUL_BOX_HEIGHT / 2.0
        else:
            if heading_deg == 0:
                self.x = FOUL_BOX_BOTTOM_RIGHT_X + FOUL_BOX_WIDTH / 2.0
                self.y = FOUL_BOX_BOTTOM_RIGHT_Y - 2.0
            elif heading_deg == 90:
                self.x = FOUL_BOX_BOTTOM_RIGHT_X + FOUL_BOX_WIDTH + 2.0
                self.y = FOUL_BOX_BOTTOM_RIGHT_Y + FOUL_BOX_HEIGHT / 2.0
            elif heading_deg == 180:
                self.x = FOUL_BOX_BOTTOM_RIGHT_X + FOUL_BOX_WIDTH / 2.0
                self.y = FOUL_BOX_BOTTOM_RIGHT_Y + FOUL_BOX_HEIGHT + 2.0
            else:
                self.x = FOUL_BOX_BOTTOM_RIGHT_X - 2.0
                self.y = FOUL_BOX_BOTTOM_RIGHT_Y + FOUL_BOX_HEIGHT / 2.0

        self._last_l = self.lm.angle()
        self._last_r = self.rm.angle()

    def home_from_foul_box(self):
        if not self.state_controller:
            return False
        if not self.state_controller.get_foul_elapsed():
            return False

        box = self.guess_foul_box()
        # angles in radians: 0, pi/2, pi, 3pi/2
        probe_angles = [0.0, pi/2, pi, 3*pi/2] if box == "TOP_LEFT" else [pi, 3*pi/2, 0.0, pi/2]

        for target_heading in probe_angles:
            error = (target_heading - self.heading + pi) % (2*pi) - pi
            self.spin_angle(error, TURN_SPEED)

            step_count = 0
            max_steps = int(FOUL_PROBE_MAX_CM / FOUL_PROBE_STEP_CM)

            while step_count < max_steps:
                self.move_distance(FOUL_PROBE_STEP_CM, FOUL_PROBE_SPEED)
                step_count += 1

                colour = self.state_controller.get_ground_colour()

                if colour == "Black":
                    self.move_distance(FOUL_PROBE_STEP_CM, FOUL_PROBE_SPEED)
                    self.heading = target_heading % (2*pi)
                    self._snap_position_after_foul_exit(box, self.heading)
                    self.state_controller.set_idle_state()
                    self.state_controller.toggle_foul_elapsed()
                    return True

                if colour == "White":
                    self.move_distance(-FOUL_BACKUP_CM, SLOW_SPEED)
                    break
            else:
                self.move_distance(-(step_count * FOUL_PROBE_STEP_CM), SLOW_SPEED)

        if self._other_robot_pos is not None:
            other_x, other_y, _ = self._other_robot_pos
            self.drive_to_point(other_x, other_y, SLOW_SPEED)
            self.state_controller.set_idle_state()
            self.state_controller.toggle_foul_elapsed()
            return True

        return False

    def start_foul_monitor(self):
        t = Thread(target=self._foul_monitor_loop)
        t.daemon = True
        t.start()


    def shutdown(self):
        self._running = False
        self.stop()
        time.sleep(0.1)