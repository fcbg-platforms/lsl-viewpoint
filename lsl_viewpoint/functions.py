from typing import TYPE_CHECKING

from .constants import EYE_A, EYE_B
from .vpx_lib import (
    vpx_get_gaze_angle,
    vpx_get_gaze_angle_corrected,
    vpx_get_gaze_angle_smoothed,
    vpx_get_gaze_binocular,
    vpx_get_gaze_point,
    vpx_get_gaze_point_corrected,
    vpx_get_gaze_point_smoothed,
)

if TYPE_CHECKING:
    from typing import Optional

    from .device import ViewPointDevice


def get_gaze_point(device: ViewPointDevice, eye: str, processing: Optional[str]) -> None:
    """Retrieve the gaze point for one or both eyes.

    Parameters
    ----------
    eye : 'A' | 'B' | 'AB'
        Eye selection. Use 'AB' for binocular selection.
    processing : None | 'smoothed' | 'corrected'
        Processing flag applied to the gaze point.
    """
    assert eye in ("A", "B", "AB"), "The eye selection should be 'A', 'B' or 'AB'."
    if eye == "AB":
        vpx_get_gaze_binocular(ViewPointDevice.gaze_point_binocular)
    else:
        if processing is None:
            accessor = vpx_get_gaze_point
            variable = ViewPointDevice.gaze_point
        elif processing == "smoothed":
            accessor = vpx_get_gaze_point_smoothed
            variable = ViewPointDevice.gaze_point_smoothed
        elif processing == "corrected":
            accessor = vpx_get_gaze_point_corrected
            variable = ViewPointDevice.gaze_point_corrected
        else:
            raise ValueError(
                "Argument 'processing' should be None, 'smoothed' or 'corrected'. "
                f"'{processing}' is invalid."
            )

        eye_idx = EYE_A if eye == "A" else EYE_B  # 0 for A, 1 for B
        accessor(eye_idx, variable[eye])


def get_gaze_angle(device: ViewPointDevice, eye: str, processing: Optional[str]) -> None:
    """Retrive the gaze angle for one eye.

    Parameters
    ----------
    eye : 'A' | 'B'
        Eye selection. Use 'AB' for binocular selection.
    processing : None | 'smoothed' | 'corrected'
        Processing flag applied to the gaze angle.
    """
    assert eye in ("A", "B"), "The eye selection should be 'A' or 'B'.
    if processing is None:
        accessor = vpx_get_gaze_angle
        variable = ViewPointDevice.gaze_angle
    elif processing == "smoothed":
        accessor = vpx_get_gaze_angle_smoothed
        variable = ViewPointDevice.gaze_angle_smoothed
    elif processing == "corrected":
        accessor = vpx_get_gaze_angle_corrected
        variable = ViewPointDevice.gaze_angle_corrected
    else:
        raise ValueError(
            "Argument 'processing' should be None, 'smoothed' or 'corrected'. "
            f"'{processing}' is invalid."
        )

    eye_idx = EYE_A if eye == "A" else EYE_B  # 0 for A, 1 for B
    accessor(eye_idx, variable[eye])
