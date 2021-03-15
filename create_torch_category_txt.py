import os, sys, math, glob, re, shutil
from mkdir import Mkdir

"""
$ ssh ubu
$ cd ~/z_04/lego
$ python3 create_torch_category_txt.py

### train, test, val = 50% 25% 25%
### trainval = train + val
"""

mkdir = Mkdir()
mkdir.main()

# lego
target_path = sys.argv[1]
_abs_path = os.path.abspath(os.getcwd())
abs_path = os.path.join(_abs_path, target_path)

glob_pattern = os.path.join(abs_path, 'images/*.jpg')
image_paths = glob.glob(glob_pattern)
image_paths.sort()
print('len image_paths {}'.format(len(image_paths)))

pattern = r'\d{4}__\w{1,10}[_?\w{1,10}?]{0,4}__(.*)_\d{4}\.jpg'
regex = re.compile(pattern)

file_type = ['_train.txt', '_train.txt', '_val.txt', '_test.txt']
txts = glob.glob(os.path.join(abs_path, 'ImageSets/Main/*'))
txts.sort()
print('len txts {}'.format(len(txts)))

base_files = ['train.txt', 'train.txt', 'val.txt', 'test.txt', ]
base_path_of_Layout = os.path.join(abs_path, 'ImageSets/Layout')
Layouts = [os.path.join(base_path_of_Layout, file) for file in base_files]
print('len Layouts {}'.format(len(Layouts)))

base_path_of_Main = os.path.join(abs_path, 'ImageSets/Main')
Mains = [os.path.join(base_path_of_Main, file) for file in base_files]
print('len Mains {}'.format(len(Mains)))

label_file = ['labels.txt']
Labels = [os.path.join(abs_path, file) for file in label_file]


class Create_Torch_Category_Txt():

    def __init__(self, image_paths, file_type, txts, Mains, Layouts, Labels):
        self.image_paths = image_paths
        self.file_type = file_type
        self.txts = txts
        self.Mains = Mains
        self.Layouts = Layouts
        self.labels = Labels
        self.lists = [
            self.txts,
            self.Mains,
            self.Layouts,
            self.labels,
        ]
        # print(self.lists)

    def Main(self):
        def get_Text(result):
            base_name = os.path.basename(result.group(0))
            label = base_name.split('.')
            text_to_add = label[0] + '\n'
            return text_to_add

        self.Init_File()
        for i, path in enumerate(self.image_paths):
            result = regex.search(path)
            tag = result.group(1)
            text_to_add = get_Text(result)
            self.Write_File(i, tag, text_to_add)
        self.Write_Label_File()

    def Init_File(self, ):
        for list in self.lists:
            for item in list:
                if os.path.exists(item):
                    os.remove(item)

    def Write_File(self, i, tag, text_to_add):
        num = i % 4
        file = os.path.join(base_path_of_Main, tag + self.file_type[num])

        self.write_common_file(file, num, text_to_add)
        self.write_common_file(self.Layouts[num], num, text_to_add)
        self.write_common_file(self.Mains[num], num, text_to_add)

        if num in [0, 1, 2]:
            for base_path in [base_path_of_Layout, base_path_of_Main]:
                file  = os.path.join(base_path, 'trainval.txt')
                self.write_common_file(file, num, text_to_add)

            file = os.path.join(base_path_of_Main, tag + '_trainval.txt')
            self.write_common_file(file, num, text_to_add)

    def write_common_file(self, file, num, text_to_add):
        if not os.path.exists(file):
            with open(file, 'w') as f:
                f.write('')
                print('***** init {}'.format(file))

        with open(file, 'a') as f:
            f.write(text_to_add)

    def Write_Label_File(self, ):
        file = self.labels[0]
        if not os.path.exists(file):
            with open(file, 'w') as f:
                f.write('')
                print('***** init {}'.format(file))

        for i, txt in enumerate(self.txts):
            if i % 4 == 0:
                _label = os.path.basename(txt)
                # print(_label)
                if _label != 'test.txt':
                    label = _label[0:(len(_label) - 9)]
                    with open(file, 'a') as f:
                        f.write(label + '\n')


CTCT = Create_Torch_Category_Txt(image_paths, file_type, txts, Mains, Layouts, Labels)
CTCT.Main()
