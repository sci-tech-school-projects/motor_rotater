import cv2
from IPython.display import Image, display
from ipywidgets import widgets
import numpy as np
import sys


def imshow(img):
    """画像を Notebook 上に表示する。
    """
    encoded = cv2.imencode(".jpg", img)[1]
    display(Image(encoded, width=400))

def adjust(img, alpha=1.0, beta=0.0):
    # 積和演算を行う。
    dst = alpha * img + beta
    # [0, 255] でクリップし、uint8 型にする。
    return np.clip(dst, 0, 255).astype(np.uint8)

def process(img, alpha, beta):
    """明るさ、コントラストを調整し、結果を表示する。
    """
    dst = adjust(img, alpha, beta)
    imshow(dst)


param_widgets = {}

# パラメータ「ゲイン」を設定するスライダー
param_widgets["alpha"] = widgets.FloatSlider(
    min=0.0, max=3.0, step=0.1, value=1.0, description="alpha: "
)

# パラメータ「バイアス」を設定するスライダー
param_widgets["beta"] = widgets.FloatSlider(
    min=-100.0, max=100.0, step=10.0, value=0.0, description="beta: "
)

for x in param_widgets.values():
    x.layout.width = "400px"

# # 画像を読み込む。
# img = cv2.imread("sample.jpg")

index = int(sys.argv[1])
print('index {}'.format(index))

cap = cv2.VideoCapture(index)

def resize_img(frame):
    shape = np.shape(frame)
    h, w, c = shape

    start_x = int(w / 5)
    start_y = int(h / 5)
    end_x = int(w / 5) * 4
    end_y = int(h / 5) * 4

    frame = frame[start_y:end_y, start_x:end_x, ::]

    return frame


# while True:
#     ret, frame = cap.read()
#
#     frame = resize_img(frame)
#
#     # cv2.imshow('resized', frame)
#     widgets.interactive(process, img=widgets.fixed(frame), **param_widgets)
#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break
#
# cap.release()
# cv2.destroyAllWindows()

ret, frame = cap.read()
frame = resize_img(frame)

# frame = cv2.imread(frame)
widgets.interactive(process, img=widgets.fixed(frame), **param_widgets)

if cv2.waitKey(1) & 0xFF == ord('q'):
    cap.release()
    cv2.destroyAllWindows()
