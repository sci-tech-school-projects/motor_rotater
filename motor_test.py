import cv2
import numpy as np
import RPi.GPIO as GPIO
import sys, os, glob, time


class Dc_motor():
    enA = 26
    in1 = 19
    in2 = 13

    key = None

    def __init__(self):
        print('***** init {}'.format(self.__class__.__name__))

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.in1, GPIO.OUT)
        GPIO.setup(self.in2, GPIO.OUT)
        GPIO.setup(self.enA, GPIO.OUT)

        GPIO.output(self.in1, GPIO.LOW)
        GPIO.output(self.in2, GPIO.LOW)
        self.p = GPIO.PWM(self.enA, 100)
        self.p.start(100)

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
    dc_motor = Dc_motor()
    dc_motor.rotate('start')
    time.sleep(100)
    dc_motor.rotate('stop')
