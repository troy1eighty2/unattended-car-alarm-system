#!/usr/bin/env python3
import argparse
import multiprocessing
import queue
import sys
import threading
from functools import lru_cache

import cv2
import numpy as np

from picamera2 import MappedArray, Picamera2
from picamera2.devices import IMX500
from picamera2.devices.imx500 import (NetworkIntrinsics,
                                      postprocess_nanodet_detection)


class Detection:
    def __init__(self, coords, category, conf, metadata):
        global picam2
        """Create a Detection object, recording the bounding box, category and confidence."""
        self.category = category
        self.conf = conf
        self.box = imx500.convert_inference_coords(coords, metadata, picam2)


def parse_detections(metadata: dict):
    """Parse the output tensor into a number of detected objects, scaled to the ISP output."""
    global args
    global excluded_labels
    global subject
    global included_labels
    bbox_normalization = intrinsics.bbox_normalization
    threshold = args.threshold
    iou = args.iou
    max_detections = args.max_detections
    labels = args.labels

    np_outputs = imx500.get_outputs(metadata, add_batch=True)
    input_w, input_h = imx500.get_input_size()
    if np_outputs is None:
        return None
    if intrinsics.postprocess == "nanodet":
        boxes, scores, classes = \
            postprocess_nanodet_detection(outputs=np_outputs[0], conf=threshold, iou_thres=iou,
                                          max_out_dets=max_detections)[0]
        from picamera2.devices.imx500.postprocess import scale_boxes
        boxes = scale_boxes(boxes, 1, 1, input_h, input_w, False, False)
    else:
        boxes, scores, classes = np_outputs[0][0], np_outputs[1][0], np_outputs[2][0]
        if bbox_normalization:
            boxes = boxes / input_h

        boxes = np.array_split(boxes, 4, axis=1)
        boxes = zip(*boxes)

    detections = [
        Detection(box, category, score, metadata)
        for box, score, category in zip(boxes, scores, classes)
        if score > threshold and int(category) < len(labels) and labels[int(category)] not in excluded_labels
    ]
    
    for det in detections:
      if included_labels[int(det.category)] not in subject:
        subject.append(included_labels[int(det.category)])
      
    
    return detections


@lru_cache
def get_labels():
    global intrinsics
    labels = intrinsics.labels

    if intrinsics.ignore_dash_labels:
        labels = [label for label in labels if label and label != "-"]
    return labels


def draw_detections(jobs, ai_queue):
    global imx500
    global picam2
    """Draw the detections for this request onto the ISP output."""
    labels = get_labels()
    # Wait for result from child processes in the order submitted.
    last_detections = []
    while True:
        job = jobs.get()
        if job is None:
          continue
        request, async_result = job
        #detections = async_result.get()
        if request is None or request.config is None:
          continue
        detections = async_result
        if detections is None:
            detections = last_detections
        last_detections = detections
        with MappedArray(request, 'main') as m:
          for detection in detections:
              x, y, w, h = detection.box
              label = f"{labels[int(detection.category)]} ({detection.conf:.2f})"

              # Calculate text size and position
              (text_width, text_height), baseline = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
              text_x = x + 5
              text_y = y + 15

              # Create a copy of the array to draw the background with opacity
              overlay = m.array.copy()

              # Draw the background rectangle on the overlay
              cv2.rectangle(overlay,
                            (text_x, text_y - text_height),
                            (text_x + text_width, text_y + baseline),
                            (255, 255, 255),  # Background color (white)
                            cv2.FILLED)

              alpha = 0.3
              cv2.addWeighted(overlay, alpha, m.array, 1 - alpha, 0, m.array)

              # Draw text on top of the background
              cv2.putText(m.array, label, (text_x, text_y),
                          cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)

              # Draw detection box
              cv2.rectangle(m.array, (x, y), (x + w, y + h), (0, 255, 0), thickness=2)
              
          frame = m.array.copy()
          #print(frame)
          ai_queue.put(frame)
        request.release()

        #if intrinsics.preserve_aspect_ratio:
        #    b_x, b_y, b_w, b_h = imx500.get_roi_scaled(request)
        #    color = (255, 0, 0)  # red
        #    cv2.putText(m.array, "ROI", (b_x + 5, b_y + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
        #    cv2.rectangle(m.array, (b_x, b_y), (b_x + b_w, b_y + b_h), (255, 0, 0, 0))

        #cv2.imshow('IMX500 Object Detection', m.array)

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=str, help="Path of the model",
                        default="/usr/share/imx500-models/imx500_network_ssd_mobilenetv2_fpnlite_320x320_pp.rpk")
    parser.add_argument("--fps", type=int, help="Frames per second")
    parser.add_argument("--bbox-normalization", action=argparse.BooleanOptionalAction, help="Normalize bbox")
    parser.add_argument("--threshold", type=float, default=0.55, help="Detection threshold")
    parser.add_argument("--iou", type=float, default=0.65, help="Set iou threshold")
    parser.add_argument("--max-detections", type=int, default=10, help="Set max detections")
    parser.add_argument("--ignore-dash-labels", action=argparse.BooleanOptionalAction, help="Remove '-' labels ")
    parser.add_argument("--postprocess", choices=["", "nanodet"],
                        default=None, help="Run post process of type")
    parser.add_argument("-r", "--preserve-aspect-ratio", action=argparse.BooleanOptionalAction,
                        help="preserve the pixel aspect ratio of the input tensor")
    parser.add_argument("--labels", type=str,
                        help="Path to the labels file")
    parser.add_argument("--print-intrinsics", action="store_true",
                        help="Print JSON network_intrinsics then exit")
    return parser.parse_args()


#if __name__ == "__main__":
def run_detection(ai_queue, detection_queue):
    #args = get_args()

    global imx500
    global intrinsics
    global args
    global included_labels
    global excluded_labels
    included_labels={
      0: "person",
      15: "bird",
      16:"cat",
      17:"dog",
      18:"horse",
      19:"sheep",
      20:"cow",
      21:"elephant",
      22:"bear",
      23:"zebra",
      24:"giraffe",

    }
    excluded_labels= {
      "bicycle",
      "car",
      "motorcycle",
      "airplane",
      "bus",
      "train",
      "truck",
      "boat",
      "traffic light",
      "fire hydrant",
      "stop sign",
      "parking meter",
      "bench",
      "backpack",
      "umbrella",
      "handbag",
      "tie",
      "suitcase",
      "frisbee",
      "skis",
      "snowboard",
      "sports ball",
      "kite",
      "baseball bat",
      "baseball glove",
      "skateboard",
      "surfboard",
      "tennis racket",
      "bottle",
      "wine glass",
      "cup",
      "fork",
      "knife",
      "spoon",
      "bowl",
      "banana",
      "apple",
      "sandwich",
      "orange",
      "broccoli",
      "carrot",
      "hot dog",
      "pizza",
      "donut",
      "cake",
      "chair",
      "couch",
      "potted plant",
      "bed",
      "dining table",
      "toilet",
      "tv",
      "laptop",
      "mouse",
      "remote",
      "keyboard",
      "cell phone",
      "microwave",
      "oven",
      "toaster",
      "sink",
      "refrigerator",
      "book",
      "clock",
      "vase",
      "scissors",
      "teddy bear",
      "hair drier",
      "toothbrush",
    }
    global subject
    subject = []
    print("break 1")
    args = argparse.Namespace(                                                                                                  
        model="/usr/share/imx500-models/imx500_network_ssd_mobilenetv2_fpnlite_320x320_pp.rpk",                                                         
        threshold=0.75,
        iou=0.65,
        max_detections=10,
        fps=60,                                                                                                                    
        preserve_aspect_ratio=False,                                                                                               
        labels="assets/coco_labels.txt",                                                                                      
        print_intrinsics=False                                                                                                    
    ) 

    print("break 2")
    # This must be called before instantiation of Picamera2
    imx500 = IMX500(args.model)
    intrinsics = imx500.network_intrinsics
    if not intrinsics:
        intrinsics = NetworkIntrinsics()
        intrinsics.task = "object detection"
    elif intrinsics.task != "object detection":
        print("Network is not an object detection task", file=sys.stderr)
        exit()

    print("break 3")
    # Override intrinsics from args
    for key, value in vars(args).items():
        if key == 'labels' and value is not None:
            with open(value, 'r') as f:
                intrinsics.labels = f.read().splitlines()
        elif hasattr(intrinsics, key) and value is not None:
            setattr(intrinsics, key, value)
    print("break 4")

    # Defaults
    if intrinsics.labels is None:
        with open("assets/coco_labels.txt", "r") as f:
            intrinsics.labels = f.read().splitlines()
    intrinsics.update_with_defaults()

    if args.print_intrinsics:
        print(intrinsics)
        exit()
    print("break 5")

    global picam2
    picam2 = Picamera2(imx500.camera_num)
    main = {'format': 'RGB888'}
    config = picam2.create_preview_configuration(main, controls={"FrameRate": intrinsics.inference_rate}, buffer_count=4)
    print("break 6")

    #imx500.show_network_fw_progress_bar()
    picam2.start(config, show_preview=False)
    if intrinsics.preserve_aspect_ratio:
        imx500.set_auto_aspect_ratio()
    print("break 7")

    #pool = multiprocessing.Pool(processes=4)
    jobs = queue.Queue()
    thread = threading.Thread(target=draw_detections, args=(jobs, ai_queue,))
    thread.start()

    print("break 8")

    while True:
        detection_queue.put(subject)
        request = picam2.capture_request()

        metadata = request.get_metadata()
        if metadata:
            detections = parse_detections(metadata)
            jobs.put((request, detections))
        else:
            #frame = picam2.capture_array()
            #ai_queue.put(frame)
            request.release()
