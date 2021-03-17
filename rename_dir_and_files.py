import os, sys, glob, re, shutil

# python3 rename_dir_and_files.py imgs/0003* imgs/0007__black__plus_axis__2__1__1_
dir_name = sys.argv[1]
new_dir_name = sys.argv[2]
image_paths = glob.glob(os.path.join(dir_name, '*'))

if not os.path.exists(new_dir_name):
    os.makedirs(new_dir_name)


def gen_new_name():
    pattern = r'(\d{4})__.{1,}'
    regex = re.compile(pattern)
    results = regex.search(new_dir_name)
    _4_digits = results.group(1)
    return _4_digits


for old_path in image_paths:
    old_base_name = os.path.basename(old_path)
    _from = old_base_name[0:6]
    _to = os.path.basename(new_dir_name)
    _to = _to[0:6]
    new_base_name = old_base_name.replace(_from, _to)

    new_path = os.path.join(new_dir_name, new_base_name)
    shutil.move(old_path, new_path)
    print(old_path, new_path, sep=" : ")
