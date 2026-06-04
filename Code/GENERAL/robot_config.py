#!/usr/bin/env pybricks-micropython

'''
╔══════════════════════════════════════════════════════════════════╗
║                  R O B O T _ C O N F I G . P Y                   ║
║   Shared constants for Attack & Defence robots.                  ║
║   Change values here instead of digging through movement code.   ║
╚══════════════════════════════════════════════════════════════════╝
'''

from math import pi

# ╔══════════════════════════════════════════════════════════════════╗
# ║                        T E A M   S E T U P                       ║
# ╚══════════════════════════════════════════════════════════════════╝

TEAM = "ATTACK"   # Change to "DEFENCE" on the defender bot

# ╔══════════════════════════════════════════════════════════════════╗
# ║              W H E E L   &   C H A S S I S   S P E C S           ║
# ╚══════════════════════════════════════════════════════════════════╝

WHEEL_DIAMETER = 5.6          # cm
WHEEL_RADIUS   = WHEEL_DIAMETER / 2.0
WHEEL_CIRCUM   = pi * WHEEL_DIAMETER
TRACK_WIDTH    = 12.3         # distance between wheel centres (cm)

# ╔══════════════════════════════════════════════════════════════════╗
# ║                    F I E L D   D I M E N S I O N S               ║
# ╚══════════════════════════════════════════════════════════════════╝

FIELD_WIDTH  = 158.0          # short side  (x axis) in cm
FIELD_LENGTH = 219.0          # long side   (y axis) in cm

# ╔══════════════════════════════════════════════════════════════════╗
# ║                    F I E L D   PO S I T I O N S                  ║
# ╚══════════════════════════════════════════════════════════════════╝

START_ATTACK_HEADING  = 180   # facing negative Y (toward hoop)
START_DEFENCE_HEADING = 0     # facing positive Y (toward attack half)

# ╔══════════════════════════════════════════════════════════════════╗
# ║                      H O O P   P O S I T I O N S                 ║
# ╚══════════════════════════════════════════════════════════════════╝

HOOP_X = FIELD_WIDTH / 2.0            # 79.0  (centre of short side)
HOOP_Y_ATTACK  = 0.0          # attack scores here
HOOP_Y_DEFENCE = 0.0          # defence guards this same hoop

# Since there’s only one physical hoop, 
# both robots must target the same actual position.
#Attack starts at y≈199,
#  drives forward (heading 180°, toward negative Y)
#  to reach y=0.

#Defence starts at y=20, 
# already near the hoop, 
# and distance_to_hoop() will be tiny
# it knows it is right there.

# ╔══════════════════════════════════════════════════════════════════╗
# ║                    F O U L   B O X   S P E C S                   ║
# ╚══════════════════════════════════════════════════════════════════╝

FOUL_BOX_WIDTH  = 30.0
FOUL_BOX_HEIGHT = 30.0

# Top-left foul box (viewed from attack side looking toward hoop)
FOUL_BOX_TOP_LEFT_X = 0.0
FOUL_BOX_TOP_LEFT_Y = FIELD_LENGTH - FOUL_BOX_HEIGHT   # y = 189

# Bottom-right foul box
FOUL_BOX_BOTTOM_RIGHT_X = FIELD_WIDTH - FOUL_BOX_WIDTH   # x = 128
FOUL_BOX_BOTTOM_RIGHT_Y = 0.0

# ╔══════════════════════════════════════════════════════════════════╗
# ║                   S T A R T   P O S I T I O N S                  ║
# ╚══════════════════════════════════════════════════════════════════╝

START_ATTACK_X  = FIELD_WIDTH / 2.0
START_ATTACK_Y  = FIELD_LENGTH - 20.0

START_DEFENCE_X = FIELD_WIDTH / 2.0
START_DEFENCE_Y = 20.0

# ╔══════════════════════════════════════════════════════════════════╗
# ║                M O V E M E N T   D E F A U L T S                 ║
# ╚══════════════════════════════════════════════════════════════════╝

DEFAULT_SPEED = 200           # deg/s for motors
SLOW_SPEED    = 100           # for precise approaches
TURN_SPEED    = 150           # deg/s when rotating

# ╔══════════════════════════════════════════════════════════════════╗
# ║                 O D O M E T R Y   S E T T I N G S                ║
# ╚══════════════════════════════════════════════════════════════════╝

ODO_SLEEP = 0.05              # seconds between position updates (20 Hz)

# ╔══════════════════════════════════════════════════════════════════╗
# ║              F O U L   B O X   H O M I N G   P A R A M S         ║
# ╚══════════════════════════════════════════════════════════════════╝

FOUL_PROBE_STEP_CM = 4.0      # small steps so we dont overshoot tape
FOUL_PROBE_SPEED   = 60       # slow and careful
FOUL_PROBE_ANGLE   = 90.0     # try each side of the box
FOUL_PROBE_MAX_CM  = 35.0     # foul box is ~30 cm, add margin
FOUL_BACKUP_CM     = 3.0      # retreat from white tape before turning

# ╔══════════════════════════════════════════════════════════════════╗
# ║              B O U N D A R Y   &   S A F E T Y                   ║
# ╚══════════════════════════════════════════════════════════════════╝

BOUNDARY_MARGIN = 5.0         # cm inside field edge considered "in bounds"

# ╔══════════════════════════════════════════════════════════════════╗
# ║              I R   B A L L   S E E K E R   T H R E S H O L D S   ║
# ╚══════════════════════════════════════════════════════════════════╝

IR_BALL_CLOSE_THRESHOLD = 40  # strength > this means ball is nearby
