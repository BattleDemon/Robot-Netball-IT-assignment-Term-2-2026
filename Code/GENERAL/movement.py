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
from pybricks.parameters import Port, Stop, Direction, Color
from pybricks.tools import wait

from math import pi, sin, cos, radians, degrees, atan2, sqrt
from threading import Thread, Lock
import time

# ─── Shared state machine (Dexter's code) ───
from state_controller import State, State_Controller

# ╔══════════════════════════════════════════════════════════════════╗
# ║              R O B O T   C O N F I G U R A T I O N               ║
# ╚══════════════════════════════════════════════════════════════════╝

# //////// Team setting ////////
# Change this to "DEFENCE" when running on the defender bot.
TEAM = "ATTACK"

# //////// Wheel specs (cm) ////////
WHEEL_DIAMETER = 5.6
WHEEL_RADIUS   = WHEEL_DIAMETER / 2.0
WHEEL_CIRCUM   = pi * WHEEL_DIAMETER
TRACK_WIDTH    = 12.3   # distance between wheel centres (cm)

# //////// Field dimensions (cm) ////////
FIELD_WIDTH  = 158.0   # short side (x axis)
FIELD_LENGTH = 219.0   # long side  (y axis)

# //////// Hoop position (centre of short side) ////////
HOOP_X = FIELD_WIDTH / 2.0   # 79.0
HOOP_Y_ATTACK = 0.0          # attack shoots toward y=0
HOOP_Y_DEFENCE = FIELD_LENGTH  # defence shoots toward y=219

# //////// Foul box dimensions (cm) ////////
# Foul boxes are in top-left and bottom-right corners.
# Each box is a white-taped rectangle.
FOUL_BOX_WIDTH  = 30.0
FOUL_BOX_HEIGHT = 30.0

# Top-left foul box coords
FOUL_BOX_TOP_LEFT_X = 0.0
FOUL_BOX_TOP_LEFT_Y = FIELD_LENGTH - FOUL_BOX_HEIGHT   # y=189

# Bottom-right foul box coords
FOUL_BOX_BOTTOM_RIGHT_X = FIELD_WIDTH - FOUL_BOX_WIDTH   # x=128
FOUL_BOX_BOTTOM_RIGHT_Y = 0.0

# //////// Start positions ////////
START_ATTACK_X = FIELD_WIDTH / 2.0
START_ATTACK_Y = FIELD_LENGTH - 20.0

START_DEFENCE_X = FIELD_WIDTH / 2.0
START_DEFENCE_Y = 20.0

# //////// Movement defaults ////////
DEFAULT_SPEED = 200       # deg/s for motors
SLOW_SPEED    = 100       # for precise approaches
TURN_SPEED    = 150       # deg/s when rotating

# //////// Odometry update rate ////////
ODO_SLEEP = 0.05          # seconds between position updates (20 Hz)

# //////// Foul box homing ////////
FOUL_PROBE_STEP_CM = 4.0     # small steps so we dont overshoot tape
FOUL_PROBE_SPEED = 60        # slow and careful
FOUL_PROBE_ANGLE = 90.0      # try each side of the box
FOUL_PROBE_MAX_CM = 35.0     # foul box is ~30cm, add margin
FOUL_BACKUP_CM = 3.0         # retreat from white tape before turning


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
        self._ball_ir_strength = 0
        self._ball_ir_position = 0

        # //////// Threads ////////
        self._running = True
        self._odo_thread = Thread(target=self._odometry_loop)
        self._odo_thread.daemon = True
        self._odo_thread.start()

    # ─── Foul signal interface (Dexter calls these) ───

    def signal_foul(self):
        '''Dexter says: "hey you have fouled". Stop moving.'''
        with self._foul_lock:
            self._foul_flag = True
            self._in_foul_box = False
            self._foul_over = False
        self.stop()

    def signal_in_foul_box(self):
        '''Dexter says: "hey you are in the foul box now".'''
        with self._foul_lock:
            self._in_foul_box = True

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

    def set_ball_ir_data(self, strength, position):
        '''Placeholder: IR thread calls this with ball seeker data.'''
        self._ball_ir_strength = strength
        self._ball_ir_position = position

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

    def reset_position(self, x=None, y=None, heading=None):
        if x is not None:
            self.x = x
        if y is not None:
            self.y = y
        if heading is not None:
            self.heading = heading % 360.0
            if self.gyro is not None:
                self._gyro_offset = self.gyro.angle() - self.heading
        self._last_l = self.lm.angle()
        self._last_r = self.rm.angle()

    # ─── Field awareness ───
    def distance_to_hoop(self):
        dx = self.hoop_x - self.x
        dy = self.hoop_y - self.y
        return sqrt(dx * dx + dy * dy)

    def angle_to_hoop(self):
        dx = self.hoop_x - self.x
        dy = self.hoop_y - self.y
        angle_from_x = degrees(atan2(dy, dx))
        angle = (90.0 - angle_from_x) % 360.0
        return angle

    def is_in_bounds(self):
        margin = 5.0
        return (margin <= self.x <= FIELD_WIDTH - margin and
                margin <= self.y <= FIELD_LENGTH - margin)

    def is_in_foul_area(self):
        '''
        True if Dexter reported white ground colour (foul box tape)
        or if our theoretical position is inside a known foul box.
        '''
        with self._foul_lock:
            if self._ground_colour == Color.WHITE:
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
            return self._ground_colour == Color.BLACK

    # ─── Higher-level helpers ───
    def face_hoop(self, speed=TURN_SPEED):
        target = self.angle_to_hoop()
        diff = (target - self.heading + 180) % 360 - 180
        self.turn_angle(diff, speed)

    def drive_to_point(self, tx, ty, speed=DEFAULT_SPEED):
        dx = tx - self.x
        dy = ty - self.y
        target_heading = (90.0 - degrees(atan2(dy, dx))) % 360.0
        diff = (target_heading - self.heading + 180) % 360 - 180

        self.turn_angle(diff, TURN_SPEED)
        dist = sqrt(dx * dx + dy * dy)
        self.move_distance(dist, speed)

    # ╔══════════════════════════════════════════════════════════════════╗
    # ║              F O U L   B O X   H O M I N G                       ║
    # ╚══════════════════════════════════════════════════════════════════╝

    def guess_foul_box(self):
        '''
        Guess which foul box we are in.

        Uses ball IR strength if available:
          - Strong signal (>40)  -> ball is close -> top-left box
          - Weak / no signal     -> ball is far  -> bottom-right box

        Falls back to checking if the other robot's position is known;
        if the other bot is on the field and we know where it is,
        we can infer which corner we were dumped in.

        Returns "TOP_LEFT" or "BOTTOM_RIGHT".
        '''
        # Primary: IR ball strength
        if self._ball_ir_strength > 40:
            return "TOP_LEFT"
        elif self._ball_ir_strength > 0:
            return "BOTTOM_RIGHT"

        # Fallback: other robot position (if comms is up)
        if self._other_robot_pos is not None:
            ox, oy, _ = self._other_robot_pos
            # If other robot is in the top half, we are probably bottom-right
            # If other robot is in the bottom half, we are probably top-left
            if oy > FIELD_LENGTH / 2:
                return "BOTTOM_RIGHT"
            else:
                return "TOP_LEFT"

        # Last resort: use our own last known position before foul
        # If we were in the top half of the field, likely dumped top-left
        if self.y > FIELD_LENGTH / 2:
            return "TOP_LEFT"
        else:
            return "BOTTOM_RIGHT"

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
            diff = (target_heading - self.heading + 180) % 360 - 180
            self.turn_angle(diff, TURN_SPEED)

            step_count = 0
            max_steps = int(FOUL_PROBE_MAX_CM / FOUL_PROBE_STEP_CM)

            while step_count < max_steps:
                self.move_distance(FOUL_PROBE_STEP_CM, FOUL_PROBE_SPEED)
                step_count += 1

                with self._foul_lock:
                    colour = self._ground_colour

                if colour == Color.BLACK:
                    # Found the field border. Cross it and get inside.
                    self.move_distance(FOUL_PROBE_STEP_CM, FOUL_PROBE_SPEED)
                    # Snap heading to cardinal so we are "straight"
                    self.heading = target_heading % 360.0
                    with self._foul_lock:
                        self._foul_flag = False
                        self._in_foul_box = False
                        self._foul_over = False
                    return True

                if colour == Color.WHITE:
                    # Hit foul box edge -- wrong way. Retreat and try next angle.
                    self.move_distance(-FOUL_BACKUP_CM, SLOW_SPEED)
                    break

            else:
                # Max steps, no tape seen. Retreat fully.
                self.move_distance(-(step_count * FOUL_PROBE_STEP_CM), SLOW_SPEED)

        # All directions tried. Use other robot as last resort.
        if self._other_robot_pos is not None:
            ox, oy, _ = self._other_robot_pos
            # Drive toward other robot's position (it is on the field)
            self.drive_to_point(ox, oy, SLOW_SPEED)
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
