import numpy as np
import argparse
import tensorflow as tf
import cv2
from deep_sort_realtime.deepsort_tracker import DeepSort

from object_detection.utils import ops as utils_ops
from object_detection.utils import label_map_util
from object_detection.utils import visualization_utils as vis_util

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

def run_inference(model, category_index, cap, tracker, valid_classes):
    while True:
        ret, image_np = cap.read()
        if not ret:
            break

        output_dict = run_inference_for_single_image(model, image_np)

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
                xmin, ymin, xmax, ymax = int(xmin * image_np.shape[1]), int(ymin * image_np.shape[0]), int(
                    xmax * image_np.shape[1]), int(ymax * image_np.shape[0])
                if xmin < 0 or ymin < 0 or xmax > image_np.shape[1] or ymax > image_np.shape[0]:
                    continue
                if xmax - xmin <= 0 or ymax - ymin <= 0:
                    continue
                detections.append(((xmin, ymin, xmax, ymax), score, class_id))
                center_x = (xmin + xmax) // 2
                center_y = (ymin + ymax) // 2
                centers.append((center_x, center_y))
                scores.append(score)

        # Update tracker
        tracks = tracker.update_tracks(detections, frame=image_np)

        # Draw highest score object
        if scores:
            max_score_index = np.argmax(scores)
            max_score = scores[max_score_index]
            max_center = centers[max_score_index]
            cv2.drawMarker(image_np, max_center, (0, 255, 0), markerType=cv2.MARKER_CROSS,
                           markerSize=20, thickness=2, line_type=cv2.LINE_AA)
            cv2.putText(image_np, f'Highest Score Center', (max_center[0] + 10, max_center[1] - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            if len(scores) > 1:
                sorted_scores = sorted(scores, reverse=True)
                if sorted_scores[0] - sorted_scores[1] < 1:
                    mean_center_x = int(np.mean([center[0] for center in centers]))
                    mean_center_y = int(np.mean([center[1] for center in centers]))
                    mean_center = (mean_center_x, mean_center_y)
                    cv2.drawMarker(image_np, mean_center, (255, 0, 0), markerType=cv2.MARKER_CROSS,
                                   markerSize=30, thickness=2, line_type=cv2.LINE_AA)
                    cv2.putText(image_np, f'Mean Center', (mean_center_x + 10, mean_center_y - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

        cv2.imshow('object_detection', cv2.resize(image_np, (800, 600)))
        if cv2.waitKey(25) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    # Model Path
    detection_model = load_model("../../data/models/ssd_mobilenet_v2_320x320_coco17_tpu-8/saved_model")

    # Path to Labelmap
    category_index = label_map_util.create_category_index_from_labelmap("../../data/label_maps/mscoco_label_map.pbtxt", use_display_name=True)

    # Track only these objects (label ids)
    valid_classes = [1]

    # Initialize DeepSORT tracker
    tracker = DeepSort(max_age=30, n_init=3, nms_max_overlap=1.0, embedder='mobilenet', half=True, bgr=True)

    cap = cv2.VideoCapture(0)
    run_inference(detection_model, category_index, cap, tracker, valid_classes)

    """
    Track object with highest score of identification using webcam
    Command to start script :-
    python 7_highest_score_track_from_webcam.py
    """
