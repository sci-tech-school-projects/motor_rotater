# Create dataset for pytorch

## at pi4p:~/motor_rotater

### create images

    ssh pi4p
    cd motor_rotater

#### Usage

args   [1]:color [2]:shape [3]:X [4]:Y [5]:Z

    python3 main.py black plus_axis 2 1 1
    python3 main.py black connector 2 1 1
    python3 main.py black connector 3 1 1
    python3 main.py black friction_snap_w_cross_hole 3 1 1

### create xml files from new images

#### Usage

args dataset path of UBUNTU MAIN MACHINEcreate_torch_category_txt.py

    mv imgs/0*/ imgs/raw_images
    python3 findContour_lego_to_gen_annotations.py /home/araya/forked/data

#### check boundings
    python3 labelImg/labelImg.py

### create_torch_category_txt.py

#### Usage

args path of dataset dir

    python3 create_torch_category_txt.py lego

#### run scp from UBUNTU MAIN MACHINE

    scp -r pi4p:~/motor_rotater/lego ./data
    scp -r pi4p:~/motor_rotater/lego/images ./data/lego
    scp -r pi4p:~/motor_rotater/lego/annotations ./data/lego
    scp -r pi4p:~/motor_rotater/lego/ImageSets ./data/lego
    scp -r pi4p:~/motor_rotater/lego/labels.txt ./data/lego

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

    python3 train_ssd.py  --dataset-type=voc --data=data/lego --model-dir=models/lego --batch-size=32 --epochs=100
    
    python3 train_ssd.py  --dataset-type=voc --data=data/lego --model-dir=models/lego --batch-size=32 --epochs=30 \
        --resume=models/lego/mb1-ssd-Epoch-99-Loss-0.2671643113717437.pth

    python3 train_ssd.py  --dataset-type=voc --data=data/lego \
        --model-dir=models/lego --batch-size=32 --epochs=100 \
        --resume=models/lego/mb1-ssd-Epoch-99-Loss-0.2671643113717437.pth

    python3 train_ssd.py --dataset-type=voc --datasets=data/lego/  \
    --model-dir=models/lego --net mb1-ssd --batch-size 32 --epochs 100

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
