import os
import sys
import math


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


def calculate_angle(x, Tx, w, r):
    """
    x:  Center of the object (bounding box) in pixels (or relative distance.)
    Tx: Least visible width of the image in pixels (or relative width.)
    w:  Real Width of the image in mm/cm/m/km.
    r:  Real distance from center of rotation to the least visible image width position.
    """
    # Calculate the value inside the arctan function
    value = (x * w) / (Tx * r)
    # Compute the arctangent (inverse tangent) of the value
    theta = math.atan(value)
    return theta
