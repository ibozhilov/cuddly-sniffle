import ev3dev.ev3 as ev3


class Config:
    def __init__(self):
        self.right_motor = ev3.LargeMotor('outC')
        self.left_motor = ev3.LargeMotor('outB')
        self.right_motor.polarity = ev3.LargeMotor.ENCODER_POLARITY_NORMAL
        self.left_motor.polarity = ev3.LargeMotor.ENCODER_POLARITY_NORMAL
        self.color_left = ev3.ColorSensor('in1')
        self.color_right = ev3.ColorSensor('in2')
        assert self.color_left.connected, "Connect a color sensor to port 1."
        assert self.color_right.connected, "Connect a color sensor to port 2."
        self.color_left.mode = 'COL-REFLECT'
        self.color_right.mode = 'COL-REFLECT'
