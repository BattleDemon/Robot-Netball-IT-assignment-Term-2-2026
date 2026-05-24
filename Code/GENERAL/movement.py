#!/usr/bin/env pybricks-micropython

'''
╔══════════════════════════════════════════════════════════════════╗
║                     M O V E M E N T . P Y                        ║
║   Shared navigation module for Attack & Defence robots.          ║
║   Handles wheel odometry, field mapping, boundary checks,        ║
║   foul detection via colour sensor, and pivot movement.          ║
║                                                                  ║
║   Written by Gabe                                                ║
║                                                                  ║
║   Code ASCII art inspired by inspired by DoGzTheFiGhTeR,         ║
║   GPC Script developer for the Cronus Zen and Cronusmax.         ║
╚══════════════════════════════════════════════════════════════════╝
'''

from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor, ColorSensor, GyroSensor
from pybricks.parameters import Port, Stop, Direction, Color
from pybricks.tools import wait

from math import pi, sin, cos, radians, degrees, atan2, sqrt
from threading import Thread
import time

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

# //////// Foul areas (white zones, right-hand corners of short sides) ////////
# Approximate boxes //////// colour sensor is the real judge, these are backups.
FOUL_X_MIN = FIELD_WIDTH - 30.0   # right side of field
FOUL_Y_BOTTOM_MAX = 30.0          # near y=0
FOUL_Y_TOP_MIN = FIELD_LENGTH - 30.0  # near y=219

# //////// Start positions ////////
# Attack starts far from their target hoop, Defence starts near theirs.
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


# ╔══════════════════════════════════════════════════════════════════╗
# ║                     D R I V E R   C L A S S                      ║
# ╚══════════════════════════════════════════════════════════════════╝

class Driver:
    '''
    Differential-drive controller with wheel odometry.
    Tracks theoretical (x, y, heading) and knows the field layout.
    '''

    def __init__(self, ev3, left_motor, right_motor, colour_sensor,
                 team=TEAM, gyro=None):
        '''
        ev3           - EV3Brick instance
        left_motor    - Motor object for left wheel
        right_motor   - Motor object for right wheel
        colour_sensor - ColorSensor for foul/boundary detection
        team          - "ATTACK" or "DEFENCE"
        gyro          - optional GyroSensor for drift correction
        '''
        self.ev3 = ev3
        self.lm = left_motor
        self.rm = right_motor
        self.cs = colour_sensor
        self.team = team
        self.gyro = gyro

        # //////// Pose (theoretical position) ////////
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

        self.heading = 0.0   # degrees, 0 = facing +y (toward attack hoop)
                             # 90 = facing +x, -90 = facing -x

        # //////// Encoder bookkeeping for odometry ////////
        self._last_l = self.lm.angle()
        self._last_r = self.rm.angle()

        # //////// Gyro offset (if used) ////////
        if self.gyro is not None:
            self._gyro_offset = self.gyro.angle()
        else:
            self._gyro_offset = 0

        # //////// Threading ////////
        self._running = True
        self._odo_thread = Thread(target=self._odometry_loop)
        self._odo_thread.daemon = True
        self._odo_thread.start()

    # ─── Internal odometry thread ───
    def _odometry_loop(self):
        '''Update x, y, heading using wheel encoder deltas.'''
        while self._running:
            # Read current encoder angles (degrees)
            l_now = self.lm.angle()
            r_now = self.rm.angle()

            dl = l_now - self._last_l
            dr = r_now - self._last_r

            # Only update if wheels moved
            if dl != 0 or dr != 0:
                # Distance each wheel travelled (cm)
                d_left  = (dl / 360.0) * WHEEL_CIRCUM
                d_right = (dr / 360.0) * WHEEL_CIRCUM

                # Average forward distance and change in heading
                d_centre = (d_left + d_right) / 2.0
                d_theta  = degrees((d_right - d_left) / TRACK_WIDTH)

                # Update heading
                self.heading += d_theta
                self.heading = self.heading % 360.0

                # If gyro available, blend it in slowly to fight drift
                if self.gyro is not None:
                    gyro_heading = (self.gyro.angle() - self._gyro_offset) % 360
                    # 90 % trust encoders, 10 % trust gyro each tick
                    self.heading = (0.9 * self.heading + 0.1 * gyro_heading) % 360

                # Convert heading to radians for trig
                h_rad = radians(self.heading)

                # Update position (0 deg = +y in our convention)
                self.x += d_centre * sin(h_rad)
                self.y += d_centre * cos(h_rad)

                # Store for next loop
                self._last_l = l_now
                self._last_r = r_now

            time.sleep(ODO_SLEEP)

    # ─── Basic movement commands ───
    def move(self, left_speed=DEFAULT_SPEED, right_speed=DEFAULT_SPEED):
        '''Start both motors at given speeds (deg/s).'''
        self.lm.run(left_speed)
        self.rm.run(right_speed)

    def stop(self, brake=True):
        '''Stop both motors.'''
        self.lm.stop()
        self.rm.stop()
        if brake:
            self.lm.brake()
            self.rm.brake()

    def move_distance(self, distance_cm, speed=DEFAULT_SPEED):
        '''
        Drive straight(ish) for a given distance in cm.
        Positive = forward, negative = backward.
        Blocks until done.
        '''
        # Calculate motor degrees needed
        rotations = distance_cm / WHEEL_CIRCUM
        target_deg = rotations * 360.0

        start_l = self.lm.angle()
        start_r = self.rm.angle()

        # Set direction
        direction = 1 if distance_cm >= 0 else -1
        self.lm.run(speed * direction)
        self.rm.run(speed * direction)

        # Wait until both motors have travelled roughly the right amount
        while True:
            travelled_l = abs(self.lm.angle() - start_l)
            travelled_r = abs(self.rm.angle() - start_r)
            if travelled_l >= abs(target_deg) and travelled_r >= abs(target_deg):
                break
            time.sleep(0.01)

        self.stop()

    def turn_angle(self, angle_deg, speed=TURN_SPEED):
        '''
        Turn in place by angle_deg degrees.
        Positive = clockwise, negative = counter-clockwise.
        Blocks until done.
        '''
        # Arc length each wheel must travel = (angle / 360) * pi * track_width
        wheel_dist = (abs(angle_deg) / 360.0) * pi * TRACK_WIDTH
        rotations = wheel_dist / WHEEL_CIRCUM
        target_deg = rotations * 360.0

        start_l = self.lm.angle()
        start_r = self.rm.angle()

        direction = 1 if angle_deg >= 0 else -1

        # One wheel forward, one backward
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
        '''
        Pivot around one stationary wheel (netball pivot rule).
        pivot_side = "LEFT"  -> left wheel stays still, right wheel moves.
        pivot_side = "RIGHT" -> right wheel stays still, left wheel moves.
        If duration_sec is None, keeps going until you call stop().
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
            raise ValueError("pivot_side must be 'LEFT' or 'RIGHT'")

        if duration_sec is not None:
            time.sleep(duration_sec)
            self.stop()

    # ─── Position / pose getters ───
    def get_position(self):
        '''Return current theoretical (x, y) in cm.'''
        return (self.x, self.y)

    def get_heading(self):
        '''Return current heading in degrees (0 = +y, 90 = +x).'''
        return self.heading

    def reset_position(self, x=None, y=None, heading=None):
        '''
        Override the theoretical position.
        Call this at startup if you place the robot at a known spot.
        '''
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
        '''Straight-line distance from robot to the hoop we are aiming at.'''
        dx = self.hoop_x - self.x
        dy = self.hoop_y - self.y
        return sqrt(dx * dx + dy * dy)

    def angle_to_hoop(self):
        '''
        Return the heading (in degrees) the robot needs to face
        to point directly at its target hoop.
        '''
        dx = self.hoop_x - self.x
        dy = self.hoop_y - self.y
        # atan2(dy, dx) gives angle from +x axis; we want 0 = +y
        angle_from_x = degrees(atan2(dy, dx))
        # Convert to our convention (0 = +y, 90 = +x)
        angle = (90.0 - angle_from_x) % 360.0
        return angle

    def is_in_bounds(self):
        '''Check if theoretical position is inside the black tape border.'''
        margin = 5.0   # a few cm inside the line
        return (margin <= self.x <= FIELD_WIDTH - margin and
                margin <= self.y <= FIELD_LENGTH - margin)

    def is_in_foul_area(self):
        '''
        True if colour sensor sees white OR theoretical position is inside
        a known foul zone. Colour sensor takes priority.
        '''
        # Primary: colour sensor
        try:
            if self.cs.color() == Color.WHITE:
                return True
        except Exception:
            pass   # sensor glitch, fall back to math

        # Backup: theoretical position
        if self.x >= FOUL_X_MIN:
            if self.y <= FOUL_Y_BOTTOM_MAX or self.y >= FOUL_Y_TOP_MIN:
                return True
        return False

    def sees_black_tape(self):
        '''True if colour sensor detects the black border tape.'''
        try:
            return self.cs.color() == Color.BLACK
        except Exception:
            return False

    # ─── Higher-level helpers ───
    def face_hoop(self, speed=TURN_SPEED):
        '''Turn in place until facing the target hoop. Blocks.'''
        target = self.angle_to_hoop()
        diff = (target - self.heading + 180) % 360 - 180   # should be shortest signed diff
        self.turn_angle(diff, speed)

    def drive_to_point(self, tx, ty, speed=DEFAULT_SPEED):
        '''
        Simple point-to-point drive: turn toward target, then drive straight.
        Does NOT avoid obstacles - just goes in a straight line.
        Blocks until done.
        '''
        dx = tx - self.x
        dy = ty - self.y
        target_heading = (90.0 - degrees(atan2(dy, dx))) % 360.0
        diff = (target_heading - self.heading + 180) % 360 - 180

        self.turn_angle(diff, TURN_SPEED)
        dist = sqrt(dx * dx + dy * dy)
        self.move_distance(dist, speed)

    def shutdown(self):
        '''Stop motors and kill the odometry thread. Call before program exit.'''
        self._running = False
        self.stop()
        time.sleep(0.1)


# ╔══════════════════════════════════════════════════════════════════╗
# ║              B A C K W A R D S   C O M P A T                     ║
# ╚══════════════════════════════════════════════════════════════════╝

# DefenceMain.py imports Driver from this file, so the class above is enough.
# If anyone still imports MyTank, keep a thin wrapper so old code doesn't break.

class MyTank(Driver):
    '''Old name - redirects to Driver so Hugo's code keeps working.'''
    def __init__(self, ev3, Lmotor, Rmotor, csL, usF, csR, usS):
        # Map old args to new Driver signature
        # Old: ev3, Lmotor, Rmotor, csL, usF, csR, usS
        # New: ev3, left_motor, right_motor, colour_sensor, team, gyro
        super().__init__(ev3, Lmotor, Rmotor, csL, team=TEAM)
        # Store unused sensors for any old code that touches them
        self.usF = usF
        self.csR = csR
        self.usS = usS
        self.csL = csL
