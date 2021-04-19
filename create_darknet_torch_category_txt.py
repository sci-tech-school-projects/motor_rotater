import os, sys, math, glob, re, shutil
from mkdir import Mkdir

"""
$ ssh ubu
$ cd ~/z_04/lego
$ python3 create_torch_category_txt.py

### train, test, val = 50% 25% 25%
### trainval = train + val
"""


class Create_Torch_Category_Txt():
    # lego
    target_path = os.path.join(os.getcwd(), sys.argv[1])
    _abs_path = os.path.abspath(os.getcwd())
    abs_path = os.path.join(_abs_path, target_path)

    glob_pattern = os.path.join(abs_path, 'images/*.jpg')
    image_paths = glob.glob(glob_pattern)
    image_paths.sort()
    print('len image_paths {}'.format(len(image_paths)))

    file_type = ['_train.txt', '_train.txt', '_val.txt', '_test.txt']
    txts = glob.glob(os.path.join(abs_path, 'ImageSets/Main/*'))
    txts.sort()
    print('len txts {}'.format(len(txts)))

    base_files = ['train.txt', 'train.txt', 'val.txt', 'test.txt', ]
    base_path_of_Layout = os.path.join(abs_path, 'ImageSets/Layout')
    Layouts = None

    base_path_of_Main = os.path.join(abs_path, 'ImageSets/Main')
    Mains = None

    label_file = ['labels.txt', 'obj.names']
    Labels = None

    def __init__(self):
        mkdir = Mkdir()
        mkdir.main()

        self.Layouts = [os.path.join(self.base_path_of_Layout, file) for file in self.base_files]
        print('len Layouts {}'.format(len(self.Layouts)))
        self.Mains = [os.path.join(self.base_path_of_Main, file) for file in self.base_files]
        print('len Mains {}'.format(len(self.Mains)))
        self.Labels = [os.path.join(self.abs_path, file) for file in self.label_file]

        self.lists = [
            self.txts,
            self.Mains,
            self.Layouts,
            self.Labels,
        ]
        # print(self.lists)
        self.labels_in_labels_txt = []

    def Main(self):
        def get_Text(result):
            base_name = os.path.basename(result.group(0))
            label = base_name.split('.')
            text_to_add = label[0] + '\n'
            return text_to_add

        self.Init_File()
        pattern = r'\d{4}__(.*?)__(.*)_\d{4}(?:_\d){0,1}\.jpg'
        regex = re.compile(pattern)
        for i, path in enumerate(self.image_paths):
            result = regex.search(path)
            tag = result.group(2)
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
        file = os.path.join(self.base_path_of_Main, tag + self.file_type[num])

        self.write_common_file(file, num, text_to_add)
        self.write_common_file(self.Layouts[num], num, text_to_add)
        self.write_common_file(self.Mains[num], num, text_to_add)

        if num in [0, 1, 2]:
            for base_path in [self.base_path_of_Layout, self.base_path_of_Main]:
                file = os.path.join(base_path, 'trainval.txt')
                self.write_common_file(file, num, text_to_add)

            file = os.path.join(self.base_path_of_Main, tag + '_trainval.txt')
            self.write_common_file(file, num, text_to_add)

    def write_common_file(self, file, num, text_to_add):
        if not os.path.exists(file):
            with open(file, 'w') as f:
                f.write('')
                print('***** init {}'.format(file))

        with open(file, 'a') as f:
            f.write(text_to_add)

    def Write_Label_File(self, ):
        def init_file(file):
            if not os.path.exists(file):
                with open(file, 'w') as f:
                    f.write('')
                    print('***** init {}'.format(file))
            return file

        def _print(list):
            for item in list:
                print(item)

        for file in self.Labels:
            init_file(file)
            for i, txt in enumerate(self.txts):
                if i % 4 == 0:
                    _label = os.path.basename(txt)
                    # print(_label)
                    if _label != 'test.txt':
                        label = _label[0:(len(_label) - 9)]
                        with open(file, 'a') as f:
                            f.write(label + '\n')

    def Write_Obj_Data(self):
        def get_class_num():
            labels_txt = os.path.join(self.abs_path, self.Labels[0])
            with open(labels_txt, 'r') as l:
                return len(l.readlines())

        obj_data = os.path.join(self.abs_path, 'obj.data')
        classes = get_class_num()
        txt = 'classes = {}\n\
        train  = data/train.txt\n\
        valid  = data/test.txt\n\
        names = data/obj.names\n\
        backup = backup/'.format(classes)
        if os.path.exists(obj_data):
            os.remove(obj_data)

        with open(obj_data, 'w') as f:
            print('***** init {}'.format(obj_data))
            f.write(txt)


if __name__ == '__main__':
    CTCT = Create_Torch_Category_Txt()
    CTCT.Main()
    CTCT.Write_Obj_Data()
