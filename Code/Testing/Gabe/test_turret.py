#!/usr/bin/env pybricks-micropython

'''
╔══════════════════════════════════════════════════════════════════╗
║               T E S T   --   T U R R E T                         ║
║  Quick standalone script to check motors + home switch.          ║
╚══════════════════════════════════════════════════════════════════╝

Controls:
  UP    -- spin turret left
  DOWN  -- spin turret right
  LEFT  -- run shooter motor (flick test)
  CENTER-- stop everything
  RIGHT -- try to find home switch
'''

from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor, TouchSensor
from pybricks.parameters import Port, Button, Stop
from pybricks.tools import wait
import time

ev3 = EV3Brick()

# adjust these ports to whatever the build uses
turret_motor  = Motor(Port.A)
shooter_motor = Motor(Port.B)
home_switch   = TouchSensor(Port.S3)

ev3.screen.print("TURRET TEST")
ev3.speaker.beep()

while True:
    btns = ev3.buttons.pressed()

    if Button.UP in btns:
        turret_motor.run(120)
        ev3.screen.print("Turret LEFT")

    elif Button.DOWN in btns:
        turret_motor.run(-120)
        ev3.screen.print("Turret RIGHT")

    elif Button.LEFT in btns:
        ev3.screen.print("SHOOT!")
        shooter_motor.run(900)
        time.sleep(0.4)
        shooter_motor.stop(Stop.BRAKE)

    elif Button.RIGHT in btns:
        # home-seek routine test
        ev3.screen.print("Homing...")
        turret_motor.run(80)
        while not home_switch.pressed:   # typo: missing ()
            wait(20)
        turret_motor.stop(Stop.BRAKE)
        turret_motor.reset_angle(0)
        ev3.screen.print("Homed")
        time.sleep(0.5)

    elif Button.CENTER in btns:
        turret_motor.stop(Stop.BRAKE)
        shooter_motor.stop(Stop.BRAKE)
        ev3.screen.print("STOP")

    wait(20)
