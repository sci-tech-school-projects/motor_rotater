import cv2
import numpy as np
import sys
import logging

logger = logging.getLogger('LoggingTest')
logger.setLevel(20)
sh = logging.StreamHandler()
logger.addHandler(sh)


class Camera_Test():
    index = int(sys.argv[1])
    # path = sys.argv[2]
    print('index {}'.format(index))
    # l = int(sys.argv[2])
    # s = int(sys.argv[3])

    """
    best tuning
    top : 1.2 0.0
    btm : 1.2 0.0
    """

    trim_rate = 1

    alpha = 1.2
    beta = 0.0

    def Main(self, ):
        cap = cv2.VideoCapture(self.index)
        while True:

            ret, frame = cap.read()
            if ret:
                h, w, c = np.shape(frame)
                frame = self.Trim_Img(frame)
                frame = self.Adjust_Alpha_Beta(frame, self.alpha, self.beta)
                frame = self.Find_Contour(frame)
                cv2.imshow('h w c : {} {} {}'.format(h, w, c), frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                elif cv2.waitKey(0) & 0xFF == ord('a'):
                    pass
        cap.release()
        cv2.destroyAllWindows()

    def Trim_Img(self, frame):
        if self.trim_rate != 1:
            h, w, c = np.shape(frame)
            start_x = int(w / self.trim_rate)
            start_y = int(h / self.trim_rate)
            end_x = int(w / self.trim_rate) * (self.trim_rate)
            end_y = int(h / self.trim_rate) * (self.trim_rate)
            frame = frame[start_y:end_y, start_x:end_x, ::]
        return frame

    def Adjust_Alpha_Beta(self, img, alpha=1.2, beta=0.0):
        return np.clip(alpha * img + beta, 0, 255).astype(np.uint8)

    def Find_Contour(self, img):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        ret, thresh = cv2.threshold(gray, 75, 255, cv2.THRESH_BINARY)
        # thresh = cv2.bitwise_not(thresh)

        contours, hierarchy = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        if self.index == 0:
            x, y, w, h = self._Get_Min_Dist_Contour(img, contours)
        if self.index in [2, 4]:
            contours = self._Sort_Cnt(img, contours)
            x, y, w, h = self._Fusion_Cnt(contours)
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 3)
        # self._Draw_Contour(img, contours)
        img = self._Concat_Imgs(gray, thresh, img)

        return img

    # def _Draw_Contour(self, img, contours):
    #     for i in range(len(contours)):
    #         print(contours[i])
    #         x, y, w, h = cv2.boundingRect(contours[i])
    #         cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 3)

    def _Get_Min_Dist_Contour(self, img, contours):
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
            if dist < min_dist and dist_area >= 15 * 15 and dist_area <= 50 * 50:
                min_dist = dist
                min_dist_index = i
                min_dist_area = dist_area
            if i % 20 == 0:
                logger.log(20, 'dist {}'.format(dist))
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
