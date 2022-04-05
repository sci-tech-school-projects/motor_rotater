import os, sys, glob, re, shutil, datetime
import time
import xml.etree.ElementTree as ET
import cv2
import numpy as np
import subprocess
import logging
from camera_test import Camera_Test
from argparse import ArgumentParser

ap = ArgumentParser()
ap.add_argument('abs_path_in_xml')
ap.add_argument('-a', '--alpha', default=1.0, type=float)
ap.add_argument('-b', '--beta', default=0.0, type=float)
ap.add_argument('-t', '--target_no', default='',
                help='1st 4 digits of perticular dataset like "0004__blue__friction_snap_w_plus_axis__2__1__1_/"')
ap.add_argument('-c', '--cam_index', default=0, help='use images from perticuler camera index')
ap.add_argument('-l', '--lower', default=75, type=int)
ap.add_argument('-u', '--upper', default=255, type=int)

args = ap.parse_args()
print(args)
# sys.exit()

logger = logging.getLogger('LoggingTest')
logger.setLevel(20)
sh = logging.StreamHandler()
logger.addHandler(sh)


class Detect_Lego_To_Gen_Annotations():
    #
    abs_path_in_xml = args.abs_path_in_xml
    abs_image_path_in_xml = os.path.join(abs_path_in_xml, 'lego/images')

    abs_path = os.path.abspath(os.getcwd())
    image_pattern = os.path.join(abs_path, 'lego/0*/{}*.jpg'.format(args.target_no))
    image_paths = glob.glob(image_pattern)
    h_w_c = []
    ex_xyXY = []
    index = None

    def __init__(self):
        print('init ', self.__class__.__name__)
        self.image_paths.sort(reverse=True)
        print(self.image_pattern)
        print(self.image_paths[0])
        self.init_logging_misannotations()

    def init_logging_misannotations(self):
        now = datetime.datetime.now()
        name = now.strftime("%%%_%_%") + '.txt'
        base_dir = os.path.join(self.abs_path, 'lego', 'miss_logs')
        self.logging_file = os.path.join(base_dir, name)
        if not os.path.exists(base_dir):
            os.mkdir(base_dir)
        with open(self.logging_file, 'w') as f:
            f.write('')

    def Main(self):
        for image_path in self.image_paths:
            self.index = int(image_path[-8])
            xyXYs = self.Get_xyXY(image_path)
            # for j, xyXY in enumerate(xyXYs):
            new_image_path = os.path.join(self.abs_path, 'lego/images', os.path.basename(image_path))
            if image_path != '':
                # if j == 0:
                #     pass
                # else:
                #     new_image_path = new_image_path.split(".")[0] + "_{}".format(j) + '.jpg'
                # if not os.path.exists(new_image_path): shutil.copy(image_path, new_image_path)
                self.Generate_xml(new_image_path, xyXYs)
            else:
                print("image_path == '': then sys.exit()")
                sys.exit()

    def Get_xyXY(self, image_path):
        def set_args_to__CT():
            CT = Camera_Test()
            CT.alpha_val = args.alpha
            CT.beta_val = args.beta
            CT.thresh_lower_val = args.lower
            CT.thresh_upper_val = args.upper
            return CT

        img = cv2.imread(image_path)
        (h, w, c) = np.shape(img)
        self.h_w_c = [str(h), str(w), str(c)]

        CT = set_args_to__CT()
        bounding_rects, _, _ = CT.Find_Contour(img.copy(), self.index)
        xyXYs = [[x, y, x + w, y + h] for [x, y, w, h] in bounding_rects]
        self._logging_misannotations(image_path, xyXYs)
        return xyXYs

    def _logging_misannotations(self, image_path, xyXYs):
        for xyXY in xyXYs:
            if xyXY == [0, 0, 0, 0]:
                image_name = os.path.basename(image_path)
                with open(self.logging_file, 'a') as f:
                    f.write(image_name)

    def Generate_xml(self, new_image_path, xyXYs=None):
        format = os.path.join(os.path.join(self.abs_path), 'format.xml')
        _xml_name = os.path.basename(new_image_path)
        xml_name = _xml_name[0:-4] + '.xml'

        new_xml_path = os.path.join(self.abs_path, 'lego/annotations', xml_name)
        shutil.copy(format, new_xml_path)
        print(new_xml_path)

        if xyXYs == None:
            raise Exception('xyXYs is None')
            param, xyXYs = self.get_param_from_neighbor_xml(new_xml_path)
        else:
            param = self.abstract_param_for_xml(os.path.basename(new_image_path))

        logger.log(20, "*** param {}".format(param))
        self.write_xml_with_parse(param, new_xml_path, new_image_path, xyXYs)

    def get_param_from_neighbor_xml(self, new_xml_path):
        def _get_detection_from_existing_xml(self, xml_path):
            tree = ET.parse(xml_path)
            detection = {'box_points':
                             [tree.find('object').find('bndbox').find('xmin').text,
                              tree.find('object').find('bndbox').find('ymin').text,
                              tree.find('object').find('bndbox').find('xmax').text,
                              tree.find('object').find('bndbox').find('ymax').text]}
            return detection

        print('__get_param_from_neighbor_xml')
        base_name = os.path.basename(new_xml_path)
        _number = int(base_name[-8:-4])
        dir_name = os.path.join(self.abs_path, 'lego/annotations')

        _pre_xml = base_name[0:-8] + '{:0=4}'.format(_number - 1) + '.xml'
        pre_xml = os.path.join(dir_name, _pre_xml)
        _nex_xml = base_name[0:-8] + '{:0=4}'.format(_number + 1) + '.xml'
        nex_xml = os.path.join(dir_name, _nex_xml)

        if os.path.exists(pre_xml):
            xml_path = pre_xml
        elif os.path.exists(nex_xml):
            xml_path = nex_xml
        else:
            xml_path = new_xml_path
        param = self.abstract_param_for_xml(os.path.basename(xml_path))
        detection = _get_detection_from_existing_xml(self, xml_path)

        return param, detection

    def abstract_param_for_xml(self, image_name):
        """
        xml_name example : 0001__light_green__square__1__2__1_2162.jpg
        """
        pattern = r"\d{4}__(\w{2,10}_{0,1}\w{0,10})__(.{1,40}?)__(\d{1,2})__(\d{1,2})__(\d{1,2})_(\d{4,5})(?:_\d){0,1}\.(\w{3})"
        regex = re.compile(pattern)
        result = regex.search(image_name)
        param = {
            'name': result[2] + '__' + result[3] + '__' + result[4] + '__' + result[5],
            'color': result[1],
            'shape': result[2],
            'x': result[3],
            'y': result[4],
            'z': result[5],
            'image_num': result[6],
            'expansion': result[7]
        }
        if param['name'] == "":
            raise Exception('param is empty')
        return param

    def write_xml_with_parse(self, param, new_xml_path, new_image_path, xyXYs):
        def remove_empty_tags():
            root = tree.getroot()
            for object in tree.findall('object'):
                for ob in object.findall('name'):
                    if ob.text == None:
                        root.remove(object)

        base_name = os.path.basename(new_image_path)
        tree = ET.parse(new_xml_path)
        root = tree.getroot()

        tree.find('folder').text = self.abs_image_path_in_xml
        tree.find('filename').text = os.path.basename(new_image_path)
        tree.find('path').text = os.path.join(self.abs_image_path_in_xml, base_name)
        # tree.find('source').find('database').text = ''

        tree.find('size').find('height').text = self.h_w_c[0]
        tree.find('size').find('width').text = self.h_w_c[1]
        tree.find('size').find('depth').text = self.h_w_c[2]
        # tree.find('segmented').text = ''

        # children = ['name', 'color', 'bndbox', 'params', 'appearance']
        # for idx, xyXY in enumerate(xyXYs):
        # logger.log(20, "*** xyXYs {}".format(xyXYs))
        # sys.exit()
        objects = root.findall('object')
        # for object in root.findall('object'):
        for idx, xyXY in enumerate(xyXYs):
            try:
                objects[idx].find('name').text = param['name']
                # objects[idx].find('pose').text = ''
                # objects[idx].find('truncated').text = ''
                # objects[idx].find('difficult').text = ''
                objects[idx].find('color').text = param['color']
                objects[idx].find('bndbox').find('xmin').text = str(xyXY[0])
                objects[idx].find('bndbox').find('ymin').text = str(xyXY[1])
                objects[idx].find('bndbox').find('xmax').text = str(xyXY[2])
                objects[idx].find('bndbox').find('ymax').text = str(xyXY[3])

                w = xyXY[2] - xyXY[0]
                h = xyXY[3] - xyXY[1]
                objects[idx].find('params').find('area').text = str(w * h)
                objects[idx].find('params').find('x').text = str(xyXY[0])
                objects[idx].find('params').find('y').text = str(xyXY[1])
                objects[idx].find('params').find('w').text = str(w)
                objects[idx].find('params').find('h').text = str(h)

                objects[idx].find('appearance').find('shape').text = param['shape']
                objects[idx].find('appearance').find('x').text = param['x']
                objects[idx].find('appearance').find('y').text = param['y']
                objects[idx].find('appearance').find('z').text = param['z']
            except IndexError:
                break

        remove_empty_tags()
        tree.write(new_xml_path)


if __name__ == '__main__':
    gen_annots = Detect_Lego_To_Gen_Annotations()
    gen_annots.Main()
