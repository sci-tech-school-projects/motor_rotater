import os, sys, math, glob, re
import cv2
import numpy as np

# lego/raw_images
target_dir = sys.argv[1]
_abs_path = os.path.abspath(os.getcwd())
abs_path = os.path.join(_abs_path, target_dir)
img_pattern = os.path.join(abs_path, '*/*.jpg')
# output_base_path = os.path.join(abs_path, 'lego/images')
img_paths = glob.glob(img_pattern)

# _abs_path = os.path.abspath(os.getcwd())
# abs_path = os.path.join(_abs_path, target_dir)
# pattern = os.path.join(abs_path, '*.jpg')
# img_paths = glob.glob(pattern)
# print(pattern)
# print(img_paths[0])

for i, img_path in enumerate(img_paths):
    img = cv2.imread(img_path)
    h, w, c = np.shape(img)
    trimmed_img = img[0:h, 0:w - 100]
    output_base_path = os.path.split(img_path)
    output_path = os.path.join(output_base_path[0], os.path.basename(img_path))
    # print(output_path)
    # sys.exit()
    cv2.imwrite(img_path, trimmed_img)
    if i == 0:
        print(img_path)
        print(h, w, c, sep=' : ')
    #     sys.exit()
