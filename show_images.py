import cv2
import numpy as np
import os, sys, glob, re, shutil, time

index = int(sys.argv[1])
print('index {}'.format(index))

"""
best tuning
top : 1.2 0.0
btm : 1.2 0.0
"""

alpha = 1.2
beta = 0.0
try:
    alpha = float(sys.argv[2])
    beta = float(sys.argv[3])
except:
    pass

cap = cv2.VideoCapture(index)


def trim_img(frame):
    shape = np.shape(frame)
    h, w, c = shape
    trim_rate = 5

    start_x = int(w / trim_rate)
    start_y = int(h / trim_rate)

    end_x = int(w / trim_rate) * (trim_rate)
    end_y = int(h / trim_rate) * (trim_rate)

    frame = frame[start_y:end_y, start_x:end_x, ::]

    return frame


def adjust(img, alpha=1.0, beta=0.0):
    dst = alpha * img + beta
    return np.clip(dst, 0, 255).astype(np.uint8)


def _sort_cnt(img, contours):
    sorted_cnt = []
    h, w, c = np.shape(img)
    for i in range(len(contours)):
        is_too_large = cv2.contourArea(contours[i]) > (w * h) // 3 * 2
        is_too_small = cv2.contourArea(contours[i]) < 0
        if is_too_large or is_too_small:
            continue
        sorted_cnt.append(contours[i])
    return sorted_cnt


def __ammend_coordinates(sorted_cnt):
    trim_size = 20
    x, y, w, h = sorted_cnt

    x = x - trim_size
    y = y - trim_size
    w = w + (trim_size * 2)
    h = h + (trim_size * 2)

    return x, y, w, h


def _fusion_cnt(contours):
    xyXYs = [[], [], [], []]
    trim_size = 20
    for idx, contour in enumerate(contours):
        x, y, X, Y = cv2.boundingRect(contours[idx])
        X = x + X
        Y = y + Y
        xyXY = [x - trim_size, y - trim_size, X + trim_size, Y + trim_size]
        for j in range(len(xyXYs)):
            xyXYs[j].append(xyXY[j])

    x, y, X, Y = [min(xyXYs[0]), min(xyXYs[1]), max(xyXYs[2]), max(xyXYs[3])]
    # x, y, w, h = __ammend_coordinates([x, y, w, h])

    return x, y, X, Y


def concat_imgs(gray, thresh, img):
    gray = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
    thresh = cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR)
    img = cv2.hconcat([gray, thresh, img])
    w, h, c = np.shape(img)
    img = cv2.resize(img, (h // 2, w // 2))
    return img


def find_contour(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ret, thresh = cv2.threshold(gray, 75, 255, cv2.THRESH_BINARY)
    # thresh = cv2.bitwise_not(thresh)

    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

    sorted_cnt = _sort_cnt(img, contours)
    x, y, X, Y = _fusion_cnt(sorted_cnt)
    cv2.rectangle(img, (x, y), (X, Y), (0, 0, 255), 3)
    img = concat_imgs(gray, thresh, img)

    cv2.imshow('img', img)
    cv2.waitKey(1)
    # if cv2.waitKey(0)  == ord('q'):
    #     return  break


def find_contours(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ret, thresh = cv2.threshold(gray, 75, 255, cv2.THRESH_BINARY)
    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

    for i in range(len(contours)):
        x, y, X, Y = cv2.boundingRect(contours[i])
        cv2.rectangle(img, (x, y), (X, Y), (0, 0, 255), 3)
        cv2.imshow('img', img)
        cv2.waitKey(1)
        # if cv2.waitKey(0)  == ord('q'):
        #     break


if __name__ == '__main__':
    # ./imgs/0013*/*
    pattern = './imgs/000*/*'
    image_paths = glob.glob(pattern)
    image_paths.sort(reverse=True)
    print(pattern)
    print(len(image_paths))

    for image_path in image_paths:
        img = cv2.imread(image_path)

        find_contour(img)
        # find_contours(img)

cv2.destroyAllWindows()
