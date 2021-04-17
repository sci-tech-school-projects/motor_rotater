import cv2
import numpy as np
import os, sys, math, glob, re, shutil, math
import logging
from argparse import ArgumentParser
from dc_motor import Dc_motor

logger = logging.getLogger('LoggingTest')
logger.setLevel(20)
sh = logging.StreamHandler()
logger.addHandler(sh)


class Camera_Test():
    """
    best tuning
    top : 1.2 0.0
    btm : 1.2 0.0
    """
    index = None
    run = True

    alpha = None
    beta = None
    thresh_up = None
    thresh_low = None
    is_test = False

    def Init(self):
        ap = ArgumentParser()
        ap.add_argument('index', default=0, help='camera index')
        ap.add_argument('-a', '--alpha', default=1.0, type=float)
        ap.add_argument('-b', '--beta', default=0.0, type=float)
        ap.add_argument('-l', '--thresh_lower', default=75, type=int)
        ap.add_argument('-u', '--thresh_upper', default=255, type=int)

        args = ap.parse_args()
        self.alpha = args.alpha
        self.beta = args.beta
        self.thresh_low = args.thresh_lower
        self.thresh_up = args.thresh_upper
        self.args = args

        print()

        dc_motor = Dc_motor(50)
        dc_motor.rotate('start')

    @property
    def alpha_val(self):
        return self.alpha

    @alpha_val.setter
    def alpha_val(self, val):
        self.alpha = val

    @property
    def beta_val(self):
        return self.beta

    @beta_val.setter
    def beta_val(self, val):
        self.beta = val

    @property
    def thresh_lower_val(self):
        return self.thresh_low

    @thresh_lower_val.setter
    def thresh_lower_val(self, val):
        self.thresh_low = val

    @property
    def thresh_upper_val(self):
        return self.thresh_up

    @thresh_upper_val.setter
    def thresh_upper_val(self, val):
        self.thresh_up = val

    @property
    def is_test_bool(self):
        return self.is_test

    @is_test_bool.setter
    def is_test_bool(self, bool):
        self.is_test = bool

    def Main(self, ):
        self.index = int(self.args.index)
        cap = cv2.VideoCapture(self.index)
        while self.run:
            ret, frame = cap.read()
            if ret:
                self.Image_Process(frame)
        cap.release()
        cv2.destroyAllWindows()

    def Image_Process(self, frame):
        h, w, c = np.shape(frame)
        # frame = self.Trim_Img(frame)

        [x, y, w, h], frame, gray, thresh = self.Find_Contour(frame, self.index)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 3)

        if self.is_test:
            frame = self._Concat_Imgs(frame, gray, thresh)
            # gray, thresh = self.Show_Gray_Thresh(gray, thresh)
            # cv2.imshow('gray_thresh', gray_thresh)

        cv2.imshow('h w c : {} '.format(np.shape(frame)), frame)
        self.Bright_Control()

    def Bright_Control(self):
        val = 0
        if cv2.waitKey(val) % 256 == ord('d'):
            self.alpha += 0.1
        elif cv2.waitKey(val) % 256 == ord('a'):
            self.alpha -= 0.1
        elif cv2.waitKey(val) % 256 == ord('w'):
            self.beta += 0.1
        elif cv2.waitKey(val) % 256 == ord('s'):
            self.beta -= 0.1
        elif cv2.waitKey(val) % 256 == ord('t'):
            self.thresh_up += 10
        elif cv2.waitKey(val) % 256 == ord('g'):
            self.thresh_up -= 10
        elif cv2.waitKey(val) % 256 == ord('h'):
            self.thresh_low += 10
        elif cv2.waitKey(val) % 256 == ord('f'):
            self.thresh_low -= 10
        elif cv2.waitKey(val) & 0xFF == ord('q'):
            self.run = False
        elif cv2.waitKey(val) & 0xFF == ord('z'):
            pass

        self.alpha = math.ceil(self.alpha * 10) / 10
        self.beta = math.ceil(self.beta * 10) / 10

    def Find_Contour(self, frame, cam_index):
        frame = self.Adjust_Alpha_Beta(frame, self.alpha, self.beta)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        ret, thresh = cv2.threshold(gray, self.thresh_low, self.thresh_up, cv2.THRESH_BINARY)
        # thresh = cv2.bitwise_not(thresh)

        contours, hierarchy = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        x, y, w, h = self._Get_Min_Dist_Contour(frame, contours, cam_index)

        return [x, y, w, h], frame, gray, thresh

    def Adjust_Alpha_Beta(self, img, alpha, beta):
        def draw_text(img):
            temple = 'alpha {} beta {} th {} {} '
            text = temple.format(self.alpha, self.beta, self.thresh_low, self.thresh_up)
            font = cv2.FONT_HERSHEY_COMPLEX
            font_size = 0.9
            color = (0, 255, 0)
            thick = 2
            cv2.putText(img, text, (20, 20), font, font_size, color, thick)
            return img

        if self.is_test:
            img = draw_text(img)
        return np.clip(alpha * img + beta, 0, 255).astype(np.uint8)

    def _Get_Min_Dist_Contour(self, img, contours, cam):
        """
        areas : 'up' = upper size, 'low' = lower size
        coors :
        length :
        """

        def _3_squares(x, y):
            return ((x ** 2) + (y ** 2)) / (1 / 2)

        areas = {0: {'up': 50 * 50, 'low': 15 * 15},
                 2: {'up': 250 * 250, 'low': 60 * 60},
                 4: {'up': 200 * 200, 'low': 60 * 60}, }
        coors = {0: {'x': 240, 'y': 180, 'X': 430, 'Y': 350},
                 2: {'x': 50, 'y': 100, 'X': 450, 'Y': 350},
                 4: {'x': 50, 'y': 0, 'X': 400, 'Y': 350}, }
        lengths = {0: {'x': coors[0]['X'] - coors[0]['x'], 'y': coors[0]['Y'] - coors[0]['y']},
                   2: {'x': coors[2]['X'] - coors[2]['x'], 'y': coors[2]['Y'] - coors[2]['y']},
                   4: {'x': coors[4]['X'] - coors[4]['x'], 'y': coors[4]['Y'] - coors[0]['y']}}

        H, W, c = np.shape(img)
        OX, OY = W / 2, H / 2  # center coors of image
        min_dist = _3_squares(OX, OY)
        min_dist_index = None
        min_dist_area = OX * OY
        base_coors = [coors[cam]['x'], coors[cam]['y'], coors[cam]['X'], coors[cam]['Y']]

        logger.log(20, 'OX {} OY {} min_dist {} '.format(OX, OY, min_dist))
        base_length = _3_squares(lengths[cam]['x'], lengths[cam]['y'])
        params = {'max': {'dist': base_length, 'index': 0, 'area': areas[cam]['up']},
                  'min': {'dist': base_length, 'index': 0, 'area': areas[cam]['low']}}

        for i in range(len(contours)):
            x, y, w, h = cv2.boundingRect(contours[i])
            x = 1 if x == 0 else x
            X = x + w
            Y = y + h
            center_x = x + (w // 2)
            center_y = y + (h // 2)
            ox, oy = x + (w / 2), y + (h / 2)
            dist = (((ox - OX) ** 2) + ((oy - OY) ** 2)) ** (1 / 2)
            dist_area = w * h
            is_dist_in_min_dist = dist < min_dist
            is_area_in_dist_area = dist_area >= areas[cam]['low'] and dist_area <= areas[cam]['up']
            is_x_in_coors = x >= coors[cam]['x'] and x <= coors[cam]['X'] \
                            and X >= coors[cam]['x'] and X <= coors[cam]['X']
            is_y_in_coors = y >= coors[cam]['y'] and y <= coors[cam]['Y'] \
                            and Y >= coors[cam]['y'] and Y <= coors[cam]['Y']
            # is_diff_rate_moderate = abs((centers['x'] - center_x) / W) <= 1.2 \
            #                         and abs((centers['y'] - center_y) / H) <= 1.2
            if is_dist_in_min_dist and is_area_in_dist_area and is_x_in_coors and is_y_in_coors:
                min_dist = dist
                min_dist_index = i
                min_dist_area = dist_area
            params = self.debug_params(params, dist, i, dist_area)
        # if min_dist_index == None:
        if min_dist_index == None:
            contour = [0, 0, 0, 0]
        else:
            txt = 'min: dist {} index {} area {} contour {}'
            contour = cv2.boundingRect(contours[min_dist_index])
            logger.log(30,
                       txt.format(min_dist, min_dist_index, min_dist_area, contour))
        return contour

    def debug_params(self, params, dist, index, area):
        params['max']['dist'] = dist if params['max']['dist'] <= dist else params['max']['dist']
        params['max']['index'] = index if params['max']['index'] <= index else params['max']['index']
        params['max']['area'] = area if params['max']['area'] <= area else params['max']['area']
        params['min']['dist'] = dist if params['min']['dist'] >= dist else params['min']['dist']
        params['min']['index'] = index if params['min']['index'] >= index else params['min']['index']
        params['min']['area'] = area if params['min']['area'] >= area else params['min']['area']
        return params

    def _Sort_Cnt(self, img, contours):
        sorted_cnt = []
        h, w, c = np.shape(img)
        for i in range(len(contours)):
            is_too_large = cv2.contourArea(contours[i]) > w * h / 2
            is_too_small = cv2.contourArea(contours[i]) < 10
            if is_too_large or is_too_small:
                continue
            sorted_cnt.append(contours[i])
        return sorted_cnt

    def _Fusion_Cnt(self, contours):
        def Ammend_Coordinates(sorted_cnt):
            trim_size = 5
            x, y, w, h = sorted_cnt

            x = x - trim_size
            y = y - trim_size
            w = w + (trim_size * 2)
            h = h + (trim_size * 2)

            return x, y, w, h

        XYWH = [[], [], [], []]
        for i in range(len(contours)):
            x, y, w, h = cv2.boundingRect(contours[i])
            xywh = [x, y, w, h]
            for j in range(len(XYWH)):
                XYWH[j].append(xywh[j])

        sorted_cnt = [min(XYWH[0]), min(XYWH[1]), max(XYWH[2]), max(XYWH[3])]
        x, y, w, h = Ammend_Coordinates(sorted_cnt)

        return x, y, w, h

    def _Concat_Imgs(self, img, gray, thresh):
        # gray = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
        thresh = cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR)
        # img = cv2.hconcat([gray, thresh, img])
        img = cv2.hconcat([thresh, img])
        h_, w_, c = np.shape(img)
        img = cv2.resize(img, (w_ // 2, h_ // 2))
        return img

    # def Show_Gray_Thresh(self, gray, thresh):
    #     h_, w_ = np.shape(gray)
    #     gray = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
    #     gray = cv2.resize(gray, (w_ // 2, h_ // 2))
    #     thresh = cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR)
    #     thresh = cv2.resize(thresh, (w_ // 2, h_ // 2))
    #     return gray, thresh


if __name__ == '__main__':
    CT = Camera_Test()
    CT.is_test_bool = True
    CT.Init()
    CT.Main()
