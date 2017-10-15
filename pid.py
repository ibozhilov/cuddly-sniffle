#!/usr/bin/env python3
import ev3dev.ev3 as ev3

right = ev3.LargeMotor('outC')
left = ev3.LargeMotor('outB')
right.polarity = ev3.LargeMotor.ENCODER_POLARITY_NORMAL
left.polarity = ev3.LargeMotor.ENCODER_POLARITY_NORMAL
colorL = ev3.ColorSensor('in1')
colorR = ev3.ColorSensor('in2')
assert colorL.connected, "Connect a color sensor to port 1."
assert colorR.connected, "Connect a color sensor to port 2."
colorL.mode = 'COL-REFLECT'
colorR.mode = 'COL-REFLECT'


def main():
    integral = 0
    prev_error = 0
    lowest_l = 100
    highest_l = 0
    lowest_r = 100
    highest_r = 0

    right.run_forever(speed_sp=50)
    previous_r = colorR.value()
    integrations = 0
    while True:
        current_r = colorR.value()
        current_l = colorL.value()
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
        if current_r / previous_r > 1.05 and integrations >= 1:
            right.stop()
            break
        previous_r = current_r
        integrations += 1

    print(lowest_l, lowest_r, highest_l, highest_r, integrations)
    thr_l = (lowest_l + highest_l) / 2
    thr_r = (lowest_l + highest_l) / 2
    right.polarity = ev3.LargeMotor.ENCODER_POLARITY_INVERSED
    right.run_forever(speed_sp=50)
    left.run_forever(speed_sp=50)

    while True:
        current_l = colorL.value()
        if thr_l * 0.95 <= current_l <= thr_l * 1.05:
            print(current_l, thr_l)
            right.polarity = ev3.LargeMotor.ENCODER_POLARITY_NORMAL
            right.stop()
            left.stop()
            break

    while True:
        kp = 8
        ki = 0
        kd = 10
        ks = 1050
        error_l = thr_l - colorL.value()
        error_r = thr_r - colorR.value()
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
            left.polarity = ev3.LargeMotor.ENCODER_POLARITY_INVERSED
        else:
            left.polarity = ev3.LargeMotor.ENCODER_POLARITY_NORMAL
        if motorpow_r < 0:
            right.polarity = ev3.LargeMotor.ENCODER_POLARITY_INVERSED
        else:
            right.polarity = ev3.LargeMotor.ENCODER_POLARITY_NORMAL
        right.run_forever(speed_sp=abs(motorpow_r))
        left.run_forever(speed_sp=abs(motorpow_l))
        prev_error = error

try:
    main()
except:
    right.stop()
    left.stop()
    raise
