import RPi.GPIO as GPIO
import os, sys, glob, re, shutil, time


class Dc_motor():
    enA = 26
    in1 = 19
    in2 = 13
    led = 15

    key = None

    def __init__(self, speed=50):
        print('***** init {}'.format(self.__class__.__name__))

        GPIO.setmode(GPIO.BCM)

        GPIO.setup(self.in1, GPIO.OUT)
        GPIO.setup(self.in2, GPIO.OUT)
        GPIO.setup(self.enA, GPIO.OUT)
        GPIO.setup(self.led, GPIO.OUT)

        GPIO.output(self.in1, GPIO.LOW)
        GPIO.output(self.in2, GPIO.LOW)
        GPIO.output(self.led, GPIO.HIGH)
        self.p = GPIO.PWM(self.enA, 100)
        self.p.start(speed)

    def rotate(self, key=None):

        if key == 'start':
            print("rotate")
            GPIO.output(self.in1, GPIO.HIGH)
            GPIO.output(self.in2, GPIO.LOW)

        elif key == 'stop':
            print("stop")
            GPIO.output(self.in1, GPIO.LOW)
            GPIO.output(self.in2, GPIO.LOW)
            self.release_gpio()

    def release_gpio(self):
        GPIO.cleanup()


if __name__ == '__main__':
    speed = 50
    try:
        speed = int(sys.argv[1])
    except IndexError:
        pass

    dc_motor = Dc_motor(speed)
    dc_motor.rotate('start')
    time.sleep(100)
    dc_motor.rotate('stop')
