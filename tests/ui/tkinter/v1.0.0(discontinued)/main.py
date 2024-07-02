import tkinter as tk
from tkinter import ttk, Label
import cv2
from PIL import Image, ImageTk
import winreg
from pygrabber.dshow_graph import FilterGraph
import sv_ttk
import win32con
import win32gui
import win32api
from ctypes import windll, create_unicode_buffer, sizeof, byref, c_wchar_p, Structure, c_ulong

CONST_MIN_WIDTH = 800
CONST_MIN_HEIGHT = 600
CONST_CONTROLS_HEIGHT = 40

# Flag to control the update_frame loop
updating_frame = False

# Function to capture video frames and update the Tkinter window
def update_frame():
    global updating_frame
    if not updating_frame:
        return
    ret, frame = cap.read()
    if ret:
        width = lbl_video.winfo_width()
        height = lbl_video.winfo_height()

        # Get the default webcam resolution
        if cap.isOpened():
            w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        else:
            w, h = CONST_MIN_WIDTH, CONST_MIN_HEIGHT  # Fallback to default if webcam is not accessible

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
            lbl_video.imgtk = imgtk
            lbl_video.config(image=imgtk)
        else:
            print("Invalid dimensions for resizing, skipping frame update")

    # Call this function again after 10ms
    lbl_video.after(10, update_frame)

# Function to change the camera based on the selected option
def change_camera(*args):
    global cap, updating_frame
    cam_index = camera_names.index(variable.get())
    # Release the previous camera
    if cap.isOpened():
        cap.release()
    # Open the new camera
    cap = cv2.VideoCapture(cam_index)
    # Ensure the update_frame loop is running
    if not updating_frame:
        updating_frame = True
        update_frame()

# Function to detect system mode
def is_dark_mode():
    try:
        # Check if the system is in dark mode
        reg_key = r'SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize'
        reg_value = 'AppsUseLightTheme'
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_key) as key:
            value, regtype = winreg.QueryValueEx(key, reg_value)
            return value == 0  # 0 means dark mode, 1 means light mode
    except Exception as e:
        print(f"Error checking system mode: {e}")
        return False  # Fallback to default

# Function to set theme based on system mode
def set_theme():
    if is_dark_mode():
        sv_ttk.use_dark_theme()
    else:
        sv_ttk.use_light_theme()  # Define your light theme function if necessary

# Function to get the list of camera names
def get_camera_names():
    graph = FilterGraph()
    return graph.get_input_devices()

# Function to update the camera options in the dropdown
def update_camera_options():
    global camera_names
    new_camera_names = get_camera_names()
    if new_camera_names != camera_names:
        camera_names = new_camera_names
        cam_option['values'] = camera_names
        if variable.get() not in camera_names:
            variable.set(camera_names[0])

# Structure to register for device notifications
class DEV_BROADCAST_DEVICEINTERFACE(Structure):
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
    dbi = DEV_BROADCAST_DEVICEINTERFACE()
    dbi.dbcc_size = sizeof(DEV_BROADCAST_DEVICEINTERFACE)
    dbi.dbcc_devicetype = win32con.DBT_DEVTYP_DEVICEINTERFACE
    dbi.dbcc_classguid = "{A5DCBF10-6530-11D2-901F-00C04FB951ED}"
    hdn = windll.user32.RegisterDeviceNotificationW(hwnd, byref(dbi), win32con.DEVICE_NOTIFY_WINDOW_HANDLE)
    if not hdn:
        raise RuntimeError("Failed to register device notification")

# Capture video from the default webcam (device 0)
cap = cv2.VideoCapture(0)

# Get the default webcam resolution
if cap.isOpened():
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) + CONST_CONTROLS_HEIGHT
else:
    width, height = CONST_MIN_WIDTH, CONST_MIN_HEIGHT + CONST_CONTROLS_HEIGHT  # Fallback to default if webcam is not accessible

# Create the main application window
root = tk.Tk()
root.title("ASAM")
root.geometry(f"{width}x{height}")
root.resizable(True, True)

# Set the minimum size of the window
root.minsize(width, height)

# Create a frame to hold the dropdown and button
frame_controls = ttk.Frame(root)
frame_controls.pack(fill=tk.X, pady=(6, 5))

# Create a Combobox to select the camera
variable = tk.StringVar(root)
camera_names = get_camera_names()
variable.set(camera_names[0])  # default camera

cam_option = ttk.Combobox(frame_controls, textvariable=variable, values=camera_names, state="readonly")
cam_option.pack(side=tk.LEFT, padx=5)

# Add padding to the text in the Combobox
style = ttk.Style()
style.configure('TCombobox', padding=(10, 0, 10, 0))  # Adjust padding as needed

# Create a button to toggle the theme
button = ttk.Button(frame_controls, text="Toggle theme", command=sv_ttk.toggle_theme)
button.pack(side=tk.LEFT, padx=5)

# Create a label to display the video frames
lbl_video = Label(root)
lbl_video.pack(fill=tk.BOTH, expand=True)

# Bind the combobox selection change to the change_camera function
variable.trace_add('write', change_camera)

# Set theme based on system mode
set_theme()

# Register the device change handler
message_map = {
    win32con.WM_DEVICECHANGE: device_change_handler
}
wc = win32gui.WNDCLASS()
wc.lpfnWndProc = message_map
wc.lpszClassName = 'DeviceChangeHandler'
wc.hInstance = win32api.GetModuleHandle(None)
class_atom = win32gui.RegisterClass(wc)
hwnd = win32gui.CreateWindow(class_atom, 'DeviceChangeHandler', 0, 0, 0, 0, 0, 0, 0, wc.hInstance, None)
register_device_notification(hwnd)

# Start updating the frames
updating_frame = True
update_frame()

# Start the Tkinter event loop
root.mainloop()

# Release the webcam and close any OpenCV windows when done
cap.release()
cv2.destroyAllWindows()

# python main.py
