#!/usr/bin/python3
import ev3dev.ev3 as ev3
from config import Config
import time

ROBOT = Config()

def sign(x):
    return ((x>0)-(x<0))

def calibrate(robot):
    robot.right_motor.run_forever(speed_sp=50)
    previous_r = 100
    lowest_l = 100
    highest_l = 0
    lowest_r = 100
    highest_r = 0

    while True:
        current_r = robot.color_right.value()
        current_l = robot.color_left.value()
        if current_l >= highest_l:
            highest_l = current_l
        elif current_l <= lowest_l:
            lowest_l = current_l
        if current_r >= highest_r:
            highest_r = current_r
        elif current_r <= lowest_r:
            lowest_r = current_r
        if current_r / previous_r > 1.05:
            robot.right_motor.stop()
            break
        previous_r = current_r

    threshold = {"left": (lowest_l + highest_l * 1.3) / 2, "right": (lowest_l + highest_l * 1.3) / 2}
    return threshold, lowest_l, highest_l, lowest_r, highest_r


def align(ROBOT, thershold):
    ROBOT.right_motor.polarity = ev3.LargeMotor.ENCODER_POLARITY_INVERSED
    ROBOT.right_motor.run_forever(speed_sp=50)
    ROBOT.left_motor.run_forever(speed_sp=50)

    while True:
        current_l = ROBOT.color_left.value()
        if thershold["left"] * 0.95 <= current_l <= thershold["left"] * 1.05:
            print(current_l, thershold["left"])
            ROBOT.right_motor.polarity = ev3.LargeMotor.ENCODER_POLARITY_NORMAL
            ROBOT.right_motor.stop()
            ROBOT.left_motor.stop()
            break


def main():
    threshold, lowest_l, highest_l, lowest_r, highest_r = calibrate(ROBOT)
    align(ROBOT, threshold)
    lowest_err_left = threshold["left"] - highest_l
    highest_err_left = threshold["left"] - lowest_l
    lowest_err_right = threshold["right"] - highest_r
    highest_err_right = threshold["right"] - lowest_r
    with open('data.csv', 'w') as file:
        file.write("error_l, error_r, error, "
                   "motorpow_l, motorpow_r, time_start, time_end \n")
        integral = 0
        kp = 0.85
        ki = 0
        kd = 0.3
        power = 400
        color_left_value = ROBOT.color_left.value()
        color_right_value = ROBOT.color_right.value()
        error_l = threshold["left"] - color_left_value
        error_r = threshold["right"] - color_right_value
        prev_error = error_l - error_r
        while True:
            time_start = time.clock()
            color_left_value = ROBOT.color_left.value()
            color_right_value = ROBOT.color_right.value()
            error_l = threshold["left"] - color_left_value
            error_l = (error_l-lowest_err_left)/(highest_err_left-lowest_err_left)
            error_r = threshold["right"] - color_right_value
            error_r = (error_r-lowest_err_right)/(highest_err_right-lowest_err_right)
            error = error_l - error_r
            integral = integral + error
            differential = prev_error - error
            proportional = kp * error
            integral_output = integral * ki
            differential_output = differential * kd
            output = proportional + integral_output + differential_output
            motorpow_r = (((1+sign(error))/2) + (((1-sign(error))/2)*(output)) + (1-abs(sign(error)))/2)*power
            motorpow_l = (((1+sign(-error))/2) + (((1-sign(-error))/2)*(output)) + (1-abs(sign(error)))/2)*power
            print (prev_error, error, motorpow_l, motorpow_r)
            if motorpow_l < 0:
                ROBOT.left_motor.polarity = ev3.LargeMotor.ENCODER_POLARITY_INVERSED
            else:
                ROBOT.left_motor.polarity = ev3.LargeMotor.ENCODER_POLARITY_NORMAL
            if motorpow_r < 0:
                ROBOT.right_motor.polarity = ev3.LargeMotor.ENCODER_POLARITY_INVERSED
            else:
                ROBOT.right_motor.polarity = ev3.LargeMotor.ENCODER_POLARITY_NORMAL
            ROBOT.right_motor.run_forever(speed_sp=abs(motorpow_r))
            ROBOT.left_motor.run_forever(speed_sp=abs(motorpow_l))
            prev_error = error
            time_end = time.clock()
            if time_end-time_start <= 0.0125:
                time.sleep(0.0125 - (time_end - time_start))
            
            #file.write(
            #    str(error_l) + ", " + str(error_r) + ", " + str(error) + ", "  + 
            #    str(motorpow_l) + ", " + str(motorpow_r) +  ", " + str(time_start) + ", " + str(time_end) + ", " +  str(time_end-time_start) + "\n")

try:
    main()
except:
    ROBOT.right_motor.stop()
    ROBOT.left_motor.stop()
    raise
