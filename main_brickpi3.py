import threading
import cv2
import numpy as np
import sys, os, glob, time
from datetime import datetime
from Brickpi3_Motors import Brickpi3_Motors
import logging

logger = logging.getLogger('LoggingTest')
logger.setLevel(20)
sh = logging.StreamHandler()
logger.addHandler(sh)


class Motor_rotater():
    cam_indexs = [0, 2]
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

    # def Run_Thread(self, cam_index):
    #     BM = Brickpi3_Motors()
    #     thread = threading.Thread(target=BM.Main, args=(cam_index,))
    #     thread.start()
    #     print('***** Run_Thread cam_index {} starts'.format(cam_index))
    #     return BM, thread
    #
    # def Join_Thread(self, BM, thread, cam_index):
    #     del BM
    #     thread.join()
    #     print('***** Run_Thread cam_index {} joined'.format(cam_index))

    def Main(self):
        file_name_counter = 0
        imgs_from_each_cam = 20
        imgs_to_create = imgs_from_each_cam * len(self.cam_indexs)
        imgs_total = 0

        BMs = [Brickpi3_Motors() for i in range(len(self.cam_indexs))]
        logger.log(20, '***** len BMs {} cam_indexs {}'.format(len(BMs), len(self.cam_indexs)))
        BMs[0].Main(self.cam_indexs[0])

        cap = cv2.VideoCapture(self.cam_indexs[0])
        print('***** cv2.VideoCapture initialized ')

        while imgs_total <= imgs_to_create:
            if imgs_total % imgs_from_each_cam == 0:
                i = imgs_total // imgs_from_each_cam
                if i % 10 == 0:
                    logger.log(20, "***** loop {}".format(i))

                if i == 0:
                    pass
                elif 1 <= i < len(self.cam_indexs):
                    logger.log(20, "***** i = {}".format(i))
                    BMs[i - 1].__del__()
                    time.sleep(3)
                    BMs[i].Run_Main_Thread(self.cam_indexs[i])
                    cap.release()
                    cap = cv2.VideoCapture(self.cam_indexs[i])
                    file_name_counter = 0
                else:
                    i = i - 1
                    break

            ret, frame = cap.read()
            cv2.imshow("cap ", frame)
            if cv2.waitKey(1) % 256 == ord('q'):
                break

            if ret and i < len(self.cam_indexs):
                # if self.cam_indexs[i] in [2, 4]:
                #     frame = self.trim_img(frame, self.cam_indexs[i])
                # frame = self.adjust(frame, brightness, 0.0)
                # cv2.imshow('frame', frame)
                # if cv2.waitKey(1) % 256 == ord('q'):
                #     pass
                self.save_img(frame, file_name_counter, self.cam_indexs[i])
                file_name_counter += 1
                imgs_total += 1
            else:
                break

        BMs[i].__del__()
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
    motor_rotater = Motor_rotater()
    motor_rotater.Main()
