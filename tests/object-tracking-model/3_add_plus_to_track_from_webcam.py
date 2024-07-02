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
    # The input needs to be a tensor, convert it using `tf.convert_to_tensor`.
    input_tensor = tf.convert_to_tensor(image)
    # The model expects a batch of images, so add an axis with `tf.newaxis`.
    input_tensor = input_tensor[tf.newaxis, ...]

    # Run inference
    output_dict = model(input_tensor)

    # All outputs are batches tensors.
    # Convert to numpy arrays, and take index [0] to remove the batch dimension.
    # We're only interested in the first num_detections.
    num_detections = int(output_dict.pop('num_detections'))
    output_dict = {key: value[0, :num_detections].numpy()
                   for key, value in output_dict.items()}
    output_dict['num_detections'] = num_detections

    # detection_classes should be ints.
    output_dict['detection_classes'] = output_dict['detection_classes'].astype(np.int64)

    # Handle models with masks:
    if 'detection_masks' in output_dict:
        # Reframe the bbox mask to the image size.
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

        # Actual detection.
        output_dict = run_inference_for_single_image(model, image_np)

        # Prepare detections for DeepSORT
        detection_boxes = output_dict['detection_boxes']
        detection_classes = output_dict['detection_classes']
        detection_scores = output_dict['detection_scores']

        detections = []
        centers = []
        for i in range(detection_boxes.shape[0]):
            if detection_scores[i] >= 0.5 and detection_classes[i] in valid_classes:  # Filter out weak detections
                box = detection_boxes[i]
                class_id = detection_classes[i]
                score = detection_scores[i]
                ymin, xmin, ymax, xmax = box
                xmin, ymin, xmax, ymax = int(xmin * image_np.shape[1]), int(ymin * image_np.shape[0]), int(
                    xmax * image_np.shape[1]), int(ymax * image_np.shape[0])
                # Ensure bounding box is within image dimensions
                if xmin < 0 or ymin < 0 or xmax > image_np.shape[1] or ymax > image_np.shape[0]:
                    continue
                # Ensure the crop is valid
                if xmax - xmin <= 0 or ymax - ymin <= 0:
                    continue
                detections.append(((xmin, ymin, xmax, ymax), score, class_id))
                center_x = (xmin + xmax) // 2
                center_y = (ymin + ymax) // 2
                centers.append((center_x, center_y))

        # Update tracker
        tracks = tracker.update_tracks(detections, frame=image_np)

        # Visualization
        for track in tracks:
            if not track.is_confirmed():
                continue
            track_id = track.track_id
            ltrb = track.to_ltrb()
            cv2.rectangle(image_np, (int(ltrb[0]), int(ltrb[1])), (int(ltrb[2]), int(ltrb[3])), (0, 255, 0), 2)
            cv2.putText(image_np, f'ID: {track_id}', (int(ltrb[0]), int(ltrb[1] - 10)), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                        (0, 255, 0), 2)

        # Draw center points
        for center in centers:
            cv2.drawMarker(image_np, center, (0, 0, 255), markerType=cv2.MARKER_CROSS,
                           markerSize=20, thickness=2, line_type=cv2.LINE_AA)

        cv2.imshow('object_detection', cv2.resize(image_np, (800, 600)))
        if cv2.waitKey(25) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Detect objects inside webcam videostream')
    parser.add_argument('-m', '--model', type=str, required=True, help='Model Path')
    parser.add_argument('-l', '--labelmap', type=str, required=True, help='Path to Labelmap')
    parser.add_argument('--valid-classes', type=int, nargs='+', default=[1], help='Valid class IDs to track (default: 1 for people)')
    args = parser.parse_args()

    detection_model = load_model(args.model)
    category_index = label_map_util.create_category_index_from_labelmap(args.labelmap, use_display_name=True)

    # Initialize DeepSORT tracker
    tracker = DeepSort(max_age=30, n_init=3, nms_max_overlap=1.0, embedder='mobilenet', half=True, bgr=True)

    cap = cv2.VideoCapture(0)
    run_inference(detection_model, category_index, cap, tracker, args.valid_classes)

# python 2_add_plus_to_track_from_webcam.py -m ssd_mobilenet_v2_320x320_coco17_tpu-8/saved_model -l data/mscoco_label_map.pbtxt --valid-classes 1
# python 2_add_plus_to_track_from_webcam.py -m ssd_mobilenet_v2_320x320_coco17_tpu-8/saved_model -l data/mscoco_label_map.pbtxt --valid-classes 1 <drone_class_id>
