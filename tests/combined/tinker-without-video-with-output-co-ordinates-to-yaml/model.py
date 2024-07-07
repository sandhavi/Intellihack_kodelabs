
import numpy as np
import tensorflow as tf
import config
import yaml
from datetime import datetime
import os

from object_detection.utils import ops as utils_ops

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


def run_inference(model, category_index, tracker):
    ret, image_np = config.cap.read()

    # Actual detection.
    output_dict = run_inference_for_single_image(model, image_np)

    # Prepare detections for DeepSORT
    detection_boxes = output_dict['detection_boxes']
    detection_classes = output_dict['detection_classes']
    detection_scores = output_dict['detection_scores']

    detections = []
    centers = []
    for i in range(detection_boxes.shape[0]):
        if detection_scores[i] >= 0.5 and detection_classes[i] in config.valid_classes:  # Filter out weak detections
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

    # Calculate mean coordinates
    if centers:
        mean_center_x = int(np.mean([center[0] for center in centers]))
        mean_center_y = int(np.mean([center[1] for center in centers]))
        return {"x": mean_center_x, "y": mean_center_y}
    else:
        return {"x": None, "y": None}


def save_detection_data(detection_data):
    # Create the output directory if it does not exist
    output_dir = 'output'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Generate the file name based on current date and time
    file_name = datetime.now().strftime("%Y-%m-%d_%H-%M-%S.yaml")
    file_path = os.path.join(output_dir, file_name)

    # Save data to YAML file
    with open(file_path, 'w') as file:
        yaml.dump(detection_data, file, default_flow_style=False)

    print(f"Detection data saved to {file_path}")