import cv2
import numpy as np
import sys

index = int(sys.argv[1])
print('index {}'.format(index))

"""
best tuning
top : 1.2 0.0
btm : 1.2 0.0
"""

trim_rate = 1

alpha = 1.2
beta = 0.0
try:
    alpha = float(sys.argv[2])
    beta = float(sys.argv[3])
except:
    pass


def Trim_Img(frame):
    shape = np.shape(frame)
    h, w, c = shape

    start_x = int(w / trim_rate)
    start_y = int(h / trim_rate)

    end_x = int(w / trim_rate) * (trim_rate)
    end_y = int(h / trim_rate) * (trim_rate)

    frame = frame[start_y:end_y, start_x:end_x, ::]

    return frame


def Adjust_Alpha_Beta(img, alpha=1.0, beta=0.0):
    dst = alpha * img + beta
    return np.clip(dst, 0, 255).astype(np.uint8)


def _ammend_coordinates(sorted_cnt):
    trim_size = 5
    x, y, w, h = sorted_cnt

    x = x - trim_size
    y = y - trim_size
    w = w + (trim_size * 2)
    h = h + (trim_size * 2)

    return x, y, w, h


def sort_cnt(img, contours):
    sorted_cnt = []
    h, w, c = np.shape(img)
    for i in range(len(contours)):
        is_too_large = cv2.contourArea(contours[i]) > w * h / 2
        is_too_small = cv2.contourArea(contours[i]) < 10
        if is_too_large or is_too_small:
            continue
        sorted_cnt.append(contours[i])
    return sorted_cnt


def fusion_cnt(contours):
    XYWH = [[], [], [], []]
    for i in range(len(contours)):
        x, y, w, h = cv2.boundingRect(contours[i])
        xywh = [x, y, w, h]
        for j in range(len(XYWH)):
            XYWH[j].append(xywh[j])

    sorted_cnt = [min(XYWH[0]), min(XYWH[1]), max(XYWH[2]), max(XYWH[3])]
    x, y, w, h = _ammend_coordinates(sorted_cnt)

    return x, y, w, h


def concat_imgs(gray, thresh, img):
    gray = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
    thresh = cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR)
    img = cv2.hconcat([gray, thresh, img])
    w, h, c = np.shape(img)
    img = cv2.resize(img, (h // 2, w // 2))
    return img


def Find_Contour(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ret, thresh = cv2.threshold(gray, 75, 255, cv2.THRESH_BINARY)
    # thresh = cv2.bitwise_not(thresh)

    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

    sorted_cnt = sort_cnt(img, contours)
    x, y, w, h = fusion_cnt(sorted_cnt)
    cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 3)
    img = concat_imgs(gray, thresh, img)

    return img


cap = cv2.VideoCapture(index)

while True:
    ret, frame = cap.read()

    if ret:
        frame = Trim_Img(frame)
        frame = Adjust_Alpha_Beta(frame, alpha, beta)
        frame = Find_Contour(frame)

        cv2.imshow('resized', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()
