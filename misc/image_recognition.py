import cv2
import numpy as np

# real time object detection using MobileNetSSD
# References:
# https://medium.com/@tauseefahmad12/object-detection-using-mobilenet-ssd-e75b177567ee
# https://medium.com/acm-juit/ssd-object-detection-in-real-time-deep-learning-and-caffe-f41e40eea968

# load pre-trained MobileNetSSD model
net = cv2.dnn.readNetFromCaffe(
    "deploy.prototxt", "mobilenet_iter_73000.caffemodel")

# class labels
CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat", "bottle", "bus", "car",
           "cat", "chair", "cow", "diningtable", "dog", "horse", "motorbike", "person",
           "pottedplant", "sheep", "sofa", "train", "tvmonitor"]

# start webcam
cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # prepare frame for detection
    h, w = frame.shape[:2]
    blob = cv2.dnn.blobFromImage(frame, 0.007843, (300, 300), 127.5)

    # perform object detection
    net.setInput(blob)
    detections = net.forward()

    # loop through detections
    for i in range(detections.shape[2]):
        confidence = detections[0, 0, i, 2]
        if confidence > 0.4:
            idx = int(detections[0, 0, i, 1])
            label = CLASSES[idx]

            # draw boxes
            box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
            startX, startY, endX, endY = box.astype("int")
            cv2.rectangle(frame, (startX, startY),
                          (endX, endY), (0, 255, 0), 2)
            cv2.putText(frame, f"{label}: {confidence:.2f}", (startX, startY - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    # display the frame
    cv2.imshow("Webcam Feed", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
