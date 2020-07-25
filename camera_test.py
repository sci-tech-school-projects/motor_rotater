import cv2
import numpy as np
import sys

index = int(sys.argv[1])
print('index {}'.format(index))

cap = cv2.VideoCapture(index)


def resize_img(frame):
    shape = np.shape(frame)
    h, w, c = shape

    start_x = int(w/5)
    start_y = int(h/5)
    end_x = int(w/5)*4
    end_y = int(h/5)*4

    frame = frame[start_y:end_y,start_x:end_x,::]

    return frame


while True:
    ret, frame = cap.read()

    frame = resize_img(frame)

    cv2.imshow('resized', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
