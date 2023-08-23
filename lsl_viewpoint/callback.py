from __future__ import annotations  # post-poned evaluation of annotations

from ctypes import CDLL, CFUNCTYPE, POINTER, c_bool, c_double, c_int, c_void_p

import numpy as np
from bsl.lsl import StreamInfo, StreamOutlet, local_clock
from bsl.lsl.constants import fmt2numpy

from . import _LIB_PATH, _SAMPLING_RATE
from .device import (
    EYE_A,
    EYE_B,
    VPX_DAT_FRESH,
    ViewPointDevice,
    _RealPoint,
    _RealRect,
    _VPX_DataQuality,
    _VPX_EyeType,
)
from .utils.logs import logger

_func_double_value = CFUNCTYPE(c_int, POINTER(c_double))
_func_double_value2 = CFUNCTYPE(c_int, _VPX_EyeType, POINTER(c_double))
_func_real_point = CFUNCTYPE(c_int, POINTER(_RealPoint))
_func_real_point2 = CFUNCTYPE(c_int, _VPX_EyeType, POINTER(_RealPoint))
_func_real_rect2 = CFUNCTYPE(c_int, _VPX_EyeType, POINTER(_RealRect))

if _LIB_PATH is None or _SAMPLING_RATE is None:
    raise RuntimeError(
        "The path to the DLL or the sampling rate is unknown. Please use "
        "lsl_viewpoint.set_config()."
    )


def load_lib() -> CDLL:
    """Load the ViewPoint DLL.

    Returns
    -------
    vpx : CDLL
        The loaded library.
    """
    try:
        vpx = CDLL(_LIB_PATH)
    except Exception:
        raise RuntimeError(
            "The DLL could not be loaded. Please check the version and the "
            "dependencies."
        )
    return vpx


VPX = load_lib()

# -- DLL version -----------------------------------------------------------------------
VPX.VPX_GetDLLVersion.restype = c_double
logger.info("ViewPoint DLL version is %s.", VPX.VPX_GetDLLVersion())

# -- timestamp functions ---------------------------------------------------------------
VPX.VPX_IsPrecisionDeltaTimeAvailableQ.restype = c_bool
if not VPX.VPX_IsPrecisionDeltaTimeAvailableQ():
    raise RuntimeError("Precision timestamps are not available.")
# equivalent to CFUNCTYPE(c_double, POINTER(c_void_p), c_int)
VPX.VPX_GetPrecisionDeltaTime.restype = c_double
VPX.VPX_GetPrecisionDeltaTime.argtypes = [POINTER(c_void_p), c_int]

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
# pupil and glint
vpx_get_pupil_size = _func_real_point2(VPX.VPX_GetPupilSize2)
vpx_get_pupil_aspect_ratio = _func_double_value2(VPX.VPX_GetPupilAspectRatio2)
vpx_get_pupil_oval_rect = _func_real_rect2(VPX.VPX_GetPupilOvalRect2)
vpx_get_pupil_angle = _func_double_value2(VPX.VPX_GetPupilAngle2)
vpx_get_pupil_diameter = _func_double_value2(VPX.VPX_GetPupilDiameter2)
vpx_get_pupil_point = _func_real_point2(VPX.VPX_GetPupilPoint2)
vpx_get_pupil_centroid = _func_real_point2(VPX.VPX_GetPupilCentroid2)
vpx_get_diff_vector = _func_real_point2(VPX.VPX_GetDiffVector2)
vpx_get_glint_point = _func_real_point2(VPX.VPX_GetGlintPoint2)
vpx_get_glint_centroid = _func_real_point2(VPX.VPX_GetGlintCentroid2)
# data quality
_func_data_quality = CFUNCTYPE(c_int, _VPX_EyeType, POINTER(_VPX_DataQuality))
vpx_get_data_quality = _func_data_quality(VPX.VPX_GetDataQuality2)
# timestamps
vpx_get_data_time = _func_double_value2(VPX.VPX_GetDataTime2)
vpx_get_data_delta_time = _func_double_value2(VPX.VPX_GetDataDeltaTime2)
vpx_get_store_time = _func_double_value2(VPX.VPX_GetStoreTime2)
vpx_get_store_delta_time = _func_double_value2(VPX.VPX_GetStoreDeltaTime2)

# -- device to store shared variables --------------------------------------------------
DEVICE = ViewPointDevice()

# -- mapping accessors/variables -------------------------------------------------------
_ACCESSOR_VARIABLES = {
    # -- gaze point/angle --------------------------------------------------------------
    "gaze_point_raw": (vpx_get_gaze_point, DEVICE.gaze_point),
    "gaze_point_smoothed": (vpx_get_gaze_point_smoothed, DEVICE.gaze_point_smoothed),
    "gaze_point_corrected": (vpx_get_gaze_point_corrected, DEVICE.gaze_point_corrected),
    "gaze_binocular_point": (vpx_get_gaze_binocular, DEVICE.gaze_point_binocular),
    "gaze_angle_raw": (vpx_get_gaze_angle, DEVICE.gaze_angle),
    "gaze_angle_smoothed": (vpx_get_gaze_angle_smoothed, DEVICE.gaze_angle_smoothed),
    "gaze_angle_corrected": (vpx_get_gaze_angle_corrected, DEVICE.gaze_angle_corrected),
    # -- gaze velocity -----------------------------------------------------------------
    "gaze_total_velocity": (vpx_get_total_velocity, DEVICE.total_velocity),
    "gaze_component_velocity": (vpx_get_component_velocity, DEVICE.component_velocity),
    "gaze_binocular_velocity": (vpx_get_velocity_binocular, DEVICE.velocity_binocular),
    # -- pupil -------------------------------------------------------------------------
    "pupil_size": (vpx_get_pupil_size, DEVICE.pupil_size),
    "pupil_aspect_ratio": (vpx_get_pupil_aspect_ratio, DEVICE.pupil_aspect_ratio),
    "pupil_oval_rect": (vpx_get_pupil_oval_rect, DEVICE.pupil_oval_rect),
    "pupil_angle": (vpx_get_pupil_angle, DEVICE.pupil_angle),
    "pupil_diameter": (vpx_get_pupil_diameter, DEVICE.pupil_diameter),
    "pupil_point": (vpx_get_pupil_point, DEVICE.pupil_point),
    "pupil_centroid": (vpx_get_pupil_centroid, DEVICE.pupil_centroid),
    # -- glint -------------------------------------------------------------------------
    "glint_diff_vector": (vpx_get_diff_vector, DEVICE.diff_vector),
    "glint_point": (vpx_get_glint_point, DEVICE.glint_point),
    "glint_centroid": (vpx_get_glint_centroid, DEVICE.glint_centroid),
    # -- data quality ------------------------------------------------------------------
    "data_quality": (vpx_get_data_quality, DEVICE.data_quality),
    # -- timestamps --------------------------------------------------------------------
    "data_time": (vpx_get_data_time, DEVICE.data_time),
    "data_delta_time": (vpx_get_data_delta_time, DEVICE.data_delta_time),
    "store_time": (vpx_get_store_time, DEVICE.store_time),
    "store_delta_time": (vpx_get_store_delta_time, DEVICE.store_delta_time),
}


# -- functions -------------------------------------------------------------------------
def get_property(name: str, eye: str) -> None:
    """Retrieve a property for the given eye.

    Parameters
    ----------
    name : str
        Name of the property to retrieve.
    eye : 'A' | 'B'
        Eye selection. Ignored if the property is binocular.
    """
    accessor, variable = _ACCESSOR_VARIABLES.get(name, (None, None))
    if accessor is None:
        raise ValueError(f"The property name '{name}' is invalid.")

    if "binocular" in name:
        accessor(variable)
    else:
        assert eye in ("A", "B"), "The eye selection should be 'A' or 'B'."
        eye_idx = EYE_A if eye == "A" else EYE_B  # 0 for A, 1 for B
        accessor(eye_idx, variable[eye])


# -- channel names ---------------------------------------------------------------------
# binocular channels are updated on A-events
_CH_NAMES = [
    # -- gaze point/angle --------------------------------------------------------------
    "gaze_point_raw_x",
    "gaze_point_raw_y",
    "gaze_point_smoothed_x",
    "gaze_point_smoothed_y",
    "gaze_point_corrected_x",
    "gaze_point_corrected_y",
    "gaze_angle_raw_x",
    "gaze_angle_raw_y",
    "gaze_angle_smoothed_x",
    "gaze_angle_smoothed_y",
    "gaze_angle_corrected_x",
    "gaze_angle_corrected_y",
    # -- velocity ----------------------------------------------------------------------
    "total_velocity",
    "component_velocity_x",
    "component_velocity_y",
    # -- pupil -------------------------------------------------------------------------
    "pupil_size_x",
    "pupil_size_y",
    "pupil_aspect_ratio",
    "pupil_angle",
    "pupil_diameter",
    "pupil_point_x",
    "pupil_point_y",
    "pupil_centroid_x",
    "pupil_centroid_y",
    # -- glint -------------------------------------------------------------------------
    "glint_diff_vector_x",
    "glint_diff_vector_y",
    "glint_point_x",
    "glint_point_y",
    "glint_centroid_x",
    "glint_centroid_y",
    # -- data quality ------------------------------------------------------------------
    "data_quality",
    # -- timestamps --------------------------------------------------------------------
    "data_time",
    "data_delta_time",
    "store_time",
    "store_delta_time",
]
_CH_NAMES_BINOCULAR = [
    # -- gaze binocular ----------------------------------------------------------------
    "gaze_point_binocular_x",
    "gaze_point_binocular_y",
    # -- velocity binocular ------------------------------------------------------------
    "velocity_binocular",
]


# -- LSL Stream ------------------------------------------------------------------------
_SINFO_A = StreamInfo(
    "ViewPoint-A",
    "Gaze",
    len(_CH_NAMES + _CH_NAMES_BINOCULAR),
    sfreq=_SAMPLING_RATE,
    dtype="float64",
    source_id="ViewPoint",
)
_SINFO_B = StreamInfo(
    "ViewPoint-B",
    "Gaze",
    len(_CH_NAMES),
    sfreq=_SAMPLING_RATE,
    dtype="float64",
    source_id="ViewPoint",
)
_OUTLETS = {
    "A": StreamOutlet(_SINFO_A, chunk_size=1),
    "B": StreamOutlet(_SINFO_B, chunk_size=1),
}

# -- callback --------------------------------------------------------------------------
_callback = CFUNCTYPE(c_int, c_int, c_int, c_int, c_int)


def callback(msg, sub_msg, p1, p2):  # noqa: D401
    """Callback function run when events are received from ViewPoint."""
    if msg != VPX_DAT_FRESH:
        return 0  # exit early

    if sub_msg == EYE_A.value:
        eye = "A"
    elif sub_msg == EYE_B.value:
        eye = "B"
    else:
        logger.debug("Sub-message different from EYE_A or EYE_B received: %s", sub_msg)
        return 0  # exit early

    # -- gaze point/angle --------------------------------------------------------------
    get_property("gaze_point_raw", eye)
    get_property("gaze_point_smoothed", eye)
    get_property("gaze_point_corrected", eye)
    get_property("gaze_angle_raw", eye)
    get_property("gaze_angle_smoothed", eye)
    get_property("gaze_angle_corrected", eye)
    # -- gaze velocity -----------------------------------------------------------------
    get_property("gaze_total_velocity", eye)
    get_property("gaze_component_velocity", eye)
    # -- pupil -------------------------------------------------------------------------
    get_property("pupil_size", eye)
    get_property("pupil_aspect_ratio", eye)
    get_property("pupil_angle", eye)
    get_property("pupil_diameter", eye)
    get_property("pupil_point", eye)
    get_property("pupil_centroid", eye)
    # -- glint -------------------------------------------------------------------------
    get_property("glint_diff_vector", eye)
    get_property("glint_point", eye)
    get_property("glint_centroid", eye)
    # -- data quality ------------------------------------------------------------------
    get_property("data_quality", eye)
    # -- timestamps --------------------------------------------------------------------
    get_property("data_time", eye)
    get_property("data_delta_time", eye)
    get_property("store_time", eye)
    get_property("store_delta_time", eye)

    # -- binocular ---------------------------------------------------------------------
    if eye == "A":
        get_property("gaze_binocular_point", eye)
        get_property("gaze_binocular_velocity", eye)

    # figure out the corresponding LSL timestamp
    current_lsl_time = local_clock()
    current_vpx_time = VPX.VPX_GetPrecisionDeltaTime(None, c_int(0))
    acquisition_time = DEVICE.data_time[eye].value
    delay = current_vpx_time - acquisition_time
    timestamp = current_lsl_time - delay

    # format the data selection into a numpy array
    data = [
        # -- gaze point/angle ----------------------------------------------------------
        DEVICE.gaze_point[eye].x,
        DEVICE.gaze_point[eye].y,
        DEVICE.gaze_point_smoothed[eye].x,
        DEVICE.gaze_point_smoothed[eye].y,
        DEVICE.gaze_point_corrected[eye].x,
        DEVICE.gaze_point_corrected[eye].y,
        DEVICE.gaze_angle[eye].x,
        DEVICE.gaze_angle[eye].y,
        DEVICE.gaze_angle_smoothed[eye].x,
        DEVICE.gaze_angle_smoothed[eye].y,
        DEVICE.gaze_angle_corrected[eye].x,
        DEVICE.gaze_angle_corrected[eye].y,
        # -- velocity ------------------------------------------------------------------
        DEVICE.total_velocity[eye].value,
        DEVICE.component_velocity[eye].x,
        DEVICE.component_velocity[eye].y,
        # -- pupil ---------------------------------------------------------------------
        DEVICE.pupil_size[eye].x,
        DEVICE.pupil_size[eye].y,
        DEVICE.pupil_aspect_ratio[eye].value,
        DEVICE.pupil_angle[eye].value,
        DEVICE.pupil_diameter[eye].value,
        DEVICE.pupil_point[eye].x,
        DEVICE.pupil_point[eye].y,
        DEVICE.pupil_centroid[eye].x,
        DEVICE.pupil_centroid[eye].y,
        # -- glint ---------------------------------------------------------------------
        DEVICE.diff_vector[eye].x,
        DEVICE.diff_vector[eye].y,
        DEVICE.glint_point[eye].x,
        DEVICE.glint_point[eye].y,
        DEVICE.glint_centroid[eye].x,
        DEVICE.glint_centroid[eye].y,
        # -- data quality --------------------------------------------------------------
        DEVICE.data_quality[eye].value,
        # -- timestamps ----------------------------------------------------------------
        DEVICE.data_time[eye].value,
        DEVICE.data_delta_time[eye].value,
        DEVICE.store_time[eye].value,
        DEVICE.store_delta_time[eye].value,
    ]
    if eye == "A":
        data += [
            DEVICE.gaze_point_binocular.x,
            DEVICE.gaze_point_binocular.y,
            DEVICE.velocity_binocular.value,
        ]

    data = np.array(data, dtype=fmt2numpy[_OUTLETS[eye]._dtype])
    _OUTLETS[eye].push_sample(data, timestamp=timestamp)
    return 0  # exit code


# register the python callback function with the viewpoint DLL
_vpx_callback = _callback(callback)
VPX.VPX_InsertCallback(_vpx_callback)
