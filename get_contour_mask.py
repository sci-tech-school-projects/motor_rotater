import cv2
import numpy as np
import logging

logger = logging.getLogger('LoggingTest')
logger.setLevel(20)
sh = logging.StreamHandler()
logger.addHandler(sh)


class Get_Contour_Mask():
    def __init__(self):
        pass

    def Main(self, img_path='images/02.jpg'):
        self.img_path = img_path
        img = cv2.imread(self.img_path)

        canvas = self.Create_Canvas(0, img)
        not_img, and_img, thresh = self.Abstruct_Shape_As_Thresh(img, canvas)

        contours, hierarchy = cv2.findContours(thresh, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
        cont_img = cv2.drawContours(img.copy(), contours, -1, (0, 0, 255), 3)
        corners = self.Get_Bounding_Rect(canvas, contours)
        rect_img = self.Draw_Contours_Rect(img, corners)

        print("***** contour len {}".format(len(contours)))
        cv2.imshow("thresh", thresh)
        cv2.imshow("cont_img", cont_img)
        cv2.imshow("rect_img", rect_img)
        cv2.waitKey()

    def Create_Canvas(self, cam_index=0, frame=None, r=100):
        h, w, c = np.shape(frame)
        canvas = np.zeros(w * h, dtype=np.uint8).reshape(h, w)
        if cam_index == 0:
            cv2.circle(canvas, (int(w // 2), int(h // 2)), int(r), 255, -1)
        elif cam_index == 2:
            center = (int(w // 2), int(h // 2) - 75)
            axis = (450, 300)
            angle = 0
            cv2.ellipse(canvas, (center, axis, angle), 255, -1)
        else:
            raise Exception("cam_index is not in [0, 2] ")
        return canvas

    def Abstruct_Shape_As_Thresh(self, img, canvas, cam_index=0):
        _not_img = cv2.bitwise_not(img.copy(), img.copy(), mask=canvas)
        not_img = _not_img.copy()
        and_img = cv2.bitwise_and(_not_img, _not_img, mask=canvas)
        gray = cv2.cvtColor(and_img, cv2.COLOR_BGR2GRAY)
        ret, thresh = cv2.threshold(gray, 127, 255, 0)

        if cam_index == 0:
            filter_s = np.array([[0, 1, 0, ], [1, 1, 1, ], [0, 1, 0, ]], np.uint8)
            filter_l = np.array([[1, 1, 1, ], [1, 1, 1, ], [1, 1, 1, ]], np.uint8)
        elif cam_index == 2:
            filter_s = np.array([[1, 1, 1, ], [1, 1, 1, ], [1, 1, 1, ]], np.uint8)
            filter_l = np.array([[1, 1, 1, 1, 1, ],
                                 [1, 1, 1, 1, 1, ],
                                 [1, 1, 1, 1, 1, ],
                                 [1, 1, 1, 1, 1, ],
                                 [1, 1, 1, 1, 1, ], ], np.uint8)
        else:
            raise Exception("cam_index not in [0, 2]")
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, filter_l)
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, filter_s)

        return not_img, and_img, thresh

    def Get_Bounding_Rect(self, canvas, contours, cam_index=0):
        rate = {0: {'H': 8 * 5, 'W': 10 * 5},
                2: {'H': 8, 'W': 10}, }

        H, W = np.shape(canvas)
        bounding_rects = []
        for contour in contours:
            (x, y, w, h) = cv2.boundingRect(contour)
            area = int(w * h)
            logger.log(10, '***** area {} w {} h {}'.format(area, w, h))
            if area > ((H // rate[cam_index]['H']) * (W // rate[cam_index]['W'])):
                bounding_rects.append((x, y, w, h))
        return bounding_rects

    def Draw_Contours_Rect(self, img, corners):
        rect_img = img.copy()
        for corner in corners:
            (x, y, w, h) = corner
            cv2.rectangle(rect_img, (x, y), (x + w, y + h), (0, 0, 255), 1)
        return rect_img


if __name__ == '__main__':
    GTM = Get_Contour_Mask()
    GTM.Main()
