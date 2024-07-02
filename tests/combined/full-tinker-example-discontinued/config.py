CONST_MIN_WIDTH = 800
CONST_MIN_HEIGHT = 600
CONST_CONTROLS_HEIGHT = 40

# Flag to control the update_frame loop
updating_frame = False

cap = None
lbl_video = None
cam_option = None
selected_camera = None

# Valid class IDs to track (default: 1 for people)
valid_classes = [1]

# Model Path
model = "data/models/ssd_mobilenet_v2_320x320_coco17_tpu-8/saved_model"

# Path to Labelmap
labelmap = "data/label_maps/mscoco_label_map.pbtxt"
