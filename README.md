# Create dataset for pytorch

## References
### jetson-inference
[Build](https://github.com/dusty-nv/jetson-inference/blob/master/docs/building-repo-2.md#downloading-models)
[Models](https://github.com/dusty-nv/jetson-inference/blob/master/docs/detectnet-console-2.md)
[Re-training SSD-Mobilenet](https://github.com/dusty-nv/jetson-inference/blob/master/docs/pytorch-ssd.md)

### Pytorch
[Single Shot MultiBox Detector Implementation in Pytorch](https://github.com/qfgaohao/pytorch-ssd)
[Forked above: ](https://github.com/dusty-nv/pytorch-ssd)

## at pi4p:~/motor_rotater

### create images

    ssh pi4p
    cd motor_rotater

#### Usage

args   [1]:color [2]:shape [3]:X [4]:Y [5]:Z

    python3 main.py black plus_axis 2 1 1

scratches

    python3 main.py black friction_snap_w_cross_hole 3 1 1
    python3 main.py black connector 3 1 1
    python3 main.py black connector 2 1 1
    python3 main.py black plus_axis 2 1 1

### create xml files from new images

#### Usage

args dataset path of UBUNTU MAIN MACHINE

[comment]: <> (    mv imgs/0*/ imgs/raw_images)
    cp -r imgs/000*/ imgs/raw_images
    python3 findContour_lego_to_gen_annotations.py /home/araya/forked/data

#### check boundings

    python3 labelImg/labelImg.py

when needed run below, and re-run findContour_lego_to_gen_annotations.py

    python3 trim_imgs.py TARGET_DIR RANGE_FROM RANGE_TO CUT_LEN_x CUT_LEN_y CUT_LEN_X CUT_LEN_Y
    python3 trim_imgs.py "imgs/raw_images/0004*" 0 499 0 150 0 0   

### create_torch_category_txt.py

#### Usage

args path of dataset dir

    python3 create_torch_category_txt.py lego

#### run scp from UBUNTU MAIN MACHINE

[comment]: <> (    scp -r pi4p:~/motor_rotater/lego ./data)

    scp -r pi4p:~/motor_rotater/lego/images ./data/lego
    scp -r pi4p:~/motor_rotater/lego/annotations ./data/lego
    scp -r pi4p:~/motor_rotater/lego/ImageSets ./data/lego
    scp -r pi4p:~/motor_rotater/lego/labels.txt ./data/lego
    cd data/lego
    ln -s images JPEGImages
    ln -s annotations Annotations
    cd ../../

##### or sync
    rsync -au --progress --inplace --delete pi4p:~/motor_rotater/lego/images ./data/lego
    rsync -au --progress --inplace --delete pi4p:~/motor_rotater/lego/annotations ./data/lego

## (only for Test)downloads fruits dataset

    python3 open_images_downloader.py --class-names "Apple,Orange,Banana,Strawberry,Grape,Pear,Pineapple,Watermelon"

## train ssd at main Ubuntu

### basic tree structure

    VOC2007/
    ├── Annotations [9963 entries exceeds filelimit, not opening dir]
    ├── ImageSets
    │         ├── Layout
    │         │         ├── test.txt
    │         │         ├── train.txt
    │         │         ├── trainval.txt
    │         │         └── val.txt
    │         ├── Main [84 entries exceeds filelimit, not opening dir]
    │         │         ├── aeroplane_test.txt
    │         │         ├── aeroplane_train.txt
    │         │         ├── aeroplane_trainval.txt
    │         │         ├── aeroplane_val.txt
    │         │         ├── bicycle_test.txt
    │         │         ├── ... (from here cut by me)
    │         │         
    │         └── Segmentation
    │             ├── test.txt
    │             ├── train.txt
    │             ├── trainval.txt
    │             └── val.txt
    ├── JPEGImages [9963 entries exceeds filelimit, not opening dir]
    ├── SegmentationClass [632 entries exceeds filelimit, not opening dir]
    └── SegmentationObject [632 entries exceeds filelimit, not opening dir]

### At ubu:~/pytorch/pytorch-ssd-forked

#### mb1-ssd

#### Basic

    cd forked
    python3 train_ssd.py  --dataset-type=voc --data=data/lego --net mb1-ssd \
        --model-dir=models/lego --batch-size=32 --epochs=100

##### Restart with using checkpoint file

    python3 train_ssd.py  --dataset-type=voc --data=data/lego \
        --model-dir=models/lego --batch-size=32 --epochs=300 \
        --resume=models/lego/mb1-ssd-Epoch-95-Loss-0.1540847239579926.pth


#### mb2-ssd-lite

    python3 train_ssd.py --dataset-type=voc --datasets=/home/araya/z_04/lego/  \
    --model-dir=models/lego --net mb2-ssd-lite --batch-size 32 \
    --pretrained-ssd=models/mb2-ssd-lite-mp-0_686.pth


    python3 train_ssd.py --dataset-type=voc --datasets=data/lego  \
    --model-dir=models/lego --net mb1-ssd --batch-size 32

    python3 train_ssd.py --dataset-type=voc --datasets=data/lego  \
    --model-dir=models/lego --net mb2-ssd-lite --batch-size 32 \
    --pretrained-ssd=models/mb2-ssd-lite-mp-0_686.pth

## convert .pth to .onnx

### fails if .pth made by mb2-ssd-lite

    python3 onnx_export.py --model-dir=models/lego

    python3 onnx_export.py --model-dir=models/lego_mb1

### send files

    scp models/lego/labels.txt jet2g:~/detection_ssd/models/lego
    scp models/lego/ssd-mobilenet.onnx jet2g:~/detection_ssd/models/lego

## at Jetson nano, activate camera with object_detection : after setting up jetson-inference

### run at ~/detection_ssd

#### live camera

    detectnet --model=models/lego/ssd-mobilenet.onnx \
    --labels=models/lego/labels.txt \
    --input-blob=input_0 --output-cvg=scores --output-bbox=boxes \
    --camera=/dev/video0
    
    detectnet --model=models/fruit/ssd-mobilenet.onnx \
    --labels=models/fruit/labels.txt \
    --input-blob=input_0 --output-cvg=scores --output-bbox=boxes \
    --camera=/dev/video0

    detectnet --model=models/lego_2/ssd-mobilenet.onnx \
    --labels=models/lego_2/labels.txt \
    --input-blob=input_0 --output-cvg=scores --output-bbox=boxes \
    --camera=/dev/video0

#### image

    detectnet --model=models/lego/ssd-mobilenet.onnx \
    --labels=models/lego/labels.txt \
    --input-blob=input_0 --output-cvg=scores --output-bbox=boxes \
    "images/*.jpg" detected_images
