import ev3dev.ev3 as ev3
from config import Config

ROBOT = Config()


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
    return threshold


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
    threshold = calibrate(ROBOT)

    align(ROBOT, threshold)

    with open('data.csv', 'w') as file:
        file.write("color_left, color_right, error_l, error_r, error, integral, diferential, proportional, "
                   "motorpow_l, motorpow_r \n")
        integral = 0
        kp = 8
        ki = 0
        kd = 0
        ks = 800
        color_left_value = ROBOT.color_left.value()
        color_right_value = ROBOT.color_right.value()
        error_l = threshold["left"] - color_left_value
        error_r = threshold["right"] - color_right_value
        prev_error = error_l - error_r
        while True:
            color_left_value = ROBOT.color_left.value()
            color_right_value = ROBOT.color_right.value()
            error_l = threshold["left"] - color_left_value
            error_r = threshold["right"] - color_right_value
            error = error_l - error_r
            integral = integral + error
            differential = prev_error - error
            proportional = kp * error
            integral_output = integral * ki
            differential_output = differential * kd
            base_speed = (pow(1.3, (-abs(error))))*ks
            motorpow_l = base_speed - (proportional + integral_output + differential_output)
            motorpow_r = base_speed + (proportional + integral_output + differential_output)
            file.write(
                str(color_left_value) + ", " + str(color_right_value) + ", " + str(error_l) + ", " +
                str(error_r) + ", " + str(error) + ", " + str(integral_output) + ", " + str(differential_output) + ", " +
                str(proportional) + ", " + str(motorpow_l) + ", " + str(motorpow_r) + "\n")
            if motorpow_l < 0:
                ROBOT.left_motor.polarity = ev3.LargeMotor.ENCODER_POLARITY_INVERSED
            else:
                ROBOT.left_motor.polarity = ev3.LargeMotor.ENCODER_POLARITY_NORMAL
            if motorpow_r < 0:
                ROBOT.right_motor.polarity = ev3.LargeMotor.ENCODER_POLARITY_INVERSED
            else:
                ROBOT.right_motor.polarity = ev3.LargeMotor.ENCODER_POLARITY_NORMAL
            ROBOT.right_motor.run_forever(speed_sp=abs(min(motorpow_r, 1050)))
            ROBOT.left_motor.run_forever(speed_sp=abs(min(motorpow_l, 1050)))
            prev_error = error

try:
    main()
except:
    ROBOT.right_motor.stop()
    ROBOT.left_motor.stop()
    raise
