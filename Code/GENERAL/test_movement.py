#!/usr/bin/env pybricks-micropython

'''
╔══════════════════════════════════════════════════════════════════╗
║                T E S T _ M O V E M E N T . P Y                   ║
║   Manual test suite for movement.py.  Run on the EV3 brick.      ║
║   Results are printed to the EV3 screen and to the console.      ║
╚══════════════════════════════════════════════════════════════════╝
'''

from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor, ColorSensor
from pybricks.parameters import Port, Direction
from pybricks.tools import wait
from movement import Driver, TEAM

# ═══════════════════════════════════════════════════════════════════
# Setup
# ═══════════════════════════════════════════════════════════════════

ev3 = EV3Brick()

left_motor = Motor(Port.B, positive_direction=Direction.CLOCKWISE)
right_motor = Motor(Port.C, positive_direction=Direction.CLOCKWISE)
colour_sensor = ColorSensor(Port.S3)

driver = Driver(ev3, left_motor, right_motor, colour_sensor, team=TEAM)

# Helper to draw text on screen without clobbering previous lines
def draw(y, text):
    ev3.screen.draw_text(0, y, str(text))

def clear():
    ev3.screen.clear()

def pause(seconds=2):
    wait(seconds * 1000)

# ═══════════════════════════════════════════════════════════════════
# Test 1 -- Initial position dump
# ═══════════════════════════════════════════════════════════════════

clear()
draw(0, "TEST 1: Start pose")
x, y = driver.get_position()
h = driver.get_heading()
draw(20, "X:  {}".format(x))
draw(40, "Y:  {}".format(y))
draw(60, "H:  {}".format(h))
draw(90, "Expected:")
draw(110, "ATTACK ~79,199,0")
draw(130, "DEFENCE ~79,20,0")
pause(4)

# ═══════════════════════════════════════════════════════════════════
# Test 2 -- Drive forward 30 cm, watch Y change
# ═══════════════════════════════════════════════════════════════════

clear()
draw(0, "TEST 2: Drive 30 cm fwd")
start_x, start_y = driver.get_position()
draw(20, "Start: {},{}".format(start_x, start_y))
driver.move_distance(30)
end_x, end_y = driver.get_position()
draw(40, "End:   {},{}".format(end_x, end_y))
delta = end_y - start_y
draw(60, "Delta Y: {}".format(delta))
draw(90, "Expected ~ -30 (attack) or ~ +30 (defence)")
pause(4)

# ═══════════════════════════════════════════════════════════════════
# Test 3 -- Turn 90 deg clockwise and counter-clockwise
# ═══════════════════════════════════════════════════════════════════

clear()
draw(0, "TEST 3: Turn 90 CW")
start_h = driver.get_heading()
draw(20, "Start H: {}".format(start_h))
driver.turn_angle(90)
mid_h = driver.get_heading()
draw(40, "After +90: {}".format(mid_h))
driver.turn_angle(-90)
end_h = driver.get_heading()
draw(60, "After -90: {}".format(end_h))
draw(90, "Mid should be start+90")
draw(110, "End should be start")
pause(4)

# ═══════════════════════════════════════════════════════════════════
# Test 4 -- Reset position to (0,0,0) and verify
# ═══════════════════════════════════════════════════════════════════

clear()
draw(0, "TEST 4: reset_position()")
driver.reset_position(0, 0, 0)
x, y = driver.get_position()
h = driver.get_heading()
draw(20, "X: {}".format(x))
draw(40, "Y: {}".format(y))
draw(60, "H: {}".format(h))
draw(90, "Expected: 0, 0, 0")
pause(3)

# ═══════════════════════════════════════════════════════════════════
# Test 5 -- Square test (drift check)
# Drive 20 cm fwd, turn 90, repeat 4x.
# Final position should be close to start.
# ═══════════════════════════════════════════════════════════════════

clear()
draw(0, "TEST 5: Square drift")
driver.reset_position(0, 0, 0)
for i in range(4):
    driver.move_distance(20)
    driver.turn_angle(90)
    draw(20 + i * 15, "Leg {} done".format(i + 1))
fx, fy = driver.get_position()
fh = driver.get_heading()
draw(90, "Final: {},{}".format(fx, fy))
draw(110, "Head:  {}".format(fh))
draw(130, "Drift X:{:.1f} Y:{:.1f}".format(fx, fy))
draw(150, "Expect close to 0,0,0")
pause(4)

# ═══════════════════════════════════════════════════════════════════
# Test 6 -- Boundary & foul detection (simulated)
# ═══════════════════════════════════════════════════════════════════

clear()
draw(0, "TEST 6: Foul/boundary logic")

# Simulate being in the middle of the field
driver.reset_position(79, 109.5, 0)
draw(20, "Mid-field in bounds?: {}".format(driver.is_in_bounds()))

# Simulate near edge
driver.reset_position(1, 109.5, 0)
draw(40, "Near edge in bounds?: {}".format(driver.is_in_bounds()))

# Simulate white tape (foul box)
driver.signal_ground_colour("White")
draw(60, "White tape -> foul?: {}".format(driver.is_in_foul_area()))

# Simulate black tape (border)
driver.signal_ground_colour("Black")
draw(80, "Black tape -> foul?: {}".format(driver.is_in_foul_area()))
draw(100, "Black tape -> bord?: {}".format(driver.sees_black_tape()))

# Simulate no tape
driver.signal_ground_colour(None)
draw(120, "None tape -> foul?: {}".format(driver.is_in_foul_area()))

pause(4)

# ═══════════════════════════════════════════════════════════════════
# Test 7 -- drive_to_point to a fixed target
# ═══════════════════════════════════════════════════════════════════

clear()
draw(0, "TEST 7: drive_to_point")
driver.reset_position(0, 0, 0)
target_x = 30
target_y = 40
draw(20, "Start: 0,0")
draw(40, "Target: {},{}".format(target_x, target_y))
driver.drive_to_point(target_x, target_y)
fx, fy = driver.get_position()
draw(60, "Final: {},{}".format(fx, fy))
draw(90, "Expect close to target")
draw(110, "Error X:{:.1f} Y:{:.1f}".format(fx - target_x, fy - target_y))
pause(4)

# ═══════════════════════════════════════════════════════════════════
# Test 8 -- face_hoop
# ═══════════════════════════════════════════════════════════════════

clear()
draw(0, "TEST 8: face_hoop")
driver.reset_position(79, 109.5, 0)
# Turn away first so we can see it correct
driver.turn_angle(45)
draw(20, "Before: {}".format(driver.get_heading()))
driver.face_hoop()
draw(40, "After:  {}".format(driver.get_heading()))
draw(70, "Expect ~0 for attack")
draw(90, "Expect ~180 for defence")
pause(4)

# ═══════════════════════════════════════════════════════════════════
# Test 9 -- Signal flow (foul -> foul box -> foul over)
# ═══════════════════════════════════════════════════════════════════

clear()
draw(0, "TEST 9: Foul signal flow")

# Start normal
draw(20, "Foul active?: {}".format(driver.is_foul_active()))

# Simulate Dexter calling foul
driver.signal_in_foul_box()
draw(40, "After signal_in: {}".format(driver.is_foul_active()))

# Simulate foul timer done
driver.signal_foul_over()
draw(60, "After signal_over: {}".format(driver.is_foul_active()))

# Note: home_from_foul_box() is NOT auto-run here because
# start_foul_monitor() was not called.  This is just a unit test.

draw(90, "Expect: False, True, True")
draw(110, "(foul cleared by homing)")
pause(4)

# ═══════════════════════════════════════════════════════════════════
# All tests done
# ═══════════════════════════════════════════════════════════════════

clear()
draw(0, "ALL TESTS COMPLETE")
draw(30, "Check each screen for results.")
draw(60, "Update robot_config.py")
draw(80, "if odometry drifts.")
pause(3)
