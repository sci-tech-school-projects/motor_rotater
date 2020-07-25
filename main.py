import cv2
import numpy as np
import RPi.GPIO as GPIO
import sys, os, glob, time
from datetime import datetime


class Motor_rotater():
    cap1 = None
    cap2 = None
    base_name = ''
    path = ''
    start_time = 0
    time = 0
    head_num = 0

    def __init__(self):
        print('***** init {}'.format(self.__class__.__name__))
        self.cap1 = cv2.VideoCapture(0)
        self.cap2 = cv2.VideoCapture(2)
        self.get_file_length()
        self.create_file_name()
        self.make_dir()

    def get_file_length(self):
        folders = glob.glob('imgs/*')
        length = len(folders)
        self.head_num = str('{:0=4}'.format(length))
        # print(self.head_num)
        # print(type(self.head_num))
        # sys.exit()

    def create_file_name(self):
        print('***** args   [1]:shape [2]:color [3]:X [4]:Y [5]:Z ')
        base_name = ''
        for i in range(1, 6):
            try:
                base_name = base_name + '_' + sys.argv[i]
            except IndexError:
                print('***** input correct arguments')
                sys.exit()
        self.base_name = base_name

    def make_dir(self):
        dir_name = self.head_num + '_' + self.base_name
        self.path = os.path.join('imgs', dir_name)
        if not os.path.exists(self.path):
            self.path = self.path + '_'
            print("***** your face is to be saved here {} ".format(self.base_name))
            os.mkdir(self.path)

    def main(self):
        counter = 0
        start_time = datetime.now()
        time = 0
        dc_motor = Dc_motor()
        dc_motor.rotate('start')
        while time <= 10:
            frame = None
            if counter % 2 == 0:
                ret, frame = self.cap1.read()
            else:
                ret, frame = self.cap2.read()

            frame = self.resize_img(frame)

            cv2.imshow('frame', frame)
            self._save_img(frame, counter)
            if cv2.waitKey(1) & 0xff == ord("q"):
                break

            counter += 1
            time = self._timer(start_time)

        dc_motor.rotate('stop')

    def resize_img(self, frame):
        shape = np.shape(frame)
        h, w, c = shape

        start_x = int(w / 5)
        start_y = int(h / 5)
        end_x = int(w / 5) * 4
        end_y = int(h / 5) * 4

        frame = frame[start_y:end_y, start_x:end_x, ::]

        return frame

    def _save_img(self, frame, counter):
        num = '{:0=4}'.format(counter)
        _path_file = os.path.join(self.path, self.base_name)
        path_file = _path_file + '_' + num + '.jpg'
        print(path_file)
        cv2.imwrite(path_file, frame)

    def _timer(self, start_time):
        time = datetime.now() - start_time
        time = time.seconds
        return time


class Dc_motor():
    enA = 26
    in1 = 19
    in2 = 13
    led = 15

    key = None

    def __init__(self):
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
    motor_rotater = Motor_rotater()
    motor_rotater.main()
