import os, sys, math, glob, re, shutil
import subprocess


class Return_Imgs_To_Raw_Images():
    def __init__(self):
        print('init ', self.__class__.__name__)
        try:
            self.range_from = int(sys.argv[1])
            self.range_to = int(sys.argv[2])
        except IndexError:
            print('usage $ python3 return_imgs_to_raw_images.py range_from range_to')
            sys.exit()

    def Main(self):
        abs_path = os.path.abspath(os.getcwd())
        for i in range(self.range_from, self.range_to):
            pattern = '{:0=4}'.format(i) + '*'
            _from = os.path.join(abs_path,'lego/images', pattern)
            froms = glob.glob(_from)
            froms.sort()
            _to = os.path.join(abs_path,'lego/raw_images', pattern)
            tos = glob.glob(_to)
            tos.sort()
            for  _t  in  tos:
                for _f in froms:
                    command = ['mv', _f, _t]
                    subprocess.call(command)
                    print(_f)
            # if not ret:
            #     print('Failed at i={} : {}'.format(i,command))


if __name__ == '__main__':
    RITRI = Return_Imgs_To_Raw_Images()
    RITRI.Main()


