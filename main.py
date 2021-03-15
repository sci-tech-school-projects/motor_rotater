import cv2
import numpy as np
import sys, os, glob, time
from datetime import datetime
from dc_motor import Dc_motor


class Motor_rotater():
    cap1 = None
    cap2 = None
    base_name = ''
    path = ''
    start_time = 0
    time = 0
    head_num = 0
    rotate_speed = 50
    limit_time = 180

    def __init__(self):
        print('***** init {}'.format(self.__class__.__name__))
        self.cap1 = cv2.VideoCapture(0)

        self.get_file_length()
        self.create_file_name()
        self.make_dir()

    def get_file_length(self):
        folders = glob.glob('imgs/*_')
        length = len(folders)
        self.head_num = str('{:0=4}'.format(length))

    def create_file_name(self):
        print('***** args   [1]:color [2]:shape [3]:X [4]:Y [5]:Z ')
        base_name = ''
        for i in range(1, 6):
            try:
                if i == 1:
                    base_name = sys.argv[i]
                else:
                    base_name = base_name + '__' + sys.argv[i]
            except IndexError:
                print('***** input correct arguments')
                sys.exit()
        self.base_name = self.head_num + '__' + base_name

    def make_dir(self):
        # dir_name = self.head_num + '__' + self.base_name
        dir_name = self.base_name
        self.path = os.path.join('imgs', dir_name)
        if not os.path.exists(self.path):
            self.path = self.path + '_'
            print("***** images to be saved here {} ".format(self.base_name))
            os.mkdir(self.path)

    def main(self, brightness):
        file_name_counter = 0
        start_time = datetime.now()
        current_time = 0
        dc_motor = Dc_motor(self.rotate_speed)
        dc_motor.rotate('start')
        active_cam = None

        while current_time <= self.limit_time:
            if current_time <= self.limit_time / 2:
                active_cam = 'cap1'
                ret, frame = self.cap1.read()
            else:
                if active_cam == 'cap1':
                    active_cam = 'cap2'
                    file_name_counter = 0
                    self.cap1.release()
                    try:
                        self.cap2 = cv2.VideoCapture(2)
                    except Exception:
                        sys.exit()
                ret, frame = self.cap2.read()

            if ret:
                frame = self._trim_img(frame)
                frame = self._adjust(frame, brightness, 0.0)

                # cv2.imshow('frame', frame)
                self._save_img(frame, file_name_counter, active_cam)
                file_name_counter += 1
                current_time = self._timer(start_time)

                if cv2.waitKey(1) & 0xff == ord("q"):
                    break
            else:
                break

        dc_motor.rotate('stop')
        self.cap2.release()
        cv2.destroyAllWindows()

    def _trim_img(self, frame):
        shape = np.shape(frame)
        h, w, c = shape
        trim_rate = 5

        start_x = int(w / trim_rate)
        start_y = int(h / trim_rate)
        end_x = w
        end_y = h

        return frame[start_y:end_y, start_x:end_x, ::]

    def _save_img(self, frame, file_name_counter, active_cam):
        num = None
        if active_cam == 'cap1':
            num = '{:0=4}'.format(file_name_counter)
        elif active_cam == 'cap2':
            num = '2{:0=3}'.format(file_name_counter)
        _path_file = os.path.join(self.path, self.base_name)
        path_file = _path_file + '_' + num + '.jpg'
        print(path_file)
        cv2.imwrite(path_file, frame)

    def _timer(self, start_time):
        time = datetime.now() - start_time
        time = time.seconds
        return time

    def _adjust(self, img, alpha=1.0, beta=0.0):

        # 積和演算を行う。
        dst = alpha * img + beta
        # [0, 255] でクリップし、uint8 型にする。
        return np.clip(dst, 0, 255).astype(np.uint8)


if __name__ == '__main__':
    try:
        brightness = float(sys.argv[6])
    except:
        brightness = 1.2
    motor_rotater = Motor_rotater()
    motor_rotater.main(brightness)
