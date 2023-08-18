from ctypes import CFUNCTYPE, c_int

from .constants import VPX_DAT_FRESH
from .device import ViewPointDevice
from .functions import get_gaze_angle, get_gaze_point
from .vpx_lib import vpx

_callback = CFUNCTYPE(c_int, c_int, c_int, c_int, c_int)


DEVICE = ViewPointDevice()


def callback(msg, sub_msg, p1, p2):  # noqa: D401
    """Callback function run when events are received from ViewPoint."""
    if msg == VPX_DAT_FRESH:
        get_gaze_point(DEVICE, eye="A", processing=None)
        get_gaze_point(DEVICE, eye="B", processing=None)
        get_gaze_angle(DEVICE, eye="A", processing=None)
        get_gaze_angle(DEVICE, eye="B", processing=None)
    return 0  # exit code


# register the python callback function with the viewpoint DLL
vpx.VPX_InsertCallback(_callback(callback))
