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
    DEFAULT_SPEED, SLOW_SPEED, TURN_SPEED, ODO_SLEEP,
    FOUL_PROBE_STEP_CM, FOUL_PROBE_SPEED, FOUL_PROBE_ANGLE,
    FOUL_PROBE_MAX_CM, FOUL_BACKUP_CM, BOUNDARY_MARGIN,
    IR_BALL_CLOSE_THRESHOLD,
)

# ─── Shared state machine (Dexter's code) ───
from state_controller import State, State_Controller


# ╔══════════════════════════════════════════════════════════════════╗
# ║                     D R I V E R   C L A S S                      ║
# ╚══════════════════════════════════════════════════════════════════╝

class Driver:
    '''
    Differential-drive controller with wheel odometry.
    Tracks theoretical (x, y, heading) and knows the field layout.

    Foul handling is driven by Dexter's Foul_Controller via signals:
      - signal_foul()          : robot has been called for a foul
      - signal_in_foul_box()   : robot is now sitting in a foul box
      - signal_foul_over()     : penalty time done, ready to re-enter
      - signal_ground_colour(c): Dexter's colour sensor sees c

    State machine integration:
      - We read State.IDLE, State.FOUL, etc. from state_controller
      - We do NOT change states ourselves; Dexter's controller does that
      - We just expose is_foul_active() so other code knows to pause
    '''

    def __init__(self, ev3, left_motor, right_motor, colour_sensor,
                 team=TEAM, gyro=None):
        self.ev3 = ev3
        self.lm = left_motor
        self.rm = right_motor
        self.cs = colour_sensor
        self.team = team
        self.gyro = gyro

        # //////// Pose ////////
        if self.team == "ATTACK":
            self.x = START_ATTACK_X
            self.y = START_ATTACK_Y
            self.hoop_x = HOOP_X
            self.hoop_y = HOOP_Y_ATTACK
        else:
            self.x = START_DEFENCE_X
            self.y = START_DEFENCE_Y
            self.hoop_x = HOOP_X
            self.hoop_y = HOOP_Y_DEFENCE

        self.heading = 0.0   # 0 = +y, 90 = +x, 180 = -y, 270 = -x

        # //////// Encoder bookkeeping ////////
        self._last_l = self.lm.angle()
        self._last_r = self.rm.angle()

        # //////// Gyro offset ////////
        if self.gyro is not None:
            self._gyro_offset = self.gyro.angle()
        else:
            self._gyro_offset = 0

        # //////// Foul state (written by Dexter's signals) ////////
        self._foul_flag = False
        self._in_foul_box = False
        self._foul_over = False
        self._ground_colour = None
        self._foul_lock = Lock()   # thread-safe access

        # //////// External data placeholders (filled by other modules later) ////////
        self._other_robot_pos = None      # (x, y, heading) from comms
        self.IR_strength = 0              # written by IRlocation.py thread
        self.IR_position = 0              # written by IRlocation.py thread

        # //////// Threads ////////
        self._running = True
        self._odo_thread = Thread(target=self._odometry_loop)
        self._odo_thread.daemon = True
        self._odo_thread.start()

    # ─── Foul signal interface (Dexter calls these) ───

    def signal_in_foul_box(self):
        '''Dexter says: "hey you are in the foul box now". Stop moving.'''
        with self._foul_lock:
            self._foul_flag = True
            self._in_foul_box = True
            self._foul_over = False
        self.stop()

    def signal_foul_over(self):
        '''Dexter says: "hey, the foul time is over, resume play".'''
        with self._foul_lock:
            self._foul_over = True

    def signal_ground_colour(self, colour):
        '''Dexter pushes ground colour reads here.'''
        with self._foul_lock:
            self._ground_colour = colour

    def is_foul_active(self):
        '''True from foul call until we are back on the field.'''
        with self._foul_lock:
            return self._foul_flag

    # ─── External data setters (called by comms / IR threads when ready) ───

    def set_other_robot_position(self, x, y, heading):
        '''Placeholder: comms module calls this with other robot's pose.'''
        self._other_robot_pos = (x, y, heading)

    def get_ball_data(self):
        '''Return current IR ball seeker data as (strength, position).'''
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
                self.heading = self.heading % 360.0

                if self.gyro is not None:
                    gyro_heading = (self.gyro.angle() - self._gyro_offset) % 360
                    self.heading = (0.9 * self.heading + 0.1 * gyro_heading) % 360

                h_rad = radians(self.heading)
                self.x += d_centre * sin(h_rad)
                self.y += d_centre * cos(h_rad)

                self._last_l = l_now
                self._last_r = r_now

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

    def turn_angle(self, angle_deg, speed=TURN_SPEED):
        wheel_dist = (abs(angle_deg) / 360.0) * pi * TRACK_WIDTH
        rotations = wheel_dist / WHEEL_CIRCUM
        target_deg = rotations * 360.0

        start_l = self.lm.angle()
        start_r = self.rm.angle()

        direction = 1 if angle_deg >= 0 else -1
        self.lm.run(-speed * direction)
        self.rm.run(speed * direction)

        while True:
            travelled = abs(self.lm.angle() - start_l)
            if travelled >= target_deg:
                break
            time.sleep(0.01)

        self.stop()
        self.heading = (self.heading + angle_deg) % 360.0

    def pivot(self, pivot_side, speed=DEFAULT_SPEED, duration_sec=None):
        if pivot_side == "LEFT":
            self.lm.stop()
            self.lm.brake()
            self.rm.run(speed)
        elif pivot_side == "RIGHT":
            self.rm.stop()
            self.rm.brake()
            self.lm.run(speed)
        else:
            raise ValueError("pivot_side must be 'LEFT' or 'RIGHT'")

        if duration_sec is not None:
            time.sleep(duration_sec)
            self.stop()

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
        True if Dexter reported white ground colour (foul box tape)
        or if our theoretical position is inside a known foul box.
        '''
        with self._foul_lock:
            if self._ground_colour == "White":
                return True

        # Backup: theoretical position inside either foul box
        if (FOUL_BOX_TOP_LEFT_X <= self.x <= FOUL_BOX_TOP_LEFT_X + FOUL_BOX_WIDTH and
            FOUL_BOX_TOP_LEFT_Y <= self.y <= FOUL_BOX_TOP_LEFT_Y + FOUL_BOX_HEIGHT):
            return True

        if (FOUL_BOX_BOTTOM_RIGHT_X <= self.x <= FOUL_BOX_BOTTOM_RIGHT_X + FOUL_BOX_WIDTH and
            FOUL_BOX_BOTTOM_RIGHT_Y <= self.y <= FOUL_BOX_BOTTOM_RIGHT_Y + FOUL_BOX_HEIGHT):
            return True

        return False

    def sees_black_tape(self):
        '''True if Dexter reported black ground colour (field border).'''
        with self._foul_lock:
            return self._ground_colour == "Black"

    # ─── Higher-level helpers ───
    def face_hoop(self, speed=TURN_SPEED):
        target_heading = self.angle_to_hoop()
        heading_error = (target_heading - self.heading + 180) % 360 - 180
        self.turn_angle(heading_error, speed)

    def drive_to_point(self, target_x, target_y, speed=DEFAULT_SPEED):
        target_dx = target_x - self.x
        target_dy = target_y - self.y
        target_heading = (90.0 - degrees(atan2(target_dy, target_dx))) % 360.0
        heading_error = (target_heading - self.heading + 180) % 360 - 180

        self.turn_angle(heading_error, TURN_SPEED)
        distance = sqrt(target_dx * target_dx + target_dy * target_dy)
        self.move_distance(distance, speed)

    # ╔══════════════════════════════════════════════════════════════════╗
    # ║              F O U L   B O X   H O M I N G                       ║
    # ╚══════════════════════════════════════════════════════════════════╝

    def guess_foul_box(self):
        '''
        Guess which foul box we are in.

        Uses ball IR strength if available:
          - Strong signal (> IR_BALL_CLOSE_THRESHOLD) -> ball is close -> top-left box
          - Weak / no signal     -> ball is far  -> bottom-right box

        Falls back to checking if the other robot's position is known;
        if the other bot is on the field and we know where it is,
        we can infer which corner we were dumped in.

        Returns "TOP_LEFT" or "BOTTOM_RIGHT".
        '''
        ir_strength, _ = self.get_ball_data()

        # Primary: IR ball strength
        if ir_strength > IR_BALL_CLOSE_THRESHOLD:
            return "TOP_LEFT"
        elif ir_strength > 0:
            return "BOTTOM_RIGHT"

        # Fallback: other robot position (if comms is up)
        if self._other_robot_pos is not None:
            other_x, other_y, _ = self._other_robot_pos
            # If other robot is in the top half, we are probably bottom-right
            # If other robot is in the bottom half, we are probably top-left
            if other_y > FIELD_LENGTH / 2:
                return "BOTTOM_RIGHT"
            else:
                return "TOP_LEFT"

        # Last resort: use our own last known position before foul
        # If we were in the top half of the field, likely dumped top-left
        if self.y > FIELD_LENGTH / 2:
            return "TOP_LEFT"
        else:
            return "BOTTOM_RIGHT"

    def _snap_position_after_foul_exit(self, box, exit_heading):
        '''Reset odometry to a known coordinate after leaving a foul box.'''
        # Normalise heading to cardinal direction
        heading = round(exit_heading) % 360

        if box == "TOP_LEFT":
            if heading == 0:
                # Exited downward (bottom edge of top-left box)
                self.x = FOUL_BOX_TOP_LEFT_X + FOUL_BOX_WIDTH / 2.0
                self.y = FOUL_BOX_TOP_LEFT_Y + FOUL_BOX_HEIGHT + 2.0
            elif heading == 90:
                # Exited rightward (right edge of top-left box)
                self.x = FOUL_BOX_TOP_LEFT_X + FOUL_BOX_WIDTH + 2.0
                self.y = FOUL_BOX_TOP_LEFT_Y + FOUL_BOX_HEIGHT / 2.0
            elif heading == 180:
                # Exited upward (top edge -- unlikely but handle it)
                self.x = FOUL_BOX_TOP_LEFT_X + FOUL_BOX_WIDTH / 2.0
                self.y = FOUL_BOX_TOP_LEFT_Y - 2.0
            else:
                # Exited leftward (left edge)
                self.x = FOUL_BOX_TOP_LEFT_X - 2.0
                self.y = FOUL_BOX_TOP_LEFT_Y + FOUL_BOX_HEIGHT / 2.0
        else:
            # BOTTOM_RIGHT box
            if heading == 0:
                # Exited downward (bottom edge)
                self.x = FOUL_BOX_BOTTOM_RIGHT_X + FOUL_BOX_WIDTH / 2.0
                self.y = FOUL_BOX_BOTTOM_RIGHT_Y - 2.0
            elif heading == 90:
                # Exited rightward (right edge)
                self.x = FOUL_BOX_BOTTOM_RIGHT_X + FOUL_BOX_WIDTH + 2.0
                self.y = FOUL_BOX_BOTTOM_RIGHT_Y + FOUL_BOX_HEIGHT / 2.0
            elif heading == 180:
                # Exited upward (top edge of bottom-right box)
                self.x = FOUL_BOX_BOTTOM_RIGHT_X + FOUL_BOX_WIDTH / 2.0
                self.y = FOUL_BOX_BOTTOM_RIGHT_Y + FOUL_BOX_HEIGHT + 2.0
            else:
                # Exited leftward (left edge)
                self.x = FOUL_BOX_BOTTOM_RIGHT_X - 2.0
                self.y = FOUL_BOX_BOTTOM_RIGHT_Y + FOUL_BOX_HEIGHT / 2.0

        self._last_l = self.lm.angle()
        self._last_r = self.rm.angle()

    def home_from_foul_box(self):
        '''
        Call after Dexter signals foul_over.

        The foul box has a WHITE outline. The game field has a BLACK outline.
        We are inside a white box and need to cross a black line to get back
        onto the field.

        Strategy:
          1. Guess which box we are in (top-left or bottom-right).
          2. Pick probe directions that face toward the field centre.
          3. Creep forward in small steps, watching ground colour.
          4. If we see BLACK -> we found the field border. Cross it and stop.
          5. If we see WHITE -> we hit the foul box edge. Back up and turn.
          6. If we see neither after max distance -> back up and try next side.

        Returns True if we think we made it onto the field.
        '''
        with self._foul_lock:
            if not self._foul_over:
                return False

        box = self.guess_foul_box()

        # Probe directions: try the sides most likely to face the field first.
        # Top-left box:  0 deg (+y, down field), 90 deg (+x, right)
        # Bottom-right:  180 deg (-y, up field), 270 deg (-x, left)
        if box == "TOP_LEFT":
            probe_angles = [0.0, 90.0, 180.0, 270.0]
        else:
            probe_angles = [180.0, 270.0, 0.0, 90.0]

        for target_heading in probe_angles:
            heading_error = (target_heading - self.heading + 180) % 360 - 180
            self.turn_angle(heading_error, TURN_SPEED)

            step_count = 0
            max_steps = int(FOUL_PROBE_MAX_CM / FOUL_PROBE_STEP_CM)

            while step_count < max_steps:
                self.move_distance(FOUL_PROBE_STEP_CM, FOUL_PROBE_SPEED)
                step_count += 1

                with self._foul_lock:
                    colour = self._ground_colour

                if colour == "Black":
                    # Found the field border. Cross it and get inside.
                    self.move_distance(FOUL_PROBE_STEP_CM, FOUL_PROBE_SPEED)
                    # Snap heading to cardinal so we are "straight"
                    self.heading = target_heading % 360.0
                    # Reset position so we know where we are
                    self._snap_position_after_foul_exit(box, self.heading)
                    with self._foul_lock:
                        self._foul_flag = False
                        self._in_foul_box = False
                        self._foul_over = False
                    return True

                if colour == "White":
                    # Hit foul box edge -- wrong way. Retreat and try next angle.
                    self.move_distance(-FOUL_BACKUP_CM, SLOW_SPEED)
                    break

            else:
                # Max steps, no tape seen. Retreat fully.
                self.move_distance(-(step_count * FOUL_PROBE_STEP_CM), SLOW_SPEED)

        # All directions tried. Use other robot as last resort.
        if self._other_robot_pos is not None:
            other_x, other_y, _ = self._other_robot_pos
            # Drive toward other robot's position (it is on the field)
            self.drive_to_point(other_x, other_y, SLOW_SPEED)
            with self._foul_lock:
                self._foul_flag = False
                self._in_foul_box = False
                self._foul_over = False
            return True

        return False

    def start_foul_monitor(self):
        '''
        Spawn a background thread that auto-runs home_from_foul_box()
        when Dexter gives the all-clear. Call once during robot init.
        '''
        t = Thread(target=self._foul_monitor_loop)
        t.daemon = True
        t.start()

    def _foul_monitor_loop(self):
        while self._running:
            with self._foul_lock:
                should_home = self._foul_over and self._in_foul_box

            if should_home:
                time.sleep(0.5)   # let Dexter finish cleanup
                self.home_from_foul_box()

            time.sleep(0.2)

    def shutdown(self):
        self._running = False
        self.stop()
        time.sleep(0.1)


# ╔══════════════════════════════════════════════════════════════════╗
# ║              B A C K W A R D S   C O M P A T                     ║
# ╚══════════════════════════════════════════════════════════════════╝

class MyTank(Driver):
    '''Old name - redirects to Driver so Hugo's code keeps working.'''
    def __init__(self, ev3, Lmotor, Rmotor, csL, usF, csR, usS):
        super().__init__(ev3, Lmotor, Rmotor, csL, team=TEAM)
        self.usF = usF
        self.csR = csR
        self.usS = usS
        self.csL = csL
