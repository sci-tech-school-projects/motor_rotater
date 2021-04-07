import cv2
import numpy as np
import sys
import logging

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
    path = 0
    run = True

    trim_rate = 1
    alpha = 1.2
    beta = 0.0

    def Main(self, ):
        self.index = int(sys.argv[1])
        cap = cv2.VideoCapture(self.index)
        while self.run:
            ret, frame = cap.read()
            if ret:
                frame = self.Image_Process(frame)
        cap.release()
        cv2.destroyAllWindows()

    def Image_Process(self, frame):
        h, w, c = np.shape(frame)
        # frame = self.Trim_Img(frame)
        frame = self.Adjust_Alpha_Beta(frame, self.alpha, self.beta)
        [x, y, w, h], frame, gray, thresh = self.Find_Contour(frame, self.index)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 3)
        cv2.imshow('h w c : {} '.format(np.shape(frame)), frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            self.run = False

        # frame = self._Concat_Imgs(gray, thresh, frame)
        return frame

    # def Trim_Img(self, frame):
    #     if self.trim_rate != 1:
    #         h, w, c = np.shape(frame)
    #         start_x = int(w / self.trim_rate)
    #         start_y = int(h / self.trim_rate)
    #         end_x = int(w / self.trim_rate) * (self.trim_rate)
    #         end_y = int(h / self.trim_rate) * (self.trim_rate)
    #         frame = frame[start_y:end_y, start_x:end_x, ::]
    #     return frame

    def Adjust_Alpha_Beta(self, img, alpha=1.2, beta=0.0):
        return np.clip(alpha * img + beta, 0, 255).astype(np.uint8)

    def Find_Contour(self, frame, cam_index):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        ret, thresh = cv2.threshold(gray, 75, 255, cv2.THRESH_BINARY)
        # thresh = cv2.bitwise_not(thresh)

        contours, hierarchy = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        [x, y, w, h] = [0, 0, 0, 0]
        x, y, w, h = self._Get_Min_Dist_Contour(frame, contours, cam_index)

        # if cam_index == 0:
        #     x, y, w, h = self._Get_Min_Dist_Contour(frame, contours, cam_index)
        # elif cam_index in [2, 4]:
        #     contours = self._Sort_Cnt(frame, contours)
        #     x, y, w, h = self._Fusion_Cnt(contours)
        # self._Draw_Contour(img, contours)

        return [x, y, w, h], frame, gray, thresh

    # def _Draw_Contour(self, img, contours):
    #     for i in range(len(contours)):
    #         print(contours[i])
    #         x, y, w, h = cv2.boundingRect(contours[i])
    #         cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 3)

    def _Get_Min_Dist_Contour(self, img, contours, cam_index):
        areas = {0: {'u': 50 * 50, 'l': 15 * 15},
                 2: {'u': 200 * 200, 'l': 75 * 75},
                 4: {'u': 200 * 200, 'l': 75 * 75}, }

        h, w, c = np.shape(img)
        OX, OY = w / 2, h / 2  # center coors of image
        min_dist = ((OX ** 2) + (OY ** 2)) ** (1 / 2)
        min_dist_index = None
        min_dist_area = OX * OY

        logger.log(20, 'OX {} OY {} min_dist {} '.format(OX, OY, min_dist))

        for i in range(len(contours)):
            x, y, w, h = cv2.boundingRect(contours[i])
            ox, oy = x + (w / 2), y + (h / 2)
            dist = (((ox - OX) ** 2) + ((oy - OY) ** 2)) ** (1 / 2)
            dist_area = w * h
            if dist < min_dist and dist_area >= areas[cam_index]['l'] and dist_area <= areas[cam_index]['u']:
                min_dist = dist
                min_dist_index = i
                min_dist_area = dist_area

        txt = 'min_dist min_dist_index min_dist_area contour {} {} {} {}'
        logger.log(20, txt.format(min_dist, min_dist_index, min_dist_area, cv2.boundingRect(contours[min_dist_index])))
        return cv2.boundingRect(contours[min_dist_index])

    def _Sort_Cnt(self, img, contours):
        # rates = {
        #     0: {'l': self.l, 's': self.s},
        #     2: {'l': 2, 's': 10},
        #     4: {'l': 2, 's': 10},
        # }

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

    def _Concat_Imgs(self, gray, thresh, img):
        gray = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
        thresh = cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR)
        img = cv2.hconcat([gray, thresh, img])
        w, h, c = np.shape(img)
        img = cv2.resize(img, (h // 2, w // 2))
        return img


if __name__ == '__main__':
    CT = Camera_Test()
    CT.Main()
