from pygrabber.dshow_graph import FilterGraph
from ctypes import windll, sizeof, byref, c_wchar_p, Structure, c_ulong
from PIL import Image, ImageTk
from deep_sort_realtime.deepsort_tracker import DeepSort
import win32con
import cv2
import config
import model

from object_detection.utils import label_map_util
from object_detection.utils import visualization_utils as vis_util

global camera_names


# Function to capture video frames and update the Tkinter window
def update_frame():
    if not config.updating_frame:
        return

    # Detect objects inside webcam videostream
    detection_model = model.load_model(config.model)
    category_index = label_map_util.create_category_index_from_labelmap(config.labelmap, use_display_name=True)

    # Initialize DeepSORT tracker
    tracker = DeepSort(max_age=30, n_init=3, nms_max_overlap=1.0, embedder='mobilenet', half=True, bgr=True)

    ret, frame = model.run_inference(detection_model, category_index, tracker)

    if ret:
        width = config.lbl_video.winfo_width()
        height = config.lbl_video.winfo_height()

        # Get the default webcam resolution
        if config.cap.isOpened():
            w = int(config.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            h = int(config.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        else:
            w, h = config.CONST_MIN_WIDTH, config.CONST_MIN_HEIGHT  # Fallback to default if webcam is not accessible

        # Video ratio
        aspect_ratio = w / h

        # Resize frame preserving the aspect ratio
        if width / height < aspect_ratio:
            new_width = width
            new_height = int(width / aspect_ratio)
        else:
            new_width = int(height * aspect_ratio)
            new_height = height

        # Ensure the new dimensions are valid
        if new_width > 0 and new_height > 0:
            frame = cv2.resize(frame, (new_width, new_height))
            # Convert the frame to RGB format
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # Convert the frame to an ImageTk object
            img = Image.fromarray(frame)
            imgtk = ImageTk.PhotoImage(image=img)
            # Update the label with the new frame
            config.lbl_video.imgtk = imgtk
            config.lbl_video.config(image=imgtk)
        else:
            print("Invalid dimensions for resizing, skipping frame update")

    # Call this function again after 2000ms
    config.lbl_video.after(2000, update_frame)


# Function to get the list of camera names
def get_camera_names():
    graph = FilterGraph()
    return graph.get_input_devices()


# Function to change the camera based on the selected option
def change_camera(*args):
    cam_index = get_camera_names().index(config.selected_camera.get())
    # Release the previous camera
    if config.cap.isOpened():
        config.cap.release()
    # Open the new camera
    config.cap = cv2.VideoCapture(cam_index)
    # Ensure the update_frame loop is running
    if not config.updating_frame:
        config.updating_frame = True
        update_frame()


# Function to update the camera options in the dropdown
def update_camera_options():
    global camera_names
    new_camera_names = get_camera_names()
    if new_camera_names != camera_names:
        camera_names = new_camera_names
        config.cam_option['values'] = camera_names
        if config.selected_camera.get() not in camera_names:
            config.selected_camera.set(camera_names[0])


# Structure to register for device notifications
class DevBroadcastDeviceInterface(Structure):
    _fields_ = [("dbcc_size", c_ulong),
                ("dbcc_devicetype", c_ulong),
                ("dbcc_reserved", c_ulong),
                ("dbcc_classguid", c_wchar_p),
                ("dbcc_name", c_wchar_p)]


# Function to handle device change notifications
def device_change_handler(hwnd, msg, wparam, lparam):
    if wparam in [win32con.DBT_DEVICEARRIVAL, win32con.DBT_DEVICEREMOVECOMPLETE]:
        update_camera_options()
    return 0


# Function to register device notifications
def register_device_notification(hwnd):
    dbi = DevBroadcastDeviceInterface()
    dbi.dbcc_size = sizeof(DevBroadcastDeviceInterface)
    dbi.dbcc_devicetype = win32con.DBT_DEVTYP_DEVICEINTERFACE
    dbi.dbcc_classguid = "{A5DCBF10-6530-11D2-901F-00C04FB951ED}"
    hdn = windll.user32.RegisterDeviceNotificationW(hwnd, byref(dbi), win32con.DEVICE_NOTIFY_WINDOW_HANDLE)
    if not hdn:
        raise RuntimeError("Failed to register device notification")

