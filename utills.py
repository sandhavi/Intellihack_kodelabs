import os
import sys
import math
import serial

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


def set_text(value):
    # Convert the value to a string if it is not None
    if value is None:
        return "None"
    else:
        return str(value)


def check_serial_port(port):
    try:
        with serial.Serial(port, timeout=1) as ser:
            return ser.is_open
    except serial.SerialException:
        return False


def calculate_angle(x, tx, w, r):
    """
    x:  Center of the object (bounding box) in pixels (or relative distance.)
    tx: Least visible width of the image in pixels (or relative width.)
    w:  Real Width of the image in mm/cm/m/km.
    r:  Real distance from center of rotation to the least visible image width position.
    """
    # Calculate the value inside the arctan function
    value = (x * w) / (tx * r)
    # Compute the arctangent (inverse tangent) of the value
    theta = math.atan(value)
    return theta
