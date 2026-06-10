#!/usr/bin/env pybricks-micropython

'''
╔══════════════════════════════════════════════════════════════════════════╗
║                T E S T _ M O V E M E N T . P Y                   ║
║   Manual test suite for movement.py.  Run on the EV3 brick.      ║
╚══════════════════════════════════════════════════════════════════╝
'''

from math import pi
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor, ColorSensor
from pybricks.parameters import Port, Direction
from pybricks.tools import wait

from movement import Driver

# ═══════════════════════════════════════════════════════════════════
# Setup
# ═══════════════════════════════════════════════════════════════════

ev3 = EV3Brick()

left_motor = Motor(Port.B, positive_direction=Direction.CLOCKWISE)
right_motor = Motor(Port.C, positive_direction=Direction.CLOCKWISE)
colour_sensor = ColorSensor(Port.S4)

driver = Driver(ev3, left_motor, right_motor, colour_sensor, team="ATTACK")

# Helper functions

def show(lines, hold=4):
    ev3.screen.clear()
    for line in lines:
        ev3.screen.print(line)
    wait(hold * 1000)


# ═══════════════════════════════════════════════════════════════════
# Test 1 -- Initial position dump
# ═══════════════════════════════════════════════════════════════════

x, y = driver.get_position()
h = driver.get_heading()
show([
    "TEST 1: Start pose",
    "X: {}".format(x),
    "Y: {}".format(y),
    "H: {}".format(h),
    "Expected: ATTACK ~79,199,0",
])

# ═══════════════════════════════════════════════════════════════════
# Test 2 -- Move forward 30 cm
# ═══════════════════════════════════════════════════════════════════

start_x, start_y = driver.get_position()
driver.move_distance(30)
end_x, end_y = driver.get_position()
show([
    "TEST 2: Drive 30 cm",
    "Start: {},{}".format(start_x, start_y),
    "End:   {},{}".format(end_x, end_y),
    "Delta Y: {}".format(end_y - start_y),
    "Expected ~-30 (attack) or ~+30 (defence)",
])

# ═══════════════════════════════════════════════════════════════════
# Test 3 -- Spin 90 degrees clockwise and back
# ═══════════════════════════════════════════════════════════════════

start_heading = driver.get_heading()
driver.spin_angle(pi / 2)
mid_heading = driver.get_heading()
driver.spin_angle(-pi / 2)
end_heading = driver.get_heading()
show([
    "TEST 3: Spin 90 deg",
    "Start: {}".format(start_heading),
    "After +90: {}".format(mid_heading),
    "After -90: {}".format(end_heading),
])

# ═══════════════════════════════════════════════════════════════════
# Test 4 -- Reset pose
# ═══════════════════════════════════════════════════════════════════

driver.reset_position(0, 0, 0)
x, y = driver.get_position()
h = driver.get_heading()
show([
    "TEST 4: Reset pose",
    "X: {}".format(x),
    "Y: {}".format(y),
    "H: {}".format(h),
    "Expected: 0,0,0",
])

# ═══════════════════════════════════════════════════════════════════
# Test 5 -- Square drift check
# ═══════════════════════════════════════════════════════════════════

driver.reset_position(0, 0, 0)
for _ in range(4):
    driver.move_distance(20)
    driver.spin_angle(pi / 2)
fx, fy = driver.get_position()
fh = driver.get_heading()
show([
    "TEST 5: Square drift",
    "Final: {},{}".format(fx, fy),
    "Heading: {}".format(fh),
    "Drift X: {:.1f}".format(fx),
    "Drift Y: {:.1f}".format(fy),
])

# ═══════════════════════════════════════════════════════════════════
# Test 6 -- drive_to_point
# ═══════════════════════════════════════════════════════════════════

driver.reset_position(0, 0, 0)
target_x = 30
target_y = 40
driver.drive_to_point(target_x, target_y)
fx, fy = driver.get_position()
show([
    "TEST 6: drive_to_point",
    "Target: {},{}".format(target_x, target_y),
    "Final: {},{}".format(fx, fy),
    "Error X: {:.1f}".format(fx - target_x),
    "Error Y: {:.1f}".format(fy - target_y),
])

# ═══════════════════════════════════════════════════════════════════
# Test 7 -- reverse_drive_to_point
# ═══════════════════════════════════════════════════════════

driver.reset_position(0, 0, 0)
target_x = -20
target_y = 0
driver.reverse_drive_to_point(target_x, target_y)
fx, fy = driver.get_position()
show([
    "TEST 7: reverse_drive_to_point",
    "Target: {},{}".format(target_x, target_y),
    "Final: {},{}".format(fx, fy),
])

# ═══════════════════════════════════════════════════════════════════
# Test 8 -- face_hoop
# ═══════════════════════════════════════════════════════════

driver.reset_position(79, 199, pi)
pre_heading = driver.get_heading()
driver.face_hoop()
post_heading = driver.get_heading()
show([
    "TEST 8: face_hoop",
    "Before: {}".format(pre_heading),
    "After: {}".format(post_heading),
    "Heading aimed at hoop.",
])

# ═══════════════════════════════════════════════════════════════════
# Test 9 -- field and boundary checks
# ═══════════════════════════════════════════════════════════

driver.reset_position(79, 109.5, 0)
show([
    "TEST 9: Boundaries",
    "In bounds?: {}".format(driver.is_in_bounds()),
    "Foul area?: {}".format(driver.is_in_foul_area()),
])

# ═══════════════════════════════════════════════════════════════════
# Completed
# ═══════════════════════════════════════════════════════════════════

show([
    "ALL TESTS COMPLETE",
    "Review results on EV3 screen.",
])
