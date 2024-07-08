import os
import sys
import math
import serial
import serial.tools.list_ports

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


def check_port(port):
    ports = [port.device for port in serial.tools.list_ports.comports()]
    if port in ports:
        return True
    else:
        return False


def calculate_angle(x, xt, w, r):
    """
    x:  Center of the object (bounding box) in pixels (or relative distance).
    xt: Least visible width of the image in pixels (or relative width).
    w:  Real Width of the image in mm/cm/m/km.
    r:  Real distance from center of rotation to the least visible image width position.
    """
    # Calculate the value inside the arctan function
    value = ((x - xt/2) * w) / (xt * r)
    # Compute the arctangent (inverse tangent) of the value
    theta = -1 * math.atan(value) * 180 / math.pi
    return theta
