# Object detection model
DetectionModel = "data/models/ssd_mobilenet_v2_320x320_coco17_tpu-8/saved_model"

# Label map
LabelMap = "data/label_maps/mscoco_label_map.pbtxt"

# Deepsort tracker
DeepsortTracker = "mobilenet"

# Crop the video stream to below ratio before feeding in ot the model
InputStreamAspectRatio = 4 / 3

# Detect object(ids) included in this array
ValidClasses = [1]
