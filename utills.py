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


def calculate_angle(axis, center_pos, image_size, real_width, real_distance):
    """
    Calculate the angle of the object relative to the center of the image.

    Parameters:
    axis (str): The axis of rotation ('horizontal' or 'vertical').
    center_pos (float): Center of the object (bounding box) in pixels (or relative distance).
    image_size (float): Least visible width/height of the image in pixels (or relative width/height).
    real_width (float): Real width/height of the image in mm/cm/m/km.
    real_distance (float): Real distance from the center of rotation to the least visible image width/height position.

    Returns:
    float: The calculated angle in degrees.
    """
    # Calculate the value inside the arctan function
    value = ((center_pos - image_size / 2) * real_width) / (image_size * real_distance)
    # Compute the arctangent (inverse tangent) of the value
    theta = -1 * math.atan(value) * 180 / math.pi
    if axis == "horizontal":
        return theta
    elif axis == "vertical":
        return -1 * theta
    else:
        return 0
