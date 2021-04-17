import os, sys, glob, re, shutil, datetime
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
    image_pattern = os.path.join(abs_path, 'lego/images/{}*.jpg'.format(args.target_no))
    output_path = os.path.join(abs_path, 'lego/detected')
    image_paths = glob.glob(image_pattern)
    h_w_c = []
    ex_xyXY = []
    index = None

    def __init__(self):
        print('init ', self.__class__.__name__)
        self.image_paths.sort(reverse=False)
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
        for i, image_path in enumerate(self.image_paths):
            self.index = int(image_path[-8])
            contour, detected_image_path = self.Get_contour(image_path)
            new_image_path = os.path.join('./lego/images', os.path.basename(image_path))
            if image_path != '':
                self.Get_image_shape(image_path)
                if contour == []:
                    print('Detect NOTHING')
                    # sys.exit()
                else:
                    self.Generate_xml(new_image_path, contour)
                # shutil.copy(image_path, new_image_path)
            else:
                print("image_path == '': then sys.exit()")
                sys.exit()

    def Get_contour(self, image_path):
        detected_name = os.path.basename(image_path)
        detected_image_path = os.path.join(self.output_path, detected_name)

        img = cv2.imread(image_path)
        CT = Camera_Test()
        CT.alpha_val = args.alpha
        CT.beta_val = args.beta
        CT.thresh_lower_val = args.lower
        CT.thresh_upper_val = args.upper

        [x, y, w, h], _, _, _ = CT.Find_Contour(img, self.index)
        # cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 3)
        # cv2.imshow('contour h w c : {} {} {} '.format(h,w,c), img)
        # if cv2.waitKey(0) % 256 == ord('q'):
        #     pass

        contour = [x, y, x + w, y + h]
        self._logging_misannotations(image_path, contour)

        return contour, detected_image_path

    def _logging_misannotations(self, image_path, contour):
        if contour == [0, 0, 0, 0]:
            image_name = os.path.basename(image_path)
            with open(self.logging_file, 'a') as f:
                f.write(image_name)

    def Get_image_shape(self, image_path):
        image = cv2.imread(image_path)
        (h, w, c) = np.shape(image)
        self.h_w_c = [str(h), str(w), str(c)]
        # print(self.h_w_c)

    def Generate_xml(self, new_image_path, contour=None):
        format = './format.xml'
        _xml_name = os.path.basename(new_image_path)
        xml_name = _xml_name[0:-4] + '.xml'

        new_xml_path = os.path.join('./lego/annotations', xml_name)
        shutil.copy(format, new_xml_path)

        if contour == None:
            param, contour = self.get_param_from_neighbor_xml(new_xml_path)
        else:
            param = self.abstract_param_for_xml(os.path.basename(new_image_path))
        self.write_xml(param, new_xml_path, new_image_path, contour)

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
        dir_name = './lego/annotations'

        _pre_xml = base_name[0:-8] + '{:0=4}'.format(_number - 1) + '.xml'
        pre_xml = os.path.join(dir_name, _pre_xml)
        _nex_xml = base_name[0:-8] + '{:0=4}'.format(_number + 1) + '.xml'
        nex_xml = os.path.join(dir_name, _nex_xml)

        xml_path = ''
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
        pattern = r"\d{4}__(\w{2,10}_{0,1}\w{0,10})__(.{1,40}?)__(\d{1,2})__(\d{1,2})__(\d{1,2})_(\d{4,5}).(\w{3})"
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
        return param

    def write_xml(self, param, new_xml_path, new_image_path, contour):
        base_name = os.path.basename(new_image_path)
        tree = ET.parse(new_xml_path)
        tree.find('filename').text = os.path.basename(new_image_path)
        tree.find('path').text = os.path.join(self.abs_image_path_in_xml, base_name)

        tree.find('size').find('height').text = self.h_w_c[0]
        tree.find('size').find('width').text = self.h_w_c[1]
        tree.find('size').find('depth').text = self.h_w_c[2]

        tree.find('object').find('name').text = param['name']
        tree.find('object').find('color').text = param['color']
        tree.find('object').find('bndbox').find('xmin').text = str(contour[0])
        tree.find('object').find('bndbox').find('ymin').text = str(contour[1])
        tree.find('object').find('bndbox').find('xmax').text = str(contour[2])
        tree.find('object').find('bndbox').find('ymax').text = str(contour[3])

        w = contour[2] - contour[0]
        h = contour[3] - contour[1]
        tree.find('object').find('params').find('area').text = str(w * h)
        tree.find('object').find('params').find('x').text = str(contour[0])
        tree.find('object').find('params').find('y').text = str(contour[1])
        tree.find('object').find('params').find('w').text = str(w)
        tree.find('object').find('params').find('h').text = str(h)

        tree.find('object').find('appearance').find('shape').text = param['shape']
        tree.find('object').find('appearance').find('x').text = param['x']
        tree.find('object').find('appearance').find('y').text = param['y']
        tree.find('object').find('appearance').find('z').text = param['z']

        tree.write(new_xml_path)
        print(new_xml_path)


if __name__ == '__main__':
    gen_annots = Detect_Lego_To_Gen_Annotations()
    gen_annots.Main()
    # cmd_array = ["python3", "split_train_validation_2.py"]
    # subprocess.call(cmd_array)
