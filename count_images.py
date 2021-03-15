import os, sys, math, glob, re, shutil


pattern = './lego/raw_images/*/*.jpg'
paths = glob.glob(pattern)
for i, path in enumerate(paths):
        pass
print('{} images'.format(i))
