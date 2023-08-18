from ctypes import Structure, c_double, c_float
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Dict


class _RealPoint(Structure):
    """Represents a real point on a 2D plane (x, y)."""

    _fields_ = [("x", c_float), ("y", c_float)]


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

        # blink events
        self._blink_event = {"A": c_double(0.0), "B": c_double(0.0)}

        # pupil and glint
        self._pupil_size = {"A": _RealPoint(1.0, 1.0), "B": _RealPoint(1.0, 1.0)}
        self._pupil_aspect_ratio = {"A": c_double(0.0), "B": c_double(0.0)}
        self._pupil_angle = {"A": c_double(0.0), "B": c_double(0.0)}
        self._pupil_diameter = {"A": c_double(0.0), "B": c_double(0.0)}
        self._pupil_point = {"A": _RealPoint(1.0, 1.0), "B": _RealPoint(1.0, 1.0)}
        self._pupil_centroid = {"A": _RealPoint(1.0, 1.0), "B": _RealPoint(1.0, 1.0)}
        self._diff_vector = {"A": _RealPoint(1.0, 1.0), "B": _RealPoint(1.0, 1.0)}
        self._glint_point = {"A": _RealPoint(1.0, 1.0), "B": _RealPoint(1.0, 1.0)}
        self._glint_centroid = {"A": _RealPoint(1.0, 1.0), "B": _RealPoint(1.0, 1.0)}

        # data quality
        self._data_quality = {"A": c_double(0.0), "B": c_double(0.0)}

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
    def blink_event(self) -> Dict[str, c_double]:
        return self._blink_event

    @property
    def pupil_size(self) -> Dict[str, _RealPoint]:
        return self._pupil_size

    @property
    def pupil_aspect_ratio(self) -> Dict[str, c_double]:
        return self._pupil_aspect_ratio

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
    def data_quality(self) -> Dict[str, c_double]:
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
