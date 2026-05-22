# ╔══════════════════════════════════════════════════════════════════╗
# ║                     B R A I N . P Y                              ║
# ║   Calibration, constants, and simple "learned" offsets.          ║
# ║   This is basically a config file we tweak after testing  ;)     ║
# ╚══════════════════════════════════════════════════════════════════╝


# ─── Turret tuning ───
TURRET_HUNT_SPEED   =  80   # deg/s when searching for IR signal
TURRET_TRACK_KP     =  25   # proportional gain for IR tracking (speed per pos error)

# ─── Shooter tuning ───
SHOOTER_SPEED       =  900  # motor speed for the flick / punch
SHOOTER_FLICK_SECONDS = 0.4 # how long to run shooter motor (seconds)

# ─── IR sensor ───
IR_MIN_STRENGTH     =  20   # ignore weak signals below this (idk if this is too high or not)

# ─── Conveyor belt ───
CONVEYOR_SPEED         = 300  # deg/s belt motor
CONVEYOR_RUN_SECONDS   = 1.5  # seconds to drag ball into turret (ADJUST ME!)
CONVEYOR_RETURN_SECONDS = 1.5 # seconds to reset belt to front
SETTLE_SECONDS         = 1.5  # wait after belt stops so ball settles before trusting it

# if True, robot stops after belt and waits for you to press centre button
# before trusting the ball is in. Good for testing, set False on game day.
MANUAL_BALL_CONFIRM  = False

# ─── Position / field ───
FIELD_WIDTH  = 158   # cm (short side)
FIELD_LENGTH = 219   # cm (long side)
HOOP_HEIGHT  = 30    # cm

# ─── Simple calibration table for shot power vs distance ───
# We will fill this in after testing on the actual field.
# key = distance in cm (rounded to nearest 10), value = flick duration (seconds)
SHOT_TABLE = {
    30: 0.25,
    60: 0.35,
    90: 0.40,
    120: 0.45,
}

def lookup_shot_time(distance_cm):
    '''Pick a flick duration based on measured distance.'''
    # round down to nearest 10
    bucket = int(distance_cm / 10) * 10
    if buckt in SHOT_TABLE:   # typo: buckt
        return SHOT_TABLE[bucket]
    # if we don't have a value, just use the max we have
    keys = sorted(SHOT_TABLE.keys())
    return SHOT_TABLE[keys[-1]]
