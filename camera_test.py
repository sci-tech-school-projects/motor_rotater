import cv2
import numpy as np
import os, sys, math, glob, re, shutil, math
import logging
from argparse import ArgumentParser
from get_contour_mask import Get_Contour_Mask

logger = logging.getLogger('LoggingTest')
logger.setLevel(20)
sh = logging.StreamHandler()
logger.addHandler(sh)


class Camera_Test():
    """
    best tuningf
    top : 1.2 0.0
    btm : 1.2 0.0
    """
    cam_index = None
    run = True

    alpha = None
    beta = None
    thresh_up = None
    thresh_low = None
    is_test = False
    images_path = None

    def Init(self):
        ap = ArgumentParser()
        ap.add_argument('index', default=0, help='camera index')
        ap.add_argument('-a', '--alpha', default=1.0, type=float)
        ap.add_argument('-b', '--beta', default=0.0, type=float)
        ap.add_argument('-l', '--thresh_lower', default=75, type=int)
        ap.add_argument('-u', '--thresh_upper', default=255, type=int)
        ap.add_argument('-i', '--images_path', default=None, help='for checking existing images')

        args = ap.parse_args()
        self.alpha = args.alpha
        self.beta = args.beta
        self.thresh_low = args.thresh_lower
        self.thresh_up = args.thresh_upper
        self.images_path = args.images_path
        self.args = args

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
        def select_source():
            if self.images_path == None:
                return cv2.VideoCapture(self.cam_index)
            else:
                return glob.glob(os.path.join(os.getcwd(), 'lego', self.images_path, '*'))

        self.cam_index = int(self.args.index)
        cap = select_source()
        i = 0
        while self.run:
            if self.images_path == None:
                ret, frame = cap.read()
            else:
                try:
                    frame = cv2.imread(cap[i])
                    ++i
                    ret = True
                except IndexError:
                    ret = False
            if ret:
                self.Image_Process(frame)
        cap.release()
        cv2.destroyAllWindows()

    def Image_Process(self, frame):
        frame = self.Adjust_Alpha_Beta(frame, self.alpha, self.beta)
        bounding_rects, frame, thresh = self.Find_Contour(frame, self.cam_index)
        for [x, y, w, h] in bounding_rects:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 3)

        if self.is_test:
            frame = self.Draw_Center_Pos(frame)
            frame = self.draw_text(frame, bounding_rects[0])
            frame = self._Concat_Imgs(frame, thresh)
            cv2.imshow('h w c : {} '.format(np.shape(frame)), frame)
            if self.images_path==None:
                self.Brightness_Control()
            else:
                self.Keycontrol()

    def Find_Contour(self, frame, cam_index):
        GCM = Get_Contour_Mask()
        canvas = GCM.Create_Canvas(cam_index, frame)
        not_img, and_img, thresh = GCM.Abstruct_Shape_As_Thresh(frame, canvas)
        contours, hierarchy = cv2.findContours(thresh, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
        bounding_rects = GCM.Get_Bounding_Rect(canvas, contours, cam_index)

        # if len(corners) == 1:
        #     corner = corners[0]
        # elif len(corners) > 1:
        #     corner = corners[1]
        # else:
        #     corner = [0, 0, 0, 0]
        return bounding_rects, frame, thresh

    def Draw_Center_Pos(self, frame):
        h, w, c = np.shape(frame)
        if self.cam_index == 0:
            r = 100
            cv2.circle(frame, (int(w // 2), int(h // 2)), int(r), (0, 0, 255), 3)
        elif self.cam_index == 2:
            center = (int(w // 2), int(h // 2) - 75)
            axis = (450, 300)
            angle = 0
            cv2.ellipse(frame, (center, axis, angle), (0, 0, 255), 3)
        return frame

    def Adjust_Alpha_Beta(self, img, alpha, beta):
        if self.is_test:
            temple = 'alpha {} beta {} th {} {} '
            text = temple.format(self.alpha, self.beta, self.thresh_low, self.thresh_up)
            font = cv2.FONT_HERSHEY_COMPLEX
            font_size = 0.9
            color = (0, 255, 0)
            thick = 2
            cv2.putText(img, text, (20, 20), font, font_size, color, thick)
        return np.clip(alpha * img + beta, 0, 255).astype(np.uint8)

    def draw_text(self, img, cornoer):
        [x, y, w, h] = cornoer
        temple = 'area {} W {} H {}'
        text = temple.format(w * h, w, h)
        font = cv2.FONT_HERSHEY_COMPLEX
        font_size = 0.9
        color = (0, 255, 0)
        thick = 2
        cv2.putText(img, text, (20, 60), font, font_size, color, thick)
        return img

    def Brightness_Control(self):
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

    def Keycontrol(self):
        if cv2.waitKey(0) & 0xFF == ord('q'):
            self.run = False
        elif cv2.waitKey(0) & 0xFF == ord('z'):
            pass


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

    def _Concat_Imgs(self, img, thresh):
        thresh = cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR)
        img = cv2.hconcat([thresh, img])
        h_, w_, c = np.shape(img)
        img = cv2.resize(img, (w_ // 2, h_ // 2))
        return img


if __name__ == '__main__':
    CT = Camera_Test()
    CT.is_test_bool = True
    CT.Init()
    CT.Main()
