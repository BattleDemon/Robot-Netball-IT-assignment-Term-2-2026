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
    START_ATTACK_HEADING, START_DEFENCE_HEADING,
    DEFAULT_SPEED, SLOW_SPEED, TURN_SPEED, ODO_SLEEP,
    FOUL_PROBE_STEP_CM, FOUL_PROBE_SPEED, FOUL_PROBE_ANGLE,
    FOUL_PROBE_MAX_CM, FOUL_BACKUP_CM, BOUNDARY_MARGIN,
    IR_BALL_CLOSE_THRESHOLD,
)


class Driver:
    '''
    Differential-drive controller with wheel odometry.
    Tracks theoretical (x, y, heading) and knows the field layout.

    Integrates with Dexter's State_Controller:
      - Foul state, ground colour, and position are pushed to the SC automatically.
      - Foul signals are handled by updating the SC directly.
    '''

    def __init__(self, ev3, left_motor, right_motor, colour_sensor,
                 team=TEAM, gyro=None, state_controller=None):
        self.ev3 = ev3
        self.lm = left_motor
        self.rm = right_motor
        self.cs = colour_sensor
        self.team = team
        self.gyro = gyro
        self.state_controller = state_controller   # Dexter's State_Controller instance

        # ╔══════════════════════════════════════════════════════════════════╗
        # ║  C O O R D I N A T E   S Y S T E M   (read this before testing!) ║
        # ╚══════════════════════════════════════════════════════════════════╝
        # Field is a rectangle: 0,0 at bottom-left (defence start area)
        #   x = 0 to 158  (short side, left -> right)
        #   y = 0 to 219  (long side,  bottom -> top)
        #
        #          Y=219 ┌──────────────────┐
        #                │     ATTACK       │  <-- attack starts around (79, 199)
        #                │    (top half)    │
        #                │                  │
        #            Y=0 │     DEFENCE      │  <-- defence starts around (79, 20)
        #                └──────────────────┘
        #               X=0                X=158
        #
        # Heading 0 deg  = facing +Y (toward the attack end)
        # Heading 90 deg = facing +X (toward the right wall)
        # Heading 180    = facing -Y (toward the defence end)
        # Heading 270    = facing -X (toward the left wall)
        #
        # IMPORTANT: The EV3 brick screen shows x and y. If our robot
        # thinks it is moving the wrong way on the field:
        #   1. Check which motor is left and which is right.
        #      Left motor should be on the LEFT side when looking from
        #      the back of the robot toward the front.
        #   2. If X increases when it should decrease, swap motor ports.
        #   3. If the robot drives backwards when told to go forward,
        #      reverse the motor Direction in the Motor() call:
        #         Motor(Port.B, positive_direction=Direction.COUNTERCLOCKWISE)
        #   4. If turning is backwards (pivots the wrong way), swap the
        #      "LEFT" / "RIGHT" calls in pivot_angle() or check motor wiring.
        #
        # TWEAKING ODOMETRY:
        #   - WHEEL_DIAMETER and TRACK_WIDTH live in robot_config.py.
        #   - If the robot drives 30 cm but odometry says 25 cm,
        #     your WHEEL_DIAMETER is too small -- increase it.
        #   - If the robot turns 90 deg but odometry drifts 120 deg,
        #     your TRACK_WIDTH is too small -- increase it.
        #   - Gyro sensor (if plugged in) blends 10 % into heading to
        #     reduce drift. If it makes things worse, unplug the gyro
        #     or change the 0.9 / 0.1 blend in _odometry_loop().
        #
        # TIP: Run test_movement.py -- it will print positions after
        # each action so you can see what is wrong.
        # ═══════════════════════════════════════════════════════════════════

        # //////// Pose ////////
        if self.team == "ATTACK":
            self.x = START_ATTACK_X
            self.y = START_ATTACK_Y
            self.heading = START_ATTACK_HEADING
            self.hoop_x = HOOP_X
            self.hoop_y = HOOP_Y_ATTACK
        else:
            self.x = START_DEFENCE_X
            self.y = START_DEFENCE_Y
            self.heading = START_DEFENCE_HEADING
            self.hoop_x = HOOP_X
            self.hoop_y = HOOP_Y_DEFENCE

        # //////// Encoder bookkeeping ////////
        self._last_l = self.lm.angle()
        self._last_r = self.rm.angle()

        # //////// Gyro offset ////////
        if self.gyro is not None:
            self._gyro_offset = self.gyro.angle()
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

    # ─── Foul signal interface (now updates State_Controller directly) ───

    def signal_in_foul_box(self):
        '''Dexter says: "you are in the foul box". Stop moving and set state.'''
        if self.state_controller:
            self.state_controller.set_foul_state()
        self.stop()

    def signal_foul_over(self):
        '''Dexter says: "foul time over, resume play". Toggle elapsed flag.'''
        if self.state_controller:
            self.state_controller.toggle_foul_elapsed()

    def signal_ground_colour(self, colour):
        '''Dexter pushes ground colour reads here.'''
        if self.state_controller:
            self.state_controller.set_ground_colour(colour)

    def is_foul_active(self):
        '''True if the robot is currently in a foul state.'''
        if self.state_controller:
            return self.state_controller.get_state() == State.FOUL
        return False

    # ─── External data setters ───

    def set_other_robot_position(self, x, y, heading):
        self._other_robot_pos = (x, y, heading)

    def get_ball_data(self):
        return (self.IR_strength, self.IR_position)

    # ─── Internal odometry thread ───
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
                d_theta  = degrees((d_right - d_left) / TRACK_WIDTH)

                self.heading += d_theta
                self.heading %= 360.0

                if self.gyro is not None:
                    gyro_heading = (self.gyro.angle() - self._gyro_offset) % 360
                    self.heading = (0.9 * self.heading + 0.1 * gyro_heading) % 360

                h_rad = radians(self.heading)
                self.x += d_centre * sin(h_rad)
                self.y += d_centre * cos(h_rad)

                self._last_l = l_now
                self._last_r = r_now

                # Keep the State_Controller in sync with the real position
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
    # ║                    T U R N I N G   M E T H O D S                 ║
    # ║                                                                  ║
    # ║  Positive angle = clockwise (following robot’s right‑hand rule)  ║
    # ║  Use  spin_angle()  when tracking the ball (fast, stays in place)║
    # ║  Use  pivot_angle() when you HAVE the ball (netball foot rule)   ║
    # ╚══════════════════════════════════════════════════════════════════╝

    def spin_angle(self, angle_deg, speed=TURN_SPEED):
        '''
        Rotate in place (both wheels opposite).
        Positive angle_deg = clockwise.
        Odometry heading is forced to the exact target to avoid drift.
        '''
        wheel_dist = (abs(angle_deg) / 360.0) * pi * TRACK_WIDTH
        target_deg = (wheel_dist / WHEEL_CIRCUM) * 360.0

        direction = 1 if angle_deg >= 0 else -1
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
        self.heading = (self.heading + angle_deg) % 360.0
        self._last_l = self.lm.angle()
        self._last_r = self.rm.angle()

    def pivot_angle(self, pivot_side, angle_deg, speed=TURN_SPEED):
        '''
        Pivot around one braked wheel (netball legal).
        Position and heading are tracked by the odometry thread.
        Positive angle_deg = clockwise.
        '''
        wheel_dist = (abs(angle_deg) / 360.0) * pi * TRACK_WIDTH * 2
        target_deg = (wheel_dist / WHEEL_CIRCUM) * 360.0

        if pivot_side == "LEFT":
            self.lm.brake()
            direction = -1 if angle_deg >= 0 else 1
            self.rm.run(speed * direction)
            motor = self.rm
        elif pivot_side == "RIGHT":
            self.rm.brake()
            direction = 1 if angle_deg >= 0 else -1
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

    def pivot(self, pivot_side, speed=DEFAULT_SPEED, duration_sec=None):
        '''
        Timed pivot (no angle control).
        '''
        if pivot_side == "LEFT":
            self.lm.stop()
            self.lm.brake()
            self.rm.run(speed)
        elif pivot_side == "RIGHT":
            self.rm.stop()
            self.rm.brake()
            self.lm.run(speed)
        else:
            return

        if duration_sec is not None:
            time.sleep(duration_sec)
            self.stop()

        self._last_l = self.lm.angle()
        self._last_r = self.rm.angle()

    # ─── Position / pose getters ───
    def get_position(self):
        return (self.x, self.y)

    def get_heading(self):
        return self.heading

    def reset_position(self, x=0.0, y=0.0, heading=0.0):
        self.x = x
        self.y = y
        self.heading = heading % 360.0
        if self.gyro is not None:
            self._gyro_offset = self.gyro.angle() - self.heading
        self._last_l = self.lm.angle()
        self._last_r = self.rm.angle()

    # ─── Field awareness ───
    def distance_to_hoop(self):
        hoop_dx = self.hoop_x - self.x
        hoop_dy = self.hoop_y - self.y
        return sqrt(hoop_dx * hoop_dx + hoop_dy * hoop_dy)

    def angle_to_hoop(self):
        hoop_dx = self.hoop_x - self.x
        hoop_dy = self.hoop_y - self.y
        angle_from_x = degrees(atan2(hoop_dy, hoop_dx))
        target_heading = (90.0 - angle_from_x) % 360.0
        return target_heading

    def is_in_bounds(self):
        return (BOUNDARY_MARGIN <= self.x <= FIELD_WIDTH - BOUNDARY_MARGIN and
                BOUNDARY_MARGIN <= self.y <= FIELD_LENGTH - BOUNDARY_MARGIN)

    def is_in_foul_area(self):
        '''
        True if the State_Controller reports white ground colour
        or if our theoretical position is inside a known foul box.
        '''
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
        target_heading = self.angle_to_hoop()
        heading_error = (target_heading - self.heading + 180) % 360 - 180
        self.spin_angle(heading_error, speed)

    def drive_to_point(self, target_x, target_y, speed=DEFAULT_SPEED):
        target_dx = target_x - self.x
        target_dy = target_y - self.y
        forward_heading = (90.0 - degrees(atan2(target_dy, target_dx))) % 360.0
        heading_error = (forward_heading - self.heading + 180) % 360 - 180
        self.spin_angle(heading_error, TURN_SPEED)
        distance = sqrt(target_dx * target_dx + target_dy * target_dy)
        self.move_distance(distance, speed)

    def reverse_drive_to_point(self, target_x, target_y, speed=DEFAULT_SPEED):
        '''
        Drive to a point by facing 180° away from it and reversing.
        '''
        target_dx = target_x - self.x
        target_dy = target_y - self.y
        forward_heading = (90.0 - degrees(atan2(target_dy, target_dx))) % 360.0
        reverse_heading = (forward_heading + 180) % 360.0
        heading_error = (reverse_heading - self.heading + 180) % 360 - 180
        self.spin_angle(heading_error, TURN_SPEED)
        distance = sqrt(target_dx * target_dx + target_dy * target_dy)
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
        heading = round(exit_heading) % 360
        if box == "TOP_LEFT":
            if heading == 0:
                self.x = FOUL_BOX_TOP_LEFT_X + FOUL_BOX_WIDTH / 2.0
                self.y = FOUL_BOX_TOP_LEFT_Y + FOUL_BOX_HEIGHT + 2.0
            elif heading == 90:
                self.x = FOUL_BOX_TOP_LEFT_X + FOUL_BOX_WIDTH + 2.0
                self.y = FOUL_BOX_TOP_LEFT_Y + FOUL_BOX_HEIGHT / 2.0
            elif heading == 180:
                self.x = FOUL_BOX_TOP_LEFT_X + FOUL_BOX_WIDTH / 2.0
                self.y = FOUL_BOX_TOP_LEFT_Y - 2.0
            else:
                self.x = FOUL_BOX_TOP_LEFT_X - 2.0
                self.y = FOUL_BOX_TOP_LEFT_Y + FOUL_BOX_HEIGHT / 2.0
        else:
            if heading == 0:
                self.x = FOUL_BOX_BOTTOM_RIGHT_X + FOUL_BOX_WIDTH / 2.0
                self.y = FOUL_BOX_BOTTOM_RIGHT_Y - 2.0
            elif heading == 90:
                self.x = FOUL_BOX_BOTTOM_RIGHT_X + FOUL_BOX_WIDTH + 2.0
                self.y = FOUL_BOX_BOTTOM_RIGHT_Y + FOUL_BOX_HEIGHT / 2.0
            elif heading == 180:
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

        if box == "TOP_LEFT":
            probe_angles = [0.0, 90.0, 180.0, 270.0]
        else:
            probe_angles = [180.0, 270.0, 0.0, 90.0]

        for target_heading in probe_angles:
            heading_error = (target_heading - self.heading + 180) % 360 - 180
            self.spin_angle(heading_error, TURN_SPEED)

            step_count = 0
            max_steps = int(FOUL_PROBE_MAX_CM / FOUL_PROBE_STEP_CM)

            while step_count < max_steps:
                self.move_distance(FOUL_PROBE_STEP_CM, FOUL_PROBE_SPEED)
                step_count += 1

                colour = self.state_controller.get_ground_colour()

                if colour == "Black":
                    self.move_distance(FOUL_PROBE_STEP_CM, FOUL_PROBE_SPEED)
                    self.heading = target_heading % 360.0
                    self._snap_position_after_foul_exit(box, self.heading)
                    # Reset foul state in the controller
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

    def _foul_monitor_loop(self):
        while self._running:
            if self.state_controller and self.state_controller.get_foul_elapsed():
                time.sleep(0.5)
                self.home_from_foul_box()
            time.sleep(0.2)

    def shutdown(self):
        self._running = False
        self.stop()
        time.sleep(0.1)