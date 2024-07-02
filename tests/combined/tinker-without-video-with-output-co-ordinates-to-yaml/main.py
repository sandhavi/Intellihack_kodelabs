import tkinter as tk
from tkinter import ttk
import sv_ttk
import cv2
import win32con
import win32gui
import win32api
import camera
import config
import ui

def main():
    # Capture video from the default webcam (device 0)
    config.cap = cv2.VideoCapture(0)
    config.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    config.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    # Get the default webcam resolution
    if config.cap.isOpened():
        width = int(config.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(config.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) + config.CONST_CONTROLS_HEIGHT
    else:
        # Fallback to default if webcam is not accessible
        width, height = config.CONST_MIN_WIDTH, config.CONST_MIN_HEIGHT + config.CONST_CONTROLS_HEIGHT

    # Create the main application window
    root = tk.Tk()
    root.title("ASAM")
    root.geometry(f"{width}x{height}")
    root.resizable(True, True)
    root.minsize(width, height)

    # Create a frame to hold the dropdown and button
    frame_controls = ttk.Frame(root)
    frame_controls.pack(fill=tk.X, pady=(6, 5))

    # Create a Combobox to select the camera
    config.selected_camera = tk.StringVar(root)
    camera_names = camera.get_camera_names()
    config.selected_camera.set(camera_names[0])  # default camera

    config.cam_option = ttk.Combobox(frame_controls, textvariable=config.selected_camera, values=camera_names, state="readonly")
    config.cam_option.pack(side=tk.LEFT, padx=5)

    # Add padding to the text in the Combobox
    style = ttk.Style()
    style.configure('TCombobox', padding=(10, 0, 10, 0))  # Adjust padding as needed

    # Create a button to toggle the theme
    button = ttk.Button(frame_controls, text="Toggle theme", command=sv_ttk.toggle_theme)
    button.pack(side=tk.LEFT, padx=5)

    # Bind the combobox selection change to the camera.change_camera function
    config.selected_camera.trace_add('write', camera.change_camera)

    # Set theme based on system mode
    ui.set_theme()

    # Register the device change handler
    message_map = {
        win32con.WM_DEVICECHANGE: camera.device_change_handler
    }
    wc = win32gui.WNDCLASS()
    wc.lpfnWndProc = message_map
    wc.lpszClassName = 'DeviceChangeHandler'
    wc.hInstance = win32api.GetModuleHandle(None)
    class_atom = win32gui.RegisterClass(wc)
    hwnd = win32gui.CreateWindow(class_atom, 'DeviceChangeHandler', 0, 0, 0, 0, 0, 0, 0, wc.hInstance, None)
    camera.register_device_notification(hwnd)

    # Start updating the frames
    config.updating_frame = True
    camera.update_frame()

    # Start the Tkinter event loop
    root.mainloop()

    # Release the webcam and close any OpenCV windows when done
    config.cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    config.CONST_MIN_WIDTH = 800
    config.CONST_MIN_HEIGHT = 600
    config.CONST_CONTROLS_HEIGHT = 40

    # Flag to control the update_frame loop
    config.updating_frame = False

    main()
