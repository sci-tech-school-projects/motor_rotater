import os, sys, glob, re, shutil

dir_name = './imgs/9999__black__friction_snap_w_cross_hole__3__1__1_'
new_dir_name = './imgs/0012__black__friction_snap_w_cross_hole__3__1__1_'
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
    _from = old_base_name[0:4]
    _to = gen_new_name()
    new_base_name = old_base_name.replace(_from, _to)

    new_path = os.path.join(new_dir_name, new_base_name)
    shutil.move(old_path, new_path)
