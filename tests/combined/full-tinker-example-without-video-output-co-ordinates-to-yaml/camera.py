import threading
import yaml
from datetime import datetime
import os
from deep_sort_realtime.deepsort_tracker import DeepSort
import cv2
import config
import model
from object_detection.utils import label_map_util
from pygrabber.dshow_graph import FilterGraph
from ctypes import windll, sizeof, byref, c_wchar_p, Structure, c_ulong
import win32con

global camera_names, file_path
frame_lock = threading.Lock()
frame = None

# Initialize global variables for threading
run_counter = 0
output_dir = 'output'
os.makedirs(output_dir, exist_ok=True)


def get_latest_filename(directory='.'):
    # Ensure the directory exists
    os.makedirs(directory, exist_ok=True)

    # Find the latest available filename
    counter = 1
    latest_file = None
    while True:
        filename = f"{directory}/{counter:04d}.yaml"
        if not os.path.isfile(filename):
            break
        counter += 1

    latest_file = f"{directory}/{counter:04d}.yaml"
    return latest_file


def save_detection_data(new_item):
    global file_path
    if os.path.isfile(file_path):
        with open(file_path, 'r') as file:
            existing_data = yaml.safe_load(file) or []
    else:
        existing_data = []

    # Append new item to existing data
    if isinstance(existing_data, list):
        combined_data = existing_data + [new_item]
    else:
        raise ValueError("Existing data is not a list.")

    # Save the combined data back to the file
    with open(file_path, 'w') as file:
        yaml.dump(combined_data, file, default_flow_style=False)


def capture_frames():
    global frame
    while config.updating_frame:
        ret, frame = config.cap.read()
        if not ret:
            break


def process_frames():
    global frame, file_path, output_dir
    detection_model = model.load_model(config.model)
    category_index = label_map_util.create_category_index_from_labelmap(config.labelmap, use_display_name=True)
    tracker = DeepSort(max_age=30, n_init=3, nms_max_overlap=1.0, embedder='mobilenet', half=True, bgr=True)

    file_path = get_latest_filename(output_dir)
    while config.updating_frame:
        with frame_lock:
            if frame is not None:
                result = model.run_inference(detection_model, category_index, tracker)

                # Check if result is a dictionary
                if isinstance(result, dict):
                    x = result.get("x")
                    y = result.get("y")
                else:
                    # Assuming result is a tuple with (x, y)
                    x, y = result

                if x is not None and y is not None:
                    detection_data = {
                        'timestamp': datetime.now().isoformat(),
                        'mean_coordinates': {'x': x, 'y': y}
                    }
                else:
                    detection_data = {
                        'timestamp': datetime.now().isoformat(),
                        'mean_coordinates': {'x': None, 'y': None}
                    }
                save_detection_data(detection_data)
                print(detection_data)
        # Sleep briefly to prevent excessive CPU usage
        threading.Event().wait(0.5)

    print(f"Detection data saved to {file_path}")

def update_frame():
    if config.updating_frame:
        threading.Thread(target=capture_frames, daemon=True).start()
        threading.Thread(target=process_frames, daemon=True).start()


def get_camera_names():
    graph = FilterGraph()
    return graph.get_input_devices()


def change_camera(*args):
    cam_index = get_camera_names().index(config.selected_camera.get())
    if config.cap.isOpened():
        config.cap.release()
    config.cap = cv2.VideoCapture(cam_index)
    if not config.updating_frame:
        config.updating_frame = True
        update_frame()


def update_camera_options():
    global camera_names
    new_camera_names = get_camera_names()
    if new_camera_names != camera_names:
        camera_names = new_camera_names
        config.cam_option['values'] = camera_names
        if config.selected_camera.get() not in camera_names:
            config.selected_camera.set(camera_names[0])


class DevBroadcastDeviceInterface(Structure):
    _fields_ = [("dbcc_size", c_ulong),
                ("dbcc_devicetype", c_ulong),
                ("dbcc_reserved", c_ulong),
                ("dbcc_classguid", c_wchar_p),
                ("dbcc_name", c_wchar_p)]


def device_change_handler(hwnd, msg, wparam, lparam):
    if wparam in [win32con.DBT_DEVICEARRIVAL, win32con.DBT_DEVICEREMOVECOMPLETE]:
        update_camera_options()
    return 0


def register_device_notification(hwnd):
    dbi = DevBroadcastDeviceInterface()
    dbi.dbcc_size = sizeof(DevBroadcastDeviceInterface)
    dbi.dbcc_devicetype = win32con.DBT_DEVTYP_DEVICEINTERFACE
    dbi.dbcc_classguid = "{A5DCBF10-6530-11D2-901F-00C04FB951ED}"
    hdn = windll.user32.RegisterDeviceNotificationW(hwnd, byref(dbi), win32con.DEVICE_NOTIFY_WINDOW_HANDLE)
    if not hdn:
        raise RuntimeError("Failed to register device notification")
