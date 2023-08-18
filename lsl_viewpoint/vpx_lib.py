from ctypes import CDLL, CFUNCTYPE, POINTER, c_double, c_int, c_voidp, cdll, sizeof
from importlib.resources import files
from typing import TYPE_CHECKING

from .device import _RealPoint
from .utils._checks import ensure_path
from .utils.logs import logger

if TYPE_CHECKING:
    from pathlib import Path
    from typing import Optional, Union


_func_double_value = CFUNCTYPE(c_int, POINTER(c_double))
_func_double_value2 = CFUNCTYPE(c_int, c_int, POINTER(c_double))
_func_real_point = CFUNCTYPE(c_int, POINTER(_RealPoint))
_func_real_point2 = CFUNCTYPE(c_int, c_int, POINTER(_RealPoint))


def load_lib(path: Optional[Union[str, Path]] = None) -> CDLL:
    """Load the ViewPoint DLL.

    Parameters
    ----------
    path : path-like | None
        Path to the VPX_InterApp_64.dll to load.

    Returns
    -------
    vpx : CDLL
        The loaded library.
    """
    if not sizeof(c_voidp) == 8:
        raise RuntimeError("This package is for x64 system only.")
    if path is None:
        path = files("lsl_viewpoint") / "lib" / "VPX_InterApp_64.dll"
    else:
        path = ensure_path(path, must_exist=True)
    if path.name != "VPX_InterApp_64.dll":
        logger.warning(
            "The expected name of the DLL is 'VPX_InterApp_64.dll' corresponding to "
            "the x64 architecture. The provided DLL '%s' might or might not work.",
            path.name,
        )
    try:
        cdll.LoadLibrary(path)
        vpx = CDLL(path)
    except Exception:
        raise RuntimeError(
            "The DLL could not be loaded. Please check the version and the "
            "dependencies."
        )
    return vpx


vpx = load_lib()

# -- accessor functions ----------------------------------------------------------------
# gaze point
vpx_get_gaze_point = _func_real_point2(vpx.VPX_GetGazePoint2)
vpx_get_gaze_point_smoothed = _func_real_point2(vpx.VPX_GetGazePointSmoothed2)
vpx_get_gaze_point_corrected = _func_real_point2(vpx.VPX_GetGazePointCorrected2)
vpx_get_gaze_binocular = _func_real_point(vpx.VPX_GetGazeBinocular)
# gaze angle
vpx_get_gaze_angle = _func_real_point2(vpx.VPX_GetGazeAngle2)
vpx_get_gaze_angle_smoothed = _func_real_point2(vpx.VPX_GetGazeAngleSmoothed2)
vpx_get_gaze_angle_corrected = _func_real_point2(vpx.VPX_GetGazeAngleCorrected2)
# velocity
vpx_get_total_velocity = _func_double_value2(vpx.VPX_GetTotalVelocity2)
vpx_get_component_velocity = _func_real_point2(vpx.VPX_GetComponentVelocity2)
vpx_get_velocity_binocular = _func_double_value(vpx.VPX_GetVelocityBinocular)
# blink
vpx_get_blink_event = _func_double_value2(vpx.VPX_GetBlinkEvent2)
# pupil and glint
vpx_get_pupil_size = _func_real_point2(vpx.VPX_GetPupilSize2)
vpx_get_pupil_aspect_ratio = _func_double_value2(vpx.VPX_GetPupilAspectRatio2)
vpx_get_pupil_angle = _func_double_value2(vpx.VPX_GetPupilAngle2)
vpx_get_pupil_diameter = _func_double_value2(vpx.VPX_GetPupilDiameter2)
vpx_get_pupil_point = _func_real_point2(vpx.VPX_GetPupilPoint2)
vpx_get_pupil_centroid = _func_real_point2(vpx.VPX_GetPupilCentroid2)
vpx_get_diff_vector = _func_real_point2(vpx.VPX_GetDiffVector2)
vpx_get_glint_point = _func_real_point2(vpx.VPX_GetGlintPoint2)
vpx_get_glint_centroid = _func_real_point2(vpx.VPX_GetGlintCentroid2)
# data quality
vpx_get_data_quality = _func_double_value2(vpx.VPX_GetDataQuality2)
# timestamps
vpx_get_data_time = _func_double_value2(vpx.VPX_GetDataTime2)
vpx_get_data_delta_time = _func_double_value2(vpx.VPX_GetDataDeltaTime2)
vpx_get_store_time = _func_double_value2(vpx.VPX_GetStoreTime2)
vpx_get_store_delta_time = _func_double_value2(vpx.VPX_GetStoreDeltaTime2)
