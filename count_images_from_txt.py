import os, sys, math, glob, re
import cv2

"""
***** aeroplane_train.txt
      len 25009

***** aeroplane_val.txt
      len 25099
      not aeroplane images
      
***** aeroplane_test.txt
      len 49519
      not aeroplane images

***** aeroplane_trainval.txt
      len 50109
      
aeroplane_train.txt, aeroplane_test.txt, aeroplane_val.txt have
  no duplicate files.
aeroplane_trainval.txt has both of train.txt and val.txt.

"""


target_dir = sys.argv[1]
_abs_path = os.path.abspath(os.getcwd())
abs_path = os.path.join(_abs_path, target_dir)
pattern = 'ImageSets/Main/*'
path = os.path.join(abs_path, pattern)
files = glob.glob(path)
files.sort()
# print(files)

pattern_regex = r'(\d{4}__.*_\d{4})'
regex = re.compile(pattern_regex)

for i, file in enumerate(files):
    with open(file, 'r') as txt:
        content = txt.read()
        content = regex.findall(content)
        for j, item in enumerate(content):
            pass
        print('{} len {} '.format(file, j))
