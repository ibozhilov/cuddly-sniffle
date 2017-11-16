#!/usr/bin/python3
import ev3dev.ev3 as ev3
from config import Config
import time

ROBOT = Config()
ROBOT.right_motor.run_forever(speed_sp=500)
ROBOT.left_motor.run_forever(speed_sp=500)
time.sleep(5)
ROBOT.right_motor.stop()
ROBOT.left_motor.stop()