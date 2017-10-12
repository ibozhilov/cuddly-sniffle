import ev3dev.ev3 as ev3
import time

right = ev3.LargeMotor('outC')
left = ev3.LargeMotor('outB')
colorL = ev3.ColorSensor('in1')
colorR = ev3.ColorSensor('in2')
lowestL = 100
highestL = 0
lowestR = 100
highestR = 0
inLine = False

assert colorL.connected, "Connect a color sensor to port 1."
assert colorR.connected, "Connect a color sensor to port 2."
colorL.mode = 'COL-REFLECT'
colorR.mode = 'COL-REFLECT'


right.run_forever(speed_sp=500)
previousR = colorR.value()
while True:
    currentR = colorR.value()
    currentL = colorL.value()
    print(currentR, currentL)
    if currentL >= highestL:
        highestL = currentL
    elif currentL <= lowestL:
        lowestL = currentL
    if currentR >= highestR:
        highestR = currentR
    elif currentR <= lowestR:
        lowestR = currentR
    if currentR / previousR > 1.05:
        break
    previousR = currentR

print(lowestL, lowestR, highestL, highestR)

time.sleep(5)
