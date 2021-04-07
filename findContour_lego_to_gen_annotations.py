import os, sys, glob, re, shutil
import xml.etree.ElementTree as ET
import cv2
import numpy as np
import subprocess
import logging
from camera_test import Camera_Test

logger = logging.getLogger('LoggingTest')
logger.setLevel(20)
sh = logging.StreamHandler()
logger.addHandler(sh)


class Detect_Lego_To_Gen_Annotations():
    #
    abs_path_in_xml = sys.argv[1]
    abs_image_path_in_xml = os.path.join(abs_path_in_xml, 'lego/images')

    abs_path = os.path.abspath(os.getcwd())
    image_pattern = os.path.join(abs_path, 'lego/images/*.jpg')
    output_path = os.path.join(abs_path, 'lego/detected')
    image_paths = glob.glob(image_pattern)
    h_w_c = []
    ex_xyXY = []
    index = None

    def __init__(self):
        print('init ', self.__class__.__name__)
        self.image_paths.sort(reverse=True)
        print(self.image_pattern)
        print(self.image_paths[0])

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

    def Get_image_shape(self, image_path):
        image = cv2.imread(image_path)
        (h, w, c) = np.shape(image)
        self.h_w_c = [str(h), str(w), str(c)]
        # print(self.h_w_c)

    def Get_contour(self, image_path):
        detected_name = os.path.basename(image_path)
        detected_image_path = os.path.join(self.output_path, detected_name)

        img = cv2.imread(image_path)
        h, w, c = np.shape(img)

        # contour = self.find_contour(img)
        CT = Camera_Test()
        [x, y, w, h], img, gray, thresh = CT.Find_Contour(img, self.index)
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 3)
        # cv2.imshow('contour h w c : {} {} {} '.format(h,w,c), img)
        # if cv2.waitKey(0) % 256 == ord('q'):
        #     pass

        # img = CT._Concat_Imgs(gray, thresh, img)
        # # cv2.imshow('img', img)
        # cv2.imshow('x, y, w, h : {} {} {} {}'.format(x, y, w, h), img)
        contour = [x, y, x + w, y + h]

        return contour, detected_image_path

    def find_contour(self, img):
        def _sort_cnt(self, img, contours):
            sorted_cnt = []
            h, w, c = np.shape(img)
            for i in range(len(contours)):
                is_too_large = cv2.contourArea(contours[i]) > w * h / 2
                is_too_small = cv2.contourArea(contours[i]) < 10
                if is_too_large or is_too_small:
                    continue
                sorted_cnt.append(contours[i])
            return sorted_cnt

        def _fusion_cnt(self, contours):
            xyXYs = [[], [], [], []]
            trim_size = 0
            for idx in range(len(contours)):
                x, y, X, Y = cv2.boundingRect(contours[idx])
                X = x + X
                Y = y + Y
                xyXY = [x - trim_size, y - trim_size, X + trim_size, Y + trim_size]
                for j in range(len(xyXYs)):
                    xyXYs[j].append(xyXY[j])
            try:
                contour = [min(xyXYs[0]), min(xyXYs[1]), max(xyXYs[2]), max(xyXYs[3])]
                self.ex_xyXY = contour
            except ValueError:
                contour = self.ex_xyXY
            return contour

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        ret, thresh = cv2.threshold(gray, 75, 255, cv2.THRESH_BINARY)
        contours, hierarchy = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
        contour = []
        if self.index == 0:
            contour = self._Get_Min_Dist_Contour(img, contours)
        if self.index in [2, 4]:
            sorted_cnt = _sort_cnt(self, img, contours)
            contour = _fusion_cnt(self, sorted_cnt)
        return contour

    def _Get_Min_Dist_Contour(self, img, contours):
        h, w, c = np.shape(img)
        OX, OY = w / 2, h / 2  # center coors of image
        min_dist = ((OX ** 2) + (OY ** 2)) ** (1 / 2)
        min_dist_index = None
        min_dist_area = OX * OY

        logger.log(20, 'OX {} OY {} min_dist {} '.format(OX, OY, min_dist))

        for i in range(len(contours)):
            x, y, w, h = cv2.boundingRect(contours[i])
            ox, oy = x + (w / 2), y + (h / 2)
            dist = (((ox - OX) ** 2) + ((oy - OY) ** 2)) ** (1 / 2)
            dist_area = w * h
            if dist < min_dist and dist_area >= 15 * 15 and dist_area <= 50 * 50:
                min_dist = dist
                min_dist_index = i
                min_dist_area = dist_area
            if i % 20 == 0:
                logger.log(20, 'dist {}'.format(dist))
        txt = 'min_dist min_dist_index min_dist_area contour {} {} {} {}'
        logger.log(20, txt.format(min_dist, min_dist_index, min_dist_area, cv2.boundingRect(contours[min_dist_index])))
        return contours[min_dist_index]

    def Generate_xml(self, new_image_path, contour=None):
        format = './lego/format.xml'
        _xml_name = os.path.basename(new_image_path)
        xml_name = _xml_name[0:-4] + '.xml'

        new_xml_path = os.path.join('./lego/annotations', xml_name)
        if os.path.exists(new_xml_path):
            if not os.path.exists('./lego/annotations/old'):
                os.mkdir('./lego/annotations/old')
            shutil.move(new_xml_path, os.path.join('./lego/annotations/old', xml_name))
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
