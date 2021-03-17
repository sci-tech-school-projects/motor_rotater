import os, sys, math, glob, re
import cv2
import numpy as np

# lego/raw_images
target_dir = sys.argv[1]
range_from = int(sys.argv[2])
range_to = int(sys.argv[3])
cut_len_x = int(sys.argv[4])
cut_len_y = int(sys.argv[5])
cut_len_X = int(sys.argv[6])
cut_len_Y = int(sys.argv[7])

_abs_path = os.path.abspath(os.getcwd())
abs_path = os.path.join(_abs_path, target_dir)
img_pattern = os.path.join(abs_path, '*.jpg')
# output_base_path = os.path.join(abs_path, 'lego/images')
img_paths = glob.glob(img_pattern)
img_paths.sort()

for i, img_path in enumerate(img_paths):
    if i >= range_from and i <= range_to:
        img = cv2.imread(img_path)
        h, w, c = np.shape(img)
        x = 0 + cut_len_x
        y = 0 + cut_len_y
        Y = h - cut_len_Y
        X = w - cut_len_X
        trimmed_img = img[y:Y, x:X]
        output_base_path = os.path.split(img_path)
        output_path = os.path.join(output_base_path[0], os.path.basename(img_path))
        # print(output_path)
        # sys.exit()
        cv2.imwrite(img_path, trimmed_img)
        if i % 500 == 0:
            print(img_path)
            print(h, w, c, sep=' : ')
        #     sys.exit()
