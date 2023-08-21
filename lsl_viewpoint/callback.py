from __future__ import annotations  # post-poned evaluation of annotations

from ctypes import CDLL, CFUNCTYPE, POINTER, c_double, c_int
from typing import TYPE_CHECKING

import numpy as np
from bsl.lsl import StreamInfo, StreamOutlet
from bsl.lsl.constants import fmt2numpy

from . import _LIB_PATH
from .buffer import Buffer
from .constants import EYE_A, EYE_B, VPX_DAT_FRESH
from .device import ViewPointDevice, _RealPoint

if TYPE_CHECKING:
    from typing import Optional

_func_double_value = CFUNCTYPE(c_int, POINTER(c_double))
_func_double_value2 = CFUNCTYPE(c_int, c_int, POINTER(c_double))
_func_real_point = CFUNCTYPE(c_int, POINTER(_RealPoint))
_func_real_point2 = CFUNCTYPE(c_int, c_int, POINTER(_RealPoint))
_callback = CFUNCTYPE(c_int, c_int, c_int, c_int, c_int)


def load_lib() -> CDLL:
    """Load the ViewPoint DLL.

    Returns
    -------
    vpx : CDLL
        The loaded library.
    """
    if _LIB_PATH is None:
        raise RuntimeError(
            "The path to the DLL is unknown. Please use lsl_viewpoint.set_lib_path()."
        )
    try:
        vpx = CDLL(_LIB_PATH)
    except Exception:
        raise RuntimeError(
            "The DLL could not be loaded. Please check the version and the "
            "dependencies."
        )
    return vpx


VPX = load_lib()

# -- accessor functions ----------------------------------------------------------------
# gaze point
vpx_get_gaze_point = _func_real_point2(VPX.VPX_GetGazePoint2)
vpx_get_gaze_point_smoothed = _func_real_point2(VPX.VPX_GetGazePointSmoothed2)
vpx_get_gaze_point_corrected = _func_real_point2(VPX.VPX_GetGazePointCorrected2)
vpx_get_gaze_binocular = _func_real_point(VPX.VPX_GetGazeBinocular)
# gaze angle
vpx_get_gaze_angle = _func_real_point2(VPX.VPX_GetGazeAngle2)
vpx_get_gaze_angle_smoothed = _func_real_point2(VPX.VPX_GetGazeAngleSmoothed2)
vpx_get_gaze_angle_corrected = _func_real_point2(VPX.VPX_GetGazeAngleCorrected2)
# velocity
vpx_get_total_velocity = _func_double_value2(VPX.VPX_GetTotalVelocity2)
vpx_get_component_velocity = _func_real_point2(VPX.VPX_GetComponentVelocity2)
vpx_get_velocity_binocular = _func_double_value(VPX.VPX_GetVelocityBinocular)
# blink
vpx_get_blink_event = _func_double_value2(VPX.VPX_GetBlinkEvent2)
# pupil and glint
vpx_get_pupil_size = _func_real_point2(VPX.VPX_GetPupilSize2)
vpx_get_pupil_aspect_ratio = _func_double_value2(VPX.VPX_GetPupilAspectRatio2)
vpx_get_pupil_angle = _func_double_value2(VPX.VPX_GetPupilAngle2)
vpx_get_pupil_diameter = _func_double_value2(VPX.VPX_GetPupilDiameter2)
vpx_get_pupil_point = _func_real_point2(VPX.VPX_GetPupilPoint2)
vpx_get_pupil_centroid = _func_real_point2(VPX.VPX_GetPupilCentroid2)
vpx_get_diff_vector = _func_real_point2(VPX.VPX_GetDiffVector2)
vpx_get_glint_point = _func_real_point2(VPX.VPX_GetGlintPoint2)
vpx_get_glint_centroid = _func_real_point2(VPX.VPX_GetGlintCentroid2)
# data quality
vpx_get_data_quality = _func_double_value2(VPX.VPX_GetDataQuality2)
# timestamps
vpx_get_data_time = _func_double_value2(VPX.VPX_GetDataTime2)
vpx_get_data_delta_time = _func_double_value2(VPX.VPX_GetDataDeltaTime2)
vpx_get_store_time = _func_double_value2(VPX.VPX_GetStoreTime2)
vpx_get_store_delta_time = _func_double_value2(VPX.VPX_GetStoreDeltaTime2)

# -- device to store shared variables --------------------------------------------------
DEVICE = ViewPointDevice()


# -- functions -------------------------------------------------------------------------
def get_gaze_point(
    device: ViewPointDevice, eye: str, processing: Optional[str]
) -> None:
    """Retrieve the gaze point for one or both eyes.

    Parameters
    ----------
    device : ViewPointDevice
        Class to store the shared variables updated.
    eye : 'A' | 'B' | 'AB'
        Eye selection. Use 'AB' for binocular selection.
    processing : None | 'smoothed' | 'corrected'
        Processing flag applied to the gaze point.
    """
    assert eye in ("A", "B", "AB"), "The eye selection should be 'A', 'B' or 'AB'."
    if eye == "AB":
        vpx_get_gaze_binocular(device.gaze_point_binocular)
    else:
        if processing is None:
            accessor = vpx_get_gaze_point
            variable = device.gaze_point
        elif processing == "smoothed":
            accessor = vpx_get_gaze_point_smoothed
            variable = device.gaze_point_smoothed
        elif processing == "corrected":
            accessor = vpx_get_gaze_point_corrected
            variable = device.gaze_point_corrected
        else:
            raise ValueError(
                "Argument 'processing' should be None, 'smoothed' or 'corrected'. "
                f"'{processing}' is invalid."
            )

        eye_idx = EYE_A if eye == "A" else EYE_B  # 0 for A, 1 for B
        accessor(eye_idx, variable[eye])


def get_gaze_angle(
    device: ViewPointDevice, eye: str, processing: Optional[str]
) -> None:
    """Retrive the gaze angle for one eye.

    Parameters
    ----------
    eye : 'A' | 'B'
        Eye selection. Use 'AB' for binocular selection.
    processing : None | 'smoothed' | 'corrected'
        Processing flag applied to the gaze angle.
    """
    assert eye in ("A", "B"), "The eye selection should be 'A' or 'B'."
    if processing is None:
        accessor = vpx_get_gaze_angle
        variable = device.gaze_angle
    elif processing == "smoothed":
        accessor = vpx_get_gaze_angle_smoothed
        variable = device.gaze_angle_smoothed
    elif processing == "corrected":
        accessor = vpx_get_gaze_angle_corrected
        variable = device.gaze_angle_corrected
    else:
        raise ValueError(
            "Argument 'processing' should be None, 'smoothed' or 'corrected'. "
            f"'{processing}' is invalid."
        )

    eye_idx = EYE_A if eye == "A" else EYE_B  # 0 for A, 1 for B
    accessor(eye_idx, variable[eye])


# -- buffer ----------------------------------------------------------------------------
_CH_NAMES = [
    "gaze_point_raw_A_x",
    "gaze_point_raw_A_y",
    "gaze_point_raw_B_x",
    "gaze_point_raw_B_y",
    "gaze_angle_raw_A_x",
    "gaze_angle_raw_A_y",
    "gaze_angle_raw_B_x",
    "gaze_angle_raw_B_y",
]
_BUFFER = Buffer(_CH_NAMES, bufsize=32)

# -- LSL Stream ------------------------------------------------------------------------
_SINFO = StreamInfo(
    "ViewPoint",
    "Gaze",
    _BUFFER.n_channels,
    sfreq=220,
    dtype="float64",
    source_id="ViewPoint",
)
_OUTLET = StreamOutlet(_SINFO, chunk_size=_BUFFER.bufsize)


# -- callback --------------------------------------------------------------------------
def callback(msg, sub_msg, p1, p2):  # noqa: D401
    """Callback function run when events are received from ViewPoint."""
    if msg == VPX_DAT_FRESH:
        # access data and store it in the shared variables in ViewPointDevice
        get_gaze_point(DEVICE, eye="A", processing=None)
        get_gaze_point(DEVICE, eye="B", processing=None)
        get_gaze_angle(DEVICE, eye="A", processing=None)
        get_gaze_angle(DEVICE, eye="B", processing=None)
        # transfer the selection of data into the buffer
        data = np.array(
            [
                DEVICE.gaze_point["A"].x,
                DEVICE.gaze_point["A"].y,
                DEVICE.gaze_point["B"].x,
                DEVICE.gaze_point["B"].y,
                DEVICE.gaze_angle["A"].x,
                DEVICE.gaze_angle["A"].y,
                DEVICE.gaze_angle["B"].x,
                DEVICE.gaze_angle["B"].y,
            ],
            dtype=fmt2numpy[_OUTLET._dtype],
        )
        _BUFFER.add_sample(data)
        # push to LSL if we have a full chunk
        if _BUFFER.is_full:
            _OUTLET.push_chunk(_BUFFER.buffer)
            _BUFFER.reset()
    return 0  # exit code


# register the python callback function with the viewpoint DLL
VPX.VPX_InsertCallback(_callback(callback))
