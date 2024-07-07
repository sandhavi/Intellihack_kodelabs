import numpy as np
import tensorflow as tf
import cv2
from deep_sort_realtime.deepsort_tracker import DeepSort
from object_detection.utils import ops as utils_ops
from object_detection.utils import label_map_util

# patch tf1 into `utils.ops`
utils_ops.tf = tf.compat.v1

# Patch the location of gfile
tf.gfile = tf.io.gfile


def load_model(model_path):
    model = tf.saved_model.load(model_path)
    return model


def run_inference_for_single_image(model, image):
    image = np.asarray(image)
    input_tensor = tf.convert_to_tensor(image)
    input_tensor = input_tensor[tf.newaxis, ...]

    output_dict = model(input_tensor)

    num_detections = int(output_dict.pop('num_detections'))
    output_dict = {key: value[0, :num_detections].numpy()
                   for key, value in output_dict.items()}
    output_dict['num_detections'] = num_detections

    output_dict['detection_classes'] = output_dict['detection_classes'].astype(np.int64)

    if 'detection_masks' in output_dict:
        detection_masks_reframed = utils_ops.reframe_box_masks_to_image_masks(
            output_dict['detection_masks'], output_dict['detection_boxes'],
            image.shape[0], image.shape[1])
        detection_masks_reframed = tf.cast(detection_masks_reframed > 0.5, tf.uint8)
        output_dict['detection_masks_reframed'] = detection_masks_reframed.numpy()

    return output_dict


def prepare_detections(output_dict, valid_classes):
    detection_boxes = output_dict['detection_boxes']
    detection_classes = output_dict['detection_classes']
    detection_scores = output_dict['detection_scores']

    detections = []
    centers = []
    scores = []
    for i in range(detection_boxes.shape[0]):
        if detection_scores[i] >= 0.5 and detection_classes[i] in valid_classes:
            box = detection_boxes[i]
            class_id = detection_classes[i]
            score = detection_scores[i]
            ymin, xmin, ymax, xmax = box
            xmin, ymin, xmax, ymax = int(xmin * 640), int(ymin * 480), int(xmax * 640), int(ymax * 480)
            if xmin < 0 or ymin < 0 or xmax > 640 or ymax > 480:
                continue
            if xmax - xmin <= 0 or ymax - ymin <= 0:
                continue
            detections.append(((xmin, ymin, xmax, ymax), score, class_id))
            center_x = (xmin + xmax) // 2
            center_y = (ymin + ymax) // 2
            centers.append((center_x, center_y))
            scores.append(score)

    return detections, centers, scores


def initialize_tracker(embedder='mobilenet'):
    tracker = DeepSort(max_age=30, n_init=3, nms_max_overlap=1.0, embedder=embedder, half=True, bgr=True)
    return tracker
