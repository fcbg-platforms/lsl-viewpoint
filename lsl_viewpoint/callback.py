from __future__ import annotations  # post-poned evaluation of annotations

from ctypes import CDLL, CFUNCTYPE, POINTER, c_double, c_int, c_bool, c_void_p

import numpy as np
from bsl.lsl import StreamInfo, StreamOutlet, local_clock
from bsl.lsl.constants import fmt2numpy

from . import _LIB_PATH, _SAMPLING_RATE
from .device import (
    ViewPointDevice,
    _RealPoint,
    _RealRect,
    _VPX_DataQuality,
    _VPX_EyeType,
    EYE_A,
    EYE_B,
    VPX_DAT_FRESH,
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


# -- functions -------------------------------------------------------------------------
def get_gaze_point(device: ViewPointDevice, eye: str, processing: str) -> None:
    """Retrieve the gaze point for one or both eyes.

    Parameters
    ----------
    device : ViewPointDevice
        Class to store the shared variables updated.
    eye : 'A' | 'B' | 'AB'
        Eye selection. Use 'AB' for binocular selection.
    processing : 'raw' | 'smoothed' | 'corrected'
        Processing flag applied to the gaze point. Disabled for binocular selection.
    """
    assert eye in ("A", "B", "AB"), "The eye selection should be 'A', 'B' or 'AB'."
    if eye == "AB":
        vpx_get_gaze_binocular(device.gaze_point_binocular)
    else:
        accessors_variables = {
            "raw": (vpx_get_gaze_point, device.gaze_point),
            "smoothed": (vpx_get_gaze_point_smoothed, device.gaze_point_smoothed),
            "corrected": (vpx_get_gaze_point_corrected, device.gaze_point_corrected),
        }
        accessor, variable = accessors_variables.get(processing, (None, None))
        if accessor is None:
            raise ValueError(
                "Argument 'processing' should be 'raw', 'smoothed' or 'corrected'. "
                f"'{processing}' is invalid."
            )
        eye_idx = EYE_A if eye == "A" else EYE_B  # 0 for A, 1 for B
        accessor(eye_idx, variable[eye])


def get_gaze_angle(device: ViewPointDevice, eye: str, processing: str) -> None:
    """Retrieve the gaze angle for one eye.

    Parameters
    ----------
    eye : 'A' | 'B'
        Eye selection.
    processing : 'raw' | 'smoothed' | 'corrected'
        Processing flag applied to the gaze angle. Disabled for binocular selection.
    """
    assert eye in ("A", "B"), "The eye selection should be 'A' or 'B'."
    accessors_variables = {
        "raw": (vpx_get_gaze_angle, device.gaze_angle),
        "smoothed": (vpx_get_gaze_angle_smoothed, device.gaze_angle_smoothed),
        "corrected": (vpx_get_gaze_angle_corrected, device.gaze_angle_corrected),
    }
    accessor, variable = accessors_variables.get(processing, (None, None))
    if accessor is None:
        raise ValueError(
            "Argument 'processing' should be 'raw', 'smoothed' or 'corrected'. "
            f"'{processing}' is invalid."
        )
    eye_idx = EYE_A if eye == "A" else EYE_B  # 0 for A, 1 for B
    accessor(eye_idx, variable[eye])


def get_gaze_velocity(device: ViewPointDevice, eye: str, property_name: str) -> None:
    """Retrieve the gaze velocity for one of both eyes.

    Parameters
    ----------
    device : ViewPointDevice
        Class to store the shared variables updated.
    eye : 'A' | 'B' | 'AB'
        Eye selection. Use 'AB' for binocular selection.
    property_name : 'total' | 'component'
        Type of velocity to retrieve, 'total' or 'component'. Disabled for binocular
        selection.
    """
    assert eye in ("A", "B", "AB"), "The eye selection should be 'A', 'B' or 'AB'."
    if eye == "AB":
        vpx_get_velocity_binocular(device.velocity_binocular)
    else:
        accessors_variables = {
            "total": (vpx_get_total_velocity, device.total_velocity),
            "component": (vpx_get_component_velocity, device.component_velocity),
        }
        accessor, variable = accessors_variables.get(property_name, (None, None))
        if accessor is None:
            raise ValueError(
                "Argument 'property_name' should be 'total' or 'component'. "
                f"'{property_name}' is invalid."
            )
        eye_idx = EYE_A if eye == "A" else EYE_B  # 0 for A, 1 for B
        accessor(eye_idx, variable[eye])


def get_pupil_property(device: ViewPointDevice, eye: str, property_name: str):
    """Retrieve a property of the pupil.

    Parameters
    ----------
    device : ViewPointDevice
        Class to store the shared variables updated.
    eye : 'A' | 'B'
        Eye selection.
    property_name : str
        Name of the property to retrieve. Can be one of: 'size', 'aspect_ratio',
        'oval_rect', 'angle', 'diameter', 'point', 'centroid'.
    """
    assert eye in ("A", "B"), "The eye selection should be 'A' or 'B'."
    accessors_variables = {
        "size": (vpx_get_pupil_size, device.pupil_size),
        "aspect_ratio": (vpx_get_pupil_aspect_ratio, device.pupil_aspect_ratio),
        "oval_rect": (vpx_get_pupil_oval_rect, device.pupil_oval_rect),
        "angle": (vpx_get_pupil_angle, device.pupil_angle),
        "diameter": (vpx_get_pupil_diameter, device.pupil_diameter),
        "point": (vpx_get_pupil_point, device.pupil_point),
        "centroid": (vpx_get_pupil_centroid, device.pupil_centroid),
    }
    accessor, variable = accessors_variables.get(property_name, (None, None))
    if accessor is None:
        raise ValueError(
            "Argument 'property_name' should be one of 'size', 'aspect_ratio', "
            f"'oval_rect', 'angle', 'diameter', 'point', 'centroid'. '{property_name}' "
            "is invalid."
        )
    eye_idx = EYE_A if eye == "A" else EYE_B  # 0 for A, 1 for B
    accessor(eye_idx, variable[eye])


# -- channel names ---------------------------------------------------------------------
_CH_NAMES = [
    # -- gaze raw ----------------------------------------------------------------------
    "gaze_point_raw_A_x",
    "gaze_point_raw_A_y",
    "gaze_point_raw_B_x",
    "gaze_point_raw_B_y",
    "gaze_angle_raw_A_x",
    "gaze_angle_raw_A_y",
    "gaze_angle_raw_B_x",
    "gaze_angle_raw_B_y",
    # -- gaze smoothed -----------------------------------------------------------------
    "gaze_point_smoothed_A_x",
    "gaze_point_smoothed_A_y",
    "gaze_point_smoothed_B_x",
    "gaze_point_smoothed_B_y",
    "gaze_angle_smoothed_A_x",
    "gaze_angle_smoothed_A_y",
    "gaze_angle_smoothed_B_x",
    "gaze_angle_smoothed_B_y",
    # -- gaze corrected ----------------------------------------------------------------
    "gaze_point_corrected_A_x",
    "gaze_point_corrected_A_y",
    "gaze_point_corrected_B_x",
    "gaze_point_corrected_B_y",
    "gaze_angle_corrected_A_x",
    "gaze_angle_corrected_A_y",
    "gaze_angle_corrected_B_x",
    "gaze_angle_corrected_B_y",
    # -- gaze binocular ----------------------------------------------------------------
    "gaze_point_binocular_x",
    "gaze_point_binocular_y",
    # -- velocity ----------------------------------------------------------------------
    "total_velocity_A",
    "total_velocity_B",
    "component_velocity_A_x",
    "component_velocity_A_y",
    "component_velocity_B_x",
    "component_velocity_B_y",
    "velocity_binocular",
    # -- pupil -------------------------------------------------------------------------
    "pupil_size_A_x",
    "pupil_size_A_y",
    "pupil_size_B_x",
    "pupil_size_B_y",
    "pupil_aspect_ratio_A",
    "pupil_aspect_ratio_B",
    "pupil_angle_A",
    "pupil_angle_B",
    "pupil_diameter_A",
    "pupil_diameter_B",
    "pupil_point_A_x",
    "pupil_point_A_y",
    "pupil_point_B_x",
    "pupil_point_B_y",
    "pupil_centroid_A_x",
    "pupil_centroid_A_y",
    "pupil_centroid_B_x",
    "pupil_centroid_B_y",
    # -- glint -------------------------------------------------------------------------
    "diff_vector_A_x",
    "diff_vector_A_y",
    "diff_vector_B_x",
    "diff_vector_B_y",
    "glint_point_A_x",
    "glint_point_A_y",
    "glint_point_B_x",
    "glint_point_B_y",
    "glint_centroid_A_x",
    "glint_centroid_A_y",
    "glint_centroid_B_x",
    "glint_centroid_B_y",
    # -- data quality ------------------------------------------------------------------
    "data_quality_A",
    "data_quality_B",
    # -- timestamps --------------------------------------------------------------------
    "data_time_A",
    "data_time_B",
    "data_delta_time_A",
    "data_delta_time_B",
    "store_time_A",
    "store_time_B",
    "store_delta_time_A",
    "store_delta_time_B",
    # -- temp --------------------------------------------------------------------------
    "current_time"
]

# -- LSL Stream ------------------------------------------------------------------------
_SINFO = StreamInfo(
    "ViewPoint",
    "Gaze",
    len(_CH_NAMES),
    sfreq=_SAMPLING_RATE,
    dtype="float64",
    source_id="ViewPoint",
)
_OUTLET = StreamOutlet(_SINFO, chunk_size=1)


# -- callback --------------------------------------------------------------------------
_callback = CFUNCTYPE(c_int, c_int, c_int, c_int, c_int)


def callback(msg, sub_msg, p1, p2):  # noqa: D401
    """Callback function run when events are received from ViewPoint."""
    if msg == VPX_DAT_FRESH and sub_msg == EYE_A.value:
        now = local_clock()
        logger.debug("Fresh data available @ time %.2f (LSL).", now)
        # access data and store it in the shared variables in ViewPointDevice
        # -- gaze raw ------------------------------------------------------------------
        get_gaze_point(DEVICE, eye="A", processing="raw")
        get_gaze_point(DEVICE, eye="B", processing="raw")
        get_gaze_angle(DEVICE, eye="A", processing="raw")
        get_gaze_angle(DEVICE, eye="B", processing="raw")
        # -- gaze smoothed -------------------------------------------------------------
        get_gaze_point(DEVICE, eye="A", processing="smoothed")
        get_gaze_point(DEVICE, eye="B", processing="smoothed")
        get_gaze_angle(DEVICE, eye="A", processing="smoothed")
        get_gaze_angle(DEVICE, eye="B", processing="smoothed")
        # -- gaze corrected ------------------------------------------------------------
        get_gaze_point(DEVICE, eye="A", processing="corrected")
        get_gaze_point(DEVICE, eye="B", processing="corrected")
        get_gaze_angle(DEVICE, eye="A", processing="corrected")
        get_gaze_angle(DEVICE, eye="B", processing="corrected")
        # -- gaze binocular ------------------------------------------------------------
        get_gaze_point(DEVICE, eye="AB", processing=None)
        # -- velocity ------------------------------------------------------------------
        get_gaze_velocity(DEVICE, eye="A", property_name="total")
        get_gaze_velocity(DEVICE, eye="B", property_name="total")
        get_gaze_velocity(DEVICE, eye="A", property_name="component")
        get_gaze_velocity(DEVICE, eye="B", property_name="component")
        get_gaze_velocity(DEVICE, eye="AB", property_name="")
        # -- pupil ---------------------------------------------------------------------
        get_pupil_property(DEVICE, eye="A", property_name="size")
        get_pupil_property(DEVICE, eye="B", property_name="size")
        get_pupil_property(DEVICE, eye="A", property_name="aspect_ratio")
        get_pupil_property(DEVICE, eye="B", property_name="aspect_ratio")
        get_pupil_property(DEVICE, eye="A", property_name="angle")
        get_pupil_property(DEVICE, eye="B", property_name="angle")
        get_pupil_property(DEVICE, eye="A", property_name="diameter")
        get_pupil_property(DEVICE, eye="B", property_name="diameter")
        get_pupil_property(DEVICE, eye="A", property_name="point")
        get_pupil_property(DEVICE, eye="B", property_name="point")
        get_pupil_property(DEVICE, eye="A", property_name="centroid")
        get_pupil_property(DEVICE, eye="B", property_name="centroid")
        # -- glint ---------------------------------------------------------------------
        vpx_get_diff_vector(EYE_A, DEVICE.diff_vector["A"])
        vpx_get_diff_vector(EYE_B, DEVICE.diff_vector["B"])
        vpx_get_glint_point(EYE_A, DEVICE.glint_point["A"])
        vpx_get_glint_point(EYE_B, DEVICE.glint_point["B"])
        vpx_get_glint_centroid(EYE_A, DEVICE.glint_centroid["A"])
        vpx_get_glint_centroid(EYE_B, DEVICE.glint_centroid["B"])
        # -- data quality --------------------------------------------------------------
        vpx_get_data_quality(EYE_A, DEVICE.data_quality["A"])
        vpx_get_data_quality(EYE_B, DEVICE.data_quality["B"])
        # -- timestamps ----------------------------------------------------------------
        vpx_get_data_time(EYE_A, DEVICE.data_time["A"])
        vpx_get_data_time(EYE_B, DEVICE.data_time["B"])
        vpx_get_data_delta_time(EYE_A, DEVICE.data_delta_time["A"])
        vpx_get_data_delta_time(EYE_B, DEVICE.data_delta_time["B"])
        vpx_get_store_time(EYE_A, DEVICE.store_time["A"])
        vpx_get_store_time(EYE_A, DEVICE.store_time["B"])
        vpx_get_store_delta_time(EYE_A, DEVICE.store_delta_time["A"])
        vpx_get_store_delta_time(EYE_B, DEVICE.store_delta_time["B"])

        # figure out the corresponding LSL timestamp
        acquisition_time = DEVICE.store_time["A"]  # same for A and B
        current_time = VPX.VPX_GetPrecisionDeltaTime(None, c_int(0))

        # format the data selection into a numpy array
        data = np.array(
            [
                # -- gaze raw ----------------------------------------------------------
                DEVICE.gaze_point["A"].x,
                DEVICE.gaze_point["A"].y,
                DEVICE.gaze_point["B"].x,
                DEVICE.gaze_point["B"].y,
                DEVICE.gaze_angle["A"].x,
                DEVICE.gaze_angle["A"].y,
                DEVICE.gaze_angle["B"].x,
                DEVICE.gaze_angle["B"].y,
                # -- gaze smoothed -----------------------------------------------------
                DEVICE.gaze_point_smoothed["A"].x,
                DEVICE.gaze_point_smoothed["A"].y,
                DEVICE.gaze_point_smoothed["B"].x,
                DEVICE.gaze_point_smoothed["B"].y,
                DEVICE.gaze_angle_smoothed["A"].x,
                DEVICE.gaze_angle_smoothed["A"].y,
                DEVICE.gaze_angle_smoothed["B"].x,
                DEVICE.gaze_angle_smoothed["B"].y,
                # -- gaze corrected ----------------------------------------------------
                DEVICE.gaze_point_corrected["A"].x,
                DEVICE.gaze_point_corrected["A"].y,
                DEVICE.gaze_point_corrected["B"].x,
                DEVICE.gaze_point_corrected["B"].y,
                DEVICE.gaze_angle_corrected["A"].x,
                DEVICE.gaze_angle_corrected["A"].y,
                DEVICE.gaze_angle_corrected["B"].x,
                DEVICE.gaze_angle_corrected["B"].y,
                # -- gaze binocular ----------------------------------------------------
                DEVICE.gaze_point_binocular.x,
                DEVICE.gaze_point_binocular.y,
                # -- velocity ----------------------------------------------------------
                DEVICE.total_velocity["A"].value,
                DEVICE.total_velocity["B"].value,
                DEVICE.component_velocity["A"].x,
                DEVICE.component_velocity["A"].y,
                DEVICE.component_velocity["B"].x,
                DEVICE.component_velocity["B"].y,
                DEVICE.velocity_binocular.value,
                # -- pupil -------------------------------------------------------------
                DEVICE.pupil_size["A"].x,
                DEVICE.pupil_size["A"].y,
                DEVICE.pupil_size["B"].x,
                DEVICE.pupil_size["B"].y,
                DEVICE.pupil_aspect_ratio["A"].value,
                DEVICE.pupil_aspect_ratio["B"].value,
                DEVICE.pupil_angle["A"].value,
                DEVICE.pupil_angle["B"].value,
                DEVICE.pupil_diameter["A"].value,
                DEVICE.pupil_diameter["B"].value,
                DEVICE.pupil_point["A"].x,
                DEVICE.pupil_point["A"].y,
                DEVICE.pupil_point["B"].x,
                DEVICE.pupil_point["B"].y,
                DEVICE.pupil_centroid["A"].x,
                DEVICE.pupil_centroid["A"].y,
                DEVICE.pupil_centroid["B"].x,
                DEVICE.pupil_centroid["B"].y,
                # -- glint -------------------------------------------------------------
                DEVICE.diff_vector["A"].x,
                DEVICE.diff_vector["A"].y,
                DEVICE.diff_vector["B"].x,
                DEVICE.diff_vector["B"].y,
                DEVICE.glint_point["A"].x,
                DEVICE.glint_point["A"].y,
                DEVICE.glint_point["B"].x,
                DEVICE.glint_point["B"].y,
                DEVICE.glint_centroid["A"].x,
                DEVICE.glint_centroid["A"].y,
                DEVICE.glint_centroid["B"].x,
                DEVICE.glint_centroid["B"].y,
                # -- data quality ------------------------------------------------------
                DEVICE.data_quality["A"].value,
                DEVICE.data_quality["B"].value,
                # -- timestamps --------------------------------------------------------
                DEVICE.data_time["A"].value,
                DEVICE.data_time["B"].value,
                DEVICE.data_delta_time["A"].value,
                DEVICE.data_delta_time["B"].value,
                DEVICE.store_time["A"].value,
                DEVICE.store_time["B"].value,
                DEVICE.store_delta_time["A"].value,
                DEVICE.store_delta_time["B"].value,
                # -- temp --------------------------------------------------------------
                current_time,
            ],
            dtype=fmt2numpy[_OUTLET._dtype],
        )
        logger.debug("%s", data)
        _OUTLET.push_sample(data, timestamp=0)
    return 0  # exit code


# register the python callback function with the viewpoint DLL
_vpx_callback = _callback(callback)
VPX.VPX_InsertCallback(_vpx_callback)
