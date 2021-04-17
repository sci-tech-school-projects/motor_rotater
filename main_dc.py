import cv2
import numpy as np
import sys, os, glob, time
from datetime import datetime
from dc_motor import Dc_motor

class Motor_rotater():
    # cam_indexs = [0, 2, 4]
    cam_indexs = [0, 2, 4]
    base_name = ''
    path = ''
    head_num = 0
    rotate_speed = 50

    # limit_time = 180

    def __init__(self):
        print('***** init {}'.format(self.__class__.__name__))

        self.Get_File_Length()
        self.Create_file_Name()
        self.Make_Dir()

    def Get_File_Length(self):
        folders = glob.glob('imgs/*_')
        length = len(folders)
        self.head_num = str('{:0=4}'.format(length))

    def Create_file_Name(self):
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

    def Make_Dir(self):
        # dir_name = self.head_num + '__' + self.base_name
        dir_name = self.base_name
        self.path = os.path.join('imgs', dir_name)
        if not os.path.exists(self.path):
            self.path = self.path + '_'
            print("***** Init path {} ".format(self.base_name))
            os.mkdir(self.path)

    def Show_Contour_Image(self, img, contour):
        x, y, w, h = cv2.boundingRect(contour)
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 3)
        cv2.imshow('x y w h {} {} {} {}'.format(x, y, w, h), img)
        if cv2.waitKey(0) % 256 == ord('q'):
            pass

    def Main(self, brightness):
        file_name_counter = 0
        imgs_from_each_cam = 500
        imgs_to_create = imgs_from_each_cam * len(self.cam_indexs)
        imgs_total = 0

        dc_motor = Dc_motor(self.rotate_speed)
        dc_motor.rotate('start')

        while imgs_total <= imgs_to_create:
            if imgs_total % imgs_from_each_cam == 0:
                i = imgs_total // imgs_from_each_cam
                if i >= 1:
                    cap.release()
                    file_name_counter = 0
                try:
                    cap = cv2.VideoCapture(self.cam_indexs[i])
                except IndexError:
                    break

            ret, frame = cap.read()
            if ret:
                if self.cam_indexs[i] in [2, 4]:
                    frame = self.trim_img(frame, self.cam_indexs[i])
                frame = self.adjust(frame, brightness, 0.0)
                # cv2.imshow('frame', frame)
                # if cv2.waitKey(1) % 256 == ord('q'):
                #     pass
                self.save_img(frame, file_name_counter, self.cam_indexs[i])
                file_name_counter += 1
                imgs_total += 1

            else:
                break

        dc_motor.rotate('stop')
        cap.release()
        cv2.destroyAllWindows()

    def trim_img(self, frame, cam_index):
        def get_trimmed_frame(frame, h, w):
            if cam_index == 0:
                x = 0
                y = 0
                X = w
                Y = h
            elif cam_index == 2:
                x = 0
                y = 0
                X = w
                Y = h
            elif cam_index == 4:
                x = 0
                y = 0
                X = w
                Y = h
            else:
                print("trim size could not be set error occured. sys.exit()")
                sys.exit()
            frame = frame[y:Y, x:X]
            return frame

        h, w, c = np.shape(frame)
        frame = get_trimmed_frame(frame, h, w)
        h, w, c = np.shape(frame)

        trim_rate = 5
        start_x = int(w / trim_rate)
        start_y = int(h / trim_rate)
        end_x = w
        end_y = h
        return frame[start_y:end_y, start_x:end_x, ::]

    def save_img(self, frame, file_name_counter, cam_index):
        num = '{}{:0=3}'.format(cam_index, file_name_counter)
        _path_file = os.path.join(self.path, self.base_name)
        path_file = _path_file + '_' + num + '.jpg'
        print(path_file)
        cv2.imwrite(path_file, frame)

    def adjust(self, img, alpha=1.0, beta=0.0):
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
    motor_rotater.Main(brightness)
