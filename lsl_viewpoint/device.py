from __future__ import annotations  # post-poned evaluation of annotations

from ctypes import Structure, c_double, c_float, c_int
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Dict


_VPX_EyeType = c_int
_VPX_DataQuality = c_int
_VPX_GlintDataQuality = c_int
_VPX_RealType = c_float


# -- constants -------------------------------------------------------------------------
# EyeType
EYE_A = _VPX_EyeType(0)
EYE_B = _VPX_EyeType(1)
SCENE_A = _VPX_EyeType(2)
SCENE_B = _VPX_EyeType(3)
OBSERVER = _VPX_EyeType(4)
VIDEO_SCREEN = _VPX_EyeType(5)
EYE_MOVIE_CHANNEL = _VPX_EyeType(6)
DUAL_EYE_MOVIE_CHANNEL = _VPX_EyeType(7)
MAX_ROUTING = _VPX_EyeType(8)
# Data quality
VPX_QUALITY_GlintIsGood = _VPX_DataQuality(0)
VPX_QUALITY_PupilOnlyIsGood = _VPX_DataQuality(1)
VPX_QUALITY_PupilFallBack = _VPX_DataQuality(2)
VPX_QUALITY_PupilCriteriaFailed = _VPX_DataQuality(3)
VPX_QUALITY_PupilFitFailed = _VPX_DataQuality(4)
VPX_QUALITY_PupilScanFailed = _VPX_DataQuality(5)
# Multi-glint quality codes
VPX_GLINT_QUALITY_Good = _VPX_GlintDataQuality(0)
VPX_GLINT_QUALITY_NoOperation = _VPX_GlintDataQuality(1)
VPX_GLINT_QUALITY_AspectCriteriaFailed = _VPX_GlintDataQuality(2)
VPX_GLINT_QUALITY_WidthCriteriaFailed = _VPX_GlintDataQuality(3)
VPX_GLINT_QUALITY_FitFailed = _VPX_GlintDataQuality(4)
VPX_GLINT_QUALITY_ScanFailed = _VPX_GlintDataQuality(5)
# Other
VPX_STATUS_ViewPointIsRunning = 1
VPX_DAT_FRESH = 2
ROI_NO_EVENT = -9999


# -- structures ------------------------------------------------------------------------
class _RealPoint(Structure):
    """Represent a real point on a 2D plane (x, y).

    Corresponds to VPX_RealPoint.
    """

    _fields_ = [("x", _VPX_RealType), ("y", _VPX_RealType)]


class _RealPoint3D(Structure):
    """Represent a real point in a 3D space (x, y, z).

    Corresponds to VPX_RealPoint3D.
    """

    _fields_ = [("x", _VPX_RealType), ("y", _VPX_RealType), ("z", _VPX_RealType)]


class _RealRect(Structure):
    """Represent a rectangle.

    Corresponds to VPX_RealRect.
    """

    _fields_ = [
        ("left", _VPX_RealType),
        ("top", _VPX_RealType),
        ("right", _VPX_RealType),
        ("bottom", _VPX_RealType),
    ]


class _PositionAngle(Structure):
    """Represent a position angle.

    Corresponds to VPX_PositionAngle.
    """

    _fields_ = [
        ("x", _VPX_RealType),
        ("y", _VPX_RealType),
        ("z", _VPX_RealType),
        ("roll", _VPX_RealType),
        ("pitch", _VPX_RealType),
        ("yaw", _VPX_RealType),
    ]


class _IntRect(Structure):
    """Represent an integer rectangle.

    Corresponds to VPX_IntRect.
    """

    _fields_ = [("left", c_int), ("top", c_int), ("right", c_int), ("bottom", c_int)]


class _GlintRecord(Structure):
    """Represent a glint record.

    Corresponds to VPX_GlintRecord.
    """

    _fields_ = [("glintPosition", _RealPoint), ("glintQuality", _VPX_GlintDataQuality)]


class ViewPointDevice:
    """ViewPoint device with reference to the shared variables.

    Parameters
    ----------
    bufsize : int
        Number of samples to keep in buffer.
    """

    def __init__(self, bufsize: int = 16) -> None:
        # gaze points
        self._gaze_point = {"A": _RealPoint(1.0, 1.0), "B": _RealPoint(1.0, 1.0)}
        self._gaze_point_smoothed = {
            "A": _RealPoint(1.0, 1.0),
            "B": _RealPoint(1.0, 1.0),
        }
        self._gaze_point_corrected = {
            "A": _RealPoint(1.0, 1.0),
            "B": _RealPoint(1.0, 1.0),
        }
        self._gaze_point_binocular = _RealPoint(1.0, 1.0)

        # gaze Angle
        self._gaze_angle = {"A": _RealPoint(1.0, 1.0), "B": _RealPoint(1.0, 1.0)}
        self._gaze_angle_smoothed = {
            "A": _RealPoint(1.0, 1.0),
            "B": _RealPoint(1.0, 1.0),
        }
        self._gaze_angle_corrected = {
            "A": _RealPoint(1.0, 1.0),
            "B": _RealPoint(1.0, 1.0),
        }

        # velocity
        self._total_velocity = {"A": c_double(0.0), "B": c_double(0.0)}
        self._component_velocity = {
            "A": _RealPoint(1.0, 1.0),
            "B": _RealPoint(1.0, 1.0),
        }
        self._velocity_binocular = c_double(0.0)

        # pupil and glint
        self._pupil_size = {"A": _RealPoint(1.0, 1.0), "B": _RealPoint(1.0, 1.0)}
        self._pupil_aspect_ratio = {"A": c_double(0.0), "B": c_double(0.0)}
        self._pupil_oval_rect = {
            "A": _RealRect(1.0, 1.0, 1.0, 1.0),
            "B": _RealRect(1.0, 1.0, 1.0, 1.0),
        }
        self._pupil_angle = {"A": c_double(0.0), "B": c_double(0.0)}
        self._pupil_diameter = {"A": c_double(0.0), "B": c_double(0.0)}
        self._pupil_point = {"A": _RealPoint(1.0, 1.0), "B": _RealPoint(1.0, 1.0)}
        self._pupil_centroid = {"A": _RealPoint(1.0, 1.0), "B": _RealPoint(1.0, 1.0)}
        self._diff_vector = {"A": _RealPoint(1.0, 1.0), "B": _RealPoint(1.0, 1.0)}
        self._glint_point = {"A": _RealPoint(1.0, 1.0), "B": _RealPoint(1.0, 1.0)}
        self._glint_centroid = {"A": _RealPoint(1.0, 1.0), "B": _RealPoint(1.0, 1.0)}

        # data quality
        self._data_quality = {"A": _VPX_DataQuality(0), "B": _VPX_DataQuality(0)}

        # timestamps
        self._data_time = {"A": c_double(0.0), "B": c_double(0.0)}
        self._data_delta_time = {"A": c_double(0.0), "B": c_double(0.0)}
        self._store_time = {"A": c_double(0.0), "B": c_double(0.0)}
        self._store_delta_time = {"A": c_double(0.0), "B": c_double(0.0)}

    @property
    def gaze_point(self) -> Dict[str, _RealPoint]:
        return self._gaze_point

    @property
    def gaze_point_smoothed(self) -> Dict[str, _RealPoint]:
        return self._gaze_point_smoothed

    @property
    def gaze_point_corrected(self) -> Dict[str, _RealPoint]:
        return self._gaze_point_corrected

    @property
    def gaze_point_binocular(self) -> _RealPoint:
        return self._gaze_point_binocular

    @property
    def gaze_angle(self) -> Dict[str, _RealPoint]:
        return self._gaze_angle

    @property
    def gaze_angle_smoothed(self) -> Dict[str, _RealPoint]:
        return self._gaze_angle_smoothed

    @property
    def gaze_angle_corrected(self) -> Dict[str, _RealPoint]:
        return self._gaze_angle_corrected

    @property
    def total_velocity(self) -> Dict[str, c_double]:
        return self._total_velocity

    @property
    def component_velocity(self) -> Dict[str, _RealPoint]:
        return self._component_velocity

    @property
    def velocity_binocular(self) -> c_double:
        return self._velocity_binocular

    @property
    def pupil_size(self) -> Dict[str, _RealPoint]:
        return self._pupil_size

    @property
    def pupil_aspect_ratio(self) -> Dict[str, c_double]:
        return self._pupil_aspect_ratio

    @property
    def pupil_oval_rect(self) -> Dict[str, _RealRect]:
        return self._pupil_oval_rect

    @property
    def pupil_angle(self) -> Dict[str, c_double]:
        return self._pupil_angle

    @property
    def pupil_diameter(self) -> Dict[str, c_double]:
        return self._pupil_diameter

    @property
    def pupil_point(self) -> Dict[str, _RealPoint]:
        return self._pupil_point

    @property
    def pupil_centroid(self) -> Dict[str, _RealPoint]:
        return self._pupil_centroid

    @property
    def diff_vector(self) -> Dict[str, _RealPoint]:
        return self._diff_vector

    @property
    def glint_point(self) -> Dict[str, _RealPoint]:
        return self._glint_point

    @property
    def glint_centroid(self) -> Dict[str, _RealPoint]:
        return self._glint_centroid

    @property
    def data_quality(self) -> Dict[str, c_int]:
        return self._data_quality

    @property
    def data_time(self) -> Dict[str, c_double]:
        return self._data_time

    @property
    def data_delta_time(self) -> Dict[str, c_double]:
        return self._data_delta_time

    @property
    def store_time(self) -> Dict[str, c_double]:
        return self._store_time

    @property
    def store_delta_time(self) -> Dict[str, c_double]:
        return self._store_delta_time
