#!/usr/bin/env python3
import ev3dev.ev3 as ev3
from config import Config


def calibrate(robot):
    robot.right_motor.run_forever(speed_sp=50)
    previous_r = robot.color_right.value()
    lowest_l = 100
    highest_l = 0
    lowest_r = 100
    highest_r = 0

    while True:
        current_r = robot.color_right.value()
        current_l = robot.color_left.value()
        if current_l >= highest_l:
            highest_l = current_l
            print(current_l, "left")
        elif current_l <= lowest_l:
            lowest_l = current_l
        if current_r >= highest_r:
            highest_r = current_r
            print(current_r, "right")
        elif current_r <= lowest_r:
            lowest_r = current_r
        if current_r / previous_r > 1.05:
            robot.right_motor.stop()
            break
        previous_r = current_r

    print(lowest_l, lowest_r, highest_l, highest_r, integrations)
    threshold = {"left": (lowest_l + highest_l) / 2, "right": (lowest_l + highest_l) / 2}
    return threshold


def align(robot, thershold):
    robot.right_motor.polarity = ev3.LargeMotor.ENCODER_POLARITY_INVERSED
    robot.right_motor.run_forever(speed_sp=50)
    robot.left_motor.run_forever(speed_sp=50)

    while True:
        current_l = robot.color_left.value()
        if thershold["left"] * 0.95 <= current_l <= thershold["left"] * 1.05:
            print(current_l, thershold["left"])
            robot.right_motor.polarity = ev3.LargeMotor.ENCODER_POLARITY_NORMAL
            robot.right_motor.stop()
            robot.left_motor.stop()
            break


def main():
    robot = Config()
    threshold = calibrate(robot)

    align(robot, threshold)

    while True:
        kp = 8
        ki = 0
        kd = 10
        ks = 1050
        error_l = threshold["left"] - robot.color_left.value()
        error_r = threshold["right"] - robot.color_right.value()
        error = error_l - error_r
        integral = integral + error
        differential = prev_error - error
        proportional = kp * error
        integral_output = integral * ki
        differential_output = differential * kd
        base_speed = (pow(1.2, (-abs(error))))*ks
        motorpow_l = base_speed - (proportional + integral_output + differential_output)
        motorpow_r = base_speed + proportional + integral_output + differential_output
        if motorpow_l < 0:
            robot.left_motor.polarity = ev3.LargeMotor.ENCODER_POLARITY_INVERSED
        else:
            robot.left_motor.polarity = ev3.LargeMotor.ENCODER_POLARITY_NORMAL
        if motorpow_r < 0:
            robot.right_motor.polarity = ev3.LargeMotor.ENCODER_POLARITY_INVERSED
        else:
            robot.right_motor.polarity = ev3.LargeMotor.ENCODER_POLARITY_NORMAL
        robot.right_motor.run_forever(speed_sp=abs(motorpow_r))
        robot.left_motor.run_forever(speed_sp=abs(motorpow_l))
        prev_error = error

try:
    main()
except:
    robot.stop()
    left.stop()
    raise
